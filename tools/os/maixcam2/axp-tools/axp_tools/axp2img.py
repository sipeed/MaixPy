import argparse
import os
import sys
import xml.etree.ElementTree as ET
import shutil
import subprocess
import lzma
import zipfile
from tqdm import tqdm

def parse_xml(xml_path):
    '''
        parse xml get partition info
        xml: xml path, content example
            <Config>
                <Project alias="AX620E" name="AX630C" version="V3.0.0_20250319114413_20250711103651">
                    <FDLLevel>2</FDLLevel>

                    <Partitions strategy="1" unit="2">

                    <Partition gap="0" id="spl" size="768" />
                    <Partition gap="0" id="ddrinit" size="512" />
                    <Partition gap="0" id="atf" size="256" />
                    <Partition gap="0" id="atf_b" size="256" />
                    <Partition gap="0" id="uboot" size="1536" />
                    <Partition gap="0" id="uboot_b" size="1536" />
                    <Partition gap="0" id="env" size="1024" />
                    <Partition gap="0" id="logo" size="6144" />
                    <Partition gap="0" id="logo_b" size="6144" />
                    <Partition gap="0" id="optee" size="1024" />
                    <Partition gap="0" id="optee_b" size="1024" />
                    <Partition gap="0" id="dtb" size="1024" />
                    <Partition gap="0" id="dtb_b" size="1024" />
                    <Partition gap="0" id="kernel" size="65536" />
                    <Partition gap="0" id="kernel_b" size="65536" />
                    <Partition gap="0" id="boot" size="131072" />
                    <Partition gap="0" id="rootfs" size="0xffffffff" />
                    </Partitions>
                    <ImgList>
                    <Img flag="2" name="INIT" select="1">
                        <ID>INIT</ID>
                        <Type>INIT</Type>
                        <Block>
                        <Base>0x0</Base>
                        <Size>0x0</Size>
                        </Block>
                        <File />
                        <Auth algo="0" />
                        <Description>Download init image file</Description>
                    </Img>
                    ...
        Return:
            [
                {
                    "start": xxx,
                    "size": xxx,
                    "content_size": xxx,
                    "file": xxx
                }
            ]
    '''
    tree = ET.parse(xml_path)
    root = tree.getroot()
    partitions = []

    # Find <Partitions>
    partitions_node = root.find('.//Partitions')
    if partitions_node is None:
        return []

    current_offset = 0

    # Build a map from partition id -> image file
    id_to_file = {}
    for img in root.findall('.//ImgList/Img'):
        part_id = img.find("ID").text.lower()
        file_value = img.find("File").text
        id_to_file[part_id] = file_value.strip() if file_value else None

    for part in partitions_node.findall('Partition'):
        part_id = part.attrib.get('id').lower()
        part_size = int(part.attrib.get('size'), 0)  # support hex (like 0xffffffff)
        if part_size == 0xffffffff:
            part_size = 0

        info = {
            "id": part_id,
            "start": current_offset,
            "size": part_size * 1024, # KiB to B
            "file": id_to_file.get(part_id)
        }

        partitions.append(info)
        current_offset += info["size"]  # assume no gap for simplicity

    return partitions

def bytes_human(size):
    if size < 1024:
        return f"{size}B"
    if size < 1024 * 1024:
        return f"{size // 1024}KiB"
    if size < 1024 * 1024 * 1024:
        return f"{size / 1024 // 1024}MiB"
    return f"{size / 1024 / 1024 // 1024}GiB"

def compress_to_xz_auto(src_path, dst_path, threads=0):
    if shutil.which("xz"):
        print("Compress with system's xz command")
        src_xz = src_path + ".xz"
        if os.path.exists(src_xz):
            print(f"auto removed {src_xz}")
            os.remove(src_xz)
        cmd = ["xz", "-z", "-k", "-9", "-v", f"-T{threads}", src_path]
        subprocess.run(cmd, check=True)
        # move src_path.xz to dst_path
        if os.path.exists(src_xz):
            os.replace(src_xz, dst_path)
        else:
            raise FileNotFoundError(f"Expected compressed file {src_xz} not found.")
    else:
        print("xz command not found, use python lzma to compress(single thread)")
        with open(src_path, 'rb') as src, lzma.open(dst_path, 'wb') as dst:
            shutil.copyfileobj(src, dst)

def check_env():
    if not shutil.which("simg2img"):
        print("[ERROR] simg2img command not found, please install first")
        return False
    if not shutil.which("xz"):
        print("[WARNING] xz command not found, please install first")
    return True

