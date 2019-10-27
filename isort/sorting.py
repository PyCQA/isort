
def module_key(
    module_name: str,
    config: Mapping[str, Any],
    sub_imports: bool = False,
    ignore_case: bool = False,
    section_name: Optional[Any] = None,
) -> str:
    match = re.match(r"^(\.+)\s*(.*)", module_name)
    if match:
        sep = " " if config["reverse_relative"] else "_"
        module_name = sep.join(match.groups())

    prefix = ""
    if ignore_case:
        module_name = str(module_name).lower()
    else:
        module_name = str(module_name)

    if sub_imports and config["order_by_type"]:
        if module_name.isupper() and len(module_name) > 1:  # see issue #376
            prefix = "A"
        elif module_name[0:1].isupper():
            prefix = "B"
        else:
            prefix = "C"
    if not config["case_sensitive"]:
        module_name = module_name.lower()
    if section_name is None or "length_sort_" + str(section_name).lower() not in config:
        length_sort = config["length_sort"]
    else:
        length_sort = config["length_sort_" + str(section_name).lower()]
    return "{}{}{}".format(
        module_name in config["force_to_top"] and "A" or "B",
        prefix,
        length_sort and (str(len(module_name)) + ":" + module_name) or module_name,
    )
