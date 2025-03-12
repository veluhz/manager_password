import os
import sqlite3
import bcrypt
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QListWidget, QDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QClipboard


# Глобальные настройки
DATABASE_NAME = "password_manager.db"
SALT_LENGTH = 16
ITERATIONS = 100_000
KEY_LENGTH = 32  # AES-256


# Инициализация базы данных
def initialize_database():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash BLOB NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS passwords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            service_name TEXT NOT NULL,
            encrypted_password BLOB NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    conn.commit()
    conn.close()


# Хэширование пароля с использованием bcrypt
def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())


# Проверка пароля
def verify_password(password: str, hashed_password: bytes) -> bool:
    return bcrypt.checkpw(password.encode(), hashed_password)


# Генерация ключа шифрования из мастер-пароля
def derive_key(master_password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_LENGTH,
        salt=salt,
        iterations=ITERATIONS,
        backend=default_backend()
    )
    return kdf.derive(master_password.encode())


# Шифрование данных
def encrypt_data(key: bytes, data: str) -> bytes:
    iv = os.urandom(16)  # Генерация случайного IV
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted = encryptor.update(data.encode()) + encryptor.finalize()
    return base64.b64encode(iv + encrypted)


# Дешифрование данных
def decrypt_data(key: bytes, encrypted_data: bytes) -> str:
    encrypted_data = base64.b64decode(encrypted_data)
    iv = encrypted_data[:16]
    ciphertext = encrypted_data[16:]
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted = decryptor.update(ciphertext) + decryptor.finalize()
    return decrypted.decode()


# Регистрация нового пользователя
def register_user(username: str, master_password: str):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        hashed_password = hash_password(master_password)
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        print(f"Пользователь '{username}' успешно зарегистрирован.")
    except sqlite3.IntegrityError:
        print("Ошибка: Пользователь с таким именем уже существует.")
    finally:
        conn.close()


# Авторизация пользователя
def authenticate_user(username: str, master_password: str) -> tuple[bool, int]:
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()

    if result:
        user_id, hashed_password = result
        if verify_password(master_password, hashed_password):
            return True, user_id
    return False, None


# Добавление пароля в хранилище
def add_password(user_id: int, service_name: str, password: str, master_password: str):
    salt = os.urandom(SALT_LENGTH)  # Генерация случайной соли
    key = derive_key(master_password, salt)
    encrypted_password = encrypt_data(key, password)

    # Сохраняем соль вместе с зашифрованным паролем
    combined_data = base64.b64encode(salt + encrypted_password)

    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO passwords (user_id, service_name, encrypted_password)
        VALUES (?, ?, ?)
    """, (user_id, service_name, combined_data))
    conn.commit()
    conn.close()
    print(f"Пароль для сервиса '{service_name}' успешно добавлен.")


# Получение пароля из хранилища
def get_password(user_id: int, service_name: str, master_password: str) -> str:
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT encrypted_password FROM passwords
        WHERE user_id = ? AND service_name = ?
    """, (user_id, service_name))
    result = cursor.fetchone()
    conn.close()

    if not result:
        print("Ошибка: Пароль для данного сервиса не найден.")
        return None

    combined_data = base64.b64decode(result[0])
    salt = combined_data[:SALT_LENGTH]  # Извлекаем соль
    encrypted_password = combined_data[SALT_LENGTH:]  # Извлекаем зашифрованный пароль

    try:
        key = derive_key(master_password, salt)
        decrypted_password = decrypt_data(key, encrypted_password)
        return decrypted_password
    except Exception as e:
        print("Ошибка при дешифровании пароля:", e)
        return None


