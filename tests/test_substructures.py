import ast

import pytest
from qchecker.match import TextRange
from qchecker.substructures import *

# A set of minimal cases that should each match exactly one substructure
unnecessary_elif = ast.parse("""
def my_function(x):
    if x > 5:
        print('do something')
    elif x <= 5:
        print('do something else')
        

my_function(10)
""")
if_else_return_bool = ast.parse("""
def my_function(x):
    if x > 5:
        return True
    else:
        return False
        

my_function(10)
""")
if_return_bool = ast.parse("""
def my_function(x):
    if x > 5:
        return False
    return True
    
    
my_function(10)
""")
if_else_assign_return = ast.parse("""
def my_function(x):
    if x > 5:
        res = 'Is Greater'
    else:
        res = 'Is Smaller or Equal'
    return res
        
    
my_function(10)
""")
if_else_assign_bool_return = ast.parse("""
def my_function(x):
    if x > 5:
        res = True
    else:
        res = False
    return res
    
    
my_function(10)
""")
if_else_assign_bool = ast.parse("""
def my_function(x):
    if x > 5:
        res = True
    else:
        res = False


my_function(10)
""")
empty_if_body = ast.parse("""
def my_function(x):
    if x > 5:
        ...
    else:
        print('Do something')


my_function(10)
""")
empty_else_body = ast.parse("""
def my_function(x):
    if x > 5:
        print('Do something')
    else:
        ...


my_function(10)
""")
nested_if = ast.parse("""
def my_function(x):
    if x > 5:
        if x < 10:
            print('In range')
    print('Not in range')


my_function(10)
""")
confusing_else = ast.parse("""
def my_function(x):
    if x > 5:
        print('Do something')
    else:
        if x < 10:
            print('Do something else')
        else:
            print('Do something else again')
            

my_function(10)
""")
unnecessary_else = ast.parse("""
def my_function(x):
    if x > 5:
        x += 1
        print(x)
    else:
        print(x)
            

my_function(10)
""")
duplicate_if_else_statement = ast.parse("""
def my_function(x):
    if x > 5:
        x += 1
        print(x)
    else:
        x -= 1
        print(x)
            

my_function(10)
""")
several_duplicate_if_else_statements = ast.parse("""
def my_function(x):
    if x > 5:
        y = x
        x += 1
        print(x)
    else:
        z = x
        x += 1
        print(x)
            

my_function(10)
""")
duplicate_if_else_body = ast.parse("""
def my_function(x):
    if x > 5:
        y = x
        x += 1
        print(x)
    else:
        y = x
        x += 1
        print(x)
            

my_function(10)
""")
declaration_assignment_division = ast.parse("""
def my_function(x):
    y: int
            

my_function(10)
""")
augementable_assignment = ast.parse("""
def my_function(x):
    x = x + 1
    return x
            

my_function(10)
""")
missed_absolute_value = ast.parse("""
def my_function(x):
    if x < 5 and x > -5:
        print('Small')
    print('Large')
            

my_function(10)
""")

minimal_cases = [
    unnecessary_elif,
    if_else_return_bool,
    if_return_bool,
    if_else_assign_return,
    if_else_assign_bool_return,
    if_else_assign_bool,
    empty_if_body,
    empty_else_body,
    nested_if,
    confusing_else,
    unnecessary_else,
    duplicate_if_else_statement,
    several_duplicate_if_else_statements,
    duplicate_if_else_body,
    declaration_assignment_division,
    augementable_assignment,
    missed_absolute_value,
]

# Minimal case produces two matches
duplicate_expression = ast.parse("""
def my_function(x):
    for i in range(len(x) // 2):
        if x[i * 2] <= x[i]:
            return x[i * 2] <= x[i]


my_function([0, 1, 2, 3, 4, 5])
""")


def get_single_match(substructure, module):
    matches = list(substructure.iter_matches(module))
    assert len(matches) == 1
    return matches[0]


def test_unnecessary_elif():
    match = get_single_match(UnnecessaryElif, unnecessary_elif)
    assert match.id == 'Unnecessary Elif'
    assert match.text_range == TextRange(3, 4, 6, 34)


def test_if_else_return_bool():
    match = get_single_match(IfElseReturnBool, if_else_return_bool)
    assert match.id == 'If/Else Return Bool'
    assert match.text_range == TextRange(3, 4, 6, 20)


