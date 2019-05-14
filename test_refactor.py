from icecream import ic
from parso.python.tree import ImportName, Keyword, Name, Newline, PythonBaseNode, PythonNode, Scope
from parso.tree import BaseNode
from typing import Any, List, NamedTuple, Type, TypeVar

from isort.parso.parser import get_node_num_of_lines, parse_code

N = TypeVar('N', bound=BaseNode)

BoxDimensions = NamedTuple('BoxDimensions', [
    ('start_pos', _Position),
    ('end_pos', _Position)
])


def create_node(cls: Type[N], children: List[_AnyPythonNode], start_pos: _Position, **kwargs: Any) -> N:
    new_node = cls(children=children, **kwargs)
    # new_node.start_pos = start_pos
    # TODO: set .parent for children to new_node
    # TODO: recompute all children start_pos according to new parent
    return new_node


def get_box_dimensions(node: PythonBaseNode) -> BoxDimensions:
    return BoxDimensions(node.start_pos, node.end_pos)


# def move_down_all_nodes_starting_from_line(tree: Module, line_number: int, steps: int) -> None:
#     nodes = list_all_nodes(tree)
#     for node in nodes:
#         if isinstance(node, PythonLeaf):
#             if node.start_pos[0] >= line_number:
#                 node.start_pos = (node.start_pos[0] + steps, node.start_pos[1])

def insert_child(index: int, root: PythonNode, child: PythonNode) -> None:
    child.parent = root
    root.children.insert(index, child)


def insert_node_into_scope(scope: Scope, node: PythonNode, line: int) -> None:
    # find suite PythonNode
    for child in scope.children:
        if isinstance(child, PythonNode) and child.type == 'suite':
            suite_node = child
            break
    else:
        raise ValueError("No 'suite' node.")

    print('suite_node.children', suite_node.children)

    node_num_of_lines = get_node_num_of_lines(node)
    node_num_of_columns = node.end_pos[1] - node.start_pos[1] + 1
    ic(node_num_of_lines, node_num_of_columns)

    line = line + 1  # first line will be newline, should stay there
    insert_child(line, suite_node, child=node)

    print('suite_node.children', suite_node.children)

    # if node_num_of_lines == 1:


DEFAULT_START_POS = (-1, -1)


def test_insert_import_node():
    code = """
def func():
    pass
    
def func2(): pass
    """.lstrip('\n ').rstrip()

    print()
    print('before', repr(code))

    tree = parse_code(code)

    import_node = create_node(ImportName,
                              [
                                  Keyword('import', DEFAULT_START_POS),
                                  Name('os', DEFAULT_START_POS, prefix=' ')
                              ],
                              start_pos=DEFAULT_START_POS)

    python_node = create_node(PythonNode,
                              [import_node,
                               Newline('\n', DEFAULT_START_POS)],
                              start_pos=DEFAULT_START_POS,
                              type='simple_stmt')

    # node_to_insert = ImportName([])
    # add_children(node_to_insert, [
    #     Keyword('import', DEFAULT_START_POS),
    #     Name('os', DEFAULT_START_POS)
    # ])
    # python_node = PythonNode('simple_stmt', [])
    # add_children(python_node, [
    #     node_to_insert,
    #     Newline('\n', DEFAULT_START_POS)
    # ])

    function1 = tree.children[0]
    print(function1.children[4])
    insert_node_into_scope(function1, python_node, 0)

    print('after', repr(tree.get_code()))
    print()
    print('after', tree.get_code())
