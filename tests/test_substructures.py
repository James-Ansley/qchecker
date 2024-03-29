from textwrap import dedent

import pytest

from qchecker.match import TextRange
from qchecker.parser import CodeModule
from qchecker.substructures import *


def test_unnecessary_elif():
    code = CodeModule(dedent('''
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
    
    def baz(x):
        if x % 2 == 0:
            print('x is even')
        elif x % 2 == 1:
            print('x is weird')
    '''))
    match1, match2, match3, match4, match5, match6 = \
        UnnecessaryElif.iter_matches(code)
    assert match1.text_range == TextRange(3, 4, 6, 27)
    assert match2.text_range == TextRange(16, 4, 19, 25)
    assert match3.text_range == TextRange(22, 4, 25, 27)
    assert match4.text_range == TextRange(28, 4, 31, 21)
    assert match5.text_range == TextRange(34, 4, 37, 25)
    assert match6.text_range == TextRange(40, 4, 43, 27)


def test_if_else_return_bool():
    code = CodeModule(dedent('''
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
    '''))
    match1, match2 = IfElseReturnBool.iter_matches(code)
    assert match1.text_range == TextRange(3, 4, 6, 20)
    assert match2.text_range == TextRange(9, 4, 12, 19)


def test_if_return_bool():
    code = CodeModule(dedent('''
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
    '''))
    match1, match2 = IfReturnBool.iter_matches(code)
    assert match1.text_range == TextRange(3, 4, 5, 16)
    assert match2.text_range == TextRange(8, 4, 10, 15)


def test_if_else_assign_bool_return():
    code = CodeModule(dedent('''
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
    '''))
    match1, match2 = IfElseAssignBoolReturn.iter_matches(code)
    assert match1.text_range == TextRange(3, 4, 7, 14)
    assert match2.text_range == TextRange(10, 4, 14, 14)


def test_if_else_assign_return():
    code = CodeModule(dedent('''
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
    '''))
    match1, match2 = IfElseAssignReturn.iter_matches(code)
    assert match1.text_range == TextRange(3, 4, 7, 14)
    assert match2.text_range == TextRange(10, 4, 14, 14)


def test_if_else_assign_bool():
    code = CodeModule(dedent('''
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
    '''))
    match1, match2 = IfElseAssignBool.iter_matches(code)
    assert match1.text_range == TextRange(3, 4, 6, 17)
    assert match2.text_range == TextRange(10, 4, 13, 16)


def test_empty_if_body():
    code = CodeModule(dedent('''
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
    '''))
    match1, match2, match3 = EmptyIfBody.iter_matches(code)
    assert match1.text_range == TextRange(3, 4, 4, 11)
    assert match2.text_range == TextRange(9, 4, 10, 12)
    assert match3.text_range == TextRange(15, 4, 16, 13)


def test_empty_else_body():
    code = CodeModule(dedent('''
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
    '''))
    match1, match2, match3 = EmptyElseBody.iter_matches(code)
    assert match1.text_range == TextRange(3, 4, 6, 11)
    assert match2.text_range == TextRange(9, 4, 12, 12)
    assert match3.text_range == TextRange(15, 4, 18, 13)


def test_nested_if():
    code = CodeModule(dedent('''
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
    '''))
    match, = NestedIf.iter_matches(code)
    assert match.text_range == TextRange(3, 4, 5, 23)


def test_unnecessary_else():
    code = CodeModule(dedent('''
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
    '''))
    match, = UnnecessaryElse.iter_matches(code)
    assert match.text_range == TextRange(4, 4, 8, 21)


def test_duplicate_if_else_statement():
    code = CodeModule(dedent('''
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
            
    if x == 1:
        and_now_for_something_completely_different(x)
    elif x == 2:
        do_something(x)
        print("A side-effect")
    else:
        do_something_else(x)
        print("A side-effect")
    '''))
    match, = DuplicateIfElseStatement.iter_matches(code)
    assert match.text_range == TextRange(3, 4, 9, 21)


def test_several_duplicate_if_else_statements():
    code = CodeModule(dedent('''
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
            
    if x == 1:
        and_now_for_something_completely_different(x)
    elif x == 2:
        do_something(x)
        do_something_different(x)
        print("A side-effect")
    else:
        do_something_else(x)
        do_something_different(x)
        print("A side-effect")
    '''))
    match, = SeveralDuplicateIfElseStatements.iter_matches(code)
    assert match.text_range == TextRange(3, 4, 11, 21)


def test_duplicate_if_else_body():
    code = CodeModule(dedent('''
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
    '''))
    match, = DuplicateIfElseBody.iter_matches(code)
    assert match.text_range == TextRange(3, 4, 8, 22)


@pytest.mark.parametrize(
    'line,should_match',
    (('x = x + 1', True),
     ('x = 1 + x', True),
     ('x = x * 2', True),
     ('x = 2 * x', True),
     ('x = x / 2', True),
     ('x = x - 2', True),
     ('x = x // 2', True),
     ('x = x ** 2', True),
     ('x = 2 / x', False),
     ('x = 2 - x', False),
     ('x = 2 // x', False),
     ('x = 2 ** x', False))
)
def test_augmentable_assignment(line, should_match):
    match = next(AugmentableAssignment.iter_matches(CodeModule(line)), None)
    assert (match is not None) == should_match
    if should_match:
        assert match.text_range == TextRange(1, 0, 1, len(line))


