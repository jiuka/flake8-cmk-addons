from flake8_plugin_utils import Plugin
from .visitor import CmkAddonsVisitor


class CmkAddonsPlugin(Plugin):
    name = 'flake8-cmk-addons'
    version = '2.3.0'
    visitors = [
        CmkAddonsVisitor
    ]
