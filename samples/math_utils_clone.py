def compute_factorial(number):
    # This function computes factorial
    # It is semantically identical to calculate_factorial in math_utils.py
    if number < 0:
        return None
    if number == 0:
        return 1
    res = 1
    for x in range(1, number + 1):
        res = res * x
    return res

def get_fib_sequence(count):
    # This computes fibonacci sequence
    # Semantically similar to calculate_fibonacci
    if count <= 0:
        return []
    if count == 1:
        return [0]
    seq = [0, 1]
    while len(seq) < count:
        next_val = seq[-1] + seq[-2]
        seq.append(next_val)
    return seq
