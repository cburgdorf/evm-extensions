from typing import Iterator
import pytest
import evm_extensions

import eth
from eth.vm import opcode_values


class ExtCodeStream(evm_extensions.CodeStream):

    # TODO: Port this over to the rust side
    def __iter__(self) -> Iterator[int]:
        # a very performance-sensitive method
        pc = self.program_counter
        while pc < self.length_cache:
            opcode = self.raw_code_bytes[pc]
            self.program_counter = pc + 1
            yield opcode
            # a read might have adjusted the pc during the last yield
            pc = self.program_counter

        yield opcode_values.STOP

@pytest.fixture(
    params=[ExtCodeStream, eth.vm.code_stream.CodeStream],
    ids=['Rust', 'Py-EVM']
)
def codestream(request):
    return request.param

@pytest.mark.parametrize(
    'input',
    (
        (True,)
    )
)
def test_codestream(input):
    stream = evm_extensions.CodeStream(b'code')
    assert len(stream) == 4
    slice = stream.read(2)
    assert slice == b'co'

def test_code_stream_accepts_bytes():
    code_stream = evm_extensions.CodeStream(b'\x02')
    assert len(code_stream) == 1
    assert code_stream[0] == 2

@pytest.mark.parametrize(
    "code_bytes", 
    (
        1010,
        '1010',
        True,
        # FIXME
        #bytearray(32)
    )
)
def test_code_stream_rejects_invalid_code_byte_values(code_bytes):
    # Fixme: Proper exceptions
    with pytest.raises(Exception):
        evm_extensions.CodeStream(code_bytes)


def test_next_returns_the_correct_next_opcode(codestream):
    iterable = codestream(b'\x01\x02\x30')
    code_stream = iter(iterable)
    assert next(code_stream) == opcode_values.ADD
    assert next(code_stream) == opcode_values.MUL
    assert next(code_stream) == opcode_values.ADDRESS

def test_peek_returns_next_opcode_without_changing_code_stream_location(codestream):
    code_stream = codestream(b'\x01\x02\x30')
    code_iter = iter(code_stream)
    assert code_stream.program_counter == 0
    assert code_stream.peek() == opcode_values.ADD
    assert code_stream.program_counter == 0
    assert next(code_iter) == opcode_values.ADD
    assert code_stream.program_counter == 1
    assert code_stream.peek() == opcode_values.MUL
    assert code_stream.program_counter == 1


def test_STOP_opcode_is_returned_when_bytecode_end_is_reached(codestream):
    iterable = codestream(b'\x01\x02')
    code_stream = iter(iterable)
    next(code_stream)
    next(code_stream)
    assert next(code_stream) == opcode_values.STOP


@pytest.mark.skip("Need to implement seek()")
def test_seek_reverts_to_original_stream_position_when_context_exits():
    code_stream = ExtCodeStream(b'\x01\x02\x30')
    code_iter = iter(code_stream)
    assert code_stream.program_counter == 0
    with code_stream.seek(1):
        assert code_stream.program_counter == 1
        assert next(code_iter) == opcode_values.MUL
    assert code_stream.program_counter == 0
    assert code_stream.peek() == opcode_values.ADD


def test_get_item_returns_correct_opcode(codestream):
    code_stream = codestream(b'\x01\x02\x30')
    assert code_stream[0] == opcode_values.ADD
    assert code_stream[1] == opcode_values.MUL
    assert code_stream[2] == opcode_values.ADDRESS


def test_is_valid_opcode_invalidates_bytes_after_PUSHXX_opcodes(codestream):
    code_stream = codestream(b'\x02\x60\x02\x04')
    assert code_stream.is_valid_opcode(0) is True
    assert code_stream.is_valid_opcode(1) is True
    assert code_stream.is_valid_opcode(2) is False
    assert code_stream.is_valid_opcode(3) is True
    assert code_stream.is_valid_opcode(4) is False


def test_is_valid_opcode_valid_with_PUSH32_just_past_boundary(codestream):
    # valid: 0 :: 33
    # invalid: 1 - 32 (PUSH32) :: 34+ (too long)
    code_stream = codestream(b'\x7f' + (b'\0' * 32) + b'\x60')
    assert code_stream.is_valid_opcode(0) is True
    for pos in range(1, 33):
        assert code_stream.is_valid_opcode(pos) is False
    assert code_stream.is_valid_opcode(33) is True
    assert code_stream.is_valid_opcode(34) is False

