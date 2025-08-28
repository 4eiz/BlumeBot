import aiosqlite
import os
from dotenv import load_dotenv

from data.users import add_user
from data.whitelist import add_to_whitelist

load_dotenv()
admin_name = os.getenv("admin_name")
admin_id = os.getenv("admin")


async def script():
    name_file = "data/create_tables.sql"
    try:
        # Асинхронное подключение к базе данных
        async with aiosqlite.connect("data/base/base.db") as sqlite_connection:
            try:
                # Чтение SQL скрипта из файла
                with open(name_file, 'r', encoding='utf-8') as file:
                    sql_script = file.read()
                
                # Разделяем скрипт на отдельные команды по ";"
                commands = sql_script.split(';')

                # Выполнение команд по одной
                for command in commands:
                    command = command.strip()  # Убираем лишние пробелы
                    if command:  # Проверяем, что команда не пустая
                        try:
                            await sqlite_connection.execute(command)
                        except aiosqlite.Error as error:
                            pass
                            # print(f"Ошибка при выполнении команды: {command}\n{error}")
                            # Игнорируем ошибку и продолжаем выполнение других команд

                await sqlite_connection.commit()
                print("Скрипт выполнен успешно.")
            except Exception as error:
                print("Ошибка при чтении или выполнении скрипта:", error)
    except aiosqlite.Error as error:
        print("Ошибка при подключении к SQLite:", error)
    finally:
        print("Соединение с SQLite закрыто.")


# Функция, которая добавляет админа во все нужные бд при запуске бота
async def settings_set():

    role = 'admin'
    specialty = 'manager'
    preferred_orders = 'small,medium,big'

    await add_user(
        user_id=admin_id, 
        username=admin_name, 
        role=role, 
        specialty=specialty, 
        stack=None, 
        preferred_orders=preferred_orders, 
        warnings=None,
    )

    await add_to_whitelist(user_id=admin_id)
