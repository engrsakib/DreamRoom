class Scene:
    def __init__(self):
        self.objects = []
        self.directional_light = None
        self.point_light = None
        self.spot_light = None
        self.lamp = None

    def add(self, obj):
        self.objects.append(obj)

    def update(self, delta_time):
        _ = delta_time

    def iter_objects(self):
        for obj in self.objects:
            yield obj
