from maix import image
import requests

# create image
img = image.Image(640, 480, image.Format.FMT_RGB)
# draw something
img.draw_rect(60, 60, 80, 80, image.Color.from_rgb(255, 0, 0))

# convert to jpeg
jpeg = img.to_format(image.Format.FMT_JPEG) # image.Format.FMT_PNG
# get jpeg bytes
jpeg_bytes = jpeg.to_bytes()

# faster way, borrow memory from jpeg object,
# but be carefully, when jpeg object is deleted, jpeg_bytes object MUST NOT be used, or program will crash
# jpeg_bytes = jpeg.to_bytes(copy = False)

# send image binary bytes to server
url = "http://192.168.0.123:8080/upload"
res = requests.post(url, data=jpeg_bytes)
print(res.status_code)
print(res.text)


