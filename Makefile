targetdir := bin
targets := $(targetdir)/gui.exe $(targetdir)/debug-gui.exe
source := gsrc/launcher.cs

all: $(targets)

$(targetdir)/gui.exe: $(source)
	gmcs -target:winexe \
		$< \
		-r:$(targetdir)/IronPython \
		-r:$(targetdir)/Microsoft.Scripting \
		-r:$(targetdir)/Microsoft.Dynamic \
		-out:$@

$(targetdir)/debug-gui.exe: $(source)
	gmcs -target:exe \
		$< \
		-r:$(targetdir)/IronPython \
		-r:$(targetdir)/Microsoft.Scripting \
		-r:$(targetdir)/Microsoft.Dynamic \
		-out:$@


clean:
	rm -f $(targets)

.PHONY: all clean
