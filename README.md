# qChecker

Quick Checker? Quality Checker? Quinoa Checker? qChecker can be whatever you
want it to be.

qChecker is a library intended to identify semantically meaningful
micro-antipatterns in student code and can describe those issues to students
along with how to fix them. For example, have your students ever written code
like this?

```python
def foo(x):
    if x % 2 == 0:
        return True
    else:
        return False
```

qChecker is here to help! The `IfElseReturnBool` pattern will have no problem
identifying this. Even specifying where in the code the defect is:
`TextRange(2,4->5,20)` and providing a description of the error with isomorphic
refactorings:

<blockquote>
Looks like you are returning two booleans inside of an If/Else statement.
It might be better if you just return the If condition or its inverse.

---

For example, instead of:

```python
if x < 5:
    return True
else:
    return False
```

Consider doing this:

```python
return x < 5
```

...
</blockquote>

## Documentation

Check out the documentation for qChecker on ReadTheDocs:
https://qchecker.readthedocs.io/

## Install

    pip install qchecker

## Usage

Currently, concrete subclasses of `qchecker.Substructure` define
an `iter_matches` class method which iterates over `qchecker.match.Match`
objects identifying where in the code those particular substructures occur.

For example:

```python
from qchecker.substructures import IfElseReturnBool

code = """
class Foo:
    def __init__(self, x):
        self.x = x
    
    def bar(self):
        if self.x < 10:
            return True
        else:
            return False
""".strip()

matches = IfElseReturnBool.iter_matches(code)
print(IfElseReturnBool.technical_description)
print(*matches, sep="\n")
```

would print the `technical_description` of the `IfElseReturnBool` Substructure
followed by a `Match` object containing the mane of the pattern matched, the
description, and the `TextRange` where the pattern occurs.

```
If(..)[Return bool] Else[Return !bool]
Match("If/Else Return Bool", "Looks like you are returning two [...]", TextRange(6,8->9,24))
```

A `SUBSTRUCTURES` constant is included in the `substructures` module that
contains all substructures. This can be used, for example:

```python
from qchecker.substructures import SUBSTRUCTURES
from qchecker.parser import CodeModule

code = CodeModule(r'''
def foo(x):
    x = x + 1
    if (x < 5) == True:
        return True
    else:
        return False
'''.strip())

matches = []
for substructure in SUBSTRUCTURES:
    matches += substructure.iter_matches(code)

for match in matches:
    print(match)
```

Which will produce the following matches:

```text
Match("Redundant Comparison", "It seems like you are comparing [...]", TextRange(3,7->3,22))
Match("Augmentable Assignment", "It looks like you are writting an [...]", TextRange(2,4->2,13))
Match("If/Else Return Bool", "Looks like you are returning two [...]", TextRange(3,4->6,20))
```

### Note:

While the `iter_matches` can take a string of code as a parameter, if you intend
to match the same piece of code against several substructures, it is better to
parse the code first into a single `CodeModule` to use with all substructures.
This has been shown to improve performance 3-4 times on assignment-sized
projects (80-400 lines of code).

The string parameter to the `iter_matches` etc. methods is deprecated and will
be removed in future versions.

## What Assumptions does qChecker Make?

qChecker assumes the code it is working on is relatively simple and isn't using
any of Python's black magic features in strange ways. This means qChecker is
only appropriate for novice students as some assumptions it makes about the
properties of the code it operates on are quite bold.

For example, qChecker assumes multiplication will always be commutative, that
every object that supports a particular operator (e.g. `__add__`) will always
have the corresponding augmented operator (e.g. `__iadd__`), and that functions
don't have any strange and wacky side effects that would cause subsequent calls
in the same expression to behave differently – among others.

## Extras - Programmatic Flake8 and Pylint

qchecker can be installed with support for programmatically running flake8 and
pylint to generate match objects.

Install qchecker with the extras "general_checks":

```text
pip install qchecker[general_checks]
```

This will allow you to import the `general` module of qchecker which reveals two
functions:

- `get_flake8_matches(code: str) -> list[Match]` which returns the matches
  detected by flake8.
- `get_pylint_matches(code: str, errors: list[str] = None) -> list[Match]` which
  returns the matches detected by pylint. A list of pylint error codes can be
  provided to only detect those errors and ignore all others.

## Citation

If you use this software, please cite it as below:

```text
@software{finnie-ansley2022qchecker,
    author = {Finnie-Ansley, James},
    month = {6},
    title = {{qChecker}},
    url = {https://github.com/James-Ansley/qchecker},
    version = {1.1.0},
    year = {2022}
}
```
