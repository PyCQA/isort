window.addEventListener('load', () => {
    var input = ace.edit("inputEditor");
    var output = ace.edit("outputEditor");
    var configurator = ace.edit("configEditor");

    [input, output, configurator].forEach((editor) => {
        editor.setTheme("ace/theme/monokai");
        editor.session.setMode("ace/mode/python");
        editor.resize();
    });

    configurator.session.setMode("ace/mode/json");

    function updateOutput() {
        output.setValue(document.sort_code(input.getValue(), configurator.getValue()));
    }

    output.setReadOnly(true);
    input.session.on('change', updateOutput);
    configurator.session.on('change', updateOutput);

    document.updateOutput = updateOutput;
});


languagePluginLoader.then(() => {
    return pyodide.loadPackage(['micropip'])
}).then(() => {
    console.log(pyodide.runPython('import sys\nsys.version'));
    console.log(pyodide.runPython('print(1 + 2)'));
    pyodide.runPython(`
import micropip

from js import document

def use_isort(*args):
    import isort
    import json
    import textwrap
    print(isort.code("import b; import a"))

    def sort_code(code, configuration):
        try:
            configuration = json.loads(configuration or "{}")
        except Exception as configuration_error:
            return "\\n".join(textwrap.wrap(f"Exception thrown trying to read given configuration {configuration_error}", 40))
        try:
            return isort.code(code, **configuration)
        except Exception as isort_error:
            return "\\n".join(textwrap.wrap(f"Exception thrown trying to sort given imports {isort_error}", 40))

    document.sort_code = sort_code
    document.updateOutput()

micropip.install('https://github.com/timothycrosley/isort/raw/develop/docs/interactive/isort-5.0.0-py3-none-any.whl').then(use_isort)`);
});
