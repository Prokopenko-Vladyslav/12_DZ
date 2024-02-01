from collections import UserDict
from datetime import datetime, date


class Field:
    def __init__(self, value):
        self.__value = None
        self.value = value

    def validate(self, value):
        pass

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        if self.validate(value):
            self.__value = value
        else:
            raise ValueError("Invalid value")


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        super().__init__(Field)
        self.number = value

    def __str__(self):
        return self.number

    def validate(self, value):
        if len(value) != 10 or not value.isdigit():
            raise ValueError("Phone number must contain 10 digits.")


class Birthday(Field):
    def __init__(self, value):
        super().__init__(value)

    def validate(self, value):
        try:
            if value is None:
                return True
            elif datetime.strptime(value, "%Y-%m-%d"):
                return True
        except ValueError:
            raise ValueError("Невірний формат дати. Використовуйте YYYY-MM-DD.")

    def __str__(self):
        return f"{self.value}"


class Record:
    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.phones = []
        self.birthday = Birthday(birthday)
        if birthday:
            self.birthday = birthday.value

    def add_phone(self, phone):
        try:
            phone_number = Phone(phone)
            self.phones.append(phone_number)
        except ValueError as e:
            print(f"Error adding phone: {e}")

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        phone_found = False
        for phone in self.phones:
            if phone.value == old_phone:
                phone.value = new_phone
                phone_found = True
                break
        if not phone_found:
            raise ValueError("Phone number not found for editing.")

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def days_to_birthday(self):
        if not self.birthday:
            return None
        today = date.today()
        birthday_day = datetime.strptime(self.birthday.value, "%Y-%m-%d")
        user_birthday_in_this_year = date(today.year, birthday_day.month, birthday_day.day)
        different = user_birthday_in_this_year - today
        if different.days > 0:
            return f'left until birthday {different.days} days'
        else:
            user_birthday_in_next_year = date(today.year + 1, birthday_day.month, birthday_day.day)
            different_new = user_birthday_in_next_year - today
            return f'left until birthday {different_new.days} days'

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"


class RecordIterator:
    def __init__(self, records):
        self.records = records
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index >= len(self.records):
            raise StopIteration
        record = self.records[self.index]
        self.index += 1
        return record


class AddressBook(UserDict):
    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def __iter__(self):
        return RecordIterator(list(self.data.values()))

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
        else:
            print(f"Record with name '{name}' not found.")

    def iterator(self, batch_size):
        records = list(self.data.values())
        for i in range(0, len(records), batch_size):
            yield records[i:i + batch_size]
