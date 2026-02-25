## Generic prompting instructions

Use these instructions when discussing design, architecture or general project structure

### Principles

This is project aims to be of high quality and maintainability. Follow established software engineering best practices and python best practices at all times. In particular:

* The ZEN of Python (import this), especially:
  * Simple is better than complex
  * Readability counts
  * Special cases aren't special enough to break the rules
  * Although practicality beats purity
  * Errors should never pass silently
  * Unless explicitly silenced
  * In the face of ambiguity, refuse the temptation to guess
  * There should be one-- and preferably only one --obvious way to do it
  * Special cases aren't special enough to break the rules
  * If the implementation is hard to explain, it's a bad idea
* SOLID principles
  * Single Responsibility Principle
  * Dependency Inversion Principle
* Clean code
* Application of design patterns where applicable
* Design patterns where applicable
* DRY, KISS and YAGNI principle

###  Approach

* Approach every question using an engineering mindset
* Start with a high level understanding of the problem before going into details
* Talk about a problem in terms of functional and non-functional requirements
* Discuss suitable application architecture patterns and software design patterns
* Go step by step, don't jump to conclusions, don't come up with a complete solution when not explicitly asked
* Always ask before implementing
* Be as concise as possible with your answers, typically no more than a few sentences.
* When giving code examples, make them as small as possible to explain the concept or relevant change.
* Always start with the most simple implementation first
* But mention alternatives if the current implementation or architecture does not follow best practices
* Always number options in your answer

## Coding instructions

Use these instructions when writing code for the project

* Code should be self explanatory
* Use no magic numbers
* Use descriptive and unambiguous names
* Don't add comments to explain what the code does
* Don't add module/class/method/function docstrings to explain what the code does
* Apply KISS and YAGNI principle
  * Make things as simple as possible, only support use cases that are actually needed
* Local reasoning is important
* Always use type hints

### Unit testing instructions

- Use `pytest` for unit tests
- Use `uv run pytest` to run tests

#### Structure

- Default: **1 source module requires 1 test module**
- Mirror package structure:
  - `src/foo/bar.py`
  - `tests/unit/foo/test_bar.py`
- In very rare cases, allow multiple test modules for clearly different concerns  (`test_<module>_<concern>.py`). But better refactor the source module then.

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
- Test classes: `Test<Class>`

### Fixtures

- Prefer fixtures over setup code
- Fixture names are nouns
- Default scope: `function`
- Shared fixtures go in `conftest.py`

### Assertions

- Use plain `assert`
  - `assert result == expected`
- Assert outcomes, not implementation details

### Parametrization

- Use `@pytest.mark.parametrize` for the same behavior with multiple inputs
- If logic branches, split into separate tests

### General

- Cover all paths
- Test behavior, not implementation
- Only test public methods and functions (no private methods/functions starting with `_`)
- Be pragmatic to avoid an explosion of test cases
- Tests must be deterministic and order-independent
- No shared mutable state
- Tests should read like executable documentation
- Make it explicit when using mocks, stubs or fakes by naming them accordingly (e.g. `StubSessionState` instead of `SessionState`)