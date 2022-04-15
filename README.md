# qChecker

A simple library for finding statement-level substructures
(e.g. micro-anti-patterns/smells) in Abstract Syntax Trees

## Install

    pip install qchecker

## Usage

> qChecker is still in alpha and significant API changes are likely

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
