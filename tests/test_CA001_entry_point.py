import pytest
from flake8_plugin_utils import assert_error, assert_not_error

from flake8_cmk_addons.visitor import CmkAddonsVisitor
from flake8_cmk_addons.errors import EntryPoint


def test_ok():
    code = """
        from cmk.agent_based.v2 import AgentSection

        agent_section_test = AgentSection(name='test')
    """
    assert_not_error(CmkAddonsVisitor, code)


@pytest.mark.parametrize('code, class_name, entry_point_prefix', [
    ['cmk.graphing.v1.metrics.Metric(name="test")', 'Metric', 'metric_'],
    ['cmk.graphing.v1.translations.Translation(name="test")', 'Translation', 'translation_'],
    ['cmk.graphing.v1.perfometers.Perfometer(name="test")', 'Perfometer', 'perfometer_'],
    ['cmk.graphing.v1.perfometers.Bidirectional(name="test")', 'Bidirectional', 'perfometer_'],
    ['cmk.graphing.v1.perfometers.Stacked(name="test")', 'Stacked', 'perfometer_'],
    ['cmk.graphing.v1.graphs.Graph(name="test")', 'Graph', 'graph_'],
    ['cmk.graphing.v1.graphs.Bidirectional(name="test")', 'Bidirectional', 'graph_'],
    ['cmk.rulesets.v1.rule_specs.ActiveCheck(name="test")', 'ActiveCheck', 'rule_spec_'],
    ['cmk.rulesets.v1.rule_specs.AgentConfig(name="test")', 'AgentConfig', 'rule_spec_'],
    ['cmk.rulesets.v1.rule_specs.AgentAccess(name="test")', 'AgentAccess', 'rule_spec_'],
    ['cmk.rulesets.v1.rule_specs.EnforcedService(name="test")', 'EnforcedService', 'rule_spec_'],
    ['cmk.rulesets.v1.rule_specs.CheckParameters(name="test")', 'CheckParameters', 'rule_spec_'],
    ['cmk.rulesets.v1.rule_specs.Host(name="test")', 'Host', 'rule_spec_'],
    ['cmk.rulesets.v1.rule_specs.InventoryParameters(name="test")', 'InventoryParameters', 'rule_spec_'],
    ['cmk.rulesets.v1.rule_specs.NotificationParameters(name="test")', 'NotificationParameters', 'rule_spec_'],
    ['cmk.rulesets.v1.rule_specs.DiscoveryParameters(name="test")', 'DiscoveryParameters', 'rule_spec_'],
    ['cmk.rulesets.v1.rule_specs.Service(name="test")', 'Service', 'rule_spec_'],
    ['cmk.rulesets.v1.rule_specs.SNMP(name="test")', 'SNMP', 'rule_spec_'],
    ['cmk.rulesets.v1.rule_specs.SpecialAgent(name="test")', 'SpecialAgent', 'rule_spec_'],
    ['cmk.server_side_calls.v1.ActiveCheckConfig(name="test")', 'ActiveCheckConfig', 'active_check_'],
    ['cmk.server_side_calls.v1.SpecialAgentConfig(name="test")', 'SpecialAgentConfig', 'special_agent_'],
])
def test_no_assignment_rulesets(code, class_name, entry_point_prefix):
    assert_error(
        CmkAddonsVisitor,
        code,
        EntryPoint,
        class_name=class_name,
        entry_point_prefix=entry_point_prefix,
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
