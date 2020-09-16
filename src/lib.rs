use pyo3::prelude::*;

mod code_stream;
pub use code_stream::CodeStream;

#[pymodule]
fn evm_extensions(_py: Python, module: &PyModule) -> PyResult<()> {
    module.add_class::<CodeStream>()?;

    Ok(())
}
