import itertools
from collections import OrderedDict, namedtuple
from operator import attrgetter, itemgetter

from parso.python.tree import EndMarker, Import, ImportFrom, ImportName, Module, Newline, PythonNode
from parso.tree import BaseNode
from typing import Any, Dict, List

from isort.finders import FindersManager
from isort.format import format_natural, format_simplified
from isort.imports import output
from isort.imports.extract import ImportsInfo
from isort.imports.output import output_imports
from isort.imports.parse import Imported, parse_from_imported_names, parse_straight_imported_names
from isort.parso import fst
from isort.parso.parser import parse_code


def has_unprocessed_imports(imports: Dict[str, Any]) -> bool:
    for key, section_dict in imports.items():
        for import_type, import_type_dict in section_dict.items():
            if import_type_dict:
                return True
    return False


def has_any_contents_left(tree: Module, index_of_first_non_top_level_node: int) -> bool:
    for node in tree.children[index_of_first_non_top_level_node:]:
        if not isinstance(node, (EndMarker, Newline)):
            return True

    return False


def extract_prefix_comment(import_node: Import) -> str:
    root_node = fst.get_root_python_node(import_node)
    node_prefix = root_node.get_first_leaf().prefix
    import_prefix_comment = node_prefix.rstrip('\n ')
    return import_prefix_comment


def extract_imported_names(node: BaseNode) -> List[str]:
    imported_names = []
    if isinstance(node, PythonNode):
        for child in node.children:
            imported_names.extend(extract_imported_names(child))

    elif isinstance(node, ImportName):
        for name_expr in node.get_defined_names():
            imported_names.append(name_expr.value)

    return imported_names


def extract_top_level_imports(parsed: Module) -> List[str]:
    top_level_imports = []
    for node in parsed.children:
        node_imported_names = extract_imported_names(node)
        top_level_imports.extend(node_imported_names)

    return top_level_imports


def get_sections_namedtuple(config: Dict[str, Any]) -> Any:
    section_names = config['sections']
    return namedtuple('Sections', section_names)(*[name for name in section_names])


class _SortImports2:
    def __init__(self, file_contents: str, config: Dict[str, Any], extension: str = "py") -> None:
        self.config = config
        self.extension = extension

        self.imports_to_remove = [format_simplified(removal) for removal in self.config['remove_imports']]
        self.imports_to_add = [format_natural(addition) for addition in self.config['add_imports']]

        self.sections = get_sections_namedtuple(self.config)
        self.finder = FindersManager(config=config, sections=self.sections)

        self.imports = OrderedDict()  # type: OrderedDict[str, Any]
        for section in self.get_sections():
            self.imports[section] = {
                'straight': [],
                'from': OrderedDict()
            }

        self.parsed_tree = parse_code(file_contents)
        fst.normalize_parsed_tree(self.parsed_tree)

        top_level_prefix = None
        index_of_first_import_python_node = None

        for import_node in list(self.parsed_tree.iter_imports()):
            if top_level_prefix is None:
                top_level_prefix = import_node.get_first_leaf().prefix

            if index_of_first_import_python_node is None:
                root_python_node = fst.get_root_python_node(import_node)
                index_of_first_import_python_node = self.parsed_tree.children.index(root_python_node)

            if isinstance(import_node, ImportName) and fst.get_parent_scope(import_node) == self.parsed_tree:
                # global straight imports
                self.extract_straight_imported_names(import_node)
                fst.remove_from_tree(import_node)

            if isinstance(import_node, ImportFrom) and fst.get_parent_scope(import_node) == self.parsed_tree:
                self.extract_from_imported_names(import_node)
                fst.remove_from_tree(import_node)

        if index_of_first_import_python_node is None:
            index_of_first_import_python_node = 0

        first_content_leaf = self.parsed_tree.children[index_of_first_import_python_node].get_first_leaf()
        fst.strip_leading_newlines_for_prefix(first_content_leaf)

        has_any_contents = has_any_contents_left(self.parsed_tree,
                                                 index_of_first_non_top_level_node=index_of_first_import_python_node)

        imports_info = ImportsInfo(self.imports, top_level_prefix, index_of_first_import_python_node)
        # for section, imports in imports_info.imports.items():
        #     print(section, imports)

        any_imports_added, next_import_index = output_imports(self.parsed_tree, imports_info, self.get_sections())

        if has_any_contents and any_imports_added:
            lines_after_imports = self.config['lines_after_imports']
            if lines_after_imports == -1:
                lines_after_imports = 1
            else:
                lines_after_imports = lines_after_imports

            for _ in range(lines_after_imports):
                fst.insert_child(self.parsed_tree, next_import_index,
                                 fst.create_newline())
                next_import_index += 1

        print('code', repr(self.parsed_tree.get_code()))

    def extract_straight_imported_names(self, import_name_node: ImportName) -> None:
        import_names = parse_straight_imported_names(import_name_node)

        for import_name, alias, suffix_comment in import_names:
            section = self.finder.find(import_name)
            if section is not None:
                imported = Imported(import_name, alias, suffix_comment)
                self.imports[section]['straight'].append(imported)

    def extract_from_imported_names(self, import_name_node: ImportFrom) -> None:
        imported_from, import_names = parse_from_imported_names(import_name_node)

        for import_name, alias, suffix_comment in import_names:
            section = self.finder.find(imported_from + '.' + import_name)
            if section is not None:
                section_from_imports = self.imports[section]['from'].setdefault(imported_from, [])
                imported = Imported(import_name, alias, suffix_comment)
                section_from_imports.append(imported)

    def get_sections(self) -> List[str]:
        return list(self.sections) + self.config['forced_separate']

    @property
    def output(self):
        return self.parsed_tree.get_code()
