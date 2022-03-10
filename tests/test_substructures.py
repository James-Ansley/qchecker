from textwrap import dedent

from qchecker.match import TextRange
from qchecker.substructures import *


def test_unnecessary_elif():
    code = dedent('''
    def foo(x):
        if x > 5:
            print('x is big')
        elif x <= 5:
            print('x is small')
    
    def bar(x):
        # No match
        if x > 5:
            print('x is big')
        elif x < 5:
            print('x is small')
    
    def baz(x):
        if x:
            print('x is')
        elif not x:
            print('x is not')
    
    def my_friend_goo(x):
        if x.isupper():
            print('SHOUTY')
        elif not x.isupper():
            print('not shouty')
            
    def baz(x):
        if not x:
            print('x is not')
        elif x:
            print('x is')
            
    def baz(x):
        if x < 5 == True:
            print('x is')
        elif x < 5 == False:
            print('x is not')
    ''')
    match1, match2, match3, match4, match5 = UnnecessaryElif.iter_matches(code)
    assert match1.text_range == TextRange(3, 4, 6, 27)
    assert match2.text_range == TextRange(16, 4, 19, 25)
    assert match3.text_range == TextRange(22, 4, 25, 27)
    assert match4.text_range == TextRange(28, 4, 31, 21)
    assert match5.text_range == TextRange(34, 4, 37, 25)


def test_if_else_return_bool():
    code = dedent('''
    def foo(x):
        if x > 5:
            return True
        else:
            return False
    
    def bar(x):
        if x > 5:
            return False
        else:
            return True
    
    def baz(x):
        # No match
        if x > 5:
            print('A side effect')
            return True
        else:
            return False
    
    def my_friend_goo(x):
        # No match
        if x > 5:
            return True
        else:
            return 5
    
    def she_always_knows_just_what_to_do(x):
        # No match
        if x > 5:
            return x
        else:
            return True
    ''')
    match1, match2 = IfElseReturnBool.iter_matches(code)
    assert match1.text_range == TextRange(3, 4, 6, 20)
    assert match2.text_range == TextRange(9, 4, 12, 19)


def test_if_return_bool():
    code = dedent('''
    def foo(x):
        if x > 5:
            return True
        return False
    
    def bar(x):
        if x > 5:
            return False
        return True
    
    def baz(x):
        # No Match
        if x > 5:
            print('A side effect')
            return True
        return False
    
    def my_friend_goo(x):
        # No Match
        if x > 5:
            return x
        return True
    
    def she_always_knows_just_what_to_do(x):
        # No Match
        if x > 5:
            return true
        return x
    ''')
    match1, match2 = IfReturnBool.iter_matches(code)
    assert match1.text_range == TextRange(3, 4, 5, 16)
    assert match2.text_range == TextRange(8, 4, 10, 15)


def test_if_else_assign_bool_return():
    code = dedent('''
    def foo(x):
        if x > 5:
            res = True
        else:
            res = False
        return res
    
    def bar(x):
        if x > 5:
            res = False
        else:
            res = True
        return res
    
    def baz(x):
        # No Match
        if x > 5:
            res = False
        else:
            res = False
        return res
    
    def my_friend_goo(x):
        # No Match
        if x > 5:
            res = True
        else:
            res = 5
        return res
    
    def she_always_knows_just_what_to_do(x):
        # No Match
        if x > 5:
            print('a side effect')
            res = True
        else:
            res = False
        return res
    
    def what_she_does_best_is_stand_and_stare(x):
        # No Match
        y = x
        if x > 5:
            res = True
        else:
            res = False
        return y
    ''')
    match1, match2 = IfElseAssignBoolReturn.iter_matches(code)
    assert match1.text_range == TextRange(3, 4, 7, 14)
    assert match2.text_range == TextRange(10, 4, 14, 14)


def test_if_else_assign_return():
    code = dedent('''
    def foo(x):
        if x > 5:
            res = 'big'
        else:
            res = 'small'
        return res
        
    def bar(x):
        if x > 5:
            res = True
        else:
            res = 5
        return res
    
    def baz(x):
        # no match
        if x > 5:
            res = True
        else:
            res = False
        return res
        
    def my_friend_goo(x):
        # no match
        y = x
        if x > 5:
            res = x
        else:
            res = 5
        return y
        
    def she_always_knows_just_what_to_do(x):
        # no match
        if x > 5:
            print('A side effect')
            res = x
        else:
            res = 5
        return res
    ''')
    match1, match2 = IfElseAssignReturn.iter_matches(code)
    assert match1.text_range == TextRange(3, 4, 7, 14)
    assert match2.text_range == TextRange(10, 4, 14, 14)


