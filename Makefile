BINDIR = $(DESTDIR)/usr/bin
MANDIR = $(DESTDIR)/usr/share/man/man1
SHAREDIR = $(DESTDIR)/usr/share/vizigrep
APPSDIR = $(DESTDIR)/usr/share/applications
DOCDIR = $(DESTDIR)/usr/share/doc/vizigrep
clean:
	rm -f *.py[co] */*.py[co]
install:
	install -d $(BINDIR)
	install -d $(MANDIR)
	install -d $(SHAREDIR)
	install -d $(APPSDIR)
	install -d $(DOCDIR)
	cp  *.py $(SHAREDIR)/
	cp -r guiapp $(SHAREDIR)/
	cp -r ui $(SHAREDIR)/
	cp vizigrep $(SHAREDIR)/
	cp vizigrep.sh $(BINDIR)/vizigrep
	cp vizigrep.man $(MANDIR)/vizigrep.1
	cp vizigrep.svg $(SHAREDIR)/
	cp vizigrep.desktop $(APPSDIR)/
	cp changelog $(DOCDIR)/
	cp copyright.txt $(DOCDIR)/
	cp README $(DOCDIR)/
uninstall:
	rm -rf $(SHAREDIR)
	rm -rf $(DOCDIR)
	rm -f $(BINDIR)/vizigrep
	rm -f $(MANDIR)/vizigrep.1
	rm -f $(APPSDIR)/vizigrep.desktop
.PHONY: install
