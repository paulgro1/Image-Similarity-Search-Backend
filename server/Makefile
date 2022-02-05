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

mk_env:
	conda env create -f environment.yml

activate_env:
	conda activate iss-backend

deactivate_env:
	conda deactivate

rmv_env: deactivate_env
	conda env remove -n iss-backend

update_env:
	conda env update -f environment.yml --prune

run: activate_env
	$(PYRUN) run.py 

init_server: activate_env
	$(PYRUN) run.py 1
