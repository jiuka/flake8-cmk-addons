from flake8_plugin_utils import Error


class EntryPoint(Error):
    code = 'CA001'
    message = 'Instances of {class_name} should be assigned to Entry Point {entry_point_prefix}{instance_name}'
