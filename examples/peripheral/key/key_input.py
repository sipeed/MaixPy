from maix import image, key, app, display

g_key = 0
g_state = 0

def on_key(key_id, state):
    '''
        this func called in a single thread
    '''
    global g_key, g_state
    print(f"key: {key_id}, state: {state}") # key.c or key.State.KEY_RELEASED
    g_key = key_id
    g_state = state

# Init key will cancel the default ok button function(exit app)
key = key.Key(on_key)
disp = display.Display()

while not app.need_exit():
    img = image.Image(disp.width(), disp.height(), image.Format.FMT_RGB888)
    msg = f"key: {g_key}, state: {g_state}"
    img.draw_string(0, 10, msg, image.Color.from_rgb(255, 255, 255), 1.5)
    disp.show(img)
