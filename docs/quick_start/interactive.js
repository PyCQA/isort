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
    pyodide.runPython(`
import micropip

from js import document

def use_isort(*args):
    import isort
    import json
    import textwrap

    print(f"Using {isort.__version__} of isort.")

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

micropip.install('isort').then(use_isort)`);
});
