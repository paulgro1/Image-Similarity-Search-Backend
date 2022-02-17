# See https://stackoverflow.com/a/12099167
ifeq ($(OS),Windows_NT)
    OPEN := CMD /C start
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

ROOT_DIR=$(dir $(abspath $(lastword $(MAKEFILE_LIST))))

all:
	$(PYRUN) $(ROOT_DIR)run.py

mk_env:
	conda env create -f $(ROOT_DIR)environment.yml

rmv_env:
	conda env remove -n iss-backend

update_env:
	conda env update -f $(ROOT_DIR)environment.yml --prune

run:
	@echo $(ROOT_DIR)run.py
	$(PYRUN) $(ROOT_DIR)run.py

init_server:
	$(PYRUN) $(ROOT_DIR)run.py 1
