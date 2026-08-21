class MathOps:
    @staticmethod
    def add(a, b):
        print(a + b)

    @staticmethod
    def subtract(a, b):
        print(a - b)

    @staticmethod
    def multiply(a, b):
        print(a * b)

    @staticmethod
    def divide(a, b):
        if b == 0:
            raise ValueError("Division by zero is not allowed.")
        else:    
            print(a / b)