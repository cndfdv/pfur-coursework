class Temperature():
    """Temperature class"""

    def __init__(self, celsius: int):
        """Initializes temperature class

        Args:
            celsius (int): temperature in celsius
        """
        self._celsius = celsius

    @property
    def celsius(self) -> int:
        """Getter for celsius temperature

        Returns:
            int: temperature in celsius
        """
        return self._celsius

    @celsius.setter
    def celsius(self, value: int):
        """Setter for celsius temperature

        Args:
            value (int): temperature in celsius
        """
        if isinstance(value, int):
            self._celsius = value
        else:
            raise TypeError("Temperature must be an integer")

    @property
    def fahrenheit(self) -> float:
        """Getter for fahrenheit temperature

        Returns:
            float: temperature in fahrenheit
        """
        return (self._celsius * 9/5) + 32

if __name__ == "__main__":
    temp = Temperature(25)
    print(f"Temperature in Celsius: {temp.celsius}")
    print(f"Temperature in Fahrenheit: {temp.fahrenheit}")

    temp.celsius = 30
    print(f"Updated Temperature in Celsius: {temp.celsius}")
    print(f"Updated Temperature in Fahrenheit: {temp.fahrenheit}")