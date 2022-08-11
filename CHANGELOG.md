# Changelog

All notable changes to this project will be documented in this file.

## [1.1.2]

### BugFixes

- `RedundantNot` now does not match chained comparisons
- `WhileAsFor` now ignores cases where test names have possibly mutating
  attribute calls in the while body.
  [#7](https://github.com/James-Ansley/qchecker/issues/7)

## [1.1.1]

### BugFixes

- `IndentationErrors` thrown during AST parsing are now rethrown
  as `SyntaxErrors`
- `cst_substructure.iter_matches` now uses metadata wrapper for parsing string
  arguments to prevent errors when constructing matches in CSTs

### Changes

- `NoOp` is now a subset of `EmptyIfBody` and `EmptyElseBody` and will not match
  if the noop is part of these patterns
- Subset substructure functionality is now deprecated and will be removed in the
  next major version. Substructures can be filtered manually if needed.

## [1.1.0]

### BugFixes

- `RedundantArithmetic` now catches `x - 0` and `x ** 1`

### Changes

- **_New Substructure_** `NoOp` to catch expressions where values are assigned
  to themselves or augmented assignments do not change the value (e.g. `x += 0`)
- **_New Substructure_** `Tautology` to catch simple boolean expressions that
  always evaluate to True (excluding the `True` constant). e.g. `x == x`
  or `x == 0 or x != 0`
- **_New Substructure_** `Contradiction` to catch simple boolean expressions
  that always evaluate to False (excluding the `False` constant).
  e.g. `x is not x` or `x == 0 and x == 1`
- **_New Substructure_** `WhileAsFor` to catch while loops that could be easily
  rewritten as for loops
- **_New Substructure_** `ForWithRedundantIndexing` to catch `for i in range`
  loops that can be replaced with for `for value in iterable` loops.
- Substructure `iter_matches` etc. methods can now take a `parser.CodeModule`
  object as a parameter. Using a single `CodeModule` for all substructures has
  been found to improve the run time of this program by 3-4 times for larger
  code blocks where all substructures are being matched.
- String parameter to substructure methods is now deprecated.
- `RedundantNot` description now gives examples of operators such as `not in`
  which students may be unaware of

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

[1.1.2]:  https://github.com/James-Ansley/qchecker/compare/v1.1.1...v1.1.2

[1.1.1]: https://github.com/James-Ansley/qchecker/compare/v1.1.0...v1.1.1

[1.1.0]: https://github.com/James-Ansley/qchecker/compare/v1.0.2...v1.1.0

[1.0.2]: https://github.com/James-Ansley/qchecker/compare/v1.0.1...v1.0.2

[1.0.1]: https://github.com/James-Ansley/qchecker/compare/v1.0.0...v1.0.1
