import math
from typing import Union


class Vector:
    """N-мерный математический вектор с поддержкой базовых операций."""

    def __init__(self, *args: Union[int, float]) -> None:
        """
        Создаёт вектор из произвольного набора числовых координат.

        Args:
            *args: Координаты вектора (целые или вещественные числа).
        """
        self.coords = tuple(args)

    def __repr__(self) -> str:
        coords_str = ", ".join(str(c) for c in self.coords)
        return f"Vector({coords_str})"

    def __add__(self, other: "Vector") -> "Vector":
        """
        Покомпонентное сложение двух векторов.

        Args:
            other: Вектор той же размерности.

        Returns:
            Новый вектор — сумма двух векторов.

        Raises:
            ValueError: Если размерности векторов не совпадают.
        """
        if len(self.coords) != len(other.coords):
            raise ValueError("Векторы разной размерности")
        new_coords = tuple(a + b for a, b in zip(self.coords, other.coords))
        return Vector(*new_coords)

    def __mul__(
        self, other: Union[int, float, "Vector"]
    ) -> Union["Vector", float]:
        """
        Умножение вектора на число или на вектор.

        Args:
            other: Число (int/float) или вектор той же размерности.

        Returns:
            Новый вектор при умножении на число; число при умножении на вектор.

        Raises:
            ValueError: Если размерности векторов не совпадают.
            TypeError: Если тип аргумента не поддерживается.
        """
        if isinstance(other, (int, float)):
            return Vector(*(c * other for c in self.coords))
        elif isinstance(other, Vector):
            if len(self.coords) != len(other.coords):
                raise ValueError("Векторы разной размерности")
            return sum(a * b for a, b in zip(self.coords, other.coords))
        raise TypeError("Умножение возможно только на число или вектор")

    @property
    def norm(self) -> float:
        """Евклидова норма (длина) вектора."""
        return math.sqrt(sum(c ** 2 for c in self.coords))
