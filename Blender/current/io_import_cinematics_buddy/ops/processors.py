from abc import ABC, abstractmethod
import json
from .keyframers import BallKeyframer, CameraKeyframer, CarKeyframer
from math import ceil
from typing import Dict, List, Optional


consts = {
    'FRAME': 0,
    'REPLAY_FRAME': 1,
    'FOV': 2,
    'CAM_LOC': 3,
    'CAM_QUAT': 4,
    'BALL_LOC': 5,
    'BALL_QUAT': 6,
    'CAR1_LOC': 8,
    'CAR1_QUAT': 9,
    'CAR2_LOC': 11,
    'CAR2_QUAT': 12,
    'CAR3_LOC': 14,
    'CAR3_QUAT': 15,
    'CAR4_LOC': 17,
    'CAR4_QUAT': 18,
    'CAR5_LOC': 20,
    'CAR5_QUAT': 21,
    'CAR6_LOC': 23,
    'CAR6_QUAT': 24,
    'CAR7_LOC': 26,
    'CAR7_QUAT': 27,
    'CAR8_LOC': 29,
    'CAR8_QUAT': 30,
    'LOC_X': 0,
    'LOC_Y': 1,
    'LOC_Z': 2,
    'QUAT_X': 0,
    'QUAT_Y': 1,
    'QUAT_Z': 2,
    'QUAT_W': 3,
    'HEADER_END': 7,
    'DATA_LINE_START': 16,
}


