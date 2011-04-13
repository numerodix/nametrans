sources := $(wildcard *.cs)
targets := $(patsubst %.cs,%.exe,$(sources))

all: $(targets)

%.exe: %.cs
	gmcs $< -pkg:gtk-sharp-2.0


clean:
	rm -f $(targets)

.PHONY: all clean
