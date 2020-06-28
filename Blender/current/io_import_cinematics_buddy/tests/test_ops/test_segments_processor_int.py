from unittest.mock import patch
from unittest.mock import MagicMock
from io_import_cinematics_buddy.tests.base import BaseTest
from io_import_cinematics_buddy.ops.processors import SegmentsProcessor


class TestSegmentsProcessorInt(BaseTest):

    def test_small(self):
        proxies = {
            'CAR_PROXY_NAME': 'carfoo',
            'BALL_PROXY_NAME': 'ballfoo',
            'STADIUM_PROXY_NAME': 'stadiumfoo'
        }
        with patch.object(SegmentsProcessor, 'process_objects') as mock_method:
            processor = SegmentsProcessor(
                self.get_resources_dir() + 'testsmall.txt',
                proxies,
                1.0,
                True,
                0,
                999999999,
                60.0,
                'foo',
                1.0,
                35.0,
                True,
                False,
                1
            )
            processor.set_snapshot_file(self.get_resources_dir() + 'small.json')
            processor.process()
            arg_list = mock_method.call_args_list
            mock_method.assert_called()

    def test_all(self):
        proxies = {
            'CAR_PROXY_NAME': 'carfoo',
            'BALL_PROXY_NAME': 'ballfoo',
            'STADIUM_PROXY_NAME': 'stadiumfoo'
        }
        with patch.object(SegmentsProcessor, 'process_objects') as mock_method:
            processor = SegmentsProcessor(
                self.get_resources_dir() + 'testall.txt',
                proxies,
                1.0,
                True,
                0,
                999999999,
                60.0,
                'foo',
                1.0,
                35.0,
                True,
                False,
                1
            )
            processor.set_snapshot_file(self.get_resources_dir() + 'unordered.json')
            processor.process()
            arg_list = mock_method.call_args_list
            mock_method.assert_called()

    def test_otdemo(self):
        proxies = {
            'CAR_PROXY_NAME': 'carfoo',
            'BALL_PROXY_NAME': 'ballfoo',
            'STADIUM_PROXY_NAME': 'stadiumfoo'
        }
        with patch.object(SegmentsProcessor, 'process_objects') as mock_method:
            processor = SegmentsProcessor(
                self.get_resources_dir() + 'otdemo.txt',
                proxies,
                1.0,
                True,
                0,
                999999999,
                60.0,
                'foo',
                float("0.25"),
                35.0,
                True,
                False,
                1
            )
            processor.set_snapshot_file(self.get_resources_dir() + 'otdemo.json')
            processor.process()
            # arg_list = mock_method.call_args_list
            mock_method.assert_called()

    def test_otdemo_small(self):
        proxies = {
            'CAR_PROXY_NAME': 'carfoo',
            'BALL_PROXY_NAME': 'ballfoo',
            'STADIUM_PROXY_NAME': 'stadiumfoo'
        }
        with patch.object(SegmentsProcessor, 'process_objects') as mock_method:
            processor = SegmentsProcessor(
                self.get_resources_dir() + 'otdemo.txt',
                proxies,
                1.0,
                True,
                0,
                999999999,
                60.0,
                'foo',
                float("0.25"),
                35.0,
                True,
                False,
                1
            )
            processor.set_snapshot_file(self.get_resources_dir() + 'otdemo-small.json')
            processor.process()
            # arg_list = mock_method.call_args_list
            mock_method.assert_called()

    def test_tv4(self):
        proxies = {
            'CAR_PROXY_NAME': 'carfoo',
            'BALL_PROXY_NAME': 'ballfoo',
            'STADIUM_PROXY_NAME': 'stadiumfoo'
        }

        with patch.object(SegmentsProcessor, 'process_objects') as mock_method:
            processor = SegmentsProcessor(
                self.get_resources_dir() + 'tv425.txt',
                proxies,
                1.0,
                True,
                0,
                999999999,
                60.0,
                'foo',
                float("0.25"),
                35.0,
                True,
                True,
                1
            )
            processor.set_snapshot_file(self.get_resources_dir() + 'tv4.json')
            processor.process()
            # arg_list = mock_method.call_args_list
            mock_method.assert_called()