def test_if_else_assign_bool():
    code = dedent('''
    def foo(x):
        if x > 5:
            y = True
        else:
            y = False
        print(y)
    
    def bar(x):
        if x > 5:
            y = False
        else:
            y = True
        print(y)
    
    def baz(x):
        # no match
        if x > 5:
            y = True
        else:
            y = False
        return y
    
    def my_friend_goo(x):
        # no match
        if x > 5:
            y = True
        else:
            y = True
    ''')
    match1, match2 = IfElseAssignBool.iter_matches(code)
    assert match1.text_range == TextRange(3, 4, 6, 17)
    assert match2.text_range == TextRange(10, 4, 13, 16)


def test_empty_if_body():
    code = dedent('''
    def foo(x):
        if x > 5:
            ...
        else:
            print('Do something')
        
    def bar(x):
        if x > 5:
            pass
        else:
            print('Do something')
    
    def baz(x):
        if x > 5:
            x = x
        else:
            x += 1
            
    def my_friend_goo(x):
        # no match
        if x > 5:
            pass
            x += 1
        else:
            x += 1
    ''')
    match1, match2, match3 = EmptyIfBody.iter_matches(code)
    assert match1.text_range == TextRange(3, 4, 4, 11)
    assert match2.text_range == TextRange(9, 4, 10, 12)
    assert match3.text_range == TextRange(15, 4, 16, 13)


def test_empty_else_body():
    code = dedent('''
    def foo(x):
        if x > 5:
            print('Do something')
        else:
            ...

    def bar(x):
        if x > 5:
            print('Do something')
        else:
            pass

    def baz(x):
        if x > 5:
            x += 1
        else:
            x = x

    def my_friend_goo(x):
        # no match
        if x > 5:
            x += 1
        else:
            pass
            x += 1
    ''')
    match1, match2, match3 = EmptyElseBody.iter_matches(code)
    assert match1.text_range == TextRange(3, 4, 6, 11)
    assert match2.text_range == TextRange(9, 4, 12, 12)
    assert match3.text_range == TextRange(15, 4, 18, 13)


def test_nested_if():
    code = dedent('''
    def foo(x):
        if x > 5:
            if x < 10:
                return True
        else:
            return False
    
    def bar(x):
        # no match
        if x > 5:
            print('A side effect')
            if x < 10:
                return True
        else:
            return False
    
    def baz(x):
        # no match
        if x > 5:
            if x < 10:
                print('med')
            else:
                print('large')
        else:
            print('small')
    ''')
    match, = NestedIf.iter_matches(code)
    assert match.text_range == TextRange(3, 4, 5, 23)


def test_unnecessary_else():
    code = dedent('''
    def foo(x):
        result = 'small'
        if x > 5:
            result = 'Large'
            return result
        else:
            return result
        
    def bar(x):
        # no match
        if x > 5:
            result = 'large'
            return result
        else:
            result = 'small'
            return result
    
    def baz(x):
        # no match
        if x > 5:
            result = 'large'
        else:
            result = 'small'
    ''')
    match, = UnnecessaryElse.iter_matches(code)
    assert match.text_range == TextRange(4, 4, 8, 21)


def test_duplicate_if_else_statement():
    code = dedent('''
    def foo(x):
        if x > 5:
            print('A side effect')
            result = 'large'
            return result
        else:
            result = 'small'
            return result
        
    def bar(x):
        # No match
        if x > 5:
            print('Hello')
            print('World')
        else:
            print('Hello')
            print('World')
    
    def baz(x):
        # no match
        result = 'small'
        if x > 5:
            result = 'Large'
            return result
        else:
            return result
    
    def my_friend_goo(x):
        # no match
        if x > 5:
            result = 'large'
        else:
            result = 'small'
    
    def she_always_knows_just_what_to_do(x):
        # no match
        if x > 5:
            print('A side effect')
            result = 'large'
            print('Do something')
            return result
        else:
            result = 'small'
            print('Do something')
            return result
    ''')
    match, = DuplicateIfElseStatement.iter_matches(code)
    assert match.text_range == TextRange(3, 4, 9, 21)


