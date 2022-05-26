# qChecker

A simple library for finding statement-level substructures
(e.g. micro-antipatterns) in Abstract and Concrete Syntax Trees

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

code = r'''
def foo(x):
    x = x + 1
    if (x < 5) == True:
        return True
    else:
        return False
'''.strip()

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

# Extras - Programmatic Flake8 and Pylint

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

# Citation

If you use this software, please cite it as below:
```text
@software{finnie-ansley2022qchecker,
    author = {Finnie-Ansley, James},
    month = {5},
    title = {{qChecker}},
    url = {https://github.com/James-Ansley/qchecker},
    version = {1.0.2},
    year = {2022}
}
```
