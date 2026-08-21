class BankAccount():
    """A simple bank account class."""

    def __init__(self, starting_balance: int=0):
        """Initializes bank account

        Args:
            starting_balance (int, optional): bank accaunt balance. Defaults to 0.
        """
        self._balance = starting_balance
        self._transactions = []

    def deposit(self, amount: int) -> None:
        """Deposits amount to the bank account

        Args:
            amount (int): amount to deposit
        """
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self._balance += amount
        self._transactions.append(f"Deposited: {amount}")
    
    def withdraw(self, amount: int) -> None:
        """Withdraws amount from the bank account

        Args:
            amount (int): amount to withdraw
        """
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > self._balance:
            raise ValueError("Dont have enough money")

        self._balance -= amount
        self._transactions.append(f"Withdrew: {amount}")
    
    @property
    def balance(self) -> int:
        """Returns the current balance of the bank account

        Returns:
            int: current balance
        """
        return self._balance

    def get_transactions(self) -> list:
        """Returns the list of transactions

        Returns:
            list: list of transactions
        """
        return self._transactions


if __name__ == "__main__":
    account = BankAccount(1000)
    account.deposit(500)
    account.withdraw(200)
    print(f"Current balance: {account.balance}")
    print("Transactions:")
    for transaction in account.get_transactions():
        print(transaction)
    account.withdraw(2000)  
    account.balance