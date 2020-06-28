import bpy
from bpy.props import BoolProperty, EnumProperty, FloatProperty, IntProperty, StringProperty
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper
from importlib import import_module
from typing import Union
from .processors import FileProcessor, LinesProcessor, SegmentsProcessor


class CinematicsBuddyImport(Operator, ImportHelper):
    """Import Cinematics Buddy Animation Export"""
    bl_idname = "import.cinematics_buddy_data"
    bl_label = "Import Cinematics Buddy Animation"
    filename_ext = ".txt"

    filter_glob: StringProperty(default="*.txt", options={'HIDDEN'})

    replay_frame_start: IntProperty(
        name="Replay Frame Start",
        description="The frame to start processing from (usually the frame of your first snapshot, use 0 to start "
                    "from first frame of export file). Ignored when snapshot file is used",
        default=0
    )

    replay_frame_end: IntProperty(
        name="Replay Frame End",
        description="The frame to end processing on (usually the frame of your last snapshot, use large number to "
                    "process till last frame of export file). Ignored when snapshot file is used",
        default=999999999
    )

    target_fps: FloatProperty(
        name="Target FPS",
        description="FPS you intend to use in Blender (use 0 to use FPS from animation export file)",
        default=60.0
    )

    include_frame_nums: BoolProperty(
        name="Include Frame Numbers",
        description="Will include keyframe for each frame number (from first column of animation export file)",
        default=True
    )

    car_proxy_name: StringProperty(
        name="Car Proxy Name",
        description='The name of the object created when you imported the octane fbx file',
        default='RL_OCTANE_PROXY'
    )

    ball_proxy_name: StringProperty(
        name="Ball Proxy Name",
        description='The name of the object created when you imported the ball fbx file',
        default='RL_BALL_PROXY'
    )

    stadium_proxy_name: StringProperty(
        name="Stadium Proxy Name",
        description='The name of the object created when you imported the stadium fbx file',
        default='RL_STADIUM_PROXY'
    )

    print_progress: BoolProperty(
        name="Print Progress to System Console",
        description="Will print processed frames to System Console",
        default=True
    )

    snapshot_filename: StringProperty(
        name="Campath File",
        description='JSON file containing path snapshots. This can improve framerate consistency (optional)',
        default='C:\\Program Files (x86)\\Steam\\steamapps\\common\\rocketleague\\Binaries\\Win64\\tv4.json'
    )

    vid_speed: EnumProperty(
        items=[
            ("2", "200%", ""),
            ("1", "100%", ""),
            ("0.5", "50%", ""),
            ("0.25", "25%", ""),
            ("0.1", "10%", ""),
            ("0.05", "5%", ""),
        ],
        name="Video Speed",
        description="Video Speed. Ignored when snapshot file isn't used",
        default="0.25",
    )

    blender_start_frame: IntProperty(
        name="First frame in Blender",
        description="This will be the first frame written in Blender timeline",
        default=1
    )

    sensor_width: FloatProperty(
        name="Sensor Width",
        description="Camera Sensor Width",
        default=35.0
    )

    maintain_sensor_focal_ratio: BoolProperty(
        name="Maintain Sensor Focal Length Ratio",
        description="",
        default=False
    )

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.prop(self, 'snapshot_filename')
        box.prop(self, 'vid_speed')
        box.prop(self, 'target_fps')
        box.prop(self, 'include_frame_nums')
        box.prop(self, 'car_proxy_name')
        box.prop(self, 'ball_proxy_name')
        box.prop(self, 'stadium_proxy_name')
        box.prop(self, 'sensor_width')
        box.prop(self, 'maintain_sensor_focal_ratio')
        box.prop(self, 'blender_start_frame')
        # box.prop(self, 'print_progress')
        # box.label(text='Frames:')
        # box.prop(self, 'replay_frame_start')
        # box.prop(self, 'replay_frame_end')

    def execute(self, context):
        return Importer.import_cinematics_data(
            context,
            self.filepath,
            self.replay_frame_start,
            self.replay_frame_end,
            self.target_fps,
            self.include_frame_nums,
            self.car_proxy_name,
            self.ball_proxy_name,
            self.stadium_proxy_name,
            self.snapshot_filename,
            float(self.vid_speed),
            self.sensor_width,
            self.maintain_sensor_focal_ratio,
            self.print_progress,
            self.blender_start_frame
        )


class Importer:

    @staticmethod
    def import_cinematics_data(
            context,
            filepath: str,
            replay_frame_start: int,
            replay_frame_end: int,
            target_fps: float,
            include_frame_nums: bool,
            car_proxy_name: str,
            ball_proxy_name: str,
            stadium_proxy_name: str,
            snapshot_filename: str,
            vid_speed: float,
            sensor_width: float,
            maintain_sensor_focal_ratio: bool,
            print_progress: bool,
            blender_start_frame: int
    ):
        unit_scale = 1 / 100.0  # centimeters

        if include_frame_nums:
            bpy.types.Camera.cb_frame = FloatProperty(
                name='CB Frame',
                description='Frame number from first column of animation export file',
                default=0.0,
                options={'ANIMATABLE'}
            )

        proxies = {
            'CAR_PROXY_NAME': car_proxy_name,
            'BALL_PROXY_NAME': ball_proxy_name,
            'STADIUM_PROXY_NAME': stadium_proxy_name
        }

        # add stadium
        scn = bpy.context.scene
        stadium_obj = bpy.data.objects.get(proxies['STADIUM_PROXY_NAME']).copy()
        stadium_obj.name = 'Stadium'
        stadium_obj.rotation_mode = 'QUATERNION'
        stadium_obj.location = (0.0, 0.0, 0.0)
        stadium_obj.rotation_quaternion = (1.0, 0.0, 0.0, 0.0)
        scn.collection.objects.link(stadium_obj)

        use_segments = True if len(snapshot_filename) else False

        module = import_module('io_import_cinematics_buddy.ops.processors')
        processor_class = getattr(
            module,
            'SegmentsProcessor' if use_segments else 'LinesProcessor'
        )

        file_processor: Union[LinesProcessor, SegmentsProcessor] = processor_class(
            filepath,
            proxies,
            unit_scale,
            include_frame_nums,
            0 if use_segments else replay_frame_start,
            999999999 if use_segments else replay_frame_end,
            target_fps,
            scn,
            vid_speed,
            sensor_width,
            maintain_sensor_focal_ratio,
            print_progress,
            blender_start_frame
        )

        if use_segments:
            file_processor.set_snapshot_file(snapshot_filename)

        file_processor.process()

        return {'FINISHED'}
