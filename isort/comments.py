def parse(line: str) -> tuple[str, str | None]:
    """Parses import lines for comments and returns back the
    import statement and the associated comment.

    Returns ``None`` as the comment when no ``#`` is present in the line,
    and an empty string when a bare ``#`` with no text is present.
    """
    comment_start = line.find("#")
    if comment_start != -1:
        return (line[:comment_start], line[comment_start + 1 :].strip())

    return (line, None)


def add_to_line(
    comments: list[str] | None,
    original_string: str = "",
    removed: bool = False,
    comment_prefix: str = "",
) -> str:
    """Returns a string with comments added if removed is not set."""
    if removed:
        return parse(original_string)[0]

    if not comments:
        return original_string

    unique_comments: list[str] = []
    for comment in comments:
        if comment not in unique_comments:
            unique_comments.append(comment)
    comment_text = "; ".join(unique_comments)
    if comment_text:
        return f"{parse(original_string)[0]}{comment_prefix} {comment_text}"
    return f"{parse(original_string)[0]}{comment_prefix}"
