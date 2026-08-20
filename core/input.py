import glfw


class InputManager:
    def __init__(self):
        self.keys_down = set()
        self.keys_pressed = set()
        self.mouse_buttons_down = set()
        self.mouse_buttons_pressed = set()
        self.mouse_buttons_released = set()
        self.cursor_position = (0.0, 0.0)

    def attach(self, window):
        glfw.set_key_callback(window, self._on_key)
        glfw.set_mouse_button_callback(window, self._on_mouse_button)

    def _on_key(self, window, key, scancode, action, mods):
        _ = scancode, mods
        if action == glfw.PRESS:
            self.keys_down.add(key)
            self.keys_pressed.add(key)
        elif action == glfw.RELEASE:
            self.keys_down.discard(key)

    def _on_mouse_button(self, window, button, action, mods):
        _ = mods
        self.cursor_position = glfw.get_cursor_pos(window)
        if action == glfw.PRESS:
            self.mouse_buttons_down.add(button)
            self.mouse_buttons_pressed.add(button)
        elif action == glfw.RELEASE:
            self.mouse_buttons_down.discard(button)
            self.mouse_buttons_released.add(button)

    def is_key_down(self, key):
        return key in self.keys_down

    def is_key_pressed(self, key):
        return key in self.keys_pressed

    def is_mouse_button_pressed(self, button):
        return button in self.mouse_buttons_pressed

    def is_mouse_button_down(self, button):
        return button in self.mouse_buttons_down

    def is_mouse_button_released(self, button):
        return button in self.mouse_buttons_released

    def get_mouse_position(self, window):
        self.cursor_position = glfw.get_cursor_pos(window)
        return self.cursor_position

    def end_frame(self):
        self.keys_pressed.clear()
        self.mouse_buttons_pressed.clear()
        self.mouse_buttons_released.clear()