def test_if_return_bool():
    match = get_single_match(IfReturnBool, if_return_bool)
    assert match.id == 'If Return Bool'
    assert match.text_range == TextRange(3, 4, 5, 15)


def test_if_else_assign_return():
    match = get_single_match(IfElseAssignReturn, if_else_assign_return)
    assert match.id == 'If/Else Assign Return'
    assert match.text_range == TextRange(3, 4, 7, 14)


def test_if_else_assign_bool_return():
    match = get_single_match(IfElseAssignBoolReturn, if_else_assign_bool_return)
    assert match.id == 'If/Else Assign Bool Return'
    assert match.text_range == TextRange(3, 4, 7, 14)


def test_if_else_assign_bool():
    match = get_single_match(IfElseAssignBool, if_else_assign_bool)
    assert match.id == 'If/Else Assign Bool'
    assert match.text_range == TextRange(3, 4, 6, 19)


def test_empty_if_body():
    match = get_single_match(EmptyIfBody, empty_if_body)
    assert match.id == 'Empty If Body'
    assert match.text_range == TextRange(3, 4, 6, 29)


def test_empty_else_body():
    match = get_single_match(EmptyElseBody, empty_else_body)
    assert match.id == 'Empty Else Body'
    assert match.text_range == TextRange(3, 4, 6, 11)


def test_nested_if():
    match = get_single_match(NestedIf, nested_if)
    assert match.id == 'Nested If'
    assert match.text_range == TextRange(3, 4, 5, 29)


def test_confusing_else():
    match = get_single_match(ConfusingElse, confusing_else)
    assert match.id == 'Confusing Else'
    assert match.text_range == TextRange(6, 8, 9, 44)


def test_unnecessary_else():
    match = get_single_match(UnnecessaryElse, unnecessary_else)
    assert match.id == 'Unnecessary Else'
    assert match.text_range == TextRange(3, 4, 7, 16)


def test_duplicate_if_else_statement():
    match = get_single_match(DuplicateIfElseStatement,
                             duplicate_if_else_statement)
    assert match.id == 'Duplicate If/Else Statement'
    assert match.text_range == TextRange(3, 4, 8, 16)


def test_several_duplicate_if_else_statements():
    match = get_single_match(SeveralDuplicateIfElseStatements,
                             several_duplicate_if_else_statements)
    assert match.id == 'Several Duplicate If/Else Statements'
    assert match.text_range == TextRange(3, 4, 10, 16)


def test_duplicate_if_else_body():
    match = get_single_match(DuplicateIfElseBody, duplicate_if_else_body)
    assert match.id == 'Duplicate If/Else Body'
    assert match.text_range == TextRange(3, 4, 10, 16)


def test_declaration_assignment_division():
    match = get_single_match(DeclarationAssignmentDivision,
                             declaration_assignment_division)
    assert match.id == 'Declaration/Assignment Division'
    assert match.text_range == TextRange(3, 4, 3, 10)


def test_augementable_assignment():
    match = get_single_match(AugmentableAssignment, augementable_assignment)
    assert match.id == 'Augmentable Assignment'
    assert match.text_range == TextRange(3, 4, 3, 13)


def test_duplicate_expression():
    match1, match2 = DuplicateExpression.iter_matches(duplicate_expression)
    assert match1.id == 'Duplicate Expression'
    assert match1.text_range == TextRange(4, 11, 4, 27)
    assert match2.id == 'Duplicate Expression'
    assert match2.text_range == TextRange(5, 19, 5, 35)


def test_missed_absolute_value():
    match = get_single_match(MissedAbsoluteValue, missed_absolute_value)
    assert match.id == 'Missed Absolute Value'
    assert match.text_range == TextRange(3, 7, 3, 23)


@pytest.mark.parametrize(
    'substructure',
    [s for s in SUBSTRUCTURES if s != DuplicateExpression]
)
def test_basic_match_is_exclusive(substructure):
    """Substructures should match exactly one minimal case each"""
    num_matches = sum(substructure.count_matches(module)
                      for module in minimal_cases)
    assert num_matches == 1


@pytest.mark.parametrize('substructure', SUBSTRUCTURES)
def test_empty(substructure):
    """Substructures should not match empty modules"""
    empty = ast.parse('')
    assert substructure.count_matches(empty) == 0
