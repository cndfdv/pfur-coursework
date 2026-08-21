l = list(range(1, 21))
print(list(filter(lambda x: x % 2 == 0, l)))
print(list(map(lambda x: x + 10, l)))
print(sorted(l, reverse=True))