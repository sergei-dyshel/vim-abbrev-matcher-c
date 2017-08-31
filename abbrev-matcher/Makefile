SHELL = /bin/bash
NAME = abbrev_matcher_c

SO := abbrev_matcher_c.so
SRC := abbrev_matcher.c
BUILD := ./build

all: $(SO)

clean:
	-rm -rf $(SO) $(BUILD)

$(SO): $(SRC)
	python3 setup.py build
	find $(BUILD) -name '*.so' -exec cp {} $@ \;
