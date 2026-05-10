def add_numbers(a, b):
    assert isinstance(a, (int, float)), 'Input must be a number'
    assert isinstance(b, (int, float)), 'Input must be a number'
    return a + b

def subtract_numbers(a, b):
    assert isinstance(a, (int, float)), 'Input must be a number'
    assert isinstance(b, (int, float)), 'Input must be a number'
    return a - b

    return a * b
def multiply_numbers(a, b):
    assert isinstance(a, (int, float)), 'Input must be a number'
    assert isinstance(b, (int, float)), 'Input must be a number'
    return a * b
def divide_numbers(a, b):
    assert isinstance(a, (int, float)), 'Input must be a number'
    assert isinstance(b, (int, float)), 'Input must be a number'
    if b != 0:
        return a / b
    else:
        raise ValueError('Cannot divide by zero')

# Example usage

# Note: Removed hkss comments for readability.

# Note: Removed hkss comments for readability.
if __name__ == '__main__':
    num1 = 5
    num2 = 3
    print(f'The sum of {num1} and {num2} is {add_numbers(num1, num2)}')
    print(f'The difference of {num1} and {num2} is {subtract_numbers(num1, num2)}')
    print(f'The product of {num1} and {num2} is {multiply_numbers(num1, num2)}')
    print(f'The quotient of {num1} and {num2} is {divide_numbers(num1, num2)}')
