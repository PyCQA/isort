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
    def javascript(self):
        return self.code

    @property
    def python(self):
        return self.code


@routes.add('\\')
class Escape(Handler):

    def start(self):
        self.children.append(PassThrough(self.parser.pop(), self))


class MultiLineComment(Handler):
    accept_children = Router((Escape, '/'))

    def _javascript(self):
        return '/* {0} */'.format(self.javascript_content)

    def _python(self):
        return '"""{0}"""'.format(self.python_content)


class JavaDocComment(MultiLineComment):

    def _javascript(self):
        return '/**\n{0}\n */'.format(self.javascript_content)

    def _python(self):
        return '""""\n{0}\n"""'.format(self.python_content)


@routes.add('/**\n')
class JavaScriptJavaDoc(JavaDocComment):
    end_on = '\n */'


@routes.add('""""\n')
class PythonJavaDoc(JavaDocComment):
    end_on = '\n"""'


@routes.add('"""')
class PythonComment(MultiLineComment):
    end_on = '"""'


@routes.add('/* ')
class JavaScriptComment(MultiLineComment):
    end_on = ' */'


@routes.add("'''")
class String(Handler):
    accept_children = Router((Escape, '\\'))
    end_on = "'''"

    def _javascript(self):
        content = self.javascript_content.split("\n")
        if len(content) <= 1:
            return Handler._javascript(self)

        output = []
        for line in content[:-1]:
             output.append("'{0}\\n' +".format(line))

        output.append("'{0}'".format(content[-1]))
        return "\n".join(output)


@routes.add("'")
class BasicString(Handler):
    accept_children = Router((Escape, '\\'))
    end_on = "'"


@routes.add('"')
class PythonBasicString(Handler):
    accept_children = Router((Escape, '\\'))
    end_on = '"'

    def _javascript(self):
        return ("'{0}'".format(self.javascript_content))


@routes.add('# ', '// ')
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

    def _javascript(self):
        content = self.python_content.split(" ")
        to_import = content[0]
        if "as" in content:
            variable_name = content[content.index('as') + 1]
        else:
            variable_name = to_import.split("/")[-1]

        if self.ended_on == " #":
            self.ended_on = " "

        return "var {0} = require('{1}');{2}".format(variable_name, to_import, self.ended_on)


@routes.add("): pass\n", ") {}\n")
class Pass(Handler):
    javascript = ') {}\n'
    python = '): pass\n'


@routes.add("True", "true")
class TrueStatement(Handler):
    javascript = 'true'
    python = 'True'


@routes.add("False", "false")
class FalseStatement(Handler):
    javascript = 'false'
    python = 'False'


@routes.add('None', 'null')
class NoneStatement(Handler):
    javascript = 'null'
    python = 'None'


@routes.add('print', 'console.log')
class PrintFunction(Handler):
    javascript = 'console.log'
    python = 'print'


@routes.add('var ')
class JavascriptSetter(Handler):
    accept_children = Router()


@routes.add('function ', 'def ')
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

    def _javascript(self):
        return "function " + self.javascript_content


@routes.add('^function(', '^def(')
class AnonymousFunction(Function):

    def _python(self):
        to_return = self.leading_whitespace + "def(" + self.python_content
        if self.ended_on == self.end_on[0]:
            to_return += ")"

        return to_return

    def _javascript(self):
        return self.leading_whitespace + "function(" + self.javascript_content


@routes.add('=def ')
class ExportFunction(Handler):
    end_on = "):\n"
    back_track = 2

    def _python(self):
        return Handler._python(self)[:-2]

    def _javascript(self):
        parts = self.javascript_content.split("(")
        return "module.exports.{0} = function({1}".format(parts[0], "(".join(parts[1:]),
                                                          self.javascript_content.split("("))


@routes.add('del ', 'delete ')
class DeleteStatement(Handler):
    javascript = 'delete '
    python = 'del '


@routes.add('if (', 'if ')
class IfStatement(Handler):
    end_on = ('):\n', ':\n', ') {\n')

    @property
    def back_track(self):
        if self.ended_on in ("):\n", ":\n"):
            return 2
        else:
            return 4

    def _python(self):
        to_return = "if {0}".format(self.python_content)
        if self.ended_on == "):\n":
            to_return += ")"

        return to_return

    def _javascript(self):
        if self.ended_on == ":\n" and self.started_on == 'if (':
            to_return = "if (({0}".format(self.javascript_content)
        else:
            to_return = "if ({0}".format(self.javascript_content)

        if self.ended_on == "):\n":
            to_return += ")"

        return to_return


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


class Block(Handler):

    def handle(self):
        self.indent = ''
        line = self.parser.text_after(self.started_at - 2, '\n')
        for character in line:
            if character in (" ", "\t"):
                self.indent += character
            else:
                break


