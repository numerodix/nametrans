targetdir := bin
targets := $(targetdir)/nametransgui.exe $(targetdir)/debug-nametransgui.exe
source := gsrc/launcher.cs
icon := resources/icon.ico

dlls := \
		-r:$(targetdir)/IronPython.dll \
		-r:$(targetdir)/Microsoft.Dynamic.dll \
		-r:$(targetdir)/Microsoft.Scripting.dll \
		-r:$(targetdir)/Microsoft.Scripting.Core.dll


all: $(targets)

$(targetdir)/nametransgui.exe: $(source)
	gmcs \
		-target:winexe \
		-win32icon:$(icon) \
		$(dlls) \
		-out:$@ \
		$<

$(targetdir)/debug-nametransgui.exe: $(source)
	gmcs \
		-target:exe \
		-win32icon:$(icon) \
		$(dlls) \
		-out:$@ \
		$<

web:
	rsync -avP --delete -e ssh web/ numerodix,nametrans@web.sourceforge.net:htdocs/


clean:
	rm -f $(targets)

.PHONY: all clean web
