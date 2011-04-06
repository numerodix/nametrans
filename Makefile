targets := debug-gui.exe gui.exe

all: $(targets)

debug-gui.exe: gui.cs
	gmcs -target:exe \
		$< \
		-r:IronPython \
		-r:Microsoft.Scripting \
		-r:Microsoft.Dynamic \
		-out:$@

gui.exe: gui.cs
	gmcs -target:winexe \
		$< \
		-r:IronPython \
		-r:Microsoft.Scripting \
		-r:Microsoft.Dynamic \
		-out:$@


clean:
	rm -f $(targets)

.PHONY: all clean
