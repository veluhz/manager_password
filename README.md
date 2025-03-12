### README

---

# Password Manager Application

## English Version

### Overview
This is a password manager application with a graphical user interface (GUI) built using **PyQt5**. The application allows users to securely store, manage, and retrieve passwords for various services. It includes features such as:
- User registration and authentication.
- Secure encryption of passwords using AES-256.
- Adding, viewing, and copying passwords.
- A modern and user-friendly interface.

The application is designed to be simple, secure, and easy to use.

---

### Features
1. **User Authentication**:
   - Users can register and log in with a master password.
   - Master passwords are securely hashed using `bcrypt`.

2. **Password Management**:
   - Add new passwords for different services.
   - View and copy passwords securely.
   - Passwords are encrypted using AES-256 with a key derived from the master password.

3. **Modern Design**:
   - Dark theme with blue accents.
   - Icons for buttons and styled dialogs.
   - Toggle password visibility in the password view dialog.

4. **Cross-Platform**:
   - Works on Windows, macOS, and Linux.

---

### Installation

#### Prerequisites
1. Python 3.8 or higher.
2. Install the required dependencies:
   ```bash
   pip install PyQt5 bcrypt cryptography pyinstaller
   ```

#### Running the Application
1. Clone the repository or download the source code.
2. Run the application:
   ```bash
   python main.py
   ```

#### Compiling to Executable
To compile the application into an `.exe` file:
1. Use PyInstaller:
   ```bash
   pyinstaller --onefile --windowed --add-data "styles.qss;." --add-data "icons/*;icons" main.py
   ```
2. Find the executable in the `dist/` folder.

---

### File Structure
```
project/
├── main.py                # Main application file
├── styles.qss             # Stylesheet for the GUI
├── icons/                 # Folder containing icons
│   ├── lock.png
│   ├── register.png
│   ├── add.png
│   └── logout.png
├── README.md              # This file
└── database.db            # SQLite database (created automatically)
```

---

### Security Notes
- Passwords are encrypted using AES-256 with a key derived from the user's master password.
- Master passwords are hashed using `bcrypt` and stored securely in the database.
- Do not share your master password or database file.

---

### License
This project is licensed under the MIT License. See the `LICENSE` file for details.

---

---

# Менеджер Паролей

## Русская версия

### Обзор
Это приложение для управления паролями с графическим интерфейсом (GUI), разработанное с использованием **PyQt5**. Приложение позволяет пользователям безопасно хранить, управлять и получать доступ к паролям для различных сервисов. Основные функции включают:
- Регистрацию и аутентификацию пользователей.
- Безопасное шифрование паролей с использованием AES-256.
- Добавление, просмотр и копирование паролей.
- Современный и удобный интерфейс.

Приложение разработано так, чтобы быть простым, безопасным и удобным в использовании.

---

### Функционал
1. **Аутентификация пользователей**:
   - Пользователи могут регистрироваться и входить в систему с мастер-паролем.
   - Мастер-пароли надёжно хэшируются с использованием `bcrypt`.

2. **Управление паролями**:
   - Добавление новых паролей для различных сервисов.
   - Просмотр и копирование паролей в буфер обмена.
   - Пароли шифруются с использованием AES-256 с ключом, полученным из мастер-пароля.

3. **Современный дизайн**:
   - Тёмная тема с синими акцентами.
   - Иконки для кнопок и стилизованные диалоговые окна.
   - Возможность временно показывать или скрывать пароль в диалоге просмотра.

4. **Кроссплатформенность**:
   - Работает на Windows, macOS и Linux.

---

### Установка

#### Предварительные требования
1. Python 3.8 или выше.
2. Установите необходимые зависимости:
   ```bash
   pip install PyQt5 bcrypt cryptography pyinstaller
   ```

#### Запуск приложения
1. Склонируйте репозиторий или скачайте исходный код.
2. Запустите приложение:
   ```bash
   python main.py
   ```

#### Компиляция в исполняемый файл
Чтобы скомпилировать приложение в `.exe` файл:
1. Используйте PyInstaller:
   ```bash
   pyinstaller --onefile --windowed --add-data "styles.qss;." --add-data "icons/*;icons" main.py
   ```
2. Найдите исполняемый файл в папке `dist/`.

---

### Структура файлов
```
project/
├── main.py                # Основной файл приложения
├── styles.qss             # Стилевой файл для GUI
├── icons/                 # Папка с иконками
│   ├── lock.png
│   ├── register.png
│   ├── add.png
│   └── logout.png
├── README.md              # Этот файл
└── database.db            # База данных SQLite (создаётся автоматически)
```

---

### Примечания по безопасности
- Пароли шифруются с использованием AES-256 с ключом, полученным из мастер-пароля пользователя.
- Мастер-пароли хэшируются с использованием `bcrypt` и хранятся в базе данных безопасным образом.
- Не передавайте свой мастер-пароль или файл базы данных другим лицам.

---

### Лицензия
Этот проект распространяется под лицензией MIT. Подробности см. в файле `LICENSE`.

--- 

### Контакты
Если у вас есть вопросы или предложения, свяжитесь с автором:
- Email: [your_email@example.com](mailto:your_email@example.com)
- GitHub: [YourGitHubProfile](https://github.com/YourGitHubProfile)

--- 

Enjoy using the Password Manager! 😊