def test_harder_is_valid_opcode(codestream):
    code_stream = codestream(b'\x02\x03\x72' + (b'\x04' * 32) + b'\x05')
    # valid: 0 - 2 :: 22 - 35
    # invalid: 3-21 (PUSH19) :: 36+ (too long)
    assert code_stream.is_valid_opcode(0) is True
    assert code_stream.is_valid_opcode(1) is True
    assert code_stream.is_valid_opcode(2) is True
    assert code_stream.is_valid_opcode(3) is False
    assert code_stream.is_valid_opcode(21) is False
    assert code_stream.is_valid_opcode(22) is True
    assert code_stream.is_valid_opcode(35) is True
    assert code_stream.is_valid_opcode(36) is False



def test_even_harder_is_valid_opcode(codestream):
    test = b'\x02\x03\x7d' + (b'\x04' * 32) + b'\x05\x7e' + (b'\x04' * 35) + b'\x01\x61\x01\x01\x01'
    code_stream = codestream(test)
    # valid: 0 - 2 :: 33 - 36 :: 68 - 73 :: 76
    # invalid: 3 - 32 (PUSH30) :: 37 - 67 (PUSH31) :: 74, 75 (PUSH2) :: 77+ (too long)
    assert code_stream.is_valid_opcode(0) is True
    assert code_stream.is_valid_opcode(1) is True
    assert code_stream.is_valid_opcode(2) is True
    assert code_stream.is_valid_opcode(3) is False
    assert code_stream.is_valid_opcode(32) is False
    assert code_stream.is_valid_opcode(33) is True
    assert code_stream.is_valid_opcode(36) is True
    assert code_stream.is_valid_opcode(37) is False
    assert code_stream.is_valid_opcode(67) is False
    assert code_stream.is_valid_opcode(68) is True
    assert code_stream.is_valid_opcode(71) is True
    assert code_stream.is_valid_opcode(72) is True
    assert code_stream.is_valid_opcode(73) is True
    assert code_stream.is_valid_opcode(74) is False
    assert code_stream.is_valid_opcode(75) is False
    assert code_stream.is_valid_opcode(76) is True
    assert code_stream.is_valid_opcode(77) is False

def test_even_harder_is_valid_opcode_first_check_deep(codestream):
    test = b'\x02\x03\x7d' + (b'\x04' * 32) + b'\x05\x7e' + (b'\x04' * 35) + b'\x01\x61\x01\x01\x01'
    code_stream = codestream(test)
    # valid: 0 - 2 :: 33 - 36 :: 68 - 73 :: 76
    # invalid: 3 - 32 (PUSH30) :: 37 - 67 (PUSH31) :: 74, 75 (PUSH2) :: 77+ (too long)
    assert code_stream.is_valid_opcode(75) is False


def test_right_number_of_bytes_invalidated_after_pushxx(codestream):
    code_stream = codestream(b'\x02\x03\x60\x02\x02')
    assert code_stream.is_valid_opcode(0) is True
    assert code_stream.is_valid_opcode(1) is True
    assert code_stream.is_valid_opcode(2) is True
    assert code_stream.is_valid_opcode(3) is False
    assert code_stream.is_valid_opcode(4) is True
    assert code_stream.is_valid_opcode(5) is False


@pytest.mark.parametrize(
    "test_fn",
    (
        test_next_returns_the_correct_next_opcode,
        test_peek_returns_next_opcode_without_changing_code_stream_location,
        test_STOP_opcode_is_returned_when_bytecode_end_is_reached,
        test_get_item_returns_correct_opcode,
        test_is_valid_opcode_invalidates_bytes_after_PUSHXX_opcodes,
        test_is_valid_opcode_valid_with_PUSH32_just_past_boundary,
        test_harder_is_valid_opcode,
        test_even_harder_is_valid_opcode,
        test_even_harder_is_valid_opcode_first_check_deep,
        test_right_number_of_bytes_invalidated_after_pushxx,
    )
)
def test_bench(benchmark, codestream, test_fn):
    benchmark(test_fn, codestream)
