n = int(input())
count = 0
for i in range(n):
    count += i + 1
    print(i + 1, (i + 1) ** 2)
print(count)