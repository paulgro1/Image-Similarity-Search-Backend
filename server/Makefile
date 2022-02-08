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
	@conda init bash && conda activate iss-backend && $(PYRUN) $(ROOT_DIR)run.py

mk_env:
	@conda init bash && conda env create -f $(ROOT_DIR)environment.yml

activate_env:
	qconda init bash && conda activate iss-backend

deactivate_env:
	@conda init bash && conda deactivate

rmv_env: deactivate_env
	@conda init bash && conda env remove -n iss-backend

update_env:
	@conda init bash && conda env update -f $(ROOT_DIR)environment.yml --prune

run:
	@echo $(ROOT_DIR)run.py
	@conda init bash && conda activate iss-backend && $(PYRUN) $(ROOT_DIR)run.py

init_server: activate_env
	@conda init bash && conda activate iss-backend && $(PYRUN) $(ROOT_DIR)run.py 1
