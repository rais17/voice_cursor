

def add_numbers(a, b):
    assert isinstance(a, (int, float)), 'Input must be a number'
    assert isinstance(b, (int, float)), 'Input must be a number'


def subtract_numbers(a, b):
    assert isinstance(a, (int, float)), 'Input must be a number'


def multiply_numbers(a, b):
    assert isinstance(a, (int, float)), 'Input must be a number'
    assert isinstance(a, (int, float)), 'Input must be a number'

def divide_numbers(a, b):
    assert isinstance(a, (int, float)), 'Input must be a number'
    assert isinstance(b, (int, float)), 'Input must be a number'
    if b != 0:
        return a / b
    else:
        raise ValueError('Cannot divide by zero')

if __name__ == '__main__':
    num1 = 5
    num2 = 3
    print(f'The quotient of {num1} and {num2} is {divide_numbers(num1, num2)}')
