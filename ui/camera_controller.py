import math

from config import settings


class CameraControllerUI:
    def __init__(self):
        self.movement_active = False
        self.look_active = False
        self.movement_vector = (0.0, 0.0)
        self.look_vector = (0.0, 0.0)
        self.knob_offset = (0.0, 0.0)

    def get_layout(self, width, height):
        radius = max(42.0, min(width, height) * 0.055)
        margin = radius * 0.9
        gap = radius * 0.3
        zoom_width = radius * 0.75
        zoom_height = radius * 0.5

        zoom_top = height - margin - zoom_height
        center_x = width - margin - radius * 1.18
        center_y = zoom_top - gap - radius * 1.18

        minus_rect = (center_x - gap * 0.5 - zoom_width, zoom_top, zoom_width, zoom_height)
        plus_rect = (center_x + gap * 0.5, zoom_top, zoom_width, zoom_height)

        return {
            "center": (center_x, center_y),
            "radius": radius,
            "zoom_regions": {"ZOOM_OUT": minus_rect, "ZOOM_IN": plus_rect},
            "elements": self._build_elements(center_x, center_y, radius, minus_rect, plus_rect),
        }

    def begin_movement_drag(self, xpos, ypos, width, height):
        if not self._inside_joystick(xpos, ypos, width, height):
            return False
        self.movement_active = True
        self.update_movement_drag(xpos, ypos, width, height)
        return True

    def update_movement_drag(self, xpos, ypos, width, height):
        if not self.movement_active:
            return 0.0, 0.0
        self.movement_vector = self._drag_vector(xpos, ypos, width, height)
        return self.movement_vector

    def end_movement_drag(self):
        self.movement_active = False
        self.movement_vector = (0.0, 0.0)
        self._release_knob()

    def begin_look_drag(self, xpos, ypos, width, height):
        if not self._inside_joystick(xpos, ypos, width, height):
            return False
        self.look_active = True
        self.update_look_drag(xpos, ypos, width, height)
        return True

    def update_look_drag(self, xpos, ypos, width, height):
        if not self.look_active:
            return 0.0, 0.0
        self.look_vector = self._drag_vector(xpos, ypos, width, height)
        return self.look_vector

    def end_look_drag(self):
        self.look_active = False
        self.look_vector = (0.0, 0.0)
        self._release_knob()

    def hit_test_zoom_controls(self, xpos, ypos, width, height):
        for action, (x, y, w, h) in self.get_layout(width, height)["zoom_regions"].items():
            if x <= xpos <= x + w and y <= ypos <= y + h:
                return action
        return None

    def _inside_joystick(self, xpos, ypos, width, height):
        layout = self.get_layout(width, height)
        center_x, center_y = layout["center"]
        return math.hypot(xpos - center_x, ypos - center_y) <= layout["radius"] * 1.18

    def _drag_vector(self, xpos, ypos, width, height):
        layout = self.get_layout(width, height)
        center_x, center_y = layout["center"]
        max_distance = layout["radius"]

        dx = xpos - center_x
        dy = ypos - center_y
        distance = math.hypot(dx, dy)
        if distance > max_distance:
            dx = dx / distance * max_distance
            dy = dy / distance * max_distance

        self.knob_offset = (dx, dy)

        vector_x = dx / max_distance
        vector_y = -dy / max_distance
        if math.hypot(vector_x, vector_y) < settings.JOYSTICK_DEADZONE:
            return 0.0, 0.0
        return vector_x, vector_y

    def _release_knob(self):
        if not self.movement_active and not self.look_active:
            self.knob_offset = (0.0, 0.0)

    def _build_elements(self, center_x, center_y, radius, minus_rect, plus_rect):
        dragging = self.movement_active or self.look_active
        knob_color = settings.JOYSTICK_ACTIVE_COLOR if dragging else settings.JOYSTICK_CENTER_COLOR

        elements = [
            {"vertices": self._circle(center_x, center_y, radius * 1.18, 36), "color": settings.JOYSTICK_BASE_COLOR},
            {"vertices": self._circle(center_x, center_y, radius, 32), "color": settings.JOYSTICK_FILL_COLOR},
            {
                "vertices": self._circle(
                    center_x + self.knob_offset[0],
                    center_y + self.knob_offset[1],
                    radius * 0.34,
                    24,
                ),
                "color": knob_color,
            },
        ]

        for rect in (minus_rect, plus_rect):
            elements.append({"vertices": self._rect(*rect), "color": settings.ZOOM_BORDER_COLOR})
            elements.append({"vertices": self._rect(rect[0] + 3.0, rect[1] + 3.0, rect[2] - 6.0, rect[3] - 6.0), "color": settings.ZOOM_FILL_COLOR})

        elements.append({"vertices": self._minus_symbol(minus_rect), "color": settings.ZOOM_SYMBOL_COLOR})
        elements.append({"vertices": self._plus_symbol(plus_rect), "color": settings.ZOOM_SYMBOL_COLOR})
        return elements

    def _rect(self, x, y, width, height):
        return [x, y, x + width, y, x + width, y + height, x, y, x + width, y + height, x, y + height]

    def _circle(self, center_x, center_y, radius, segments):
        vertices = []
        for index in range(segments):
            angle_a = (2.0 * math.pi * index) / segments
            angle_b = (2.0 * math.pi * (index + 1)) / segments
            vertices.extend(
                [
                    center_x, center_y,
                    center_x + math.cos(angle_a) * radius, center_y + math.sin(angle_a) * radius,
                    center_x + math.cos(angle_b) * radius, center_y + math.sin(angle_b) * radius,
                ]
            )
        return vertices

    def _minus_symbol(self, rect):
        x, y, width, height = rect
        bar_width = width * 0.50
        bar_height = max(4.0, height * 0.12)
        return self._rect(x + (width - bar_width) * 0.5, y + (height - bar_height) * 0.5, bar_width, bar_height)

    def _plus_symbol(self, rect):
        x, y, width, height = rect
        bar_width = width * 0.50
        bar_height = max(4.0, height * 0.12)
        vertical_width = max(4.0, width * 0.12)
        horizontal = self._rect(x + (width - bar_width) * 0.5, y + (height - bar_height) * 0.5, bar_width, bar_height)
        vertical = self._rect(x + (width - vertical_width) * 0.5, y + height * 0.24, vertical_width, height * 0.52)
        return horizontal + vertical
