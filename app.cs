using System;
using IronPython.Hosting;
using Microsoft.Scripting;
using Microsoft.Scripting.Hosting;

public class App {
	static void Main(string[] args) {
		string pyscript = "glade.py";
		if (args.Length > 0) {
			pyscript = args[0];
		}

		string path = System.IO.Path.GetDirectoryName(
			System.Reflection.Assembly.GetExecutingAssembly().GetName().CodeBase).Substring(5);
		if (path.StartsWith("\\")) {
			path = path.Substring(1);
		}

		pyscript = System.IO.Path.Combine(path, pyscript);

		ScriptRuntimeSetup scriptRuntimeSetup = new ScriptRuntimeSetup();

		LanguageSetup language = Python.CreateLanguageSetup(null);
		language.Options["FullFrames"] = true;
		scriptRuntimeSetup.LanguageSetups.Add(language);

		ScriptRuntime runtime = new Microsoft.Scripting.Hosting.ScriptRuntime(scriptRuntimeSetup);
		ScriptScope scope = runtime.CreateScope();
		ScriptEngine engine = runtime.GetEngine("python");

		// add sys.path inside python code instead, makes it runnable also
		// with ipy.exe
/*
		var paths = engine.GetSearchPaths();
		paths.Add(path);
		paths.Add(System.IO.Path.Combine(path, "pylib"));
		engine.SetSearchPaths(paths);
*/
		ScriptSource source = engine.CreateScriptSourceFromFile(pyscript);
		source.Compile();

		try {
			source.Execute(scope);
		} catch (IronPython.Runtime.Exceptions.SystemExitException e) {}
	}
}
