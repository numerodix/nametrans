targets := debug-gui.exe gui.exe
source := gsrc/launcher.cs

all: $(targets)

debug-gui.exe: $(source)
	gmcs -target:exe \
		$< \
		-r:IronPython \
		-r:Microsoft.Scripting \
		-r:Microsoft.Dynamic \
		-out:$@

gui.exe: $(source)
	gmcs -target:winexe \
		$< \
		-r:IronPython \
		-r:Microsoft.Scripting \
		-r:Microsoft.Dynamic \
		-out:$@


clean:
	rm -f $(targets)

.PHONY: all clean
