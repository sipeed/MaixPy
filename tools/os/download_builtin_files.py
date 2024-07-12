import os
import sys
import requests
import subprocess
import tarfile
import zipfile

curr_dir = os.path.abspath(os.path.dirname(__file__))

def get_release_builtin_files_url():
    owner = "sipeed"
    repo = "MaixPy"
    url = f"https://api.github.com/repos/{owner}/{repo}/releases"

    # Make the request to the GitHub API
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        releases = response.json()
        releases = sorted(releases, key=lambda x: x['created_at'], reverse=True)
        release = releases[0]
        for asset in release['assets']:
            if "builtin_files" in asset['name']:
                if (not asset['name'].endswith(".zip")) and ((not asset['name'].endswith(".tar.xz"))) and (not asset['name'].endswith(".xz")):
                    raise Exception(f"bultin_files only support .zip, .tar.xz, .xz format, but found {asset['name']}")
                return asset['browser_download_url'], asset['name']
    else:
        raise Exception(f"Failed to retrieve releases: {response.status_code}")
    return None, None

def download_file(url, output_path, force=False):
    save_dir = os.path.dirname(output_path)
    # Ensure the save directory exists
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    if os.path.exists(output_path) and not force:
        print(f"-- file {os.path.basename(output_path)} already exists, skip download")
        return
    try:
        # Use subprocess to call wget
        subprocess.run(
            ["wget", "--progress=dot:giga", "-O", output_path, url],
            check=True
        )
        print(f"Download completed: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

def unzip(file_path, unzip_path):
    """
    解压文件
    支持 .xz .tar.xz .zip 格式
    """
    ext = os.path.splitext(file_path)[1]
    if ext not in [".xz", ".tar.xz", ".zip"]:
        raise Exception("file format not support unzip")
    if not os.path.exists(unzip_path):
        os.makedirs(unzip_path)

    if file_path.endswith('.tar.xz') or file_path.endswith('.xz'):
        with tarfile.open(file_path, 'r:xz') as tar:
            tar.extractall(path=unzip_path, filter='data')
    elif file_path.endswith('.zip'):
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(unzip_path)
    else:
        raise ValueError("Unsupported file format")

def get_builtin_files(file_path = "", unzip_path=""):
    url, filename = get_release_builtin_files_url()
    if not url:
        raise Exception("get base system image download url failed")
    print(f"-- download os builtin files {filename} from url: {url}")
    if not file_path:
        file_path = os.path.join(curr_dir, "tmp", filename)
    download_file(url, file_path)
    if unzip_path:
        unzip(file_path, unzip_path)
        return unzip_path
    return file_path


if __name__ == "__main__":
    import argparse
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument(
        "-o", "--out", help="download file path, default will save to tmp/***.img.xz", default="",
    )
    args_parser.add_argument(
        "--unzip", help="directly unzip files to --out dir", type=str, default="",
    )
    args = args_parser.parse_args()

    os_builtin_files = get_builtin_files(args.out, args.unzip)
    print(f"\n-- got builtin files: {os_builtin_files}")

