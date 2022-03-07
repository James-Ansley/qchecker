import ast

from qchecker.substructures import MissedAbsoluteValue

missed_absolute_value = ast.parse("""
def my_function(x):
    if x < 5 and x > -5:
        print('Small')
    print('Large')


my_function(10)
""")

matches = MissedAbsoluteValue.iter_matches(missed_absolute_value)
for match in matches:
    print(repr(match))
