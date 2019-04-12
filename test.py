def foldl(f, x0, lst):
    if not lst:
        return x0
    return foldl(f, f(x0, lst[0]), lst[1:])


def foldr(f, x0, lst):
    if not lst:
        return x0
    return f(lst[0], foldr(f, x0, lst[1:]))


def foldl2(f, x0, lst):
    return foldr(lambda f_1, f_2: f(f_2, f_1), x0, lst)


def foldr2(f, x0, lst):
    return foldl(lambda x, y: f(y, x), x0, lst)
# def foldr2(f, x0, lst):
#     return foldl(..., ..., lst)(...)


f = lambda x, y: x / y
print(foldl(f, 1, [1, 2, 3, 4]), foldl2(f, 1, [1, 2, 3, 4]), "\n", foldr(f, 1, [1, 2, 3]), foldr2(f, 1, [1, 2, 3, 4]))

# f = lambda x, y: x / y
# print(f)


def f(x, y):
    return x / y


def f_1(f, x, y):
    return f(x, y) / y


def f_2(y):
    return y

