LIBDIR = $(DESTDIR)/usr/share/pyshared/vizigrep
BINDIR = $(DESTDIR)/usr/bin
clean:
	rm -f *.py[co] */*.py[co]
install:
	mkdir -p $(LIBDIR)
	mkdir -p $(BINDIR)
	cp  *.py $(LIBDIR)/
	cp  *.glade $(LIBDIR)/
	cp license.txt $(LIBDIR)/
	cp README $(LIBDIR)/
	cp vizigrep $(LIBDIR)/
	cp vizigrep.sh $(BINDIR)/vizigrep
uninstall:
	rm -rf $(LIBDIR)
	rm -f $(BINDIR)/vizigrep