# Диалог просмотра пароля
class PasswordDialog(QDialog):
    def __init__(self, service_name, password, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Пароль для {service_name}")
        self.setGeometry(200, 200, 400, 150)

        layout = QVBoxLayout()

        # Отображение пароля
        self.password_label = QLineEdit(password)
        self.password_label.setEchoMode(QLineEdit.Password)  # Скрываем пароль
        layout.addWidget(self.password_label)

        # Кнопка "Показать/Скрыть"
        self.show_password_button = QPushButton("Показать пароль")
        self.show_password_button.setCheckable(True)
        self.show_password_button.clicked.connect(self.toggle_password_visibility)
        layout.addWidget(self.show_password_button)

        # Кнопка "Скопировать"
        copy_button = QPushButton("Скопировать пароль")
        copy_button.clicked.connect(lambda: self.copy_to_clipboard(password))
        layout.addWidget(copy_button)

        self.setLayout(layout)

    def toggle_password_visibility(self):
        """Переключает видимость пароля."""
        if self.show_password_button.isChecked():
            self.password_label.setEchoMode(QLineEdit.Normal)
            self.show_password_button.setText("Скрыть пароль")
        else:
            self.password_label.setEchoMode(QLineEdit.Password)
            self.show_password_button.setText("Показать пароль")

    def copy_to_clipboard(self, password):
        """Копирует пароль в буфер обмена."""
        clipboard = QApplication.clipboard()
        clipboard.setText(password)
        QMessageBox.information(self, "Успех", "Пароль скопирован в буфер обмена.")


# Главное окно приложения
class PasswordManagerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Менеджер паролей")
        self.setGeometry(100, 100, 400, 300)

        # Загрузка стилей
        with open("styles.qss", "r") as f:
            self.setStyleSheet(f.read())

        # Инициализация базы данных
        initialize_database()

        # Текущий пользователь и мастер-пароль
        self.current_user_id = None
        self.master_password = None

        # Показать экран авторизации
        self.show_login_screen()

    def show_login_screen(self):
        """Показывает экран авторизации/регистрации."""
        self.login_screen = QWidget()
        layout = QVBoxLayout()

        # Заголовок
        title = QLabel("Авторизация/Регистрация")
        title.setObjectName("Title")  # Для стилизации через QSS
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Поле для имени пользователя
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Имя пользователя")
        layout.addWidget(self.username_input)

        # Поле для мастер-пароля
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Мастер-пароль")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        # Кнопка "Войти"
        login_button = QPushButton("Войти")
        login_button.setIcon(QIcon("icons/lock.png"))  # Убедитесь, что файл lock.png находится в папке icons
        login_button.clicked.connect(self.login)
        layout.addWidget(login_button)

        # Кнопка "Зарегистрироваться"
        register_button = QPushButton("Зарегистрироваться")
        register_button.setIcon(QIcon("icons/register.png"))
        register_button.clicked.connect(self.register)
        layout.addWidget(register_button)

        self.login_screen.setLayout(layout)
        self.setCentralWidget(self.login_screen)

    def login(self):
        """Обработка входа пользователя."""
        username = self.username_input.text()
        master_password = self.password_input.text()

        success, user_id = authenticate_user(username, master_password)
        if success:
            self.current_user_id = user_id
            self.master_password = master_password
            self.show_main_screen()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверное имя пользователя или мастер-пароль.")

    def register(self):
        """Обработка регистрации нового пользователя."""
        username = self.username_input.text()
        master_password = self.password_input.text()

        try:
            register_user(username, master_password)
            QMessageBox.information(self, "Успех", "Пользователь успешно зарегистрирован.")
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Ошибка", "Пользователь с таким именем уже существует.")

    def show_main_screen(self):
        """Показывает главное окно после входа."""
        self.main_screen = QWidget()
        layout = QVBoxLayout()

        # Заголовок
        title = QLabel("Главное меню")
        title.setObjectName("Title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Кнопка "Добавить пароль"
        add_password_button = QPushButton("Добавить пароль")
        add_password_button.setIcon(QIcon("icons/add.png"))
        add_password_button.clicked.connect(self.show_add_password_dialog)
        layout.addWidget(add_password_button)

        # Список сохранённых паролей
        self.password_list = QListWidget()
        self.load_passwords()

        # Подключаем обработчик двойного клика
        self.password_list.itemDoubleClicked.connect(self.on_password_list_double_click)
        layout.addWidget(self.password_list)

        # Кнопка "Выход"
        logout_button = QPushButton("Выйти")
        logout_button.setIcon(QIcon("icons/logout.png"))
        logout_button.clicked.connect(self.logout)
        layout.addWidget(logout_button)

        self.main_screen.setLayout(layout)
        self.setCentralWidget(self.main_screen)

    def load_passwords(self):
        """Загружает список сохранённых паролей."""
        self.password_list.clear()
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT service_name FROM passwords WHERE user_id = ?", (self.current_user_id,))
        services = cursor.fetchall()
        conn.close()

        for service in services:
            self.password_list.addItem(service[0])

    def show_add_password_dialog(self):
        """Показывает диалоговое окно для добавления пароля."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить пароль")
        layout = QVBoxLayout()

        # Поле для названия сервиса
        service_name_input = QLineEdit()
        service_name_input.setPlaceholderText("Название сервиса")
        layout.addWidget(service_name_input)

        # Поле для пароля
        password_input = QLineEdit()
        password_input.setPlaceholderText("Пароль")
        password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(password_input)

        # Кнопка "Сохранить"
        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(lambda: self.save_password(
            service_name_input.text(), password_input.text(), dialog))
        layout.addWidget(save_button)

        dialog.setLayout(layout)
        dialog.exec_()

    def save_password(self, service_name, password, dialog):
        """Сохраняет новый пароль."""
        if not service_name or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля.")
            return

        add_password(self.current_user_id, service_name, password, self.master_password)
        self.load_passwords()
        dialog.close()

    def logout(self):
        """Выход из аккаунта."""
        self.current_user_id = None
        self.master_password = None
        self.show_login_screen()

    def on_password_list_double_click(self, item):
        """Обработчик двойного клика на элементе списка."""
        service_name = item.text()
        self.show_password(service_name)

    def show_password(self, service_name):
        """Показывает пароль для выбранного сервиса."""
        password = get_password(self.current_user_id, service_name, self.master_password)
        if password:
            dialog = PasswordDialog(service_name, password, self)
            dialog.exec_()


if __name__ == "__main__":
    app = QApplication([])
    window = PasswordManagerApp()
    window.show()
    app.exec_()