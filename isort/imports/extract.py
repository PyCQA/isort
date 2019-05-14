import itertools
from collections import OrderedDict

from parso.python.tree import ImportFrom, ImportName, Module
from typing import Any, Dict, NamedTuple

from isort.finders import FindersManager
from isort.imports.parse import Imported, parse_from_imported_names, parse_straight_imported_names
from isort.parso import fst

ImportsInfo = NamedTuple('ImportsInfo', [
    ('imports', Dict[str, Any]),
    ('top_level_prefix', str),
    ('index_of_first_import_node', int)
])


def extract_imports(parsed_tree: Module, config: Dict[str, Any], sections: Any) -> ImportsInfo:
    imports = OrderedDict()

    for section in itertools.chain(sections, config['forced_separate']):
        imports[section] = {
            'straight': [],
            'from': OrderedDict()
        }

    finder = FindersManager(config=config, sections=sections)

    top_level_prefix = None
    index_of_first_import_python_node = None

    for import_node in list(parsed_tree.iter_imports()):
        if top_level_prefix is None:
            top_level_prefix = import_node.get_first_leaf().prefix

        if index_of_first_import_python_node is None:
            root_python_node = fst.get_root_python_node(import_node)
            index_of_first_import_python_node = parsed_tree.children.index(root_python_node)

        if isinstance(import_node, ImportName) and fst.get_parent_scope(import_node) == parsed_tree:
            # global straight imports
            import_names = parse_straight_imported_names(import_node)

            for import_name, alias, suffix_comment in import_names:
                section = finder.find(import_name)
                if section is not None:
                    imported = Imported(import_name, alias, suffix_comment)
                    imports[section]['straight'].append(imported)

            fst.remove_from_tree(import_node)

        if isinstance(import_node, ImportFrom) and fst.get_parent_scope(import_node) == parsed_tree:
            imported_from, import_names = parse_from_imported_names(import_node)

            for import_name, alias, suffix_comment in import_names:
                section = finder.find(import_name)
                if section is not None:
                    section_from_imports = imports[section]['from'].setdefault(imported_from, [])
                    imported = Imported(import_name, alias, suffix_comment)
                    section_from_imports.append(imported)

            fst.remove_from_tree(import_node)

    if index_of_first_import_python_node is None:
        index_of_first_import_python_node = 0

    return ImportsInfo(imports, top_level_prefix, index_of_first_import_python_node)
