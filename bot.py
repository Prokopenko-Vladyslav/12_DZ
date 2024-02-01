import sys
from typing import List
from main import Record, AddressBook, Name, Phone, Birthday
from datetime import datetime
import pickle


address_book = AddressBook()


# для збереження у файлу
def save_to_file(filename):
    try:
        with open(filename, 'wb') as file:
            pickle.dump(address_book.data, file)
    except IOError:
        print("Помилка: не вдалося зберегти адресну книгу.")


# для завантаження з файлу
def load_from_file(filename):
    try:
        with open(filename, 'rb') as file:
            address_book.data = pickle.load(file)
        print("Адресна книга успішно завантажена.")
    except (IOError, pickle.UnpicklingError):
        print("Помилка: не вдалося завантажити адресну книгу.")


def input_error(func):
    def wrapper(*args):
        try:
            return func(*args)
        except KeyError:
            return "Enter user name"
        except ValueError:
            return "Give me name and phone please"
        except IndexError:
            return "Invalid input"
    return wrapper


# Функция для додавання нового контакту
@input_error
def add_contact(name: str, phones: List[str]) -> str:
    # Створюємо екземпляр запису
    name_field = Name(name)
    record = Record(name_field)

    for phone in phones:
        phone_field = Phone(phone)
        phone_field.value = phone   # setter
        record.add_phone(phone_field)

    # Додаємо запис в адресну книгу
    address_book.add_record(record)
    return "Contact added"


@input_error
def change_contact(name: str, old_phone: str, new_phone: str) -> str:
    record = address_book.data.get(name)
    if not record:
        return "Contact not found"

    for phone in record.phones:
        if phone.value == old_phone:
            phone.value = new_phone
            return "Phone number updated"

    return "Old phone number not found for the contact"


@input_error
def phone_number(name: str) -> str:
    record = address_book.data.get(name)
    if record:
        phones = record.phones
        if phones:
            return phones[0]
    return "Phone number not found"


# Функция для установки дня рождения у контакта
@input_error
def set_birthday(name: str, birthday: Birthday) -> str:
    record = address_book.data.get(name)
    if not record:
        return "Contact not found"
    try:
        birthday_date_str = birthday.value.strftime("%d-%m-%Y")
        birthday_date = datetime.strptime(birthday_date_str, "%d-%m-%Y").date()
        birthday_field = Birthday(birthday_date)
        record.set_birthday(birthday_field)
        return "Birthday set"
    except ValueError:
        return f"Invalid date format. Please use the format: DD-MM-YYYY. Birthday: {birthday.value}"


def show_all() -> str:
    if not address_book.data:
        return "No contacts found"
    output = ""
    for name, record in address_book.data.items():
        phones = [phone.value for phone in record.phones]  # Получаем все значения номеров телефонов
        phones_str = ", ".join(phones)  # Преобразуем список в строку с разделителем ", "
        birthday_info = ""
        if record.birthday:
            days_to_birthday = record.days_to_birthday()
            if days_to_birthday == 0:
                birthday_info = " (Today is their birthday!)"
            elif days_to_birthday > 0:
                birthday_info = f" ({days_to_birthday} days until their birthday)"
            else:
                birthday_info = f" (Their birthday has already passed)"
        output += f"{name}: {phones_str}{birthday_info}\n"
    return output


def exit_bot() -> None:
    print("Good bye!")
    sys.exit()


def execute_command(command: str) -> str:
    action = command.split()
    if action[0].lower() == 'hello':
        return "How can I help you?"
    elif action[0].lower() == 'add':         # add_contact, change_contact phone_number, show_all, 
        if len(action) < 3:
            return "Missing input"
        name = action[1]
        phones = action[2:]
        return add_contact(name, phones)
    elif action[0].lower() == 'change':
        if len(action) < 4:
            return "Missing input"
        name = action[1]
        old_phone = action[2]
        new_phone = action[3]
        return change_contact(name, old_phone, new_phone)
    elif action[0].lower() == 'phone':
        if len(action) < 2:
            return "Missing input"
        name = action[1]
        return phone_number(name)
    elif len(action) >= 2 and action[0].lower() == "show" and action[1].lower() == "all":
        return show_all()
    elif action[0].lower() == "birthday":
        if len(action) < 3:
            return "Missing input"
        name = action[1]
        birthday_str = action[2]
        try:
            birthday = datetime.strptime(birthday_str, "%d-%m-%Y").date()
            birthday_field = Birthday(birthday)
            return set_birthday(name, birthday_field)
        except ValueError:
            return "Invalid date format. Please use the format: DD-MM-YYYY"    
    elif len(action) == 2 and action[0].lower() == 'good' and action[1].lower() == 'bye':
        return exit_bot()
    elif len(action) == 1 and action[0].lower() in ['close', 'exit']:
        return exit_bot()
    else:
        return "Command not recognized."


def main() -> None:
    print("Welcome to the assistant bot!")
    load_from_file("address_book.json")  # Загрузка книги контактів з файлу
    while True:
        command = input("Enter command: ")
        response = execute_command(command)
        print(response)
        save_to_file("address_book.json")  # Запись в книгу контактів після обробки кождої команди


if __name__ == "__main__":
    main()
