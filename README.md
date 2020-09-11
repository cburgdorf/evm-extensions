# EVM Extensions

A collection of performance critical EVM helpers that originate in [Py-EVM](https://github.com/ethereum/py-evm) but were rewritten in Rust to speed up Py-EVMs internals.


## Running the tests

The library exposes a pure Python API and all tests are implemented in [`python_tests.py`](https://github.com/cburgdorf/evm-extensions/blob/master/python_tests.py)

Run the tests:

```
make test
```


## Benchmarks

We provide some benchmarks.

### Running the benchmarks

```
make benchmark
```
