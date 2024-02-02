import sys
from typing import List
from model import Record, AddressBook, Name, Phone, Birthday
from datetime import datetime
import pickle


address_book = AddressBook()


# Для збереження у файлу
def save_to_file(filename):
    try:
        with open(filename, 'wb') as file:
            pickle.dump(address_book.data, file)
    except IOError:
        print("Error: Failed to save address book.")  # Помилка: не вдалося зберегти адресну книгу.
 

# Для завантаження з файлу
def load_from_file(filename):
    try:
        with open(filename, 'rb') as file:
            address_book.data = pickle.load(file)
        print("Address book loaded successfully.")  # Адресна книга успішно завантажена.
    except (IOError, pickle.UnpicklingError):
        print("Error: Failed to load address book.")   # Помилка: не вдалося завантажити адресну книгу.


# Декоратор для обработки помилок
def input_error(func):
    def wrapper(*args):
        try:
            return func(*args)
        except KeyError:
            return "Contact not found"
        except ValueError:
            return "Invalid input"
        except IndexError:
            return "Missing input"
    return wrapper


# Функция для додавання нового контакту
@input_error
def add_contact(name: str, phones: List[str]) -> str:
    # Зтворюємо екземпляр запису
    name_field = Name(name)
    record = Record(name_field)

    for phone in phones:
        phone_field = Phone(phone)
        phone_field.value = phone   # setter
        record.add_phone(phone_field)

    # Додаємо запис в адресну книгу
    address_book.add_record(record)
    return "Contact added"


# Змінити номер телефону у вже існуючого контакту
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


# Функция для пошуку номера телефону по імені контакту
@input_error
def phone_number(name: str) -> str:
    record = address_book.data.get(name)
    if record:
        phones = record.phones
        if phones:
            return phones[0]
    return "Phone number not found"


# Функция для встановлення дня народження
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
        phones = [phone.value for phone in record.phones] 
        phones_str = ", ".join(phones)  # Перетворимо список у рядок з роздільником ","
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


# Функція для пагінації контактів
def paginate_contacts(page_size: int) -> str:
    output = ""
    for page in address_book.paginate(page_size):
        for name, record in page:
            phones = [phone.value for phone in record.phones]
            phones_str = ", ".join(phones)
            if record.birthday:
                birthday = record.birthday.strftime("%d-%m-%Y")
                output += f"{name}: {phones_str}(Birthday: {birthday})\n"
            else:
                output += f"{name}: {phones_str}\n"
        output += "---\n"
    return output


# Функція для пошуку за збігом
def search_contacts(query):
    matching_contacts = []
    for record in address_book.data.values():
        name = record.name.value
        phone_numbers = [phone.value for phone in record.phones]
        if query in name or any(query in number for number in phone_numbers):
            matching_contacts.append(record)

    if len(matching_contacts) == 0:
        return "No matching contacts found."

    output = ""
    for record in matching_contacts:
        name = record.name.value
        phones = ", ".join(phone.value for phone in record.phones)
        output += f"Name: {name}\nPhone Numbers: {phones}\n\n"

    return output


def exit_bot() -> None:
    print("Good bye!")
    sys.exit()


def execute_command(command: str) -> str:
    action = command.split()
    if action[0].lower() == 'hello':
        return "How can I help you?"
    elif action[0].lower() == 'add':
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
    elif len(action) >= 2 and action[0].lower() == 'good' and action[1].lower() == 'bye':
        return exit_bot()
    elif len(action) == 1 and action[0].lower() in ['close', 'exit']:
        return exit_bot()
    elif action[0].lower() == "paginate":
        if len(action) < 2:
            return "Missing input"
        page_size = int(action[1])
        return paginate_contacts(page_size)

    elif action[0].lower() == "search":
        if len(action) < 2:
            return "Missing input"
        search_query = " ".join(action[1:])
        search_result = search_contacts(search_query)
        return search_result
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
