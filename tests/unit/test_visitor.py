
import pytest

import ast
from textwrap import dedent

from flake8_cmk_addons.visitor import CmkAddonsVisitor


@pytest.fixture
def visitor():
    return CmkAddonsVisitor()


def test_function_map(visitor):
    assert 'foo' not in visitor.function
    tree = ast.parse(dedent(r'''
        def foo():
            pass
    '''))
    visitor.visit(tree)
    assert 'foo' in visitor.function


def test_fqpn_map(visitor):
    tree = ast.parse(dedent(r'''
        from pytest import alice
        from pytest import alice as bob
    '''))
    visitor.visit(tree)
    assert visitor.fqpn_map['alice'] == 'pytest.alice'
    assert visitor.fqpn_map['bob'] == 'pytest.alice'


@pytest.mark.parametrize('node, result', [
    [ast.Name(id='alice'), 'alice'],
    [ast.Attribute(value=ast.Name(id='alice'), attr='bob'), 'alice.bob'],
    [ast.Attribute(value=ast.Attribute(value=ast.Name(id='alice'), attr='bob'), attr='carol'), 'alice.bob.carol'],
])
def test_get_fqpn(visitor, node, result):
    assert visitor.get_fqpn(node) == result


@pytest.mark.parametrize('node, result', [
    [ast.Name(id='alice'), 'pytest.alice'],
    [ast.Attribute(value=ast.Name(id='alice'), attr='bob'), 'pytest.alice.bob'],
    [ast.Attribute(value=ast.Name(id='bob'), attr='carol'), 'pytest.alice.carol'],
])
def test_get_fqpn_with_maps(visitor, node, result):
    tree = ast.parse(dedent(r'''
        from pytest import alice
        from pytest import alice as bob
    '''))
    visitor.visit(tree)
    assert visitor.get_fqpn(node) == result
