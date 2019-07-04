include Makefile.mk

NAME=cfn-storagegateway-provider

help:
	@echo 'make                 - builds a zip file to target/.'
	@echo 'make clean           - the workspace.'

do-build: target/$(NAME)-$(VERSION).zip

target/$(NAME)-$(VERSION).zip: src/*.py requirements.txt
	mkdir -p target/content
	docker build --build-arg ZIPFILE=$(NAME)-$(VERSION).zip -t $(NAME)-lambda:$(VERSION) -f Dockerfile.lambda . && \
		ID=$$(docker create $(NAME)-lambda:$(VERSION) /bin/true) && \
		docker export $$ID | (cd target && tar -xvf - $(NAME)-$(VERSION).zip) && \
		docker rm -f $$ID && \
		chmod ugo+r target/$(NAME)-$(VERSION).zip

venv: requirements.txt
	virtualenv -p python3 venv  && \
	. ./venv/bin/activate && \
	pip3 --quiet install --upgrade pip && \
	pip3 --quiet install -r requirements.txt
	
clean:
	rm -rf venv target src/*.pyc tests/*.pyc

test: venv
	. ./venv/bin/activate && \
	pip --quiet install -r test-requirements.txt && \
	cd src && \
	PYTHONPATH="$(PWD)"/src pytest ../tests/test*.py

autopep:
	autopep8 --experimental --in-place --max-line-length 132 src/*.py tests/*.py
