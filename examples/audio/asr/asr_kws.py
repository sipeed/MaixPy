from maix import app, nn

speech = nn.Speech("/root/models/am_3332_192_int8.mud")
speech.init(nn.SpeechDevice.DEVICE_MIC, "hw:0,0")

kw_tbl = ['xiao3 ai4 tong2 xue2',
          'ni3 hao3',
          'tian1 qi4 zen3 me yang4']
kw_gate = [0.1, 0.1, 0.1]

def callback(data:list[float], len: int):
    for i in range(len):
        print(f"\tkw{i}: {data[i]:.3f};", end=' ')
    print("\n")

speech.kws(kw_tbl, kw_gate, callback, True)

while not app.need_exit():
    frames = speech.run(1)
    if frames < 1:
        print("run out\n")
        speech.deinit()
        break
