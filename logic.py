from PyQt6.QtWidgets import *
from gui import *
import csv
import os


#add account number input box (done)
#if pin is invalid, display a clearer message (done)
#create a unique account number so 2 people can have the same pin and same name but have a different account number (done)
#create a new input field for the account number, rename the pin box to the account number then create a new box for the pin logic (done)
#add type hinting and docstrings, no need for a test case file(done)

class Logic(QMainWindow, Ui_mainWindow):
    def __init__(self) -> None:
        """
        Initialize the Logic class, setting up the UI and connecting signals to slots.
        """
        super().__init__()

        self.setupUi(self)
        self.create_acc_button.clicked.connect(lambda: self.acc_create())
        self.login_button.clicked.connect(lambda: self.login())

        self.enter_button.clicked.connect(self.enter_logic)
        self.exit_button.clicked.connect(self.exit_logic)

        self.__first_entry = self.first_entry
        self.__last_entry = self.last_entry
        self.__account_num_entry = self.account_num_entry
        self.__pin_entry = self.pin_entry
        self.__amount_entry = self.amount_entry
        self.__balance = None

    def get_first(self) -> str:
        """
        Get the first name entered by the user.

        Returns:
            str: The first name in lowercase and stripped of whitespace.
        """
        return self.__first_entry.text().lower().strip()

    def get_last(self) -> str:
        """
        Get the last name entered by the user.

        Returns:
            str: The last name in lowercase and stripped of whitespace.
        """
        return self.__last_entry.text().lower().strip()

    def get_account_num(self) -> str:
        """
        Get the account number entered by the user.

        Returns:
            str: The account number stripped of whitespace.
        """
        return self.__account_num_entry.text().strip()

    def get_pin(self) -> str:
        """
        Get the PIN entered by the user.

        Returns:
            str: The PIN stripped of whitespace.
        """
        return self.__pin_entry.text().strip()

    def get_balance(self) -> float | None:
        """
        Get the current balance of the user's account.

        Returns:
            float | None: The current balance or None if not set.
        """
        return self.__balance

    def set_balance(self, balance: float) -> None:
        """
        Set the current balance of the user's account.

        Args:
            balance (float): The balance to set.
        """
        self.__balance = balance

    def acc_create(self) -> None:
        """
        Creates a new account with the provided details and initial balance.
        """
        initial_balance = 100
        csv_file = 'data.csv'
        file_exists = os.path.isfile(csv_file)

        try:
            if self.get_first() == '' or self.get_last() == '' or self.get_account_num() == '' or self.get_pin() == '':
                raise ValueError("All fields must be filled.")
            elif len(self.get_account_num()) != 4 or len(self.get_pin()) != 4:
                raise ValueError("Account number and PIN must be 4 digits")

            if file_exists:
                with open(csv_file, 'r') as infile:
                    reader = csv.reader(infile)
                    for row in reader:
                        if len(row) < 5:
                            continue  #verifies only rows that have the length expectations are read
                        if row[0] == self.get_first() and row[1] == self.get_last() and row[
                            2] == self.get_account_num():
                            raise ValueError("Account already exists, please login.")
                        elif row[2] == self.get_account_num():
                            raise ValueError("Account number is already taken, please choose another.")

            with open(csv_file, 'a', newline='') as infile:
                writer = csv.writer(infile)
                if not file_exists:
                    writer.writerow(['First', 'Last', 'Account#', 'PIN', 'Balance'])
                writer.writerow(
                    [self.get_first(), self.get_last(), self.get_account_num(), self.get_pin(), initial_balance])
                self.status_label.setText('Account created! Please log in.')

        except ValueError as e:
            self.status_label.setWordWrap(True)
            self.status_label.setText(str(e))

    def login(self) -> None:
        """
        Handle the user login process by verifying the account details.
        """
        first_name = self.get_first()
        last_name = self.get_last()
        account_num = self.get_account_num()
        pin = self.get_pin()
        csv_file = 'data.csv'
        file_exists = os.path.isfile(csv_file)

        self.withdraw_button.setChecked(False)
        self.deposit_button.setChecked(False)

        try:
            if first_name == '' or last_name == '' or account_num == '' or pin == '':
                raise ValueError("All fields must be filled.")
            if not os.path.isfile(csv_file):
                raise ValueError("No accounts exist yet. Please create an account proceed.") #shows if csv file hasn't been created yet
            account_num = int(account_num)
            pin = int(pin)
            account_found = False
            incorrect_pin = False
            with open('data.csv', 'r', newline='') as infile:
                reader = csv.reader(infile)
                for row in reader:
                    if row[0].lower() == first_name and row[1].lower() == last_name and int(row[2]) == account_num:
                        account_found = True
                        if int(row[3]) == pin:
                            self.set_balance(float(row[4]))
                            self.status_label.setText(f'Welcome {first_name.capitalize()}!')
                            self.action_label.setVisible(True)
                            self.withdraw_button.setChecked(False)
                            self.deposit_button.setChecked(False)
                            self.withdraw_button.setVisible(True)
                            self.deposit_button.setVisible(True)
                            self.appear()
                            return  # login succesful
                        else:
                            incorrect_pin = True
                            break  #if code reaches here, then it means you have the wrong pin
            if incorrect_pin:
                raise ValueError("Incorrect PIN, please try again.")
            elif not account_found:
                raise ValueError(
                    "No account found with those details. Please verify account number and other details are correct.")
        except ValueError as e:
            self.status_label.setWordWrap(True)
            self.status_label.setText(str(e))

    def appear(self) -> None:
        """
        Display the account details and options after a successful login.
        """
        self.amount_label.setVisible(True)
        self.amount_entry.setVisible(True)
        self.acc_details.setVisible(True)
        self.acc_details.setText(f'Your current balance: ${self.get_balance():.2f}')
        self.enter_button.setVisible(True)
        self.exit_button.setVisible(True)

    def enter_logic(self) -> None:
        """
        Handle the logic for withdrawals and deposits based on user input.
        """
        amount_text = self.__amount_entry.text()
        if self.withdraw_button.isChecked():
            self.appear()
            try:
                amount = float(amount_text)
                if amount > self.get_balance():
                    raise ValueError("Insufficient funds")

                if amount <= 0:
                    raise ValueError("Withdrawal amount must be positive")

                self.set_balance(self.get_balance() - amount)
                self.update_csv(self.get_first(), self.get_last(), self.get_account_num(), self.get_pin(),
                                self.get_balance())
                self.acc_details.setWordWrap(True)
                self.acc_details.setText(f'You withdrew: ${amount:.2f}. '
                                         f'                          Your new balance is: ${self.get_balance():.2f}')
            except ValueError as e:
                self.status_label.setText(str(e))

        elif self.deposit_button.isChecked():
            self.appear()
            try:
                amount = float(amount_text)
                if amount <= 0:
                    raise ValueError("Deposit amount must be positive")

                self.set_balance(self.get_balance() + amount)
                self.update_csv(self.get_first(), self.get_last(), self.get_account_num(), self.get_pin(),
                                self.get_balance())
                self.acc_details.setWordWrap(True)
                self.acc_details.setText(f'You deposited: ${amount:.2f}. '
                                         f'                          Your new balance is: ${self.get_balance():.2f}')
            except ValueError as e:
                self.status_label.setText(str(e))

        self.withdraw_button.setChecked(False)
        self.deposit_button.setChecked(False)

    def update_csv(self, first_name: str, last_name: str, account_num: str, pin: str, new_balance: float) -> None:
        """
        Update the CSV file with the new balance after a transaction.

        Args:
            first_name (str): The user's first name.
            last_name (str): The user's last name.
            account_num (str): The user's account number.
            pin (str): The user's PIN.
            new_balance (float): The new balance to update in the file.
        """
        csv_file = 'data.csv'
        rows = []

        with open(csv_file, 'r', newline='') as infile:
            reader = csv.reader(infile)
            for row in reader:
                if row[0].lower() == first_name.lower() and row[1].lower() == last_name.lower() and row[2] == str(
                        account_num) and row[3] == str(pin):
                    row[4] = new_balance
                rows.append(row)

        with open(csv_file, 'w', newline='') as outfile:
            writer = csv.writer(outfile)
            writer.writerows(rows)

    def exit_logic(self) -> None:
        """
        Clear all inputs and reset the UI after the user exits.
        """
        self.first_entry.clear()
        self.last_entry.clear()
        self.account_num_entry.clear()
        self.pin_entry.clear()
        self.amount_entry.clear()
        self.status_label.setText('Please create an account or log in.')
        self.withdraw_button.setChecked(False)
        self.deposit_button.setChecked(False)
        self.action_label.setVisible(False)
        self.withdraw_button.setChecked(False)
        self.deposit_button.setChecked(False)
        self.withdraw_button.setVisible(False)
        self.deposit_button.setVisible(False)
        self.enter_button.setVisible(False)
        self.exit_button.setVisible(False)
        self.amount_label.setVisible(False)
        self.amount_entry.setVisible(False)
        self.acc_details.setVisible(False)
