targets := app.exe wapp.exe

all: $(targets)

app.exe: app.cs
	gmcs -target:exe \
		$< \
		-r:IronPython \
		-r:Microsoft.Scripting \
		-r:Microsoft.Dynamic \
		-out:$@

wapp.exe: app.cs
	gmcs -target:winexe \
		$< \
		-r:IronPython \
		-r:Microsoft.Scripting \
		-r:Microsoft.Dynamic \
		-out:$@


clean:
	rm -f $(targets)

.PHONY: all clean
