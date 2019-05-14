from operator import attrgetter, itemgetter

from parso.python.tree import ImportFrom, Keyword, Module, Name, Operator, PythonNode
from typing import Any, Dict, List, NamedTuple, Union

from isort.imports.extract import ImportsInfo
from isort.imports.parse import Imported
from isort.natural import nsorted
from isort.parso import fst


def create_single_import_node(imported: Imported) -> Union[Name, PythonNode]:
    if imported.alias:
        return fst.create_python_container_node('import_as_name', [
            fst.create_python_leaf(Name, imported.name),
            fst.create_python_leaf(Keyword, 'as', prefix=' '),
            fst.create_python_leaf(Name, imported.alias, prefix=' ')
        ])
    else:
        return fst.create_python_leaf(Name, imported.name)


def new_straight_import_node(imported: Imported) -> PythonNode:
    new_import_node = create_single_import_node(imported)
    # after "import" and after ","
    first_leaf = new_import_node if isinstance(new_import_node, Name) else new_import_node.get_first_leaf()
    first_leaf.prefix = ' '

    trailing_newline = fst.create_newline()
    new_node = fst.create_python_container_node('simple_stmt', [
        fst.create_python_leaf(Keyword, 'import'),
        new_import_node,
        trailing_newline
    ])

    if imported.suffix_comment:
        trailing_newline.prefix = imported.comments.suffix

    return new_node


def new_from_import_node(from_: str, imports: List[Imported]) -> PythonNode:
    import_as_names = []
    for i, imported in enumerate(imports):
        new_import_node = create_single_import_node(imported)
        # after "import" and after ","
        first_leaf = new_import_node if isinstance(new_import_node, Name) else new_import_node.get_first_leaf()
        first_leaf.prefix = ' '

        import_as_names.append(new_import_node)
        if i + 1 != len(imports):
            # not last
            import_as_names.append(fst.create_python_leaf(Operator, ','))

    import_from_children = [
        fst.create_python_leaf(Keyword, 'from'),
        fst.create_python_leaf(Name, from_, prefix=' '),
        fst.create_python_leaf(Keyword, 'import', prefix=' '),
        fst.create_python_container_node('import_as_names', import_as_names)
    ]

    trailing_newline = fst.create_newline()
    new_node = fst.create_python_container_node('simple_stmt', [
        fst.create_python_node(ImportFrom, import_from_children),
        trailing_newline
    ])
    return new_node


OutputImportsInfo = NamedTuple('OutputImportsInfo', [
    ('any_imports_added', bool),
    ('last_import_index', int)
])


def has_unprocessed_imports(imports: Dict[str, Any]) -> bool:
    for key, section_dict in imports.items():
        for import_type, import_type_dict in section_dict.items():
            if import_type_dict:
                return True
    return False


def _sort_by_module():
    pass


def output_imports(parsed_tree: Module, imports_info: ImportsInfo,
                   config: Dict[str, Any], sections: Any) -> OutputImportsInfo:
    order_by_import_type = config['order_by_type']

    any_imports_added = False
    top_level_prefix_added = False

    next_import_index = imports_info.index_of_first_import_node

    for section in sections:
        section_added = False

        section_straight_imports = imports_info.imports[section].pop('straight')
        if section_straight_imports:
            any_imports_added = True
            section_added = True

            for imported in nsorted(section_straight_imports, key=itemgetter(0)):
                new_node = new_straight_import_node(imported)
                if not top_level_prefix_added:
                    new_node.get_first_leaf().prefix = imports_info.top_level_prefix
                    top_level_prefix_added = True

                fst.insert_child(parsed_tree, next_import_index,
                                 new_node)
                next_import_index += 1

        section_from_imports = imports_info.imports[section].pop('from')
        if section_from_imports:
            any_imports_added = True
            section_added = True

            for imported_from, imports in section_from_imports.items():
                imports = nsorted(imports, key=attrgetter('name'))
                new_node = new_from_import_node(imported_from, imports)
                if not top_level_prefix_added:
                    new_node.get_first_leaf().prefix = imports_info.top_level_prefix
                    top_level_prefix_added = True

                fst.insert_child(parsed_tree, next_import_index,
                                 new_node)
                next_import_index += 1

        if section_added and has_unprocessed_imports(imports_info.imports):
            fst.insert_child(parsed_tree, next_import_index,
                             fst.create_newline())
            next_import_index += 1

    return OutputImportsInfo(any_imports_added, next_import_index)
