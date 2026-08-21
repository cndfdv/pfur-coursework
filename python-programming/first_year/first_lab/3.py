n = int(input())
print(n)
fac = 1
for i in range(1, n+1):
    fac *= i
    print(n-i)
print(fac)