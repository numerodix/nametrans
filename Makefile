targetdir := bin
targets := $(targetdir)/nametransgui.exe $(targetdir)/debug-nametransgui.exe
source := gsrc/launcher.cs
icon := resources/icon.ico

all: $(targets)

$(targetdir)/nametransgui.exe: $(source)
	gmcs \
		-target:winexe \
		-out:$@ \
		-win32icon:$(icon) \
		-r:$(targetdir)/IronPython \
		-r:$(targetdir)/Microsoft.Scripting \
		$<

$(targetdir)/debug-nametransgui.exe: $(source)
	gmcs \
		-target:exe \
		-out:$@ \
		-win32icon:$(icon) \
		-r:$(targetdir)/IronPython \
		-r:$(targetdir)/Microsoft.Scripting \
		$<

web:
	rsync -avP --delete -e ssh web/ numerodix,nametrans@web.sourceforge.net:htdocs/


clean:
	rm -f $(targets)

.PHONY: all clean web