@pytest.mark.filterwarnings('ignore')
def test_duplicate_expression():
    code = CodeModule(dedent('''
    if x[i * 2 - 1] < x[i * 2]:
        child = x[i * 2 - 1]
    else:
        child = x[i * 2]
    '''))
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
    matches = MissedAbsoluteValue.iter_matches(CodeModule(code))
    lines = code.splitlines()
    for i, match in enumerate(matches, start=1):
        assert match.text_range == TextRange(i, 3, i, len(lines[i - 1]) - 5)


@pytest.mark.parametrize(
    'line,should_match',
    (('x + x', True),
     ('x + x + x', True),
     ('y + x + x + x', True),
     ('(y * x) + (y * x)', True),
     ('y + x + x * x', False),
     ('y * x + x', False),
     ('x + x_1', False),
     ('abc + abcd', False),
     ('xy + y', False))
)
def test_repeated_addition(line, should_match):
    match = next(RepeatedAddition.iter_matches(CodeModule(line)), None)
    assert (match is not None) == should_match
    if should_match:
        assert match.text_range == TextRange(1, 0, 1, len(line))


@pytest.mark.parametrize(
    'line,should_match',
    (('x * x * x', True),
     ('x * x * x * x', True),
     ('y * x * x * x', True),
     ('(y + x) * (y + x) * (y + x)', True),
     ('x * x', False),
     ('x * x * x_1', False),
     ('x * x + x', False),
     ('x * x * x ** 0.5', False),  # ToDo – Check this in the future
     ('abc * abc * abcd', False),
     ('abcd * bcd * bcd', False))
)
def test_repeated_multiplication(line, should_match):
    match = next(RepeatedMultiplication.iter_matches(CodeModule(line)), None)
    assert (match is not None) == should_match
    if should_match:
        assert match.text_range == TextRange(1, 0, 1, len(line))


@pytest.mark.parametrize(
    'line,should_match',
    (('1 * x', True),
     ('x / x', True),
     ('x / 1', True),
     ('x + 0', True),
     ('0 + x', True),
     ('x - 0', True),
     ('x * 1', True),
     ('+x', True),
     ('x ** 1', True),
     ('x + 1', False),
     ('x / y', False),
     ('-x', False),
     ('1 / x', False),
     ('x // 1', False))
)
def test_redundant_arithmetic(line: str, should_match: bool):
    match = next(RedundantArithmetic.iter_matches(CodeModule(line)), None)
    assert (match is not None) == should_match
    if should_match:
        assert match.text_range == TextRange(1, 0, 1, len(line))


@pytest.mark.parametrize(
    'line,should_match',
    (('not x < y', True),
     ('not x > y', True),
     ('not x == y', True),
     ('not x != y', True),
     ('not x <= y', True),
     ('not x >= y', True),
     ('not x is y', True),
     ('not x is not y', True),
     ('not x in y', True),
     ('not x not in y', True),
     ('x not in y', False),
     ('x is not y', False),
     ('x != y', False),
     ('x < y', False),
     ('x and not y', False),
     ('not x and y', False),
     ('not x < val <= y', False),
     ('not x > val <= y', False),
     )
)
def test_redundant_not(line, should_match):
    match = next(RedundantNot.iter_matches(CodeModule(line)), None)
    assert (match is not None) == should_match
    if should_match:
        assert match.text_range == TextRange(1, 0, 1, len(line))


def test_confusing_else():
    code = CodeModule(dedent('''
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
    '''))
    match, = ConfusingElse.iter_matches(code)
    assert match.text_range == TextRange(6, 8, 9, 31)


def test_else_if():
    code = CodeModule(dedent('''
    def foo(x):
        if x > 10:
            return 'Big'
        else:
            if x > 5:
                return 'med'
        return 'small'

    def foo(x):
        # No match
        if x > 10:
            return 'Big'
        elif x > 5:
            return 'med'
        else:
            return 'small'
            
    def foo(x):
        # No match
        if x > 10:
            return 'Big'
        else:
            if x > 5:
                return 'med'
            else:
                return 'small'
    '''))
    match, = ElseIf.iter_matches(code)
    assert match.text_range == TextRange(5, 4, 6, 16)


@pytest.mark.parametrize(
    'line,should_match',
    (('(x < 5) == True', True),
     ('(x == 5) == False', True),
     ('(x is not y) == True', True),
     ('foo(x) == True', True),
     ('seq[3] == True', True),
     ('seq[3] == False', True),
     ('True == (x < 5)', True),
     ('False == (x == 5)', True),
     ('True == (x is not y)', True),
     ('True == foo(x)', True),
     ('True == seq[3]', True),
     ('False == seq[3]', True),
     ('x is True', False),
     ('True is x', False))
)
def test_redundant_comparison(line, should_match):
    match = next(RedundantComparison.iter_matches(CodeModule(line)), None)
    assert (match is not None) == should_match
    if should_match:
        assert match.text_range == TextRange(1, 0, 1, len(line))


