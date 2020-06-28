import bpy
from math import cos, floor, radians
from typing import Union
from mathutils import Quaternion


# Object Keyframer
class ObjectKeyframer:
    obj = None
    base_unit: float = 1.0
    color = None
    blender_start_frame = 1
    unit_scale: float = 1.0
    prev_quat: Union[Quaternion, None] = None
    prev_subframe: float = 0.0
    ninety: float = 0.0

    def __init__(self, prefix: str, headers: dict, consts: dict, scn, unit_scale, color=(1, 1, 1, 1)):
        self.prefix = prefix
        self.headers = headers
        self.consts = consts
        self.scn = scn
        self.unit_scale = unit_scale
        self.color = color
        self.ninety = cos(radians(90)/2)
        return

    def set_blender_start_frame(self, blender_start_frame: int):
        self.blender_start_frame = blender_start_frame

    @staticmethod
    def round(num: float) -> float:
        return float(round(num, 6))

    def add_subframe(self, subframe: float, line: list):
        subframe = self.round(subframe + self.blender_start_frame)
        obj = self.get_object()
        obj.rotation_mode = 'QUATERNION'

        loc = [self.round(float(x)) for x in line[self.consts[self.prefix + '_LOC']].split(',')]
        rot = [self.round(float(x)) for x in line[self.consts[self.prefix + '_QUAT']].split(',')]

        obj.location = (loc[self.consts['LOC_X']] * self.unit_scale, -loc[self.consts['LOC_Y']] * self.unit_scale,
                        loc[self.consts['LOC_Z']] * self.unit_scale)

        quat = self.get_rotation(
            rot[self.consts['QUAT_W']],
            rot[self.consts['QUAT_X']],
            rot[self.consts['QUAT_Y']],
            rot[self.consts['QUAT_Z']]
        )

        # if this subframe and previous subframe both fall on real frames or within the same real frame
        # then polarity constraint is not necessary
        if self.prev_quat:
            real_frame = floor(subframe)
            prev_real_frame = floor(self.prev_subframe)
            if real_frame != prev_real_frame:
                if self.round(real_frame - subframe) or self.round(prev_real_frame - self.prev_subframe):
                    if self.prev_quat.dot(quat) < 0:
                        quat.negate()

        obj.rotation_quaternion = (quat.w, quat.x, quat.y, quat.z)
        self.prev_quat = quat

        obj.keyframe_insert(data_path='location', frame=subframe)
        obj.keyframe_insert(data_path='rotation_quaternion', frame=subframe)
        self.interpolate(self.get_list_for_keyframing())
        self.prev_subframe = subframe

        return

    @staticmethod
    def interpolate(objs: list):
        for obj in objs:
            for fcurve in obj.animation_data.action.fcurves:
                list_len = len(fcurve.keyframe_points)
                if list_len:
                    index = -1 if list_len > 1 else 0
                    kf = fcurve.keyframe_points[index]
                    kf.interpolation = 'LINEAR'
                    fcurve.update()
        return

    def get_rotation(self, w: float, x: float, y: float, z: float) -> Quaternion:
        return Quaternion((w, -y, -x, -z))

    def get_object(self):
        if self.obj is None:
            bpy.ops.mesh.primitive_plane_add()
            obj = bpy.context.active_object
            obj.name = self.prefix
            self.obj = obj
        return self.obj

    def set_object(self, obj):
        obj.rotation_mode = 'QUATERNION'
        obj.location = (0.0, 0.0, 0.0)
        obj.rotation_quaternion = (1.0, 0.0, 0.0, 0.0)
        self.scn.collection.objects.link(obj)
        return

    def apply_color(self, obj):
        obj_color = bpy.data.materials.new(self.prefix + 'Color')
        obj_color.diffuse_color = self.color
        mat_slots = obj.material_slots
        polys = obj.data.polygons
        obj.data.materials.append(obj_color)
        mat_slots[0].material = None
        obj.data.materials.append(obj_color)
        polys[0].material_index = 1
        return

    def get_list_for_keyframing(self):
        return [self.obj]


