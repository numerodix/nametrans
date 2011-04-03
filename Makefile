targets := $(patsubst %.cs,%.exe,$(wildcard *.cs))

all: $(targets)

%.exe: %.cs
	gmcs -target:winexe \
		$< \
		-r:IronPython \
		-r:Microsoft.Scripting \
		-r:Microsoft.Dynamic \
		-out:$@


clean:
	rm -f $(targets)

.PHONY: all clean