class FileProcessor(ABC):
    filepath: str = None
    unit_scale: float = None
    include_frame_nums: bool = None
    replay_frame_start: int = None
    replay_frame_end: int = None
    target_fps: float = None
    scn = None
    vid_speed: float = None
    sensor_width: float = None
    maintain_sensor_focal_ratio: bool = None
    print_progress: bool = False
    blender_start_frame: int = 1
    objs: list = None

    def __init__(
            self,
            filepath: str,
            proxies:  dict,
            unit_scale: float,
            include_frame_nums: bool,
            replay_frame_start: int,
            replay_frame_end: int,
            target_fps: float,
            scn,
            vid_speed: float,
            sensor_width: float,
            maintain_sensor_focal_ratio: bool,
            print_progress: bool,
            blender_start_frame: int
    ):
        global consts
        consts['CAR_PROXY_NAME'] = proxies['CAR_PROXY_NAME']
        consts['BALL_PROXY_NAME'] = proxies['BALL_PROXY_NAME']
        consts['STADIUM_PROXY_NAME'] = proxies['STADIUM_PROXY_NAME']

        self.filepath = filepath
        self.unit_scale = unit_scale
        self.include_frame_nums = include_frame_nums
        self.replay_frame_start = replay_frame_start
        self.replay_frame_end = replay_frame_end
        self.target_fps = target_fps
        self.scn = scn
        self.vid_speed = vid_speed
        self.sensor_width = sensor_width
        self.maintain_sensor_focal_ratio = maintain_sensor_focal_ratio
        self.print_progress = print_progress
        self.blender_start_frame = blender_start_frame

        self.objs: List[dict] = [
            {'type': 'camera', 'prefix': 'CAM', 'obj': None},
            {'type': 'ball', 'prefix': 'BALL', 'obj': None},
            {'type': 'car', 'prefix': 'CAR1', 'obj': None, 'color': (0, 0, 1, 1)},
            {'type': 'car', 'prefix': 'CAR2', 'obj': None, 'color': (0, 1, 0, 1)},
            {'type': 'car', 'prefix': 'CAR3', 'obj': None, 'color': (1, 0, 1, 1)},
            {'type': 'car', 'prefix': 'CAR4', 'obj': None, 'color': (1, 0, 0, 1)},
            {'type': 'car', 'prefix': 'CAR5', 'obj': None, 'color': (1, .898, 0, 1)},
            {'type': 'car', 'prefix': 'CAR6', 'obj': None, 'color': (1, .647, 0, 1)},
            {'type': 'car', 'prefix': 'CAR7', 'obj': None, 'color': (0, 0, 0, 1)},
            {'type': 'car', 'prefix': 'CAR8', 'obj': None, 'color': (1, 1, 1, 1)}
        ]

        return

    @staticmethod
    def add_cb_header(headers: dict, line: str):
        parts = line.split(':', 2)
        if len(parts) == 2:
            parts[0] = parts[0].lower().strip()
            parts[1] = parts[1].strip()
            if parts[0] in ["framerate", "frames", "cars"]:
                parts[1] = int(parts[1])
            headers[parts[0]] = parts[1]
        return

    @staticmethod
    def get_file_len(filename):
        with open(filename) as f:
            for i, l in enumerate(f):
                pass
        return i + 1

    def get_highest_subframe(self) -> float:
        highest_subframe = 0.0
        for obj in self.objs:
            if obj['obj'] is not None:
                highest_obj_subframe = obj['obj'].highest_subframe
                if highest_obj_subframe > highest_subframe:
                    highest_subframe = highest_obj_subframe
        return highest_subframe

    def process(self) -> None:
        headers = {}
        frame = 0
        # if self.print_progress:
        #     file_len = self.get_file_len(self.filepath)
        self.log("Loading header.")
        with open(self.filepath) as fp:
            line_num = 0
            for line in fp:
                line_num += 1
                if line_num < consts['DATA_LINE_START']:
                    if line_num < consts['HEADER_END']:
                        self.add_cb_header(headers, line)
                    continue

                line = line.split()

                if line[consts['FRAME']] == "END" or int(line[consts['REPLAY_FRAME']]) > self.replay_frame_end:
                    self.process_end(line, frame, headers)
                    break

                if int(line[consts['REPLAY_FRAME']]) < self.replay_frame_start:
                    continue

                self.log("Processing replay frame: {} / {}".format(
                    line[consts['REPLAY_FRAME']],
                    str(self.replay_frame_end) + " " * 10))
                self.process_line(line, frame, headers)
                frame += 1
            fp.close()
            highest_subframe = self.get_highest_subframe()
            if highest_subframe:
                self.scn.frame_start = self.blender_start_frame
                self.scn.frame_end = ceil(highest_subframe)
            self.log('Processing complete.')
        return

    def log(self, msg: str):
        if self.print_progress:
            print(msg, flush=True)

    @abstractmethod
    def process_line(self, line: list, frame: int, headers: dict):
        return

    @abstractmethod
    def process_end(self, line: list, frame: int, headers: dict):
        return

    def create_camera_keyframer(
            self,
            prefix: str,
            headers: dict,
            scn,
            unit_scale,
            include_frame_nums: bool,

    ) -> CameraKeyframer:
        keyframer = CameraKeyframer(
            prefix,
            headers,
            consts,
            scn,
            unit_scale,
            include_frame_nums,
            self.sensor_width,
            self.maintain_sensor_focal_ratio
        )
        keyframer.set_blender_start_frame(self.blender_start_frame)
        return keyframer

    def create_ball_keyframer(
            self,
            prefix: str,
            headers: dict,
            scn,
            unit_scale,
            color=(1, 1, 1, 1)
    ) -> BallKeyframer:
        keyframer = BallKeyframer(
            prefix,
            headers,
            consts,
            scn,
            unit_scale,
            color
        )
        keyframer.set_blender_start_frame(self.blender_start_frame)
        return keyframer

    def create_car_keyframer(
            self,
            prefix: str,
            headers: dict,
            scn,
            unit_scale,
            color=(1, 1, 1, 1)
    ) -> CarKeyframer:
        keyframer = CarKeyframer(
            prefix,
            headers,
            consts,
            scn,
            unit_scale,
            color
        )
        keyframer.set_blender_start_frame(self.blender_start_frame)
        return keyframer


class LinesProcessor(FileProcessor):
    __subframe_scale: float = None

    def process_line(self, line: list, frame: int, headers: dict):
        if self.__subframe_scale is None:
            target_fps = self.target_fps if self.target_fps else headers['framerate']
            self.__subframe_scale = target_fps / headers['framerate']
        subframe = frame * self.__subframe_scale
        self.process_objects(headers, line, subframe)
        return

    def process_end(self, line: list, frame: int, headers: dict):
        return

    def process_objects(self, headers: dict, line: list, subframe: float):
        for index, obj in enumerate(self.objs):
            if obj['obj'] is None:
                if obj['type'] == 'camera':
                    obj['obj'] = self.create_camera_keyframer(
                        obj['prefix'],
                        headers,
                        self.scn,
                        self.unit_scale,
                        self.include_frame_nums
                    )
                elif obj['type'] == 'ball':
                    obj['obj'] = self.create_ball_keyframer(
                        obj['prefix'],
                        headers,
                        self.scn,
                        self.unit_scale
                    )
                elif index - 2 < headers['cars']:
                    obj['obj'] = self.create_car_keyframer(
                        obj['prefix'],
                        headers,
                        self.scn,
                        self.unit_scale,
                        obj['color']
                    )
                else:
                    continue
            obj['obj'].add_subframe(subframe, line)
        return


