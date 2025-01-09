from maix import i18n

trans_dict = {
    "zh": {
        "hello": "你好"
    },
    "en": {
    }
}

trans = i18n.Trans(trans_dict)
tr = trans.tr

trans.set_locale("zh")
print(tr("hello"))
print(tr("my friend"))

