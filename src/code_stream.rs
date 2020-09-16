use pyo3::class::PyMappingProtocol;
use pyo3::prelude::*;
use std::cell::RefCell;
use std::cmp;
use std::collections::HashSet;

const PUSH1: usize = 0x60;
const PUSH32: usize = 0x7f;
const STOP: usize = 0x00;

#[pyclass(subclass)]
pub struct CodeStream {
    #[pyo3(get, set)]
    program_counter: usize,
    #[pyo3(get)]
    raw_code_bytes: Vec<u8>,
    #[pyo3(get)]
    length_cache: usize,
    invalid_positions: RefCell<HashSet<usize>>,
    valid_positions: RefCell<HashSet<usize>>,
}

#[pymethods]
impl CodeStream {
    #[new]
    pub fn new(code_bytes: Vec<u8>) -> CodeStream {
        CodeStream {
            program_counter: 0,
            length_cache: code_bytes.len(),
            raw_code_bytes: code_bytes,
            invalid_positions: RefCell::new(HashSet::new()),
            valid_positions: RefCell::new(HashSet::new()),
        }
    }

    pub fn read(&mut self, size: usize) -> &[u8] {
        let old_program_counter = self.program_counter;
        let target_program_counter = old_program_counter + size;
        self.program_counter = target_program_counter;
        &self.raw_code_bytes[old_program_counter..target_program_counter]
    }

    pub fn peek(&self) -> usize {
        let pc = self.program_counter;
        if pc < self.length_cache {
            self.raw_code_bytes[pc].into()
        } else {
            STOP
        }
    }

    pub fn is_valid_opcode(&self, position: usize) -> bool {
        if position >= self.length_cache || self.invalid_positions.borrow().contains(&position) {
            false
        } else if self.valid_positions.borrow().contains(&position) {
            true
        } else {
            // An opcode is not valid, if it is the "data" following a PUSH_
            // So we look at the previous 32 bytes (PUSH32 being the largest) to see if there
            // is a PUSH_ before the opcode in this position.
            for disqualifier in self.potentially_disqualifying_opcode_positions(position) {
                // Now that we found a PUSH_ before this position, we check if *that* PUSH is valid
                if self.is_valid_opcode(disqualifier) {
                    // If the PUSH_ valid, then the current position is invalid
                    self.invalid_positions.borrow_mut().insert(position);
                    return false;
                }
                //Otherwise, keep looking for other potentially disqualifying PUSH_ codes
            }
            // We didn't find any valid PUSH_ opcodes in the 32 bytes before position; it's valid
            self.valid_positions.borrow_mut().insert(position);
            true
        }
    }
}

impl CodeStream {
    // These methods do not need to be exposed to Python

    fn potentially_disqualifying_opcode_positions(
        &self,
        position: usize,
    ) -> impl Iterator<Item = usize> + '_ {
        // Look at the last 32 positions (from 1 byte back to 32 bytes back).
        // Don't attempt to look at negative positions.
        let deepest_lookback = cmp::min(32, position);

        (1..deepest_lookback + 1)
            .rev()
            .filter_map(move |bytes_back| {
                let earlier_position = position - bytes_back;
                let opcode = self.raw_code_bytes[earlier_position].into();
                if PUSH1 + (bytes_back - 1) <= opcode && opcode <= PUSH32 {
                    Some(earlier_position)
                } else {
                    None
                }
            })
    }
}

#[pyproto]
impl PyMappingProtocol for CodeStream {
    fn __len__(&self) -> PyResult<usize> {
        Ok(self.length_cache)
    }

    fn __getitem__(&self, key: usize) -> PyResult<usize> {
        Ok(self.raw_code_bytes[key].into())
    }

    // fn __iter__(&self, py: Python) -> () {
    //   let iter = IntoPy::into_py(
    //     Py::new(py, PyMappingIter::new(self.map.iter().map(|(k, _)| k.to_owned()).collect()))?,
    //     py,
    //   );

    //   Ok(iter)
    // }
}
