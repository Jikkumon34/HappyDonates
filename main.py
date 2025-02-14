from pathlib import Path

def edit_balance(user_data, new_balance):
    user_data[2] = str(int(user_data[2]) + new_balance)

def main():
    filepath = "E:\\Programming\\Python\\Task\\ATMBasicL1\\ATMdata.txt"
    user_id = input("Enter Your ATM ID: ")
    user_pin = input("Enter Your ATM PIN: ")

    with open(filepath) as emp:
        contents = emp.readlines()

    found_user = next((user_data.split("-") for user_data in contents if user_id == user_data.split("-")[0] and user_pin == user_data.split("-")[1]), None)

    if found_user:
        i = contents.index(found_user)
        amount = int(found_user[2])

        choice = int(input("1: WITHDRAW\n2: CASH DEPOSIT\n3: BALANCE\nCHOICE: "))

        if choice == 1:
            withdraw = int(input("Enter the Amount to Withdraw: "))
            if amount - withdraw >= 0:
                edit_balance(found_user, -withdraw)
            else:
                print(f"Insufficient Balance: {amount}")
        elif choice == 2:
            deposit = int(input("Enter the Amount to Deposit: "))
            edit_balance(found_user, deposit)
        elif choice == 3:
            print(f"Balance is: {amount}")
        else:
            return

        print(f"Updated Balance is: {amount}")
    else:
        print("INVALID ATM ID OR ATM PIN")

if __name__ == "__main__":
    main()
