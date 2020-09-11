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
	python -m pytest -vv -s python-tests/

.PHONY: benchmark
.ONESHELL:
benchmark: venv
	. venv/bin/activate
	rm -rf target/release/evm_extensions.so
	cargo build --release
	cp target/release/libevm_extensions.so target/release/evm_extensions.so
	echo "EVM EXTENSIONS: PUSH_POP"
	python -m timeit -n 300 -u msec  -s'import benchmark' 'benchmark.bench_push_pop()'
	echo "PY-EVM (NOT THIS LIBRARY): PUSH_POP"
	python -m timeit -n 300 -u msec  -s'import benchmark' 'benchmark.bench_pyevm_push_pop()'


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
