LIBDIR = $(DESTDIR)/usr/share/pyshared/vizigrep
BINDIR = $(DESTDIR)/usr/bin
MANDIR = $(DESTDIR)/usr/share/man/man1
clean:
	rm -f *.py[co] */*.py[co]
install:
	mkdir -p $(LIBDIR)
	mkdir -p $(BINDIR)
	mkdir -p $(MANDIR)
	cp  *.py $(LIBDIR)/
	cp  *.glade $(LIBDIR)/
	cp README $(LIBDIR)/
	cp vizigrep $(LIBDIR)/
	cp vizigrep.sh $(BINDIR)/vizigrep
	cp vizigrep.man $(MANDIR)/vizigrep.1
uninstall:
	rm -rf $(LIBDIR)
	rm -f $(BINDIR)/vizigrep

