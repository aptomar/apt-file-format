

TARGETDIR = $(DESTDIR)/opt/aptomar
PROGDIR = $(TARGETDIR)/aptofile
SRCDIR = src



all:

install:
	mkdir -p $(TARGETDIR)
	mkdir -p $(PROGDIR)
	python setup.py install --root debian/tmp

.PHONY: test
test:
	@cd test && python testAptofile.py

check: test
