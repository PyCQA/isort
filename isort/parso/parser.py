from contextlib import contextmanager
from pathlib import Path

from parso.python.tree import Module, Newline, PythonLeaf, PythonNode, _LeafWithoutNewlines
from parso.tree import BaseNode, NodeOrLeaf
from parso.utils import parse_version_string
from typing import Iterator, List, Optional, TYPE_CHECKING, Tuple, Union

if TYPE_CHECKING:
    from isort.parso import fst, tokenizer


class Comment(_LeafWithoutNewlines):
    type = 'comment'
    __slots__ = ()


def partition_whitespaces(s: str, reverse=False) -> Tuple[str, str]:
    if not reverse:
        for i, ch in enumerate(s):
            if ch != ' ':
                break
    else:
        for i, ch in enumerate(reversed(s)):
            if ch != ' ':
                break

        i = len(s) - i

    whitespaces = s[:i]
    remaining = s[i:]
    return whitespaces, remaining


def contains_newlines(prefix_nodes: List[PythonLeaf]) -> bool:
    return any([isinstance(node, Newline) for node in prefix_nodes])


class PrefixPartsConsumer:
    def __init__(self, node: 'fst._AnyPythonNode'):
        self.node = node
        self.parts = list(node._split_prefix())
        self.current_ind = 0
        self.last_prefix = ''

    @contextmanager
    def incremented_position(self) -> Iterator[None]:
        if self.current_ind + 1 == len(self.parts):
            return

        self.current_ind += 1
        yield
        self.current_ind -= 1

    def _consume_comment(self) -> Tuple[Optional[Union[Comment, PythonNode]], int]:
        from isort import fst

        part = self.parts[self.current_ind]
        if part.type == 'comment':
            if part.start_pos[0] == self.node.line:
                self.last_prefix += part.value
                return None, 1

            comment = fst.create_python_leaf(Comment, part.value)

            # see if next one is newline, then make PythonNode from both of them
            with self.incremented_position():
                newline, _ = self._consume_newline()
                if newline is not None:
                    new_container_node = fst.create_python_container_node('simple_stmt', [
                        comment, newline
                    ])
                    return new_container_node, 2

        return None, 0

    def _consume_newline(self) -> Tuple[Optional[Newline], int]:
        from isort import fst

        part = self.parts[self.current_ind]
        if part.type == 'newline':
            return fst.create_newline(), 1

        return None, 0

    def consume_element(self) -> Union[Comment, Newline]:
        current_part = self.parts[self.current_ind]

        consumers = [self._consume_comment, self._consume_newline]
        for consumer in consumers:
            element, num_consumed = consumer(current_part)
            self.current_ind += num_consumed

            if element is not None:
                element.get_first_leaf().prefix = self.last_prefix
                element.parent = self.node.parent
                self.last_prefix = ''
                return element
        else:
            self.last_prefix = current_part.value
            self.current_ind += 1

    def extract_prefix_parts_as_nodes(self):
        from isort import fst

        child_ind = 0

        while self.current_ind != len(self.parts):
            element = self.consume_element()
            fst.insert_child(self.node, child_ind, element)
            child_ind += 1


def extract_all_line_comments(node: BaseNode) -> None:
    if not isinstance(node, PythonLeaf):
        for child in node.children:
            extract_elements_from_prefixes(child)
        return

    PrefixPartsConsumer(node).extract_prefix_parts_as_nodes()


def extract_elements_from_prefixes(node: BaseNode) -> None:
    if not isinstance(node, PythonLeaf):
        for child in node.children:
            extract_elements_from_prefixes(child)
        return

    end_whitespaces = ''
    if node.prefix.strip(' '):
        # contains comments
        prefix_nodes = []

        spacing = 0
        for part in node._split_prefix():
            # print(f'{part!r}, {part.value!r}')

            if part.type == 'spacing':
                spacing = len(part.value)

            if part.type == 'comment':
                comment = Comment(part.value, part.start_pos)
                comment.parent = node.parent
                comment.prefix = ' ' * part.start_pos[1]
                prefix_nodes.append(comment)
                spacing = 0

            if part.type == 'newline':
                newline = Newline(part.value, part.start_pos)
                newline.parent = node.parent
                if spacing:
                    newline.prefix = ' ' * spacing
                prefix_nodes.append(newline)
                spacing = 0

        beginning_whitespaces, _ = partition_whitespaces(node.prefix)
        prefix_nodes[0].prefix = beginning_whitespaces

        if contains_newlines(prefix_nodes):
            _, end_whitespaces = partition_whitespaces(node.prefix, reverse=True)

        index_of_current_node = node.parent.children.index(node)
        node.parent.children = node.parent.children[:index_of_current_node] + \
                               prefix_nodes + \
                               node.parent.children[index_of_current_node:]
        if len(end_whitespaces):
            node.prefix = end_whitespaces
        else:
            node.prefix = ''


def get_node_num_of_lines(node: PythonNode) -> int:
    return node.end_pos[0] - node.start_pos[0] + 1


def remove_nodes_on_the_line(nodes: List[NodeOrLeaf], line_number: int) -> None:
    for node in nodes:
        # if node resides completely on the line, remove it, or ends just at the beginning of the next one (newline)
        if ((node.start_pos[0] == line_number and node.end_pos[0] == line_number)
                or (node.start_pos[0] == line_number and node.end_pos == (line_number + 1, 0))):
            if node.parent is not None:
                node.parent.children.remove(node)
                continue

        if isinstance(node, BaseNode):
            remove_nodes_on_the_line(node.children, line_number)
            if len(node.children) == 0:
                node.parent.children.remove(node)


def list_all_nodes(tree: Module) -> List[NodeOrLeaf]:
    def scan(children):
        for element in children:
            yield element
            if isinstance(element, BaseNode):
                yield from scan(element.children)

    return list(scan(tree.children))


def remove_line(tree: Module, line_number: int) -> None:
    print('removing line', line_number)

    all_tree_nodes = list_all_nodes(tree)
    remove_nodes_on_the_line(all_tree_nodes, line_number)


def move_up_all_nodes_starting_from_line(tree: Module, line_number: int, steps: int) -> None:
    nodes = list_all_nodes(tree)
    for node in nodes:
        if isinstance(node, PythonLeaf):
            if node.start_pos[0] > line_number:
                node.start_pos = (node.start_pos[0] - steps, node.start_pos[1])


def move_down_all_nodes_starting_from_line(tree: Module, line_number: int, steps: int) -> None:
    nodes = list_all_nodes(tree)
    for node in nodes:
        if isinstance(node, PythonLeaf):
            if node.start_pos[0] >= line_number:
                node.start_pos = (node.start_pos[0] + steps, node.start_pos[1])


def parse_code(code: str) -> Module:
    from . import tokenizer

    version_info = parse_version_string('3.7')
    with (Path(__file__).parent / 'grammar37.txt').open() as f:
        grammar_text = f.read()

    grammar = tokenizer.MyPythonGrammar(version_info, grammar_text)
    tree = grammar.parse(code)
    return tree
