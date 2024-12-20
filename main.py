import re
from datetime import datetime
import json
import os


class PhoneBookEntry:

    def __init__(self, name, surname, phone, birthdate=None):
        self.name = self.capitalize_first(name)
        self.surname = self.capitalize_first(surname)
        self.phone = self._format_phone(phone)
        self.birthdate = self._validate_date(birthdate) if birthdate else None

    @staticmethod
    def capitalize_first(text):
        """Делает первую букву заглавной"""
        if not text:
            raise ValueError("Имя/Фамилия не может быть пустым")
        if not re.match("^[a-zA-Z0-9 ]+$", text):
            raise ValueError("Разрешены только латинские буквы, цифры и пробелы")
        return text[0].upper() + text[1:].lower()

    @staticmethod
    def _format_phone(phone):
        """Форматирует и проверяет номер телефона"""
        phone = phone.strip().replace('+7', '8')
        if not re.match("^[0-9]{11}$", phone):
            raise ValueError("Номер телефона должен содержать ровно 11 цифр")
        return phone

    @staticmethod
    def _validate_date(date_str):
        """Проверяет формат даты"""
        try:
            return datetime.strptime(date_str, "%d.%m.%Y").strftime("%d.%m.%Y")
        except ValueError:
            raise ValueError("Неверный формат даты. Используйте ДД.ММ.ГГГГ")

    def to_dict(self):
        """Конвертирует запись в словарь для хранения"""
        return {
            'name': self.name,
            'surname': self.surname,
            'phone': self.phone,
            'birthdate': self.birthdate
        }

    @classmethod
    def from_dict(cls, data):
        """Создает запись из словаря"""
        return cls(data['name'], data['surname'], data['phone'], data['birthdate'])


class PhoneBook:

    def __init__(self, filename='phonebook.json'):
        self.filename = filename
        self.entries = []
        self.load_from_file()

    def load_from_file(self):
        """Загружает записи из файла"""
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    self.entries = [PhoneBookEntry.from_dict(entry) for entry in data]
            else:
                # Создает пустой файл, если он не существует
                with open(self.filename, 'w', encoding='utf-8') as file:
                    json.dump([], file)
                self.entries = []
        except json.JSONDecodeError:
            print("Предупреждение: Поврежденный формат файла")
            self.entries = []
            # Создает новый пустой файл
            with open(self.filename, 'w', encoding='utf-8') as file:
                json.dump([], file)

    def save_to_file(self):
        """Сохраняет записи в файл"""
        with open(self.filename, 'w', encoding='utf-8') as file:
            json.dump([entry.to_dict() for entry in self.entries], file, indent=2)

    def add_entry(self, name, surname, phone, birthdate=None):
        """Добавляет новую запись в телефонную книгу"""
        if self.find_entry(name, surname):
            raise ValueError("Запись с таким именем и фамилией уже существует")
        entry = PhoneBookEntry(name, surname, phone, birthdate)
        self.entries.append(entry)
        self.save_to_file()

    def find_entry(self, name=None, surname=None, phone=None, birthdate=None):
        """Ищет записи, соответствующие заданным критериям"""
        results = self.entries[:]
        if name:
            results = [e for e in results if e.name.lower() == name.lower()]
        if surname:
            results = [e for e in results if e.surname.lower() == surname.lower()]
        if phone:
            results = [e for e in results if e.phone == phone]
        if birthdate:
            results = [e for e in results if e.birthdate == birthdate]
        return results

    def delete_entry(self, name, surname):
        """Удаляет запись по имени и фамилии"""
        entries = self.find_entry(name, surname)
        if not entries:
            raise ValueError("Запись не найдена")
        self.entries.remove(entries[0])
        self.save_to_file()

    def update_entry(self, name, surname, new_data):
        """Обновляет существующую запись"""
        entries = self.find_entry(name, surname)
        if not entries:
            raise ValueError("Запись не найдена")
        entry = entries[0]

        if 'name' in new_data:
            entry.name = PhoneBookEntry.capitalize_first(new_data['name'])
        if 'surname' in new_data:
            entry.surname = PhoneBookEntry.capitalize_first(new_data['surname'])
        if 'phone' in new_data:
            entry.phone = PhoneBookEntry._format_phone(new_data['phone'])
        if 'birthdate' in new_data:
            entry.birthdate = PhoneBookEntry._validate_date(new_data['birthdate'])

        self.save_to_file()

    def get_age(self, name, surname):
        """Вычисляет возраст для заданной записи"""
        entries = self.find_entry(name, surname)
        if not entries or not entries[0].birthdate:
            raise ValueError("Запись не найдена или дата рождения не указана")
        birthdate = datetime.strptime(entries[0].birthdate, "%d.%m.%Y")
        today = datetime.now()
        age = today.year - birthdate.year
        if today.month < birthdate.month or (today.month == birthdate.month and today.day < birthdate.day):
            age -= 1
        return age


