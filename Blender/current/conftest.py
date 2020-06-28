import builtins
from unittest.mock import MagicMock

_python_import = builtins.__import__


def _test_suite_import_setup(name, *args, **kwargs):
    if name == 'bpy':
        bpy_ = MagicMock(name='bpy_mock')
        bpy_.data = MagicMock(name="bpy_mock.data")
        return bpy_
    return _python_import(name, *args, **kwargs)


builtins.__import__ = _test_suite_import_setup
