BINDIR = $(DESTDIR)/usr/bin
MANDIR = $(DESTDIR)/usr/share/man/man1
SHAREDIR = $(DESTDIR)/usr/share/vizigrep
APPSDIR = $(DESTDIR)/usr/share/applications
clean:
	rm -f *.py[co] */*.py[co]
install:
	mkdir -p $(BINDIR)
	mkdir -p $(MANDIR)
	mkdir -p $(SHAREDIR)
	mkdir -p $(APPSDIR)
	cp  *.py $(SHAREDIR)/
	cp  *.glade $(SHAREDIR)/
	cp vizigrep $(SHAREDIR)/
	cp vizigrep.sh $(BINDIR)/vizigrep
	cp vizigrep.man $(MANDIR)/vizigrep.1
	cp vizigrep.svg $(SHAREDIR)/
	cp vizigrep.desktop $(APPSDIR)/
uninstall:
	rm -rf $(SHAREDIR)
	rm -f $(BINDIR)/vizigrep
.PHONY: install
