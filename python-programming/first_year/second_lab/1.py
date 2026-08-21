with open("data/data.txt") as f:
    s = list(map(int, f.readlines()))
    print(s)
    res = [sum(s), sum(s) / len(s), max(s), min(s)]
    print(res)

formats = ["Сумма: ", "Среднее: ", "Максимум: ", "Минимум: "]
with open("result/1.txt", "w") as f:
    for el in zip(formats, res):
        f.write(str(el[0]) + str(el[1]) + "\n")