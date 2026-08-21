import math
from abc import ABC, abstractmethod


class Shape(ABC):
    """Abstract shape class"""

    @abstractmethod
    def area(self):
        """Calculates area of a figure"""
        pass

    @abstractmethod
    def perimeter(self):
        """calculates a perimeter of a figure"""
        pass


class Rectangle(Shape):
    """Reacangle class"""

    def __init__(self, width: int, height: int):
        """IniInitializes rectangle class

        Args:
            width (int): width of rectangle
            height (int): height of rectangle
        """

        self.width = width
        self.height = height

    def area(self) -> int:
        """calculate rectangle area

        Returns:
            int: rectangle area
        """

        return self.width * self.height

    def perimeter(self) -> int:
        """calculate rectangle perimeter

        Returns:
            int: rectangle perimeter
        """

        return (self.width + self.height) * 2

class Circle(Shape):
    """Circle class"""

    def __init__(self, radius: int):
        """IniInitializes circle class

        Args:
            radius (int): circle radius
        """
        self.radius = radius

    def area(self) -> float:
        """calculate circle area

        Returns:
            float: circle area
        """
        return math.pi * self.radius**2

    def perimeter(self) -> float:
        """calculate circle perimeter

        Returns:
            float: circle perimeter
        """
        return 2 * math.pi * self.radius
    
class Triangle(Shape):
    """Triangle class"""

    def __init__(self, a: int, b: int, c: int):
        """IniInitializes triangle class

        Args:
            a (int): a side
            b (int): b side
            c (int): c side
        """
        self.a = a
        self.b = b
        self.c = c

    def area(self) -> float:
        """calculate triangle area

        Returns:
            float: triangle area
        """
        p = self.perimeter() / 2
        return math.sqrt(p * (p - self.a) * (p - self.b) * (p - self.c))
    
    def perimeter(self) -> int:
        """calculate triangle perimeter

        Returns:
            float: triangle perimeter
        """
        return self.a + self.b + self.c

def print_shape_info(shape: Shape):
    """Prints figure info

    Args:
        shape (Shape): a figure to describe
    """
    print(f"Тип фигуры: {type(shape).__name__}")
    print(f"Площадь: {shape.area():.2f}")
    print(f"Периметр: {shape.perimeter():.2f}")
    print()

shapes = [
    Rectangle(5, 10),
    Circle(4),
    Triangle(3, 4, 5)
]

for shape in shapes:
    print_shape_info(shape)