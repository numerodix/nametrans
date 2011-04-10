# Author: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

import clr
import System
import System.Diagnostics
import System.Reflection

import fnmatch
import re
import os

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

def get_platform_string_windows():
    """
    Reference: http://solarbeam.git.sourceforge.net/git/gitweb.cgi?p=solarbeam/solarbeam;a=blob;f=libsolar/Util/Platform/PlatformDetect.cs;h=df154da3546f42a8a439af2c6a6c058d180949d5;hb=HEAD
    Reference: http://support.microsoft.com/kb/304283
    Reference: http://www.codeproject.com/KB/system/osversion.aspx
    Reference: http://www.codeguru.com/cpp/w-p/system/systeminformation/article.php/c8973/
    """
    platform_string = "Windows"

    os = System.Environment.OSVersion
    ver_str = ("%s.%s.%s.%s" % (
        os.Platform, os.Version.Major, os.Version.Minor, os.Version.Revision))

    index = [
        ["Win32Windows.[0-9]*.0",           "Windows 95"],
        ["Win32Windows.[0-9]*.10.2222A",    "Windows 98 Second Edition"],
        ["Win32Windows.[0-9]*.10",          "Windows 98"],
        ["Win32Windows.[0-9]*.90",          "Windows Me"],
        ["Win32NT.3",                       "Windows NT 3.51"],
        ["Win32NT.4",                       "Windows NT 4.0"],
        ["Win32NT.5.0",                     "Windows 2000"],
        ["Win32NT.5.1",                     "Windows XP"],
        ["Win32NT.5.2",                     "Windows 2003"],
        ["Win32NT.6.0",                     "Windows Vista"],
        ["Win32NT.6.1",                     "Windows 7"],
    ]

    for (pat, plat_str) in index:
        if re.match('^' + pat, ver_str):
            platform_string = "%s  (%s)" % (plat_str, ver_str)
            break

    return platform_string

def invoke(cmd, args=None):
    args = args if args else []
    p = System.Diagnostics.Process()
    p.StartInfo.UseShellExecute = False
    p.StartInfo.RedirectStandardOutput = True
    p.StartInfo.FileName = cmd
    p.StartInfo.Arguments = " ".join(args)
    try:
        p.Start()
        output = p.StandardOutput.ReadToEnd().Trim()
        p.WaitForExit()
        if p.ExitCode == 0:
            return output
    except:
        return ""

def get_platform_string_unix():
    """
    Reference: http://solarbeam.git.sourceforge.net/git/gitweb.cgi?p=solarbeam/solarbeam;a=blob;f=libsolar/Util/Platform/PlatformDetect.cs;h=df154da3546f42a8a439af2c6a6c058d180949d5;hb=HEAD
    """
    platform_string = "Unix"

    def join_nonempty(sep, *args):
        args = filter(lambda i: i != '', args)
        return sep.join(args)

    def get_platform_string():
        os = invoke("uname", ["-s"])
        release = invoke("uname", ["-r"])
        machine = invoke("uname", ["-m"])

        if os == "SunOS":
            os = "Solaris"
            machine = invoke("uname", ["-p"])

        return join_nonempty(" ", os, release, machine)

    def get_version_string():

        # Try lsb_release

        def find_prop(args):
            s = invoke(args[0], args[1:])
            return re.sub('^.*?:\s*', '', s).strip()

        distro = find_prop(["lsb_release", "-i"])
        release = find_prop(["lsb_release", "-r"])
        codename = find_prop(["lsb_release", "-c"])

        # Try /etc/lsb-release

        if not distro and os.path.exists('/etc/lsb-release'):
            def find_line(key, s):
                m = re.search('(?m)^' + re.escape(key) + '=(.*)$', s)
                if m:
                    return m.group(1).strip()
                return ''

            content = open('/etc/lsb-release').read()
            distro = find_line('DISTRIB_ID', content)
            release = find_line('DISTRIB_RELEASE', content)
            codename = find_line('DISTRIB_CODENAME', content)

        # Try /etc/ files

        elif not distro:
            fps = os.listdir('/etc')
            def pred(fp):
                for pat in ["*-rel*", "*_ver*", "*-version"]:
                    if fnmatch.fnmatch(fp, pat):
                        return True
            fps = filter(pred, fps)

            if fps and "debian_version" in fps:
                distro = "Debian"
                codename = open("/etc/debian_version").read().strip()

            elif fps:
                fp = fps[0]
                distro = open(os.path.join('/etc', fp)).read().strip()

        if distro == "n/a": distro = ""
        if release == "n/a": release = ""
        if codename == "n/a": codename = ""

        return join_nonempty(" ", distro, release, codename)

    parts = [get_platform_string(), get_version_string()]
    joined = join_nonempty(" ~ ", *parts)
    if joined:
        platform_string = joined

    return platform_string

def get_platform_string():
    platform_string = None

    p = System.Environment.OSVersion.Platform
    if p == System.PlatformID.Unix:
        platform_string = get_platform_string_unix()
    else:
        platform_string = get_platform_string_windows()

    return platform_string

