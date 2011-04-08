targetdir := bin
targets := $(targetdir)/nametransgui.exe $(targetdir)/debug-nametransgui.exe
source := gsrc/launcher.cs
icon := resources/icon.ico

all: $(targets)

$(targetdir)/nametransgui.exe: $(source)
	gmcs -target:winexe \
		$< \
		-r:$(targetdir)/IronPython \
		-r:$(targetdir)/Microsoft.Scripting \
		-r:$(targetdir)/Microsoft.Dynamic \
		/win32icon:$(icon) \
		-out:$@

$(targetdir)/debug-nametransgui.exe: $(source)
	gmcs -target:exe \
		$< \
		-r:$(targetdir)/IronPython \
		-r:$(targetdir)/Microsoft.Scripting \
		-r:$(targetdir)/Microsoft.Dynamic \
		/win32icon:$(icon) \
		-out:$@

web:
	rsync -avP --delete -e ssh web/ numerodix,nametrans@web.sourceforge.net:htdocs/


clean:
	rm -f $(targets)

.PHONY: all clean web
