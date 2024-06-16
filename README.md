# flake8-cmk-addons

## Description

A `flake8` plugin checking common issues or inconsistencies Checkmk Addons.

Currently the following errors are reported:

| Code    | Description |
| ------- | ----------- |
| [CA001] | Instances of {class_name} should be assigned to Entry Point {entry_point_prefix}{instance_name} |

## Installation

    pip install flake8-cmk-addons

## Configuration

## For developers

### Install deps and setup pre-commit hook

    poetry install

## License

MIT

## Change Log

**Unreleased**
