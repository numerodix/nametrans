sources := $(wildcard *.c)
targets := $(patsubst %.c,%,$(sources))

all: $(targets)

%: %.c
	cc -o $@ $< `pkg-config --cflags --libs gtk+-2.0 gthread-2.0`


clean:
	rm -f $(targets)

.PHONY: all clean
