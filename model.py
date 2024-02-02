from collections import UserDict
from datetime import datetime, date


class Field:
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self.validate(new_value)
        self._value = new_value

    def validate(self, value):
        pass


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
            raise ValueError


class Birthday(Field):
    def validate(self, value):
        # Перевіряємо, що значення є допустимою датою
        if not isinstance(value, str):
            raise ValueError("Invalid date format. Please use the format: DD-MM-YYYY")
        try:
            datetime.strptime(value, "%d-%m-%Y")
        except ValueError:
            raise ValueError("Invalid date format. Please use the format: DD-MM-YYYY")


class Record:
    def __init__(self, name: Name, birthday: Birthday = None):
        self.name = name
        self.phones = []
        self.birthday = None
        if birthday:
            self.birthday = birthday.value

    def add_phone(self, phone: Phone):
        self.phones.append(phone)

    def remove_phone(self, phone: Phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone: Phone, new_phone: Phone):
        phone_found = False
        for phone in self.phones:
            if phone.value == old_phone:
                phone.value = new_phone
                phone_found = True
                break
        if not phone_found:
            raise ValueError("Phone number not found for editing.")

    def find_phone(self, phone: Phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    @property
    def birthday(self):
        return self._birthday

    @birthday.setter
    def birthday(self, new_birthday):
        if new_birthday is None:
            self._birthday = None
        else:
            self._birthday = new_birthday

    def days_to_birthday(self, birthday: Birthday):
        if self.birthday is None:
            return -1

        today = date.today()
        next_birthday = date(today.year, self.birthday.month, self.birthday.day)

        if today > next_birthday:
            next_birthday = date(today.year + 1, self.birthday.month, self.birthday.day)

        days_until_birthday = (next_birthday - today).days
        return days_until_birthday


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

    def paginate(self, page_size):
        records = list(self.data.values())
        total_records = len(records)
        num_pages = (total_records + page_size - 1) // page_size

        for page in range(num_pages):
            start_index = page * page_size
            end_index = (page + 1) * page_size
            yield [(record.name.value, record) for record in records[start_index:end_index]]