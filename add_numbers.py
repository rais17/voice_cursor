def add_numbers(a, b):
    assert isinstance(a, (int, float)), 'Input must be a number'
    assert isinstance(b, (int, float)), 'Input must be a number'
    return a + b

# Function to subtract two numbers
# a: first number, should be int or float
# b: second number, should be int or float
# Ensures both inputs are either integers or floats
# Returns the result of subtracting b from a
def subtract_numbers(a, b):
    assert isinstance(a, (int, float)), 'Input must be a number'  # Check if 'a' is a number
    assert isinstance(b, (int, float)), 'Input must be a number'  # Check if 'b' is a number
    return a - b  # Perform subtraction and return the result


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
