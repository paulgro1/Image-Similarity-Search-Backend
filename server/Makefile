
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
	@echo starting server
	python run.py 

init_server: activate_env
	python run.py 1
