# Conventions

## Unit tests

This project uses `pytest` . Follow these rules to keep tests consistent, readable, and maintainable.

### Structure

- Default: **1 source module → 1 test module**
- Mirror package structure:
  - `src/foo/bar.py`
  - `tests/unit/foo/test_bar.py`
- Multiple test modules allowed only for clearly different concerns  (`test_<module>_<concern>.py`)

### Functions vs classes

- **Prefer plain test functions**
- Use test classes only for logical grouping or shared fixtures
- Test classes:
  - Start with `Test`
  - No `__init__`, no inheritance
  - No `setUp` / `tearDown`

### Naming

- Test files: `test_<module>.py`
- Test functions: `test_<unit>_<condition>_<expected>`
  - Describe observable behavior, not implementation details
  - Examples:
    - `test_parse_valid_input_returns_ast()`
    - `test_parse_empty_input_raises_error()`
- Test classes: `Test<Unit>`

### Fixtures

- Prefer fixtures over setup code
- Fixture names are nouns
- Default scope: `function`
- Shared fixtures go in `conftest.py`

### Assertions

- Use plain `assert`
  - `assert result == expected`
- One behavior per test
- Assert outcomes, not implementation details

### Parametrization

- Use `@pytest.mark.parametrize` for the same behavior with multiple inputs
- If logic branches, split into separate tests

### General

- Tests must be deterministic and order-independent
- No shared mutable state
- Tests should read like executable documentation
