"""The core logic that decides how to build the VERY Abstract Syntax Tree.

Defines what text gets matched and what handler will represent it.
"""
from .router import Router

routes = Router()


class AbstractHandler(object):
    __slots__ = ('parent', 'index')
    started_on = ""
    source = ""
    children = ()

    def __init__(self, parent):
        self.parent = parent
        self.index = parent and len(parent.children) or 0

    @property
    def prev(self):
        if self.index > 0:
            return self.parent and self.parent.children[self.index - 1]

    @property
    def next(self):
        if self.parent and self.index < len(self.parent.children) -1:
            return self.parent.children[self.index + 1]

    def __repr__(self):
        self_representation = "{0}({1})".format(self.__class__.__name__, self.index)
        if self.started_on:
            self_representation = "{0} <-- {1}".format(self_representation, self.started_on)

        representation = [self_representation]
        for child in self:
            for index, line in enumerate(repr(child).split("\n")):
                if index == 0:
                    representation.append("|---" + line)
                else:
                    representation.append("|  " + line)
        return "\n".join(representation)

    def __str__(self):
        return self.source

    def __iter__(self):
        return self.children.__iter__()


class Handler(AbstractHandler):
    """A Handler encapsulates both the node / position information in the produced AST alongside the code used
       to generate the nodes contained within it"""
    start_on = ()
    end_on = ()
    yield_for = ()
    accept_children = routes
    back_track = 0

    def __init__(self, parser, started_on='', started_at=0, parent=None):
        AbstractHandler.__init__(self, parent)
        self.parser = parser
        self.index = parent and len(parent.children) or 0
        self.children = []
        self.started_on = started_on
        self.started_at = started_at
        self.start_index = started_at - len(started_on) + 1
        self.ended_on = ''
        self.ended_at = 0
        if isinstance(self.end_on, str):
            self.end_on = (self.end_on, )
        if isinstance(self.yield_for, str):
            self.yield_for = (self.yield_for, )

        self.start()

    def __getitem__(self, index):
        return self.children[index]

    def handle(self):
        pass

    @property
    def last_child(self):
        return self.children and self.children[-1]

    def start(self):
        self.handle()
        if not self.end_on and self.parent:
            self.parser -= self.back_track or 0
            self.ended_at = self.parser.index
            return

        while self.parser.more:
            (text, matched) = self.parser.text_till(self.yield_for + self.end_on + self.accept_children.match_on)
            if text:
                self.children.append(PassThrough(text, self))
            if matched in self.end_on:
                self.parser += len(matched) - 1
                self.ended_on = matched
                break

            if not matched:
                break

            handler = self.accept_children.get(matched, None)
            if handler:
                self.parser += len(matched) - 1
                self.children.append(handler(self.parser, matched, self.parser.index - 1, parent=self))
                handler.ended_at = self.parser.index
            else:
                raise NotImplementedError('There is no support to handle ' + matched)

        self.parser -= self.back_track or 0
        self.ended_at = self.parser.index

    @property
    def leading_whitespace(self):
        if self.started_on.startswith('^'):
            return self.parser.code[self.start_index]

        return ""

    @property
    def javascript_content(self):
        return "".join((child.javascript for child in self.children))

    def _javascript(self):
        return (self.started_on or '') + self.javascript_content + (self.ended_on or '')

    @property
    def javascript(self):
        return self._javascript()

    @property
    def python_content(self):
        return "".join((child.python for child in self.children))

    def _python(self):
        return (self.started_on or '') + self.python_content + (self.ended_on or '')

    @property
    def python(self):
        return self._python()

    def behind(self, amount=1):
        return self.parser.behind(self.started_at, amount)

    def ahead(self, amount=1):
        return self.parser.ahead(self.ended_at, amount)

    def next_content(self, amount=1):
        return self.parser.next_content(self.ended_at, amount)

    def prev_content(self, amount=1):
        return self.parser.next_content(self.started_at, amount)


class PassThrough(AbstractHandler):
    __slots__ = ('code')

    def __init__(self, code, parent):
        AbstractHandler.__init__(self, parent)
        self.code = code

    @property
    def python(self):
        return self.code


@routes.add('\\')
class Escape(Handler):

    def start(self):
        self.children.append(PassThrough(self.parser.pop(), self))