class Segment:
    duration: float = 0.0
    start_time: float = 0.0
    start_frame = 0
    out_frame = 0


class SegmentsProcessor(LinesProcessor):
    snapshots: list = None
    segments: List[Segment] = None
    segment_lines = []
    __current_segment: int = 0

    def set_snapshot_file(self, snapshot_filename: str):
        try:
            with open(snapshot_filename) as f:
                snapshots = dict(sorted(json.load(f).items()))
                self.snapshots = list(snapshots.values())
        except Exception:
            raise Exception('Unable to parse snapshot file: {} Ensure file is readable and '
                            'contains valid JSON'.format(snapshot_filename))

        if len(self.snapshots) < 1:
            raise Exception('No snapshots in file: {}'.format(snapshot_filename))

    def process_line(self, line: list, frame: int, headers: dict):
        segment = self.get_current_segment()
        if segment is not None:
            replay_frame = int(line[consts['REPLAY_FRAME']])
            if not replay_frame < segment.out_frame:
                self.write_out_lines(segment, headers)
                self.segment_lines = []
                self.__current_segment += 1
            if replay_frame >= segment.start_frame:
                self.segment_lines.append(line)

    def process_end(self, line: list, frame: int, headers: dict):
        segment = self.get_current_segment()
        if segment is not None:
            self.write_out_lines(segment, headers)

    def write_out_lines(self, segment: Segment, headers: dict):
        line_len = len(self.segment_lines)
        if line_len:
            parts: Dict[str, List] = {}
            for x in range(line_len):
                replay_frame_num = str(self.segment_lines[x][consts['REPLAY_FRAME']])
                if replay_frame_num not in parts.keys():
                    parts[replay_frame_num] = [self.segment_lines[x]]
                else:
                    parts[replay_frame_num].append(self.segment_lines[x])

            prev_subframe = 0.0
            prev_replay_frame = 0

            expected_parts_count = segment.out_frame - segment.start_frame
            part_duration = segment.duration / expected_parts_count
            for e in range(expected_parts_count):
                ep = segment.start_frame + e
                if str(ep) in parts.keys():
                    replay_frames_count = len(parts[str(ep)])
                    replay_frame_duration = part_duration / replay_frames_count
                    for r in range(replay_frames_count):
                        subframe = (segment.start_time * self.target_fps) + (e * part_duration * self.target_fps)\
                                   + (r * replay_frame_duration * self.target_fps)

                        if subframe < prev_subframe:
                            self.log("subframe {} less than {}".format(subframe, prev_subframe))
                        prev_subframe = subframe

                        replay_frame = int(parts[str(ep)][r][0])
                        if replay_frame < prev_replay_frame:
                            self.log("replay_frame {} less than {}".format(replay_frame, prev_replay_frame))
                        prev_replay_frame = replay_frame

                        self.process_objects(headers, parts[str(ep)][r], subframe)
                else:
                    continue
        return

    def get_current_segment(self) -> Optional[Segment]:
        if self.segments is None:
            self.init_segments()
        if self.__current_segment < len(self.segments):
            return self.segments[self.__current_segment]
        return None

    def init_segments(self) -> None:
        self.segments = []
        snapshot_upper = len(self.snapshots) - 1
        start_time = 0.0
        s = 0
        for s in range(snapshot_upper):
            segment = Segment()
            segment.start_time = start_time
            segment.start_frame = self.snapshots[s]['frame']
            segment.out_frame = self.snapshots[s + 1]['frame']
            segment.duration = \
                (self.snapshots[s + 1]['timestamp'] - self.snapshots[s]['timestamp']) * 1 / self.vid_speed
            self.segments.append(segment)
            start_time += segment.duration

        # TODO: Limit dup code
        segment = Segment()
        segment.start_time = start_time
        segment.start_frame = self.snapshots[s + 1]['frame']
        segment.out_frame = self.snapshots[s + 1]['frame'] + 1
        segment.duration = 1 / self.vid_speed / self.target_fps
        self.segments.append(segment)
        self.replay_frame_end = segment.out_frame - 1
        return


