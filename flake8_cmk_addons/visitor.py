import ast
from typing import Optional
from flake8_plugin_utils import Visitor
from flake8_cmk_addons import errors as err


def simplify_keywords(keywords):
    return {
        kw.arg: kw.value
        for kw in keywords
    }


class CmkAddonsVisitor(Visitor):
    CALL_CHECKS = {
        # cmk.agent_based.v2
        'cmk.agent_based.v2.AgentSection': 'AgentSection',
        'cmk.agent_based.v2.SimpleSNMPSection': 'SimpleSNMPSection',
        'cmk.agent_based.v2.SNMPSection': 'SNMPSection',
        'cmk.agent_based.v2.CheckPlugin': 'CheckPlugin',
        'cmk.agent_based.v2.InventoryPlugin': 'InventoryPlugin',
        # cmk.graphing.v1
        'cmk.graphing.v1.metrics.Metric': 'Metric',
        'cmk.graphing.v1.translations.Translation': 'Translation',
        'cmk.graphing.v1.perfometers.Perfometer': 'Perfometer',
        'cmk.graphing.v1.perfometers.Bidirectional': 'Perfometer',
        'cmk.graphing.v1.perfometers.Stacked': 'Perfometer',
        'cmk.graphing.v1.graphs.Graph': 'Graph',
        'cmk.graphing.v1.graphs.Bidirectional': 'Graph',
        # cmk.rulesets.v1
        'cmk.rulesets.v1.rule_specs.ActiveCheck': 'RuleSpec',
        'cmk.rulesets.v1.rule_specs.AgentConfig': 'RuleSpec',
        'cmk.rulesets.v1.rule_specs.AgentAccess': 'RuleSpec',
        'cmk.rulesets.v1.rule_specs.EnforcedService': 'RuleSpec',
        'cmk.rulesets.v1.rule_specs.CheckParameters': 'RuleSpec',
        'cmk.rulesets.v1.rule_specs.Host': 'RuleSpec',
        'cmk.rulesets.v1.rule_specs.InventoryParameters': 'RuleSpec',
        'cmk.rulesets.v1.rule_specs.NotificationParameters': 'RuleSpec',
        'cmk.rulesets.v1.rule_specs.DiscoveryParameters': 'RuleSpec',
        'cmk.rulesets.v1.rule_specs.Service': 'RuleSpec',
        'cmk.rulesets.v1.rule_specs.SNMP': 'RuleSpec',
        'cmk.rulesets.v1.rule_specs.SpecialAgent': 'RuleSpec',
        # cmk.server_side_calls.v1
        'cmk.server_side_calls.v1.ActiveCheckConfig': 'ActiveCheckConfig',
        'cmk.server_side_calls.v1.SpecialAgentConfig': 'SpecialAgentConfig',
    }

    def __init__(self, config: None = None) -> None:
        super(CmkAddonsVisitor, self).__init__()
        self.function = {}
        self.fqpn_map = {}

    def visit_FunctionDef(self, node):
        self.function[node.name] = node

    def visit_ImportFrom(self, node: ast.ImportFrom):
        for name in node.names:
            import_name = name.asname if name.asname else name.name
            self.fqpn_map[import_name] = f"{node.module}.{name.name}"

    def get_fqpn(self, node: ast.Name | ast.Attribute) -> Optional[str]:
        parts = []
        while True:
            if isinstance(node, ast.Name):
                parts.append(node.id)
                break
            if isinstance(node, ast.Attribute):
                parts.append(node.attr)
                node = node.value
            else:
                return None
        if parts[-1] in self.fqpn_map:
            parts[-1] = self.fqpn_map[parts[-1]]
        return '.'.join(reversed(parts))

    def check_entry_point(self, call, targets, func_name, entry_point_prefix):
        keywords = simplify_keywords(call.keywords)
        if targets is None:
            self.error_from_node(err.EntryPoint, call,
                                 class_name=func_name,
                                 entry_point_prefix=entry_point_prefix,
                                 instance_name=keywords['name'].value)
        elif targets[0].id != f"{entry_point_prefix}{keywords['name'].value}":
            self.error_from_node(err.EntryPoint, targets[0],
                                 class_name=func_name,
                                 entry_point_prefix=entry_point_prefix,
                                 instance_name=keywords['name'].value)

    def check_AgentSection(self, call, targets=None):
        self.check_entry_point(call, targets, 'AgentSection', 'agent_section_')

    def check_RuleSpec(self, call, targets=None):
        if isinstance(call.func, ast.Attribute):
            func_name = call.func.attr
        else:
            func_name = call.func.id
        self.check_entry_point(call, targets, func_name, 'rule_spec_')

    def check_ActiveCheckConfig(self, call, targets=None):
        self.check_entry_point(call, targets, 'ActiveCheckConfig', 'active_check_')

    def check_SpecialAgentConfig(self, call, targets=None):
        self.check_entry_point(call, targets, 'SpecialAgentConfig', 'special_agent_')

    def check_Metric(self, call, targets=None):
        self.check_entry_point(call, targets, 'Metric', 'metric_')

    def check_Translation(self, call, targets=None):
        self.check_entry_point(call, targets, 'Translation', 'translation_')

    def check_Perfometer(self, call, targets=None):
        if isinstance(call.func, ast.Attribute):
            func_name = call.func.attr
        else:
            func_name = call.func.id
        self.check_entry_point(call, targets, func_name, 'perfometer_')

    def check_Graph(self, call, targets=None):
        if isinstance(call.func, ast.Attribute):
            func_name = call.func.attr
        else:
            func_name = call.func.id
        self.check_entry_point(call, targets, func_name, 'graph_')

    def check_Call(self, call: ast.Call, targets=None):
        fqpn = self.get_fqpn(call.func)
        check_name = self.CALL_CHECKS.get(fqpn)
        if hasattr(self, f'check_{check_name}'):
            check = getattr(self, f'check_{check_name}')
            check(call=call, targets=targets)
            return
        self.generic_visit(call)

    def visit_Assign(self, node):
        if isinstance(node.value, ast.Call):
            self.check_Call(call=node.value, targets=node.targets)
            return
        self.generic_visit(node)

    def visit_Call(self, node):
        self.check_Call(call=node)
