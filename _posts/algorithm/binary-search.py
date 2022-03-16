def binary_search(arr, val):
    ldx, rdx = 0, len(arr)-1
    while ldx <= rdx:
        mdx = (ldx + rdx) // 2
        if arr[mdx] < val:
            ldx = mdx + 1
        elif arr[mdx] > val:
            rdx = mdx - 1
        else:
            return mdx
    return None

def lower_bound(arr, val):
    ldx, rdx = 0, len(arr)
    while ldx < rdx:
        mdx = (ldx + rdx) // 2
        if arr[mdx] >= val:
            rdx = mdx
        else:
            ldx = mdx + 1
    return ldx

def upper_bound(arr, val):
    ldx, rdx = 0, len(arr)
    while ldx < rdx:
        mdx = (ldx + rdx) // 2
        if arr[mdx] <= val:
            ldx = mdx + 1
        else:
            rdx = mdx
    return ldx

arr = [0,2,4,6,8,10,12,14,16,18]
print(binary_search(arr, 4))