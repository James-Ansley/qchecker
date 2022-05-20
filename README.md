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

### Note:

The `DuplicateExpression` substructure is now deprecated and will be removed or
moved in future versions. This substructure is also not in the `SUBSTRUCTURES`
constant. A temporary `ALL_SUBSTRUCTURES` constant has been added that includes
it along with all other substructures. A warning will show when trying to
match `DuplicateExpression` substructures. To disable this, filter
the `DeprecationWarning` warning type:

```python
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
```
