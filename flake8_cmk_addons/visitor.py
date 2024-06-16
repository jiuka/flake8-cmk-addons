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
        'cmk.agent_based.v2.AgentSection': 'AgentSection',
        'cmk.agent_based.v2.SimpleSNMPSection': 'SimpleSNMPSection',
        'cmk.agent_based.v2.SNMPSection': 'SNMPSection',
        'cmk.agent_based.v2.CheckPlugin': 'CheckPlugin',
        'cmk.agent_based.v2.InventoryPlugin': 'InventoryPlugin',
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
