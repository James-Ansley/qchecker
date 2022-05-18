It looks like the code at the end of this if block is the same as the entire
else block!
This means in either case, the same code will be run regardless of whether the
if-condition is True or False.
In this case, it might be better to remove this duplicate code by moving it
outside of the if and else block.

For example, instead of:
```python
if x < 5:
    x = 5
    do_something(x)
    print('Done!')
else:
    do_something(x)
    print('Done!')
```

Consider doing this:
```python
if x < 5:
    x = 5
do_something(x)
print("Done!")
```

Here, the duplicate lines `do_something(x)` and `print("Done!")` were moved
outside the if and else block.