@routes.add('):\n', ':\n')
class PythonBlock(Block):
    end_on = ('\n\n', ')', '    , ')
    javascript_start_with = ") {\n"

    @property
    def back_track(self):
        if self.ended_on == ")" and isinstance(self.parent, Parens):
            return 1

    def _javascript(self):
        content = self.javascript_start_with + self.javascript_content.rstrip(" ").rstrip("\t")

        extra = ""
        if self.ended_on == self.end_on[1]:
            extra = ")"
        elif self.ended_on == self.end_on[2]:
            extra = ", "

        last_child = self.last_child
        if last_child:
            last_child_index = len(self.children) - 1
            while (not self.children[last_child_index].javascript.strip() and not
                   isinstance(last_child, PythonNoop) and last_child_index > 0):
                self.children[last_child_index] = PassThrough('', self)
                last_child_index -= 1
            last_child = self.children[last_child_index]
        if isinstance(last_child, PythonBlock) and last_child.javascript.endswith("\n"):
            content += self.indent + "}" + extra
            if(isinstance(self.prev, (ExportFunction, AnonymousFunction)) and not self.ahead() in (".", "(", ";")
               and not extra == ", "):
                content += ";"
            if not extra:
                content += "\n\n"
            return content
        if(not self.javascript_content.replace("\n", "").strip().endswith(";") and not
           isinstance(last_child, (PythonNoop, EndOfLine, SingleLineComment)) and not self.ahead() in
           (".", "(", ";") and not extra == ", "):
            if content[-1] == "\n":
                content = content[:-1] + ";" + "\n"
            else:
                content += ";"

        if extra:
            content += self.indent + "}" + extra
        else:
            content += "\n" + self.indent + "}"
        if(isinstance(self.prev, (ExportFunction, AnonymousFunction)) and not self.ahead() in (".", "(", ";")
           and not extra == ", "):
            content += ";"

        if not extra:
            content += "\n"

        return content


@routes.add('try:\n')
class PythonTry(PythonBlock):
    javascript_start_with = "try {\n"


@routes.add(') {\n', 'try {\n')
class JavascriptBlock(Block):
    end_on = ("};", "}")
    python_start_with = ":\n"

    def _python(self):
        if not self.python_content.strip():
            to_return = "{0}{1}pass\n\n".format(self.python_start_with, self.indent + "    ")
        else:
            to_return = "{0}{1}".format(self.python_start_with, self.python_content)
        if isinstance(self.prev, Function):
            to_return = ")" + to_return

        return to_return


@routes.add('try {\n')
class JavascriptTry(JavascriptBlock):
    python_start_with = "try:\n"


@routes.add('(')
class Parens(Handler):
    end_on = ")"
    yield_for = ") {\n"

    def _javascript(self):
        if isinstance(self.last_child, PythonBlock) and self.last_child.ended_on == ")":
            return "(" + self.javascript_content

        return Handler._javascript(self)

    def _python(self):
        if isinstance(self.last_child, PythonBlock) and self.last_child.ended_on == ")":
            return "(" + self.python_content

        return Handler._python(self)


@routes.add('{')
class Dictionary(Handler):
    end_on = '}'


@routes.add(' is not ', ' !== ')
class IsNotStatement(Handler):
    javascript = ' !== '
    python = ' is not '


@routes.add(' is ', ' === ')
class IsStatement(Handler):
    javascript = ' === '
    python = ' is '


@routes.add(' not ', ' !')
class NotStatement(Handler):
    javascript = ' !'
    python = ' not '


@routes.add('not ', '!')
class NotStatement(Handler):
    python = 'not '
    javascript = '!'


@routes.add('Unset', 'undefined')
class Unset(Handler):
    javascript = 'undefined'
    python = 'Unset'


@routes.add(' and ', ' && ')
class AndKeyword(Handler):
    javascript = ' && '
    python = ' and '


@routes.add(' or ', ' || ')
class OrKeyword(Handler):
    javascript = ' || '
    python = 'or '


@routes.add('pass\n')
class PythonNoop(Handler):
    javascript = '\n'


@routes.add(';\n')
class EndOfStatement(Handler):
    back_track = 1

    def _python(self):
        return ''

    def _javascript(self):
        if self.behind() in ('\n', ' ', '\t', '/') or isinstance(self.prev, MultiLineComment):
            return ''

        return ';'


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


@routes.add('^String', '^str', '(String', '(str')
class String(Handler):

    def handle(self):
        if self.started_on.startswith("("):
            self.leading_whitespace = "("

    def _python(self):
        return self.leading_whitespace + 'str'

    def _javascript(self):
        return self.leading_whitespace + 'String'


@routes.add('^Boolean', '^bool', '(Boolean', '(bool')
class Boolean(Handler):

    def handle(self):
        if self.started_on.startswith("("):
            self.leading_whitespace = "("

    def _python(self):
        return self.leading_whitespace + 'bool'

    def _javascript(self):
        return self.leading_whitespace + 'Boolean'


@routes.add('^Number', '^int', '(Number', '(int')
class Number(Handler):

    def handle(self):
        if self.started_on.startswith("("):
            self.leading_whitespace = "("

    def _python(self):
        return self.leading_whitespace + 'int'

    def _javascript(self):
        return self.leading_whitespace + 'Number'


@routes.add('@')
class Decorator(Handler):
    end_on = ('\n', ')\n')

    def handle(self):
        (parts, _) = self.parser.text_till(("("), keep_index=True)
        self.function_name = parts.split()[-1]

    def _javascript(self):
        return "{1} = {0}({1});\n".format(Handler._javascript(self)[1:-1], self.function_name)


@routes.add('.append(', '.push(')
class Append(Handler):
    javascript = '.push'
    python = '.append'
    back_track = 1


@routes.add('raise ', 'throw ')
class Append(Handler):
    javascript = 'throw '
    python = 'raise '


no_nested_parens = routes.excluding('(')
IfStatement.accept_children = no_nested_parens
Function.accept_children = no_nested_parens
ElifStatement.accept_children = no_nested_parens
ExportFunction.accept_children = no_nested_parens
Decorator.accept_children = no_nested_parens
