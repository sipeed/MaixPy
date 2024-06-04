from maix import image, key, app, display

class App:
    def __init__(self):
        self.key_obj = key.Key(self.on_key)
        self.disp = display.Display()
        self.key_id = 0
        self.state = 0

    def on_key(self, key_id, state):
        '''
            this func called in a single thread
        '''
        print(f"key: {key_id}, state: {state}") # key.c or key.State.KEY_RELEASED
        self.key_id = key_id
        self.state = state

    def run(self):
        while not app.need_exit():
            img = image.Image(self.disp.width(), self.disp.height(), image.Format.FMT_RGB888)
            msg = f"key: {self.key_id}, state: {self.state}"
            img.draw_string(0, 10, msg, image.Color.from_rgb(255, 255, 255), 1.5)
            self.disp.show(img)

App().run()
