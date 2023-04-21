link-conda-env:
	ln -sf environments-and-requirements/environment-mac.yml environment.yml

link-conda-env-intel:
	ln -sf environments-and-requirements/environment-mac-intel.yml environment.yml

link-conda-ci:
	ln -sfv continuous_integration/environment-3.10-dev.yaml environment.yml

# conda-update: conda-lock-env
# 	conda env update
# 	conda list --explicit > installed_conda.txt
# 	pip freeze > installed_pip.txt

conda-update-lock:
	conda env update
	conda env export > environment.yml.lock
	conda list -e > conda.requirements.txt
	pip list --format=freeze > requirements.txt
	conda list --explicit > installed_conda.txt
	pip freeze > installed_pip.txt

conda-update-prune:
	conda env update --prune
	conda list --explicit > installed_conda.txt
	pip freeze > installed_pip.txt

conda-activate:
	pyenv activate anaconda3-2022.05
	conda activate pytorch-lab3

conda-delete:
	conda env remove -n pytorch-lab3

conda-lock-env:
	conda env export > environment.yml.lock
	conda list -e > conda.requirements.txt
	pip list --format=freeze > requirements.txt

conda-env-export:
	conda env export
	conda list --explicit

conda-history:
	conda env export --from-history

env-works:
	python ./contrib/is-mps-available.py
	python ./contrib/does-matplotlib-work.py

env-test: env-works

setup-dataset-scratch-env:
	bash contrib/setup-dataset-scratch-env.sh

download-dataset: setup-dataset-scratch-env
	curl -L 'https://www.dropbox.com/s/8w1jkcvdzmh7khh/twitter_facebook_tiktok.zip?dl=1' > ./scratch/datasets/twitter_facebook_tiktok.zip
	unzip -l ./scratch/datasets/twitter_facebook_tiktok.zip

unzip-dataset:
	unzip ./scratch/datasets/twitter_facebook_tiktok.zip -d './scratch/datasets'
	rm -fv ./scratch/datasets/twitter_facebook_tiktok.zip

zip-dataset:
	bash contrib/zip-dataset.sh
	ls -ltah ./scratch/datasets/twitter_facebook_tiktok.zip

install-postgres:
	brew install postgresql@14

label-studio:
	label-studio

start-docker-services:
	docker-compose -f deploy/docker-compose.yml -f deploy/docker-compose.otlp.yml --project-directory . up

ps-docker-services:
	docker-compose -f deploy/docker-compose.yml -f deploy/docker-compose.otlp.yml --project-directory . ps

start-docker-services-d:
	docker-compose -f deploy/docker-compose.yml -f deploy/docker-compose.otlp.yml --project-directory . up -d

start-docker-ci-d:
	lima nerdctl compose -f deploy/docker-compose.yml -f deploy/docker-compose.otlp.yml --project-directory . up -d

rm-docker-services:
	docker-compose -f deploy/docker-compose.yml -f deploy/docker-compose.otlp.yml --project-directory . rm -v

download-model:
	bash contrib/download-model.sh

web:
	python -m dancedetector

worker:
	python -m dancedetector.worker

cli:
	python -m dancedetector.cli

# test-classify:
# # curl -X POST 'http://localhost:8000/classify' --form 'file=@"/Users/malcolm/dev/bossjones/dancedetector/dancedetector/tests/fixtures/test1.jpg"' -d '{"json": {"exchange_name": "7cf7aaa6aea14e0d9ffbde33e689b1e8","routing_key": "90e78f506fd84cf39bb05014c66cae44","queue_name": "b504ebf81a044ae39f402e7f47f30ebc","message": "d66a3c34d2da4153a7e5451a48bb6960"}}'
# # > {"inference_id":"30684d7f-b86a-4014-9029-85554dccf3e7"}

doku:
	docker pull amerkurev/doku:latest || true
	docker run --rm --name doku -d -v /var/run/docker.sock:/var/run/docker.sock:ro -v /:/hostroot:ro -p 9090:9090 amerkurev/doku

view-memray:
	python -m http.server 8848 --bind 0.0.0.0 --directory ${HOME}/dev/bossjones/dancedetector

basic-mem-profile:
	python -m memray run -f -o lel.bin -m dancedetector.cli --predict ~/Downloads/icloud_photos_downloader/hyenawhite/screenshots/screenshots --workers 100
# memray flamegraph --leaks --split-threads -f --temporary-allocations lel.bin
	memray flamegraph lel.bin
	memray summary lel.bin
