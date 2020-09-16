.PHONY: all
all:
	@echo "Run my targets individually!"

.PHONY: venv
.ONESHELL:
venv:
	test -d venv || python3 -m venv venv
	. venv/bin/activate
	pip install -r requirements-dev.txt


.PHONY: develop
.ONESHELL:
develop: venv
	. venv/bin/activate
	maturin develop

.PHONY: lint
.ONESHELL:
lint: 
	cargo fmt
	cargo clippy --all-targets --all-features

.PHONY: test
.ONESHELL:
test: develop
	. venv/bin/activate
	python -m pytest -vv -k 'not test_bench' -s python-tests/

.PHONY: benchmark
.ONESHELL:
benchmark: venv
	. venv/bin/activate
	maturin develop --release
	python -m pytest --benchmark-group-by=param:test_fn -vv -s python-tests/

.PHONY: build
.ONESHELL:
build: venv
	. venv/bin/activate
	maturin build

.PHONY: dist
.ONESHELL:
dist: venv
	. venv/bin/activate
	pip install twine
	rm -rf target/wheels/*
	docker run --rm -v $(shell pwd):/io konstin2/maturin build --release --strip
	twine upload target/wheels/*
