targetdir := bin
targets := $(targetdir)/nametransgui.exe $(targetdir)/debug-nametransgui.exe
source := gsrc/launcher.cs

all: $(targets)

$(targetdir)/nametransgui.exe: $(source)
	gmcs -target:winexe \
		$< \
		-r:$(targetdir)/IronPython \
		-r:$(targetdir)/Microsoft.Scripting \
		-r:$(targetdir)/Microsoft.Dynamic \
		-out:$@

$(targetdir)/debug-nametransgui.exe: $(source)
	gmcs -target:exe \
		$< \
		-r:$(targetdir)/IronPython \
		-r:$(targetdir)/Microsoft.Scripting \
		-r:$(targetdir)/Microsoft.Dynamic \
		-out:$@

web:
#	rsync -avP --delete -e ssh web/ numerodix,nametrans@web.sourceforge.net:htdocs/
	rsync -avP --delete -e ssh web/ matusia@matusiak.eu:www/tmp/


clean:
	rm -f $(targets)

.PHONY: all clean web
