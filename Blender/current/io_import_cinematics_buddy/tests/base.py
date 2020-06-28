from abc import ABC
import os


class BaseTest(ABC):

    @staticmethod
    def get_resources_dir() -> str:
        return os.path.dirname(os.path.realpath(__file__)) + os.sep + 'resources' + os.sep
