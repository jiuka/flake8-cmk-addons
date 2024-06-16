from flake8_plugin_utils import assert_error, assert_not_error

from flake8_cmk_addons.visitor import CmkAddonsVisitor
from flake8_cmk_addons.errors import EntryPoint


def test_ok():
    code = """
        from cmk.agent_based.v2 import AgentSection

        agent_section_test = AgentSection(name='test')
    """
    assert_not_error(CmkAddonsVisitor, code)


def test_no_assignment():
    code = """
        from cmk.agent_based.v2 import AgentSection

        AgentSection(name='test')
    """
    assert_error(
        CmkAddonsVisitor,
        code,
        EntryPoint,
        class_name='AgentSection',
        entry_point_prefix='agent_section_',
        instance_name='test',
    )


def test_assignment_to_foo():
    code = """
        from cmk.agent_based.v2 import AgentSection

        foo = AgentSection(name='test')
    """
    assert_error(
        CmkAddonsVisitor,
        code,
        EntryPoint,
        class_name='AgentSection',
        entry_point_prefix='agent_section_',
        instance_name='test',
    )


def test_assignment_to_agent_section_pytest():
    code = """
        from cmk.agent_based.v2 import AgentSection

        agent_section_pytest = AgentSection(name='test')
    """
    assert_error(
        CmkAddonsVisitor,
        code,
        EntryPoint,
        class_name='AgentSection',
        entry_point_prefix='agent_section_',
        instance_name='test',
    )
