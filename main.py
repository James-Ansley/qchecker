import ast
from textwrap import dedent

from qchecker.general import *
from qchecker.substructures import RedundantIndexedFor

code = dedent('''
    def foo(seq):
        for i in range(len(seq)):
            print(seq[i])
    
    def bar(seq):
        for i in range(len(seq)):
            yield seq[i]
    
    def baz(seq):
        for i in range(len(seq)):
            seq[i] += 1
    
    def goo(seq):
        for i in range(len(seq)):
            print(i)
''')

for match in RedundantIndexedFor.iter_matches(code):
    print(repr(match))
    print()
    print(match.text_range.grab_range(code))
    print()
