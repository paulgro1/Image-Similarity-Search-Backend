# See https://stackoverflow.com/a/12099167
ifeq ($(OS),Windows_NT)
    OPEN := start
	PYRUN := python
else
    UNAME := $(shell uname -s)
    ifeq ($(UNAME),Linux)
        OPEN := xdg-open
		PYRUN := python
    endif
	ifeq ($(UNAME),Darwin)
        OPEN := open
		PYRUN := python3
    endif
endif

run:
	cd server && make run
	
write_docs:
	$(PYRUN) doc.py
