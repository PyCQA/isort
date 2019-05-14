from parso.python.tree import ImportFrom, ImportName, Name, PythonNode
from typing import List, NamedTuple, Optional, Tuple, Union


Imported = NamedTuple('Imported', [
    ('name', str),
    ('alias', Optional[str]),
    ('suffix_comment', str)
])


def consume_same_line_suffix_comment(node: Name) -> str:
    next_leaf = node.get_next_leaf()
    if not next_leaf:
        return ''

    same_line_comment, sep, remaining_comment = next_leaf.prefix.partition('\n')
    if not sep:
        # no newlines
        return same_line_comment
    else:
        next_leaf.prefix = remaining_comment
        return same_line_comment


def _parse_imported_name(node: Union[Name, PythonNode]) -> Optional[Imported]:
    if isinstance(node, Name):
        suffix_comment = consume_same_line_suffix_comment(node)
        return Imported(node.value, None, suffix_comment)

    if isinstance(node, PythonNode) and node.type == 'dotted_name':
        import_name_parts = []
        for node in node.children:
            if isinstance(node, Name):
                import_name_parts.append(node.value)
        suffix_comment = consume_same_line_suffix_comment(node.get_last_leaf())
        return Imported('.'.join(import_name_parts), None, suffix_comment)

    if isinstance(node, PythonNode) and node.type == 'import_as_name':
        name = node.children[0].value
        alias = node.children[2].value

        suffix_comment = consume_same_line_suffix_comment(node.children[2])
        return Imported(name, alias, suffix_comment)

    return None


def parse_straight_imported_names(import_node: ImportName) -> List[Imported]:
    import_names = []  # type: List[Imported]
    for child in import_node.children:
        imported = _parse_imported_name(child)
        if imported:
            import_names.append(imported)

    return import_names


def parse_from_imported_names(import_node: ImportFrom) -> Tuple[str, List[Imported]]:
    imported_from = _parse_imported_name(import_node.children[1]).name

    import_expr = import_node.children[3]
    imports = []  # type: List[Imported]
    if isinstance(import_expr, PythonNode) and import_expr.type == 'import_as_names':
        for i in range(0, len(import_expr.children), 2):
            import_as_node = import_expr.children[i]
            imported = _parse_imported_name(import_as_node)
            if imported:
                imports.append(imported)

    elif isinstance(import_expr, Name):
        imported = _parse_imported_name(import_expr)
        if imported:
            imports.append(imported)

    else:
        # TODO: remove later
        raise ValueError('Unknown type of import_as {import_expr}'.format(import_expr=repr(import_expr)))

    return imported_from, imports
