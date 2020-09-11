use pyo3::prelude::*;


#[pyclass]
pub struct Stack {
  values: Vec<u32>,
}

#[pymethods]
impl Stack {
  #[new]
  pub fn new() -> Stack {
      Stack { values: vec![] }
  }

  pub fn push_int(&mut self, value: u32) {
      self.values.push(value);
  }

  pub fn pop1_int(&mut self) -> Option<u32> {
    self.values.pop()
  }
}
