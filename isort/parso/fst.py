from parso.python.prefix import PrefixPart
from parso.python.tree import EndMarker, Module, Newline, Operator, PythonBaseNode, PythonLeaf, PythonNode, Scope
from parso.tree import BaseNode, Leaf
from typing import List, Tuple, Type, TypeVar, Union

# aliases
_AnyPythonNode = Union[PythonBaseNode, PythonLeaf, PythonNode]
_AnyContainerNode = Union[PythonBaseNode, PythonNode]
_Position = Tuple[int, int]

L = TypeVar('L', bound=PythonLeaf)
N = TypeVar('N', bound=PythonBaseNode)


def create_python_leaf(cls: Type[L], value: str, prefix: str = '') -> L:
    leaf = cls(value, (-1, -1), prefix=prefix)
    return leaf


def create_python_node(cls: Type[N], children: List[PythonLeaf]) -> N:
    node = cls([])
    for child in children:
        child.parent = node
    node.children = children
    return node


def create_python_container_node(type: str, children: List[_AnyPythonNode]) -> PythonNode:
    node = PythonNode(type, [])
    for child in children:
        child.parent = node
    node.children = children
    return node


def create_newline() -> Newline:
    return Newline('\n', (-1, -1))


def insert_child(node: _AnyContainerNode, pos: int, child: _AnyPythonNode) -> None:
    node.children.insert(pos, child)
    if child.parent is not None:
        raise ValueError('parent is already set')
    child.parent = node


def append_child(node: _AnyContainerNode, child: _AnyPythonNode) -> None:
    node.children.append(child)
    if child.parent is not None:
        raise ValueError('parent is already set')
    child.parent = node


def get_parent_scope(node: _AnyPythonNode) -> Scope:
    node = node.parent  # step at least once
    while not isinstance(node, Scope):
        node = node.parent
    return node


def is_container_ends_with_newline(node: _AnyContainerNode) -> bool:
    return node.children and isinstance(node.children[-1], Newline)


def is_newline_container_node(node: _AnyContainerNode) -> bool:
    if isinstance(node, Scope) or len(node.children) != 1:
        return False

    if isinstance(node.children[0], Newline) or is_newline_container_node(node.children[0]):
        return True

    return False


def remove_from_tree(node: _AnyPythonNode) -> None:
    if node.parent is None:
        # Module
        return

    parent = node.parent
    node.parent = None

    parent.children.remove(node)

    if len(parent.children) == 0 or is_newline_container_node(parent):
        remove_from_tree(parent)


def get_parent_python_node(node: _AnyPythonNode) -> PythonNode:
    node = node.parent  # step at least once
    while not isinstance(node, PythonNode) or node.type != 'simple_stmt':
        if isinstance(node.parent, Module):
            # not a PythonNode as a last container type
            return node

        node = node.parent
    return node


def get_root_python_node(node: _AnyPythonNode) -> PythonNode:
    while not isinstance(node.parent, Scope):
        node = node.parent
    return node


def strip_leading_newlines_for_prefix(leaf: Leaf) -> None:
    leaf.prefix = leaf.prefix.lstrip('\n')


def create_line_comment_node(contents: str, prefix: str = '') -> PythonNode:
    return create_python_container_node('comment_stmt', [
        create_python_leaf(Operator, contents, prefix),
        create_newline()
    ])


def _collect_prefix_from_parts(parts: List[PrefixPart]) -> str:
    val = ''
    for part in parts:
        val += part.value
    return val


def normalize_parsed_tree(tree: Module) -> None:
    """
    1. Extracts comment from Endmarker, if exists
    2. Ensures that file ends with newline, merges it with Endmarker comment if exists
    """
    endmarker = tree.get_last_leaf()  # type: EndMarker
    leaf_before_endmarker = tree.get_last_leaf().get_previous_leaf()

    last_node = get_parent_python_node(leaf_before_endmarker)
    module = get_root_python_node(last_node).parent

    if not is_container_ends_with_newline(last_node) or endmarker.prefix != '':
        newline = create_newline()

        if endmarker.prefix == '':
            append_child(last_node, newline)
        else:
            prefix_parts = list(endmarker._split_prefix())

            # if comment present in the prefix_parts, make new comment_stmt node with the contents
            for i, part in enumerate(prefix_parts):
                if part.type == 'comment':
                    comment_node = create_line_comment_node(part.value,
                                                            prefix=_collect_prefix_from_parts(prefix_parts[:i]))
                    insert_child(module, -1, comment_node)

                    endmarker.prefix = _collect_prefix_from_parts(prefix_parts[i + 1:])
                    break
            else:
                append_child(last_node, newline)


def _print(node: _AnyPythonNode, indent=0) -> None:
    indentation_step = ' ' * 4
    print(indent * indentation_step + repr(node))

    if isinstance(node, BaseNode):
        for child in node.children:
            _print(child, indent + 1)


def _print_delimiter(prefix=''):
    delimiter = '=' * 100
    if prefix:
        print(prefix.upper(), delimiter)
    else:
        print(delimiter)