class MultiLineComment(Handler):
    accept_children = Router((Escape, '/'))

    def _python(self):
        return '"""{0}"""'.format(self.python_content)


@routes.add('"""')
class PythonComment(MultiLineComment):
    end_on = '"""'


@routes.add("'''")
class String(Handler):
    accept_children = Router((Escape, '\\'))
    end_on = "'''"


@routes.add("'")
class BasicString(Handler):
    accept_children = Router((Escape, '\\'))
    end_on = "'"


@routes.add('"')
class PythonBasicString(Handler):
    accept_children = Router((Escape, '\\'))
    end_on = '"'

@routes.add('# ')
class SingleLineComment(Handler):
    accept_children = Router()
    end_on = "\n"
    back_track = 1


@routes.add("import ")
class PythonImport(Handler):
    end_on = ("\n", " #", " //")

    @property
    def back_track(self):
        if self.ended_on == " #":
            return 1
        return 0

@routes.add('def ')
class Function(Handler):
    end_on = ("):\n", ") {\n")

    @property
    def back_track(self):
        if self.ended_on == "):\n":
            return 2
        elif self.ended_on == ") {\n":
            return 4

    def _python(self):
        to_return = "def " + self.python_content
        if self.ended_on == self.end_on[0]:
            return "def " + self.python_content + ")"

        return to_return


@routes.add('^def(')
class AnonymousFunction(Function):
pace + "function(" + self.javascript_content


@routes.add('if (', 'if ')
class IfStatement(Handler):
    end_on = ('):\n', ':\n', ') {\n')

    @property
    def back_track(self):
        if self.ended_on in ("):\n", ":\n"):
            return 2
        else:
            return 4


@routes.add('for (', 'for ')
class ForStatement(Handler):
    javascript = 'for ('
    python = 'for '


@routes.add('while (', 'while ')
class WhileStatement(Handler):
    javascript = 'while ('
    python = 'while '


@routes.add('elif ', '^} else if (')
class ElifStatement(Handler):
    end_on = (":\n", ") {\n")

    def _python(self):
        return self.leading_whitespace + 'elif ' + self.python_content + ":\n"

    def _javascript(self):
        return self.leading_whitespace + '} else if (' + self.javascript_content + ") {\n"


@routes.add('except Exception as ', 'except', '^} catch (')
class ExceptStatement(Handler):
    end_on = (":\n", ") {\n")

    def _python(self):
        if self.python_content:
            return self.leading_whitespace + 'except Exception as ' + self.python_content + ":\n"
        return self.leading_whitespace + 'except' + self.python_content + ":\n"

    def _javascript(self):
        return self.leading_whitespace + '} catch (' + self.javascript_content + ") {\n"


@routes.add('else:\n', '^} else {\n')
class ElseStatement(Handler):

    def _python(self):
        return self.leading_whitespace + 'else:\n'

    def _javascript(self):
        return self.leading_whitespace + '} else {\n'


@routes.add('try:\n')
class PythonTry(PythonBlock):
    pass


@routes.add('(')
class Parens(Handler):
    end_on = ")"


@routes.add('\n')
class EndOfLine(Handler):

    def _python(self):
        return '\n'

    def _javascript(self):
        if self.behind() in ('\n', ' ', '\t', '/', ',', '{', '+'):
            return "\n"
        if(isinstance(self.prev, (EndOfStatement, Block, SingleLineComment)) or isinstance(self.parent, Dictionary) or
           isinstance(self.prev, MultiLineComment) or
           self.next_content() in (';', '.', '(')):
            return "\n"
        elif(isinstance(self.prev, Parens) and isinstance(self.prev.last_child, PythonBlock) and
             self.prev.last_child.ended_on == ")"):
            return "\n"

        return ';\n'


@routes.add('@')
class Decorator(Handler):
    end_on = ('\n', ')\n')

    def handle(self):
        (parts, _) = self.parser.text_till(("("), keep_index=True)
        self.function_name = parts.split()[-1]


no_nested_parens = routes.excluding('(')
IfStatement.accept_children = no_nested_parens
Function.accept_children = no_nested_parens
ElifStatement.accept_children = no_nested_parens
ExportFunction.accept_children = no_nested_parens
Decorator.accept_children = no_nested_parens
