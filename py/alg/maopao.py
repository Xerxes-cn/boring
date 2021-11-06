def maopao(data: list):
    l = len(data)
    for i in range(l-1, -1, -1):
        print(i)
        for j in range(i):
            if data[j] > data[j+1]:
                data[j], data[j+1] = data[j+1], data[j]
    return data


def xuanze(data: list):
    l = len(data)
    for i in range(l-1):
        for j in range(i+1, l):
            if data[i] > data[j]:
                data[i], data[j] = data[j], data[i]
    return data


def charu(data: list):
    l = len(data)
    for i in range(1, l):
        tmp = data[i]
        no = i - 1
        while no >= 0 and tmp < data[no]:
            data[no + 1] = data[no]
            no -= 1
        data[no+1] = tmp
    return data


def shell(data: list):
    l = len(data)
    k = 1
    jmp = l // 2
    while jmp != 0:
        for i in range(jmp, l):
            tmp = data[i]
            j = i - jmp
            while tmp < data[j] and j >= 0:
                data[j+jmp] = data[j]
                j -= jmp
            data[jmp+j] = tmp
        k += 1
        jmp //= 2
    return data


def merge_sort(nums: list):
    if len(nums) < 2:
        return nums
    mid = len(nums) // 2
    left = merge_sort(nums[:mid])
    right = merge_sort(nums[mid:])
    result = []
    while left and right:
        if left[0] > right[0]:
            result.append(right.pop(0))
        else:
            result.append(left.pop(0))
    if left:
        result += left
    if right:
        result += right
    return result


if __name__ == '__main__':
    data = [100, 30, 22, 18, 90, 122, 9, 2222]
    print(merge_sort(data))


