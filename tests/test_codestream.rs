extern crate evm_extensions;
use evm_extensions::CodeStream;

// //use rstest::rstest;
// //use stack::Stack;

// // This is encoded as a string. Wouldn't an address be formatted as a pure binary instead?
// // https://github.com/paritytech/parity-common/blob/0431acb4f34751af44c664b0b0a6f36b0cd147b3/rlp/tests/tests.rs#L222-L231
// // #[rstest(input, expected,
// //     case(H160::from(hex!("ef2d6d194084c2de36e0dabfce45d046b37d1106")),
// //     vec![
// //         0x94, 0xef, 0x2d, 0x6d, 0x19, 0x40, 0x84, 0xc2, 0xde, 0x36, 0xe0, 0xda, 0xbf, 0xce, 0x45, 0xd0, 0x46, 0xb3,
// //         0x7d, 0x11, 0x06,
// //     ]),
// // )]
#[test]
fn test_is_valid_opcode_invalidates_bytes_after_PUSHXX_opcodes() {
    let mut stream = CodeStream::new(vec![2, 96, 2, 4]);
    assert_eq!(stream.is_valid_opcode(0), true);
    assert_eq!(stream.is_valid_opcode(1), true);
    assert_eq!(stream.is_valid_opcode(2), false);
    assert_eq!(stream.is_valid_opcode(3), true);
    assert_eq!(stream.is_valid_opcode(4), false);
}
