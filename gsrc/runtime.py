# Author: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

import clr
import System
import System.Reflection

def get_runtime_string():
    runtime = None

    mono_runtime = System.Type.GetType('Mono.Runtime', False)
    if mono_runtime:
        dm = mono_runtime.GetMethod('GetDisplayName',
                                    System.Reflection.BindingFlags.Static 
                                    | System.Reflection.BindingFlags.NonPublic
                                    | System.Reflection.BindingFlags.DeclaredOnly
                                    | System.Reflection.BindingFlags.ExactBinding)
        if dm:
            runtime = dm.Invoke(None, System.Array[object]([]))
        else:
            runtime = System.Environment.Version
        runtime = "Mono %s" % runtime
    else:
        ver = System.Environment.Version
        runtime = ".NET %s.%s" % (ver.Major, ver.Minor)

    return runtime

def get_assemblies():
    assemblies = []
    for ass in System.AppDomain.CurrentDomain.GetAssemblies():
        assemblies.append(ass)
    assemblies.sort(key=lambda ass: getattr(ass, 'FullName').lower())
    return assemblies

