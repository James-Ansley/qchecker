# Changelog

All notable changes to this project will be documented in this file.

## [1.0.2]

### Bugfixes

- Fixed expression tree parsing so `RepeatedAddition` and
  `RepeatedMultiplication` patterns consider order of operations.
  [#5](https://github.com/James-Ansley/qchecker/issues/5)

### Changes

- `RepeatedAddition` and `RepeatedMultiplication` patterns now consider
  non-adjacent repeats. For example, `x + y + x` is now considered a repeated
  addition.

## [1.0.1]

### Bugfixes

- Fixed issue in `RepeatedAddition` and `RepeatedMultiplication` where an
  operand whose prefix/suffix matched the preceding/proceeding operands would be
  counted as a repeated operand. e.g. `x + x1` and `ab + b` are no longer
  matched.
- `RepeatedMultiplication` description no longer incorrectly lists squares as
  instances
- Fixed "couuld" typo in `MergeableEqual` description
- Fixed error where `DuplicateIfElseStatement` and
  `SeveralDuplicateIfElseStatements` would match on elif
  blocks [#3](https://github.com/James-Ansley/qchecker/issues/3)
- Fixed incorrect handling of CST parser errors. Parser errors are now rethrown
  as syntax errors

### Changes

- Substructure `iter_matches` function now cannot be _guaranteed_ to lazily
  search code for matches. This affects some substructure `is_present` functions
  too.
- Deprecation warnings have been removed

[1.0.2]: https://github.com/James-Ansley/qchecker/compare/v1.0.1...v1.0.2

[1.0.1]: https://github.com/James-Ansley/qchecker/compare/v1.0.0...v1.0.1
