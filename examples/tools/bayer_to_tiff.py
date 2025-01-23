import numpy as np
import cv2

def read_12bit_packed_bayer(file_path, width, height):
    with open(file_path, 'rb') as f:
        raw_data = f.read()

    raw_data = np.frombuffer(raw_data, dtype=np.uint8)
    total_pixels = width * height
    bayer_data = np.zeros(total_pixels, dtype=np.uint16)

    for i in range(0, len(raw_data), 3):
        byte1 = raw_data[i]
        byte2 = raw_data[i + 1]
        byte3 = raw_data[i + 2]

        pixel1 = ((byte1 << 4) | (byte3 >> 4)) & 0xFFF  # 取低 12bit
        pixel2 = ((byte2 << 4) | (byte3 & 0xF)) & 0xFFF  # 取低 12bit

        idx = (i // 3) * 2
        if idx < total_pixels:
            bayer_data[idx] = pixel1
        if idx + 1 < total_pixels:
            bayer_data[idx + 1] = pixel2

    bayer_image = bayer_data.reshape((height, width))
    return bayer_image

def bayer_to_rgb(bayer_image, bayer_pattern=cv2.COLOR_BayerRG2RGB):
    bayer_image_16bit = (bayer_image << 4).astype(np.uint16)
    rgb_image = cv2.cvtColor(bayer_image_16bit, bayer_pattern)
    return rgb_image

def save_16bit_tiff(image, file_path):
    cv2.imwrite(file_path, image)

# If you wish to obtain the conversion results quickly, 
# we recommend running this tool on a PC. You will need to install opencv-python and numpy locally.

bayer_file_path = "/maixapp/share/picture/2025-01-23/xxx.raw"   # Your bayer image path
width = 2560
height = 1440
output_tiff_path = "/root/output.tiff"

print('read bayer')
bayer_image = read_12bit_packed_bayer(bayer_file_path, width, height)

print('bayer to rgb')
rgb_image = bayer_to_rgb(bayer_image)

print('save tiff')
save_16bit_tiff(rgb_image, output_tiff_path)
