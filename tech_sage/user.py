import re
import pickle
import hashlib
from pathlib import Path
from collections import UserDict
from rich.table import Table
from rich.console import Console


def generate_filename(username):
    hasher = hashlib.md5()
    hasher.update(username.encode("utf-8"))
    return f"address_book_{hasher.hexdigest()}.pkl"

class User:
    def __init__(self, name, username, password, email):
        self.name = name
        self.username = username
        self.password_hash = self.hash_password(password)
        self.email = email

    def hash_password(self, password):
        hasher = hashlib.sha256()
        hasher.update(password.encode('utf-8'))
        return hasher.hexdigest()

    def check_password(self, password):
        return self.password_hash == self.hash_password(password)

    def create_personal_file(self):
        filename = generate_filename(self.username)
        if not Path(filename).exists():
            with open(filename, 'wb') as file:
                pickle.dump({}, file)
        return filename

    def __str__(self) -> str:
        return f"user(name={self.name.value}, username={self.username})"


class UserRegistration:
    def __init__(self):
        self.users = []

    def register_user(self):
        name = self.get_valid_name()
        username = self.get_unique_username()
        password = self.get_valid_password()
        email = self.get_unique_email()

        user = User(name, username, password, email)
        self.users.append(user)
        self.save_user_data(user)
        print("Реєстрація успішна!")

    def save_user_data(self, user):
        with open('user_data.pkl', 'wb') as file:
            pickle.dump(self.users, file)

    def get_valid_name(self):
        while True:
            name = input("Введіть ваше ім'я: ").strip().capitalize()
            if re.match(r'^[А-Яа-яA-Za-z\s]+$', name):
                return name
            elif " " in name:
                print("Username не може містити пробіли.")
            else:
                print("Некоректне ім'я. Введіть лише літери української або англійської абеток.")

    def get_unique_username(self):
        while True:
            username = input("Введіть бажаний username: ")
            if " " in username:
                print("Username не може містити пробіли.")
            elif self.is_username_taken(username):
                print("Username вже зайнятий. Введіть інший username.")
            else:
                return username


    def is_username_taken(self, username):
        for user in self.users:
            if user.username == username:
                return True
        return False




    def get_valid_password(self):
        while True:
            password = input("Введіть бажаний пароль: ")
            if len(password) < 10:
                print("Пароль повинен містити щонайменше 10 символів.")
            elif not any(char.isupper() for char in password):
                print("Пароль повинен містити щонайменше одну літеру верхнього регістру.")
            elif not any(char.isdigit() for char in password):
                print("Пароль повинен містити щонайменше одну цифру.")
            elif re.search(r'[^a-zA-Z0-9_]', password):
                print("Пароль не повинен містити спеціальних символів.")
            else:
                return password

    def get_unique_email(self):
        while True:
            email = input("Введіть вашу електронну пошту: ")
            if self.is_email_taken(email):
                print("Електронна пошта вже зареєстрована. Введіть іншу електронну пошту.")
            else:
                return email

    def is_email_taken(self, email):
        for user in self.users:
            if user.email == email:
                return True
        return False




class UserBook(UserDict):
    record_id = None

    def __init__(self, owner_username):
        self.file = generate_filename(owner_username)
        self.data ={}
        self.record_id = 0
        self.record = {}
        self.load()
        super().__init__()

    def dump(self):
        with open(self.file, "wb") as file:
            pickle.dump((self.record_id, dict(self.data)), file)

    def load(self):
        file_path = Path(self.file)
        if not file_path.exists():
            return
        with open(self.file, "rb") as file:
            self.record_id, data = pickle.load(file)
            self.data.update(data)

    def authenticate_user(self, username, password):
        if username not in self.data:
            return False
        return self.data[username].check_password(password)


class Controller:
    def __init__(self):
        self.registration = UserRegistration()
        self.book = UserBook(owner_username="Grigo")

    def do_exit(self):
        self.book.dump()
        print("Данні користувачів збережено! Вихід...")
        return True

    def do_save(self):
        self.book.dump()
        print("Данні користувачів збережено!")

    def do_load(self):
        self.book.load()
        print("Данні користувачів відновлено")

    def do_add_user(self):
        self.registration.register_user()

    # def do_add_user(self, name, username, password):
    #     user = User(name, username, password)
    #     user.create_personal_file()
    #     self.book.add_user(user)
    #     self.view.render(f"Користувача {username} успішно зареєстровано")

    def do_enter(self, username, password):
        if self.book.authenticate_user(username, password):
            print(f"Користувача {username} успішно ідентифіковано")
        else:
            print("Помилка індитифікації")

 

    def do_list_book(self):
        if not self.book.data:
            print("Адресна книга порожня.")
        else:
            # Створюємо об’єкт таблиці з необхідними заголовками
            table = Table(show_header=True, header_style="bold violet", border_style="bold magenta")
            table.add_column("User", style="dim", width=12)  # Додаємо заголовок User
            table.add_column("Username", style="dim", width=12)  # Додаємо заголовок Username
            table.add_column("Email", style="dim", width=20)    # Додаємо заголовок Email

            # Додаємо рядки з інформацією користувачів
            for record in self.book.data.values():
                table.add_row(record.name, record.username, record.email)  # Змінено звертання до атрибутів
                
            print(table)  # Виводимо таблицю


controller = Controller()

while True:
    command = input("Введіть команду (add_user, enter): ")
    if command == "add_user":
        controller.do_add_user()
    elif command == "enter":
        controller.do_enter()
    elif command == "list_book":
        controller.do_list_book()
    elif command == "exit":
        controller.do_exit()
    elif command == "save":
        controller.do_save()
    elif command == "load":
        controller.do_load()
    else:
        print("Невідома команда. Спробуйте ще раз.")
