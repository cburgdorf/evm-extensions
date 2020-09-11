use pyo3::prelude::*;

mod stack;
pub use stack::Stack;


#[pymodule]
fn evm_extensions(_py: Python, module: &PyModule) -> PyResult<()> {
    module.add_class::<Stack>()?;

    Ok(())
}
