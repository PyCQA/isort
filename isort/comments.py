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
    base, existing_comment = parse(original_string)
    if existing_comment is not None:
        # An existing comment was stripped off, leaving the whitespace that used to
        # precede it (the previous ``comment_prefix`` spacing). Drop it so re-adding a
        # comment does not accumulate leading spaces on every run. Bases without a
        # comment (e.g. the indentation-only strings used by the multi-line wrap modes)
        # are left untouched so their indentation is preserved.
        base = base.rstrip()
    if comment_text:
        return f"{base}{comment_prefix} {comment_text}"
    return f"{base}{comment_prefix}"
