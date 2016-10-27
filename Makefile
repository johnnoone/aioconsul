install:
	python -m pip install -q -e .

test: install
	python -m pip install -r requirements-tests.txt
	pytest --cov aioconsul --cov-report term-missing -v

docs:
	python -m pip install -r docs/requirements.txt
	(cd docs ; rm -rf _build/* ; sphinx-build -a -b html -d _build/doctrees . _build/html)

bin/consul:
	mkdir -p bin
	curl https://releases.hashicorp.com/consul/0.7.0/consul_0.7.0_darwin_amd64.zip \
		--output bin/consul.zip
	(cd bin ; unzip consul.zip ; chmod 0755 consul ; rm -f consul.zip)

container:
	docker build -t aioconsul .

serve: container

	docker run -it --rm -v $(PWD):/app aioconsul /bin/bash

.PHONY: test install docs
