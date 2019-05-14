import re

from parso.grammar import PythonGrammar
from parso.python import tree
from parso.python.parser import Parser
from parso.python.token import PythonTokenTypes, TokenType
from parso.python.tokenize import PythonToken
from parso.python.tree import PythonBaseNode


class CommentStmt(PythonBaseNode):
    type = 'comment_stmt'
    __slots__ = ()


class MyPythonTokenTypes:
    STRING = PythonTokenTypes.STRING
    NAME = PythonTokenTypes.NAME
    NUMBER = PythonTokenTypes.NUMBER
    OP = PythonTokenTypes.OP
    NEWLINE = PythonTokenTypes.NEWLINE
    INDENT = PythonTokenTypes.INDENT
    DEDENT = PythonTokenTypes.DEDENT
    ENDMARKER = PythonTokenTypes.ENDMARKER
    ERRORTOKEN = PythonTokenTypes.ERRORTOKEN
    ERROR_DEDENT = PythonTokenTypes.ERROR_DEDENT
    FSTRING_START = PythonTokenTypes.FSTRING_START
    FSTRING_STRING = PythonTokenTypes.FSTRING_STRING
    FSTRING_END = PythonTokenTypes.FSTRING_END

    COMMENT = TokenType('COMMENT', contains_syntax=False)


class MyParser(Parser):
    node_map = {
        'expr_stmt': tree.ExprStmt,
        'classdef': tree.Class,
        'funcdef': tree.Function,
        'file_input': tree.Module,
        'import_name': tree.ImportName,
        'import_from': tree.ImportFrom,
        'break_stmt': tree.KeywordStatement,
        'continue_stmt': tree.KeywordStatement,
        'return_stmt': tree.ReturnStmt,
        'raise_stmt': tree.KeywordStatement,
        'yield_expr': tree.YieldExpr,
        'del_stmt': tree.KeywordStatement,
        'pass_stmt': tree.KeywordStatement,
        'global_stmt': tree.GlobalStmt,
        'nonlocal_stmt': tree.KeywordStatement,
        'print_stmt': tree.KeywordStatement,
        'assert_stmt': tree.AssertStmt,
        'if_stmt': tree.IfStmt,
        'with_stmt': tree.WithStmt,
        'for_stmt': tree.ForStmt,
        'while_stmt': tree.WhileStmt,
        'try_stmt': tree.TryStmt,
        'comp_for': tree.CompFor,
        # Not sure if this is the best idea, but IMO it's the easiest way to
        # avoid extreme amounts of work around the subtle difference of 2/3
        # grammar in list comoprehensions.
        'list_for': tree.CompFor,
        # Same here. This just exists in Python 2.6.
        'gen_for': tree.CompFor,
        'decorator': tree.Decorator,
        'lambdef': tree.Lambda,
        'old_lambdef': tree.Lambda,
        'lambdef_nocond': tree.Lambda,
        'comment_stmt': CommentStmt,
    }

    _leaf_map = {
        PythonTokenTypes.STRING: tree.String,
        PythonTokenTypes.NUMBER: tree.Number,
        PythonTokenTypes.NEWLINE: tree.Newline,
        PythonTokenTypes.ENDMARKER: tree.EndMarker,
        PythonTokenTypes.FSTRING_STRING: tree.FStringString,
        PythonTokenTypes.FSTRING_START: tree.FStringStart,
        PythonTokenTypes.FSTRING_END: tree.FStringEnd,
    }


class MyPythonGrammar(PythonGrammar):
    def _get_token_namespace(self):
        return MyPythonTokenTypes

    def _tokenize_lines(self, lines, start_pos):
        tokens = super()._tokenize_lines(lines, start_pos)

        any_comment_regex = '#[^\n]*\n'
        for token in tokens:
            remaining = token.prefix
            match = re.search(any_comment_regex, remaining)

            while match:
                row = token.start_pos[0]
                left_ind, right_ind = match.span()
                prefix, comment, remaining = remaining[:left_ind], remaining[left_ind:right_ind], remaining[right_ind:]

                comment_token = PythonToken(MyPythonTokenTypes.COMMENT, comment[:-1], (row, 1 + len(prefix)), prefix)
                yield comment_token

                newline_token = PythonToken(PythonTokenTypes.NEWLINE, '\n', (row, 1 + len(prefix) + len(comment)), '')
                yield newline_token

                match = re.search(any_comment_regex, remaining)
                row += 1

            token = PythonToken(token.type, token.string, token.start_pos, remaining)
            yield token
