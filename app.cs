// Author: Martin Matusiak <numerodix@gmail.com>
// Licensed under the GNU Public License, version 3.

using System;
using IronPython.Hosting;
using Microsoft.Scripting;
using Microsoft.Scripting.Hosting;

public class App {
	static void Main(string[] args) {
		string pyscript = "gui.py";
		string path = GetPathToExecutable();
		pyscript = System.IO.Path.Combine(path, pyscript);

		ScriptRuntimeSetup scriptRuntimeSetup = new ScriptRuntimeSetup();

		LanguageSetup language = Python.CreateLanguageSetup(null);
		language.Options["FullFrames"] = true;
		scriptRuntimeSetup.LanguageSetups.Add(language);

		ScriptRuntime runtime = new Microsoft.Scripting.Hosting.ScriptRuntime(scriptRuntimeSetup);
		ScriptScope scope = runtime.CreateScope();
		scope.SetVariable("__SYS_ARGV", args);
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
		} catch (IronPython.Runtime.Exceptions.SystemExitException e) {
			Console.WriteLine(e.StackTrace);
		}
	}

	static string GetPathToExecutable() {
		string path = System.IO.Path.GetDirectoryName(
			System.Reflection.Assembly.GetExecutingAssembly().GetName().CodeBase).Substring(5);
		if (path.StartsWith("\\")) {
			path = path.Substring(1);
		}
		return path;
	}
}
