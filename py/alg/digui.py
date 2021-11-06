# 递归
def fib(n):
    if n == 0:
        return n
    if n in [1, 2]:
        return n
    n = fib(n-1) + fib(n-2)
    return n

# 贪心
res_list = [None] * 100  # noqa


def fibonacii(n):
    res = res_list[n]
    if res is None:
        res_list[n] = res = fib(n)
    return res


if __name__ == '__main__':
    # print(fib(10))
    print(fibonacii(10))
    print(res_list)

