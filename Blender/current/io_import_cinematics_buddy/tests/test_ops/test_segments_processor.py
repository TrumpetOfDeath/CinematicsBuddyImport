import pytest
from io_import_cinematics_buddy.ops.processors import SegmentsProcessor
from io_import_cinematics_buddy.tests.base import BaseTest


class TestSegmentsProcessor(BaseTest):

    def test_ordered_json(self):
        segments_processor = self.get_segments_processor()
        segments_processor.set_snapshot_file(self.get_resources_dir() + 'unordered.json')
        assert len(segments_processor.snapshots) == 6
        prev_frame: int = 0
        prev_timestamp: float = 0.0
        for s in segments_processor.snapshots:
            assert s['frame'] > prev_frame
            assert s['timestamp'] > prev_timestamp
            prev_frame = s['frame']
            prev_timestamp = s['timestamp']

    @staticmethod
    def get_segments_processor() -> SegmentsProcessor:
        proxies = {
            'CAR_PROXY_NAME': 'carfoo',
            'BALL_PROXY_NAME': 'ballfoo',
            'STADIUM_PROXY_NAME': 'stadiumfoo'
        }
        return SegmentsProcessor(
            'foo.txt',
            proxies,
            1.0,
            True,
            1,
            1,
            60.0,
            'foo',
            1.0,
            35.0,
            True,
            False,
            1
        )

    def test_missing_json(self):
        with pytest.raises(Exception, match=r'(?i)snapshot'):
            self.get_segments_processor().set_snapshot_file(self.get_resources_dir() + 'non-existent.json')

    def test_init_segments(self):
        segments_processor = self.get_segments_processor()
        segments_processor.set_snapshot_file(self.get_resources_dir() + 'unordered.json')
        segments_processor.init_segments()
        segments = segments_processor.segments
        assert len(segments) == 6
        assert round(segments[5].duration, 6) == 0.016667

