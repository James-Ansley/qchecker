# qChecker

A simple library for finding statement-level substructures
(e.g. micro-anti-patterns/smells) in Abstract Syntax Trees

## Install

    pip install qchecker

## Usage

> qChecker is still in alpha and significant API changes are likely

Currently, subclasses of `qchecker.Substructure` define structure names,
descriptions, and an `iter_matches` class method which iterates
over `qchecker.TextRange`s that match the pattern defined by the
Substructure's `technical_description`.

For example:

```python
import ast

from qchecker import IfElseReturnBool

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

module = ast.parse(code)
matches = IfElseReturnBool.iter_matches(module)
print(IfElseReturnBool.technical_description)
print(*matches, sep="\n")
```

would print the `technical_description` of the `IfElseReturnBool` Substructure
followed by a `TextRange` with the start and end line numbers and column offsets
of the structure in the `code` string.

```
If(..)[Return bool] Else[Return !bool]
TextRange(6,8->9,24)
```

A `SUBSTRUCTURES` list provides the list of all subclasses of `Substructure`.
