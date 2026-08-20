import math

from config import settings


class CameraControllerUI:
    def __init__(self):
        self.movement_active = False
        self.movement_vector = (0.0, 0.0)
        self.knob_offset = (0.0, 0.0)

    def get_layout(self, width, height):
        movement_radius = max(42.0, min(width, height) * 0.055)
        look_radius = movement_radius * 0.72
        margin = movement_radius * 0.9
        gap = movement_radius * 0.28
        look_pad = look_radius * 0.85

        movement_center_x = width - margin - movement_radius * 1.45
        movement_center_y = height - margin - movement_radius * 1.45

        look_center_x = movement_center_x
        look_center_y = movement_center_y - movement_radius * 3.1

        up_rect = (look_center_x - look_pad * 0.5, look_center_y - look_radius - gap - look_pad, look_pad, look_pad)
        down_rect = (look_center_x - look_pad * 0.5, look_center_y + look_radius + gap, look_pad, look_pad)
        left_rect = (look_center_x - look_radius - gap - look_pad, look_center_y - look_pad * 0.5, look_pad, look_pad)
        right_rect = (look_center_x + look_radius + gap, look_center_y - look_pad * 0.5, look_pad, look_pad)
        minus_rect = (look_center_x - look_pad - gap * 0.7, up_rect[1] - look_pad * 0.9, look_pad * 0.9, look_pad * 0.7)
        plus_rect = (look_center_x + gap * 0.7, up_rect[1] - look_pad * 0.9, look_pad * 0.9, look_pad * 0.7)

        layout = {
            "movement_center": (movement_center_x, movement_center_y),
            "movement_radius": movement_radius,
            "look_center": (look_center_x, look_center_y),
            "look_radius": look_radius,
            "look_regions": {
                "LOOK_UP": up_rect,
                "LOOK_DOWN": down_rect,
                "LOOK_LEFT": left_rect,
                "LOOK_RIGHT": right_rect,
                "ZOOM_OUT": minus_rect,
                "ZOOM_IN": plus_rect,
            },
            "elements": self._build_elements(
                movement_center_x,
                movement_center_y,
                movement_radius,
                look_center_x,
                look_center_y,
                look_radius,
                up_rect,
                down_rect,
                left_rect,
                right_rect,
                minus_rect,
                plus_rect,
            ),
        }
        return layout

    def begin_movement_drag(self, xpos, ypos, width, height):
        layout = self.get_layout(width, height)
        center_x, center_y = layout["movement_center"]
        radius = layout["movement_radius"] * 1.35
        hit = self._distance(xpos, ypos, center_x, center_y) <= radius
        if hit:
            self.movement_active = True
            self.update_movement_drag(xpos, ypos, width, height)
            return True
        return False

    def update_movement_drag(self, xpos, ypos, width, height):
        if not self.movement_active:
            return 0.0, 0.0

        layout = self.get_layout(width, height)
        center_x, center_y = layout["movement_center"]
        max_distance = layout["movement_radius"]

        dx = xpos - center_x
        dy = ypos - center_y
        distance = math.hypot(dx, dy)
        clamped_distance = min(distance, max_distance)

        if distance > 0.0:
            dx = dx / distance * clamped_distance
            dy = dy / distance * clamped_distance

        self.knob_offset = (dx, dy)

        joystick_x = dx / max_distance
        joystick_y = -dy / max_distance
        magnitude = min(1.0, math.hypot(joystick_x, joystick_y))

        if magnitude < settings.JOYSTICK_DEADZONE:
            self.movement_vector = (0.0, 0.0)
        else:
            self.movement_vector = (joystick_x, joystick_y)

        return self.movement_vector

    def end_movement_drag(self):
        self.movement_active = False
        self.movement_vector = (0.0, 0.0)
        self.knob_offset = (0.0, 0.0)

    def hit_test_look_controls(self, xpos, ypos, width, height):
        for action, rect in self.get_layout(width, height)["look_regions"].items():
            x, y, w, h = rect
            if x <= xpos <= x + w and y <= ypos <= y + h:
                return action
        return None

    def _build_elements(
        self,
        move_cx,
        move_cy,
        move_r,
        look_cx,
        look_cy,
        look_r,
        up_rect,
        down_rect,
        left_rect,
        right_rect,
        minus_rect,
        plus_rect,
    ):
        elements = [
            {"vertices": self._circle(move_cx, move_cy, move_r * 1.18, 32), "color": settings.JOYSTICK_BASE_COLOR},
            {"vertices": self._circle(move_cx, move_cy, move_r, 30), "color": settings.JOYSTICK_FILL_COLOR},
            {"vertices": self._circle(move_cx + self.knob_offset[0], move_cy + self.knob_offset[1], move_r * 0.32, 24), "color": settings.JOYSTICK_CENTER_COLOR},
            {"vertices": self._arrow_marker("UP", move_cx, move_cy, move_r * 1.28), "color": settings.JOYSTICK_ARROW_COLOR},
            {"vertices": self._arrow_marker("DOWN", move_cx, move_cy, move_r * 1.28), "color": settings.JOYSTICK_ARROW_COLOR},
            {"vertices": self._arrow_marker("LEFT", move_cx, move_cy, move_r * 1.28), "color": settings.JOYSTICK_ARROW_COLOR},
            {"vertices": self._arrow_marker("RIGHT", move_cx, move_cy, move_r * 1.28), "color": settings.JOYSTICK_ARROW_COLOR},
            {"vertices": self._circle(look_cx, look_cy, look_r * 1.16, 28), "color": settings.JOYSTICK_BASE_COLOR},
            {"vertices": self._circle(look_cx, look_cy, look_r, 24), "color": settings.JOYSTICK_FILL_COLOR},
            {"vertices": self._circle(look_cx, look_cy, look_r * 0.22, 18), "color": settings.JOYSTICK_CENTER_COLOR},
        ]

        for rect in (up_rect, down_rect, left_rect, right_rect):
            elements.append({"vertices": self._rect(rect[0], rect[1], rect[2], rect[3]), "color": settings.JOYSTICK_BASE_COLOR})
            elements.append({"vertices": self._rect(rect[0] + 3.0, rect[1] + 3.0, rect[2] - 6.0, rect[3] - 6.0), "color": settings.JOYSTICK_FILL_COLOR})

        elements.extend(
            [
                {"vertices": self._arrow("UP", up_rect), "color": settings.JOYSTICK_ARROW_COLOR},
                {"vertices": self._arrow("DOWN", down_rect), "color": settings.JOYSTICK_ARROW_COLOR},
                {"vertices": self._arrow("LEFT", left_rect), "color": settings.JOYSTICK_ARROW_COLOR},
                {"vertices": self._arrow("RIGHT", right_rect), "color": settings.JOYSTICK_ARROW_COLOR},
            ]
        )

        for rect in (minus_rect, plus_rect):
            elements.append({"vertices": self._rect(rect[0], rect[1], rect[2], rect[3]), "color": settings.ZOOM_BORDER_COLOR})
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

    def _arrow(self, direction, rect):
        x, y, width, height = rect
        center_x = x + width * 0.5
        center_y = y + height * 0.5
        if direction == "UP":
            points = [(center_x, y + height * 0.22), (x + width * 0.28, y + height * 0.66), (x + width * 0.72, y + height * 0.66)]
        elif direction == "DOWN":
            points = [(center_x, y + height * 0.78), (x + width * 0.28, y + height * 0.34), (x + width * 0.72, y + height * 0.34)]
        elif direction == "LEFT":
            points = [(x + width * 0.22, center_y), (x + width * 0.66, y + height * 0.28), (x + width * 0.66, y + height * 0.72)]
        else:
            points = [(x + width * 0.78, center_y), (x + width * 0.34, y + height * 0.28), (x + width * 0.34, y + height * 0.72)]

        vertices = []
        for px, py in points:
            vertices.extend([px, py])
        return vertices

    def _arrow_marker(self, direction, center_x, center_y, distance):
        size = distance * 0.16
        if direction == "UP":
            return [center_x, center_y - distance, center_x - size, center_y - distance + size * 1.2, center_x + size, center_y - distance + size * 1.2]
        if direction == "DOWN":
            return [center_x, center_y + distance, center_x - size, center_y + distance - size * 1.2, center_x + size, center_y + distance - size * 1.2]
        if direction == "LEFT":
            return [center_x - distance, center_y, center_x - distance + size * 1.2, center_y - size, center_x - distance + size * 1.2, center_y + size]
        return [center_x + distance, center_y, center_x + distance - size * 1.2, center_y - size, center_x + distance - size * 1.2, center_y + size]

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

    def _distance(self, x1, y1, x2, y2):
        return math.hypot(x1 - x2, y1 - y2)
