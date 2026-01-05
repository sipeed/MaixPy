from maix import sdv1_5

model = sdv1_5.SDV1_5("/root/models/lcm-lora-sdv1-5-maixcam2/model.mud")
model.init(img2img=True)
model.refer(prompt="A white dog.", save_path="/root/text2img.jpg")
model.refer(prompt="Replace the dog with a cat.", init_image_path="/root/text2img.jpg", seed=1, save_path="/root/img2img.jpg")

model.deinit()