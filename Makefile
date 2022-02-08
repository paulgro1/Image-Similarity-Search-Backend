include ./server/Makefile

write_docs:
	$(PYRUN) doc.py

show_docs:
	$(OPEN) $(subst server/,,$(ROOT_DIR))docs/index.html