@pytest.mark.parametrize(
    'line,should_match',
    (('x == 5 or x == 4', True),
     ('x == "a" or x == "b"', True),
     ('x == "a" or x == 3', True),
     ('x == "a" and x == 3', False),
     ('x == 2 or y == 3', False),
     ('x == 2 and y == 3', False))
)
def test_mergeable_equal(line, should_match):
    match = next(MergeableEqual.iter_matches(CodeModule(line)), None)
    assert (match is not None) == should_match
    if should_match:
        assert match.text_range == TextRange(1, 0, 1, len(line))


@pytest.mark.parametrize(
    'line,should_match',
    (('for x in range(1):...', True),
     ('for _ in range(1):...', True),
     ('for x in range(0):...', True),
     ('for _ in range(0):...', True),
     ('for x in []:...', False),  # maybe check this
     ('for x in [y]:...', False),  # maybe check this
     ('for x in range(10):...', False),
     ('for x in foo(1):...', False),
     ('for x in foo(0):...', False),
     ('for x in y:...', False))
)
def test_redundant_for(line, should_match):
    match = next(RedundantFor.iter_matches(CodeModule(line)), None)
    assert (match is not None) == should_match
    if should_match:
        assert match.text_range == TextRange(1, 0, 1, len(line) - 4)


@pytest.mark.parametrize(
    'line,should_match',
    (('x = x', True),
     ('x *= 1', True),
     ('x **= 1', True),
     ('x /= 1', True),
     ('x -= 0', True),
     ('x += 0', True),
     ('x //= 1', False),
     ('x = y', False),
     ('x = x + 1', False),
     ('x = None', False),
     ('x == x', False))
)
def test_nop(line, should_match):
    match = next(NoOp.iter_matches(CodeModule(line)), None)
    assert (match is not None) == should_match
    if should_match:
        assert match.text_range == TextRange(1, 0, 1, len(line))


@pytest.mark.parametrize(
    'line,should_match',
    (('x == x', True),
     ('3 == 3', True),
     ('x is x', True),
     ('x == 0 or x != 0', True),
     ('x or not x', True),
     ('x % 2 == 0 or x % 2 == 1', True),
     ('x or True', True),
     ('True or x', True),
     ('True', False),
     ('x == 0 and x != 0', False),
     ('x != x', False))
)
def test_tautology(line, should_match):
    match = next(Tautology.iter_matches(CodeModule(line)), None)
    assert (match is not None) == should_match
    if should_match:
        assert match.text_range == TextRange(1, 0, 1, len(line))


@pytest.mark.parametrize(
    'line,should_match',
    (('x != x', True),
     ('3 != 3', True),
     ('x is not x', True),
     ('x == 0 and x != 0', True),
     ('x and not x', True),
     ('x % 2 == 0 and x % 2 == 1', True),
     ('x and False', True),
     ('False and x', True),
     ('False', False),
     ('x == 0 or x != 0', False),
     ('x == x', False))
)
def test_contradiction(line, should_match):
    match = next(Contradiction.iter_matches(CodeModule(line)), None)
    assert (match is not None) == should_match
    if should_match:
        assert match.text_range == TextRange(1, 0, 1, len(line))


def test_while_as_for():
    code = CodeModule(dedent('''
    while x < 5:
        print('do something', y)
        x += 3
        print('do something', x)

    while x < y:
        y = y - 1
        print('do something', x, y)

    # ToDo in the future, maybe?
    while x > 3 * y:
        print('do something', x, y)
        y = y + x // 10

    # no match
    while x < y:
        y *= 3
        print('do something')

    # no match
    while x < y:
        x += 1
        y += 1
        print('do something')

    # no match
    while x < y:
        y = 2
        x += 3
        print('do something')
    
    # no match
    while x < len(y):
        y.pop()
        x += 1
        print('do something')
    '''))
    match1, match2 = WhileAsFor.iter_matches(code)
    assert match1.text_range == TextRange(2, 0, 5, 28)
    assert match2.text_range == TextRange(7, 0, 9, 31)


def test_for_with_redundant_indexing():
    code = CodeModule(dedent('''
    for i in range(len(s)):
        print(s[i])
        
    def foo(vals):
        for i in range(len(vals)):
            y = vals[i] + 5
            print(y)
    
    # no match
    def bar(vals):
        for i in range(len(vals)):
            i += 1
            print(vals[i])
    
    # no match        
    def baz(vals):
        for i in range(len(vals)):
            vals[i] += 1
    
    # no match
    def goo(vals):
        for val in vals:
            print(val)
    
    # no match
    def goo(vals):
        for i in range(len(vals)):
            print(val[i])
            print(i)
            
    # no match
    def goo(vals):
        for i in range(len(vals)):
            print(val[i // 2])
            print(val[i])
    '''))
    match1, match2 = ForWithRedundantIndexing.iter_matches(code)
    assert match1.text_range == TextRange(2, 0, 3, 15)
    assert match2.text_range == TextRange(6, 4, 8, 16)