def test_several_duplicate_if_else_statements():
    code = dedent('''
    def foo(x):
        if x > 5:
            print('A side effect')
            result = 'large'
            print('Do something')
            return result
        else:
            result = 'small'
            print('Do something')
            return result
        
    def bar(x):
        # No match
        if x > 5:
            print('Hello')
            print('World')
        else:
            print('Hello')
            print('World')
    
    def baz(x):
        # no match
        result = 'small'
        if x > 5:
            result = 'Large'
            return result
        else:
            return result
    
    def my_friend_goo(x):
        # no match
        if x > 5:
            result = 'large'
        else:
            result = 'small'
    ''')
    match, = SeveralDuplicateIfElseStatements.iter_matches(code)
    assert match.text_range == TextRange(3, 4, 11, 21)


def test_duplicate_if_else_body():
    code = dedent('''
    def foo(x):
        if x > 5:
            print('Hello')
            print('World')
        else:
            print('Hello')
            print('World')
        
    def bar(x):
        # No match
        if x > 5:
            print('A side effect')
            result = 'large'
            print('Do something')
            return result
        else:
            result = 'small'
            print('Do something')
            return result
    
    def baz(x):
        # no match
        result = 'small'
        if x > 5:
            result = 'Large'
            return result
        else:
            return result
    
    def my_friend_goo(x):
        # no match
        if x > 5:
            result = 'large'
        else:
            result = 'small'
    ''')
    match, = DuplicateIfElseBody.iter_matches(code)
    assert match.text_range == TextRange(3, 4, 8, 22)


def test_declaration_assignment_division():
    code = dedent('''
    def foo(x):
        y: int
        y = x
    
    def bar(x):
        y: int = x
    
    def baz(x: int):
        return x
    ''')
    match, = DeclarationAssignmentDivision.iter_matches(code)
    assert match.text_range == TextRange(3, 4, 3, 10)


def test_augmentable_assignment():
    code = dedent('''
    x = x + 1
    x = 1 + x
    x = x * 2
    x = 2 * x
    x = x / 2
    x = x - 2
    x = x // 2
    x = x ** 2
    
    # No match
    x = 2 / x
    x = 2 - x
    x = 2 // x
    x = 2 ** x
    ''').strip()
    matches = AugmentableAssignment.iter_matches(code)
    lines = code.splitlines()
    for i, match in enumerate(matches, start=1):
        assert match.text_range == TextRange(i, 0, i, len(lines[i - 1]))


def test_duplicate_expression():
    code = dedent('''
    if x[i * 2 - 1] < x[i * 2]:
        child = x[i * 2 - 1]
    else:
        child = x[i * 2]
    ''')
    match1, match2 = DuplicateExpression.iter_matches(code)
    assert match1.text_range == TextRange(2, 3, 2, 15)
    assert match2.text_range == TextRange(3, 12, 3, 24)


def test_missed_absolute_value():
    code = dedent('''
    if x == 5 or x == -5: ...
    if x < 5 and x > -5: ...
    if x <= 5 and x >= -5: ...
    if x != 5 and x != -5: ...
    
    if x == 5 and x == -5: ...
    if x < 5 and x < -5: ...
    if x <= 5 and x > -5: ...
    if x < 5 and x > -6: ...
    ''').strip()
    matches = MissedAbsoluteValue.iter_matches(code)
    lines = code.splitlines()
    for i, match in enumerate(matches, start=1):
        assert match.text_range == TextRange(i, 3, i, len(lines[i - 1]) - 5)


def test_repeated_addition():
    code = dedent('''
    y = x + x
    y = x + x + x
    y = y + x + x + x
    ''')
    match1, match2, match3 = RepeatedAddition.iter_matches(code)
    assert match1.text_range == TextRange(2, 4, 2, 9)
    assert match2.text_range == TextRange(3, 4, 3, 13)
    assert match3.text_range == TextRange(4, 4, 4, 17)


def test_repeated_multiplication():
    code = dedent('''
    y = x * x * x
    y = x * x * x * x
    y = y * x * x * x
    
    y = x * x
    ''')
    match1, match2, match3 = RepeatedMultiplication.iter_matches(code)
    assert match1.text_range == TextRange(2, 4, 2, 13)
    assert match2.text_range == TextRange(3, 4, 3, 17)
    assert match3.text_range == TextRange(4, 4, 4, 17)


def test_confusing_else():
    code = dedent('''
    def foo(x):
        if x < 5:
            print('x is small')
        else:
            if x < 10:
                print('x is medium')
            else:
                print('x is large')
            
    def bar(x):
        if x < 5:
            print('x is small')
        elif x < 10:
            print('x is medium')
        else:
            print('x is large')
    ''')
    match, = ConfusingElse.iter_matches(code)
    assert match.text_range == TextRange(6, 8, 9, 31)
