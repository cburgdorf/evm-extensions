import random
from target.release import evm_extensions
import eth

def bench_push_pop():
    stack = evm_extensions.Stack()
    for i in range(1000):
        stack.push_int(random.randint(1, 10000))

    for i in range(1000):
        stack.pop1_int()


def bench_pyevm_push_pop():
    stack = eth.vm.stack.Stack()
    for i in range(1000):
        stack.push_int(random.randint(1, 10000))

    for i in range(1000):
        stack.pop1_int()
