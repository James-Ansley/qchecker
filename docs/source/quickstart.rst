Quick Start
===========

qChecker defines many :class:`Substructure <qchecker.substructures.Substructure>` classes that each detect some kind of micro-antipattern.
These can be imported individually or all inside of a constant :code:`SUBSTRUCTURES` tuple from the :mod:`substructures <qchecker.substructures>` module.


Install
=======

To install qChecker use the following command::

    pip install qchecker

qChecker also allows pylint and flake8 to be run programmatically.
However, it will need to be installed with the :code:`general_checks` extra::

    pip install qchecker[general_checks]

Usage
=====

The intended use case for qChecker is to use the :mod:`substructures <qchecker.substructures>` module.
:class:`Substructures <qchecker.substructures.Substructure>` create :class:`Match <qchecker.match.Match>` objects that contain names, :class:`Description <qchecker.descriptions.Description>`, and :class:`TextRange <qchecker.match.TextRange>` of detected micro-antipatterns

For example::

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

Which would produce::

    If(..)[Return bool] Else[Return !bool]
    Match("If/Else Return Bool", "Looks like you are returning two [...]", TextRange(6,8->9,24))

Or, if you want to process all substructures::

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

Which would produce::

    Match("Redundant Comparison", "It seems like you are comparing [...]", TextRange(3,7->3,22))
    Match("Augmentable Assignment", "It looks like you are writting an [...]", TextRange(2,4->2,13))
    Match("If/Else Return Bool", "Looks like you are returning two [...]", TextRange(3,4->6,20))
