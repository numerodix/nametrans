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

		ScriptRuntimeSetup scriptRuntimeSetup = new ScriptRuntimeSetup();

		LanguageSetup language = Python.CreateLanguageSetup(null);
		language.Options["FullFrames"] = true;
		scriptRuntimeSetup.LanguageSetups.Add(language);

		ScriptRuntime runtime = new Microsoft.Scripting.Hosting.ScriptRuntime(scriptRuntimeSetup);
		ScriptScope scope = runtime.CreateScope();
		ScriptEngine engine = runtime.GetEngine("python");
		ScriptSource source = engine.CreateScriptSourceFromFile(pyscript);
		source.Compile();

		try {
			source.Execute(scope);
		} catch (IronPython.Runtime.Exceptions.SystemExitException e) {}
	}
}
