from maix import app, nn, time

speech = nn.Speech("/root/models/am_3332_192_int8.mud")
speech.init(nn.SpeechDevice.DEVICE_MIC, "hw:0,0")

kw_tbl = ['xiao3 ai4 tong2 xue2',
          'tian1 mao1 jing1 ling2',
          'tian1 qi4 zen3 me yang4']
kw_gate = [0.1, 0.1, 0.1]
similar_char = ['xin1', 'ting1', 'jin1']

def kws_callback(data:list[float], len: int):
    maxp = -1
    for i in range(len):
        print(f"\tkw{i}: {data[i]:.3f};", end=' ')
        if data[i] > maxp:
            maxp = data[i]
    print("\n")

speech.kws(kw_tbl, kw_gate, kws_callback, True)

while not app.need_exit():
    frames = speech.run(1)
    if frames < 1:
        print("run out\n")
        break
