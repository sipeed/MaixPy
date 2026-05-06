from maix import key as _key


class Key:
    def __init__(self, *args, **kwargs):
        self._pressed = False
        self._key_obj = _key.Key(self._on_key)

    def _on_key(self, key_id, state):
        if state == _key.State.KEY_RELEASED:
            self._pressed = False
        else:  # KEY_PRESSED or KEY_LONG_PRESSED
            self._pressed = True

    def is_pressed(self) -> bool:
        return self._pressed

    def close(self) -> None:
        if self._key_obj is not None:
            del self._key_obj
            self._key_obj = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