def axp2img(arg_input, arg_output):
    if not check_env():
        return -1

    file_name = os.path.splitext(os.path.basename(arg_input))[0]
    if os.path.isfile(arg_input):
        input_dir = os.path.abspath(os.path.dirname(arg_input))
        temp_dir = os.path.join(input_dir, "temp")
        os.makedirs(temp_dir, exist_ok=True)
        print(f"unzip axp to {temp_dir}...")
        out_dir = os.path.join(input_dir, "out")
        # unzip arg_input to temp_dir
        with zipfile.ZipFile(arg_input, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        arg_input = temp_dir
    else:
        out_dir = os.path.join(arg_input, "out")
        temp_dir = os.path.join(arg_input, "temp")

    if not arg_output:
        arg_output = os.path.join(out_dir, f"{file_name}.img.xz")

    supported_format = [".xz", ".img"]
    format = os.path.splitext(arg_output)[1]
    if format not in supported_format:
        print(f"Not support output format {format}, supported: {supported_format}")
        sys.exit(1)

    print(f"Out:\n\t{arg_output}")

    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(temp_dir, exist_ok=True)

    # find xml file
    files = os.listdir(arg_input)
    xml_path = None
    for name in files:
        if name.endswith(".xml"):
            xml_path = os.path.join(arg_input, name)
            break
    if not xml_path:
        print(f"xml file not found in {arg_input}")
        sys.exit(1)
    info = parse_xml(xml_path)
    print("part info:")
    for i, part in enumerate(info):
        print(f"\tPart {i + 1}: {part['id']}")
        print(f"\t         start: {part['start']} ({bytes_human(part['start'])})")
        print(f"\t          size: { 'AUTO' if part['size'] == 0 else bytes_human(part['size'])}")
        print(f"\t          file: {part['file']}")
    print("")

    for i, part in enumerate(info):
        if part["file"] and "sparse" in part["file"]:
            print("recover sparse filesystem file ...")
            out_name = part["file"].replace("sparse", "raw")
            os.makedirs(temp_dir, exist_ok=True)
            raw_path = os.path.join(temp_dir, out_name)
            if os.path.exists(raw_path):
                os.remove(raw_path)
            sparse_file = os.path.join(arg_input, part['file'])
            cmd = f"simg2img {sparse_file} {raw_path}"
            print("Execute:", cmd)
            print("Source file size:", bytes_human(os.path.getsize(sparse_file)))
            ret = os.system(cmd)
            if ret != 0:
                print("simg2img command execute failed")
                sys.exit(1)
            part["file"] = os.path.relpath(raw_path, arg_input)
            part["size"] = os.path.getsize(raw_path)
            print(f"{part['file']} size: {bytes_human(part['size'])}")

    # generate bin file
    print("Generate bin file ...")
    out_img_path = arg_output if arg_output.endswith(".img") else os.path.join(out_dir, f"{file_name}.img")
    with open(out_img_path, "wb") as f:
        chunk_size = 1024 * 1024
        for i, part in enumerate(info):
            print(f"\n\n[{i}/{len(info)}] Writing {part['id']}, size: {bytes_human(part['size'])}:")
            padding_size = part["size"]
            if part["file"]:
                file = os.path.join(arg_input, part["file"])
                file_size = os.path.getsize(file)
                padding_size = part["size"] - file_size
                pbar = tqdm(total=file_size, unit='B', unit_scale=True, unit_divisor=1024, desc=f"[{part['id']}] {part['file']}")
                with open(file, "rb") as f2:
                    while True:
                        chunk = f2.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        pbar.update(len(chunk))
                del pbar
                import gc
                gc.collect()
            if padding_size != 0:
                zero_block = b'\x00' * chunk_size
                full_chunks = padding_size // chunk_size
                remainder = padding_size % chunk_size
                pbar2 = tqdm(total=padding_size, unit='B', unit_scale=True, unit_divisor=1024, desc=f"[{part['id']}] padding")

                for _ in range(full_chunks):
                    f.write(zero_block)
                    pbar2.update(chunk_size)
                if remainder:
                    f.write(b'\x00' * remainder)
                    pbar2.update(remainder)
                del pbar2
                import gc
                gc.collect()

    # xz
    if arg_output.endswith(".xz"):
        print("\nCompress to xz format:")
        print("                   from:", out_img_path)
        print("                     to:", arg_output)
        compress_to_xz_auto(out_img_path, arg_output)
        print("xz compress complete, remove img file")
        os.remove(out_img_path)
        print("xz file saved to", arg_output)

    if temp_dir:
        shutil.rmtree(temp_dir)

def main():
    parser = argparse.ArgumentParser(description="convert axp file to image bin file")
    parser.add_argument("-i", "--input", type=str, default="", required=True, help="input axp file path")
    parser.add_argument("-o", "--output", type=str, default="", help="output file path, default same dir as axp file with .img.xz format")
    args = parser.parse_args()

    sys.exit(axp2img(args.input, args.output))

if __name__ == "__main__":
    main()