def main():
    """Обработка консольного интерфейса"""
    phone_book = PhoneBook()

    while True:
        print("\nОперации с телефонной книгой:")
        print("1. Просмотреть все записи")
        print("2. Поиск записей")
        print("3. Добавить новую запись")
        print("4. Удалить запись")
        print("5. Обновить запись")
        print("6. Узнать возраст человека")
        print("7. Выход")

        try:
            choice = input("\nВведите ваш выбор (1-7): ").strip()

            if choice == '1':
                if not phone_book.entries:
                    print("Телефонная книга пуста")
                else:
                    for entry in phone_book.entries:
                        print(f"\nИмя: {entry.name}")
                        print(f"Фамилия: {entry.surname}")
                        print(f"Телефон: {entry.phone}")
                        if entry.birthdate:
                            print(f"Дата рождения: {entry.birthdate}")
                        print("-" * 30)

            elif choice == '2':
                print("\nВведите критерии поиска (нажмите Enter, чтобы пропустить):")
                name = input("Имя: ").strip() or None
                surname = input("Фамилия: ").strip() or None
                phone = input("Телефон: ").strip() or None
                birthdate = input("Дата рождения (ДД.ММ.ГГГГ): ").strip() or None

                results = phone_book.find_entry(name, surname, phone, birthdate)
                if not results:
                    print("Записи не найдены")
                else:
                    for entry in results:
                        print(f"\nИмя: {entry.name}")
                        print(f"Фамилия: {entry.surname}")
                        print(f"Телефон: {entry.phone}")
                        if entry.birthdate:
                            print(f"Дата рождения: {entry.birthdate}")
                        print("-" * 30)

            elif choice == '3':
                print("\nВведите данные новой записи:")
                name = input("Имя: ").strip()
                surname = input("Фамилия: ").strip()
                phone = input("Телефон: ").strip()
                birthdate = input("Дата рождения (ДД.ММ.ГГГГ, необязательно): ").strip() or None

                try:
                    phone_book.add_entry(name, surname, phone, birthdate)
                    print("Запись успешно добавлена")
                except ValueError as e:
                    print(f"Ошибка: {e}")

            elif choice == '4':
                name = input("\nВведите имя: ").strip()
                surname = input("Введите фамилию: ").strip()

                try:
                    phone_book.delete_entry(name, surname)
                    print("Запись успешно удалена")
                except ValueError as e:
                    print(f"Ошибка: {e}")

            elif choice == '5':
                name = input("\nВведите имя записи для обновления: ").strip()
                surname = input("Введите фамилию записи для обновления: ").strip()

                print("\nВведите новые значения (нажмите Enter, чтобы пропустить):")
                new_data = {}
                new_name = input("Новое имя: ").strip()
                if new_name:
                    new_data['name'] = new_name
                new_surname = input("Новая фамилия: ").strip()
                if new_surname:
                    new_data['surname'] = new_surname
                new_phone = input("Новый телефон: ").strip()
                if new_phone:
                    new_data['phone'] = new_phone
                new_birthdate = input("Новая дата рождения (ДД.ММ.ГГГГ): ").strip()
                if new_birthdate:
                    new_data['birthdate'] = new_birthdate

                try:
                    phone_book.update_entry(name, surname, new_data)
                    print("Запись успешно обновлена")
                except ValueError as e:
                    print(f"Ошибка: {e}")

            elif choice == '6':
                name = input("\nВведите имя: ").strip()
                surname = input("Введите фамилию: ").strip()

                try:
                    age = phone_book.get_age(name, surname)
                    print(f"Возраст: {age} лет")
                except ValueError as e:
                    print(f"Ошибка: {e}")

            elif choice == '7':
                print("Выход из программы")
                break

            else:
                print("Неверный выбор. Пожалуйста, введите число от 1 до 7.")

        except Exception as e:
            print(f"Произошла ошибка: {e}")
            continue


if __name__ == "__main__":
    main()
