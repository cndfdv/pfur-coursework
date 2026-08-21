a, b = input().split()
if type(a) is int and type(b) is int:
    a, b = int(a), int(b)
    if b != 0:
        print(a / b)
    else:
        raise ValueError
else:
    raise ValueError