# Car Keyframer
class CarKeyframer(ObjectKeyframer):
    proxy_object_name = 'RL_OCTANE_PROXY'

    def __init__(self, prefix: str, headers: dict, consts: dict, scn, unit_scale, color=(1, 1, 1, 1)):
        super().__init__(prefix, headers, consts, scn, unit_scale, color)
        self.proxy_object_name = consts['CAR_PROXY_NAME']
        return

    def get_rotation(self, w: float, x: float, y: float, z: float) -> Quaternion:
        quat = Quaternion((w, -x, y, -z))
        return quat

    def get_object(self):
        if self.obj is None:
            # mesh = bpy.context.scene.objects[self.proxy_object_name].data
            obj = bpy.data.objects.get(self.proxy_object_name).copy()
            obj.name = self.prefix
            # obj.scale = (self.base_unit * self.unit_scale, self.base_unit *
            #              self.unit_scale, self.base_unit * self.unit_scale)
            self.set_object(obj)
            # mesh.update(calc_edges=True)
            self.obj = obj
        return self.obj


# Ball Keyframer
class BallKeyframer(CarKeyframer):
    def __init__(self, prefix: str, headers: dict, consts: dict, scn, unit_scale, color=(1, 1, 1, 1)):
        super().__init__(prefix, headers, consts, scn, unit_scale, color)
        self.proxy_object_name = consts['BALL_PROXY_NAME']
        return


# Camera Keyframer
class CameraKeyframer(ObjectKeyframer):
    default_sensor_width = 36.0
    cam_data = None
    cam = None
    include_frame_nums: bool = False
    sensor_width_keyframe_added: bool = False
    sensor_width: float = 35.0
    maintain_sensor_focal_ratio: bool = True

    def __init__(
            self,
            prefix: str,
            headers: dict,
            consts: dict,
            scn,
            unit_scale,
            include_frame_nums: bool,
            sensor_width: float,
            maintain_sensor_focal_ratio: bool
    ):
        super().__init__(prefix, headers, consts, scn, unit_scale)
        self.include_frame_nums = include_frame_nums
        self.sensor_width = sensor_width
        self.maintain_sensor_focal_ratio = maintain_sensor_focal_ratio
        return

    def get_data(self):
        if self.cam_data is None:
            self.cam_data = bpy.data.cameras.new(self.headers['camera'])
            self.cam_data.sensor_fit = 'HORIZONTAL'
            self.cam_data.sensor_width = self.sensor_width
            self.cam_data.angle = radians(90)
        return self.cam_data

    def get_rotation(self, w: float, x: float, y: float, z: float) -> Quaternion:
        # rotate -90d on z, +90d on x
        quat = super().get_rotation(w, x, y, z)
        quat = Quaternion((self.ninety, 0.0, 0.0, -self.ninety)) @ quat
        return quat @ Quaternion((self.ninety, self.ninety, 0.0, 0.0))

    def get_object(self):
        if self.cam is None:
            self.cam = bpy.data.objects.new(self.headers['camera'], self.get_data())
            self.scn.camera = self.cam
            self.set_object(self.cam)
        return self.cam

    def add_subframe(self, subframe: float, line: list):
        cam_data = self.get_data()
        cam_data.angle = radians(float(line[self.consts['FOV']]))
        if self.maintain_sensor_focal_ratio:
            cam_data.lens = cam_data.lens * self.default_sensor_width / self.sensor_width
        cam_data.keyframe_insert(data_path='lens', frame=subframe + self.blender_start_frame)
        if not self.sensor_width_keyframe_added:
            cam_data.keyframe_insert(data_path='sensor_width', frame=subframe + self.blender_start_frame)
            self.sensor_width_keyframe_added = True
        if self.include_frame_nums:
            cam_data.cb_frame = float(line[self.consts['FRAME']])
            cam_data.keyframe_insert(data_path='cb_frame', frame=subframe + self.blender_start_frame)
        super().add_subframe(subframe, line)
        return

    def get_list_for_keyframing(self):
        return [self.get_object(), self.get_data()]
