LIBDIR = $(DESTDIR)/usr/share/pyshared/vizigrep
BINDIR = $(DESTDIR)/usr/bin
MANDIR = $(DESTDIR)/usr/share/man/man1
SHAREDIR = $(DESTDIR)/usr/share/vizigrep
APPSDIR = $(DESTDIR)/usr/share/applications
clean:
	rm -f *.py[co] */*.py[co]
install:
	mkdir -p $(LIBDIR)
	mkdir -p $(BINDIR)
	mkdir -p $(MANDIR)
	mkdir -p $(SHAREDIR)
	mkdir -p $(APPSDIR)
	cp  *.py $(LIBDIR)/
	cp  *.glade $(LIBDIR)/
	cp README $(LIBDIR)/
	cp vizigrep $(LIBDIR)/
	cp vizigrep.sh $(BINDIR)/vizigrep
	cp vizigrep.man $(MANDIR)/vizigrep.1
	cp vizigrep.svg $(SHAREDIR)/
	cp vizigrep.desktop $(APPSDIR)/
uninstall:
	rm -rf $(LIBDIR)
	rm -ff $(SHAREDIR)
	rm -f $(BINDIR)/vizigrep


