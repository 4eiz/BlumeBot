import aiosqlite
import os
from dotenv import load_dotenv




load_dotenv()
admin_id = os.getenv("admin")



async def add_user(user_id, username, role, specialty, stack, preferred_orders, warnings=None, receive_regular_notifications=True, total_earnings=0.0):
    db = None
    try:
        db = await aiosqlite.connect('data/base/base.db')
        insert_query = '''
        INSERT INTO users (id, username, role, specialty, stack, preferred_orders, warnings, receive_regular_notifications, total_earnings)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        await db.execute(insert_query, (
            user_id, 
            username, 
            role, 
            specialty, 
            stack, 
            preferred_orders, 
            warnings, 
            receive_regular_notifications,
            total_earnings
        ))
        await db.commit()
        print("Пользователь успешно добавлен.")
    except aiosqlite.Error as error:
        # print("Не удалось добавить пользователя в таблицу users.", error)
        pass
    finally:
        if db:
            try:
                await db.close()
            except aiosqlite.Error as close_error:
                print("Ошибка при закрытии соединения.", close_error)


async def get_user_info(user_id):
    db = None
    try:
        db = await aiosqlite.connect('data/base/base.db')
        select_query = '''
        SELECT * FROM users WHERE id = ?
        '''
        async with db.execute(select_query, (user_id,)) as cursor:
            user = await cursor.fetchone()
            if user:
                # Преобразование результата в словарь
                user_dict = {
                    "id": user[0],
                    "username": user[1],
                    "role": user[2],
                    "specialty": user[3],
                    "stack": user[4],
                    "preferred_orders": user[5],
                    "warnings": user[6],
                    "joined_at": user[7],
                    "receive_regular_notifications": bool(user[8]),
                    "total_earnings": user[9]  # Добавлено новое поле
                }
                return user_dict
            else:
                print("Пользователь не найден.")
                return None
    except aiosqlite.Error as error:
        print("Ошибка при получении данных пользователя.", error)
        return None
    finally:
        if db:
            try:
                await db.close()
            except aiosqlite.Error as close_error:
                print("Ошибка при закрытии соединения.", close_error)



async def update_user(user_id, username=None, role=None, specialty=None, stack=None, preferred_orders=None, warnings=None, receive_regular_notifications=None):
    db = None
    try:
        db = await aiosqlite.connect('data/base/base.db')
        # Формирование запроса на обновление только тех полей, которые переданы
        update_fields = []
        update_values = []

        if username is not None:
            update_fields.append("username = ?")
            update_values.append(username)
        if role is not None:
            update_fields.append("role = ?")
            update_values.append(role)
        if specialty is not None:
            update_fields.append("specialty = ?")
            update_values.append(specialty)
        if stack is not None:
            update_fields.append("stack = ?")
            update_values.append(stack)
        if preferred_orders is not None:
            update_fields.append("preferred_orders = ?")
            update_values.append(preferred_orders)
        if warnings is not None:
            update_fields.append("warnings = ?")
            update_values.append(warnings)
        if receive_regular_notifications is not None:
            update_fields.append("receive_regular_notifications = ?")
            update_values.append(receive_regular_notifications)

        if not update_fields:
            print("Нет данных для обновления.")
            return

        update_query = f'''
        UPDATE users
        SET {', '.join(update_fields)}
        WHERE id = ?
        '''
        update_values.append(user_id)
        await db.execute(update_query, tuple(update_values))
        await db.commit()
        print("Пользователь успешно обновлен.")
    except aiosqlite.Error as error:
        print("Ошибка при обновлении данных пользователя.", error)
    finally:
        if db:
            try:
                await db.close()
            except aiosqlite.Error as close_error:
                print("Ошибка при закрытии соединения.", close_error)



async def is_admin(user_id):
    db = None
    try:
        db = await aiosqlite.connect('data/base/base.db')
        select_query = '''
        SELECT role FROM users WHERE id = ?
        '''
        cursor = await db.execute(select_query, (user_id,))
        result = await cursor.fetchone()

        if result and result[0] == 'admin':
            return True
        return False
    except aiosqlite.Error as error:
        # print("Ошибка при проверке пользователя:", error)
        return False
    finally:
        if db:
            try:
                await db.close()
            except aiosqlite.Error as close_error:
                print("Ошибка при закрытии соединения.", close_error)



async def get_user_statistics(user_id: int):
    """
    Получает статистику пользователя:
    - Время в студии,
    - Заработанная сумма,
    - Выговоры,
    - Количество активных заказов,
    - Количество отклонённых заказов.
    
    Параметры:
    - user_id (int): ID пользователя.
    
    Возвращает:
    - dict: Словарь с данными о статистике пользователя.
    """
    
    db = None
    try:
        db = await aiosqlite.connect('data/base/base.db')
        
        # Запрос на получение данных о пользователе
        user_query = '''
        SELECT username, joined_at, total_earnings, warnings
        FROM users
        WHERE id = ?
        '''
        
        cursor = await db.execute(user_query, (user_id,))
        user_data = await cursor.fetchone()
        await cursor.close()
        
        if not user_data:
            print(f"Пользователь с ID {user_id} не найден.")
            return {}
        
        username, joined_at, total_earnings, warnings = user_data
        
        # Запрос на получение данных о заказах пользователя
        orders_query = '''
        SELECT status, is_active
        FROM order_assignments
        WHERE user_id = ?
        '''
        
        cursor = await db.execute(orders_query, (user_id,))
        orders = await cursor.fetchall()
        await cursor.close()
        
        active_orders_count = 0
        rejected_orders_count = 0
        
        # Подсчет количества активных и отклонённых заказов
        for order in orders:
            status, is_active = order
            if status == 'in_progress' and is_active == 1:
                active_orders_count += 1
            elif status == 'rejected' and is_active == 0:
                rejected_orders_count += 1

        # Формируем итоговый словарь с результатами
        statistics = {
            "username": username,
            "joined_at": joined_at,
            "total_earnings": total_earnings,
            "warnings": warnings,
            "active_orders_count": active_orders_count,
            "rejected_orders_count": rejected_orders_count
        }
        
        return statistics
    
    except aiosqlite.Error as error:
        print("Ошибка при получении статистики пользователя:", error)
        return {}
    
    finally:
        if db:
            try:
                await db.close()
            except aiosqlite.Error as close_error:
                print("Ошибка при закрытии соединения:", close_error)



async def get_users_by_role(requester_id: int):
    """
    Возвращает список пользователей в зависимости от того, кто делает запрос:
    - Если запрос делает главный админ (ID = 1538252), возвращается полный список пользователей.
    - Иначе возвращается список пользователей с ролью 'member'.

    Параметры:
    - requester_id (int): ID пользователя, который делает запрос.

    Возвращает:
    - list of dicts: Список пользователей. Каждый словарь содержит:
        - id (int): ID пользователя.
        - username (str): Имя пользователя.
        - role (str): Роль пользователя ('admin', 'member' и т.д.).
    """
    db = None
    try:
        db = await aiosqlite.connect('data/base/base.db')
        
        if requester_id == int(admin_id):
            # Если запрос делает главный админ, возвращаем всех пользователей
            query = '''
            SELECT id, username, role
            FROM users
            '''
        else:
            # Если запрос делает обычный пользователь, возвращаем только пользователей с ролью 'member'
            query = '''
            SELECT id, username, role
            FROM users
            WHERE role = 'member'
            '''
        
        cursor = await db.execute(query)
        users = await cursor.fetchall()
        await cursor.close()

        # Преобразуем кортежи в список словарей
        user_list = [
            {
                "id": user[0],
                "username": user[1],
                "role": user[2]
            }
            for user in users
        ]
        
        return user_list

    except aiosqlite.Error as error:
        print("Ошибка при получении списка пользователей:", error)
        return []
    
    finally:
        if db:
            try:
                await db.close()
            except aiosqlite.Error as close_error:
                print("Ошибка при закрытии соединения:", close_error)



async def delete_user_data(user_id: int):
    """
    Удаляет всю информацию о пользователе из связанных таблиц по user_id.
    Если в одной из таблиц нет информации, удаление продолжается.

    Параметры:
    - user_id (int): ID пользователя для удаления.
    
    Возвращает:
    - bool: True, если данные успешно удалены, False в случае ошибки.
    """
    db = None
    try:
        db = await aiosqlite.connect('data/base/base.db')

        # Удаляем назначения заказов пользователя из order_assignments
        try:
            delete_assignments_query = '''
            DELETE FROM order_assignments
            WHERE user_id = ?
            '''
            await db.execute(delete_assignments_query, (user_id,))
        except aiosqlite.Error as error:
            print(f"Ошибка при удалении назначений заказов для user_id {user_id}: {error}")

        # Удаляем заказы, созданные пользователем, из orders
        try:
            delete_orders_query = '''
            DELETE FROM orders
            WHERE created_by = ?
            '''
            await db.execute(delete_orders_query, (user_id,))
        except aiosqlite.Error as error:
            print(f"Ошибка при удалении заказов для user_id {user_id}: {error}")

        # Удаляем действия администратора, связанные с пользователем, из admin_actions
        try:
            delete_admin_actions_query = '''
            DELETE FROM admin_actions
            WHERE admin_id = ? OR target_user_id = ?
            '''
            await db.execute(delete_admin_actions_query, (user_id, user_id))
        except aiosqlite.Error as error:
            print(f"Ошибка при удалении действий администратора для user_id {user_id}: {error}")

        # Удаляем пользователя из whitelist, если он есть
        try:
            delete_whitelist_query = '''
            DELETE FROM whitelist
            WHERE user_id = ?
            '''
            await db.execute(delete_whitelist_query, (user_id,))
        except aiosqlite.Error as error:
            print(f"Ошибка при удалении из whitelist для user_id {user_id}: {error}")

        # Удаляем запросы пользователя из requests, если они есть
        try:
            delete_requests_query = '''
            DELETE FROM requests
            WHERE user_id = ?
            '''
            await db.execute(delete_requests_query, (user_id,))
        except aiosqlite.Error as error:
            print(f"Ошибка при удалении из requests для user_id {user_id}: {error}")

        # Удаляем самого пользователя из users
        try:
            delete_user_query = '''
            DELETE FROM users
            WHERE id = ?
            '''
            await db.execute(delete_user_query, (user_id,))
        except aiosqlite.Error as error:
            print(f"Ошибка при удалении пользователя с user_id {user_id}: {error}")

        # Фиксируем изменения
        await db.commit()

        print(f"Информация о пользователе с ID {user_id} успешно удалена.")
        return True

    except aiosqlite.Error as db_error:
        print(f"Общая ошибка при работе с базой данных: {db_error}")
        return False

    finally:
        if db:
            try:
                await db.close()
            except aiosqlite.Error as close_error:
                print(f"Ошибка при закрытии соединения с базой данных: {close_error}")



async def check_regular_notifications(user_id: int) -> bool:
    """
    Проверяет, получает ли пользователь регулярные уведомления.

    Параметры:
    - user_id (int): ID пользователя.

    Возвращает:
    - bool: True, если пользователь получает регулярные уведомления (receive_regular_notifications = 1),
            иначе False.
    """
    db = None
    try:
        db = await aiosqlite.connect('data/base/base.db')

        # SQL-запрос для получения receive_regular_notifications по user_id
        query = '''
        SELECT receive_regular_notifications
        FROM users
        WHERE id = ?
        '''
        cursor = await db.execute(query, (user_id,))
        result = await cursor.fetchone()
        await cursor.close()

        # Проверяем, если ли результат
        if result is not None:
            receive_notifications = result[0]
            return receive_notifications == 1
        
        # Если пользователь не найден
        print(f"Пользователь с ID {user_id} не найден.")
        return False

    except aiosqlite.Error as error:
        print("Ошибка при выполнении запроса:", error)
        return False

    finally:
        if db:
            try:
                await db.close()
            except aiosqlite.Error as close_error:
                print("Ошибка при закрытии соединения:", close_error)



async def toggle_regular_notifications(user_id: int) -> bool:
    """
    Переключает значение поля receive_regular_notifications для пользователя.
    Если значение равно 1, то меняет его на 0, и наоборот.

    Параметры:
    - user_id (int): ID пользователя.

    Возвращает:
    - bool: True, если значение было успешно переключено, иначе False.
    """
    db = None
    try:
        db = await aiosqlite.connect('data/base/base.db')

        # SQL-запрос для получения текущего значения receive_regular_notifications
        query_select = '''
        SELECT receive_regular_notifications
        FROM users
        WHERE id = ?
        '''
        cursor = await db.execute(query_select, (user_id,))
        result = await cursor.fetchone()
        await cursor.close()

        # Проверяем, если ли результат
        if result is not None:
            current_value = result[0]
            # Меняем значение на противоположное
            new_value = 0 if current_value == 1 else 1

            # SQL-запрос для обновления значения receive_regular_notifications
            query_update = '''
            UPDATE users
            SET receive_regular_notifications = ?
            WHERE id = ?
            '''
            await db.execute(query_update, (new_value, user_id))
            await db.commit()

            print(f"Значение receive_regular_notifications для пользователя с ID {user_id} успешно обновлено на {new_value}.")
            return True

        # Если пользователь не найден
        print(f"Пользователь с ID {user_id} не найден.")
        return False

    except aiosqlite.Error as error:
        print("Ошибка при обновлении значения receive_regular_notifications:", error)
        return False

    finally:
        if db:
            try:
                await db.close()
            except aiosqlite.Error as close_error:
                print("Ошибка при закрытии соединения:", close_error)



async def get_all_users_notification_settings() -> list:
    """
    Возвращает список словарей с ID пользователей и значениями receive_regular_notifications для всех пользователей.

    Возвращает:
    - list: Список словарей, каждый словарь содержит 'user_id' и 'rrn'.
    """
    db = None
    try:
        db = await aiosqlite.connect('data/base/base.db')

        # SQL-запрос для получения ID пользователей и значений receive_regular_notifications
        query = '''
        SELECT id, receive_regular_notifications
        FROM users
        '''
        cursor = await db.execute(query)
        result = await cursor.fetchall()
        await cursor.close()

        # Преобразуем результат в список словарей
        users_notifications = [
            {
                'user_id': row[0],
                'rrn': row[1]
            }
            for row in result
        ]

        return users_notifications

    except aiosqlite.Error as error:
        print("Ошибка при получении значений receive_regular_notifications:", error)
        return []

    finally:
        if db:
            try:
                await db.close()
            except aiosqlite.Error as close_error:
                print("Ошибка при закрытии соединения:", close_error)



async def add_warning(user_id: int) -> bool:
    """
    Добавляет один выговор пользователю по его ID. Если поле warnings равно None, устанавливает его в 1.

    Параметры:
    - user_id (int): ID пользователя, которому нужно добавить выговор.

    Возвращает:
    - bool: True, если выговор был успешно добавлен, иначе False.
    """
    db = None
    try:
        db = await aiosqlite.connect('data/base/base.db')

        # SQL-запрос для обновления поля warnings. Если значение None, устанавливаем его в 1.
        query = '''
        UPDATE users
        SET warnings = CASE 
            WHEN warnings IS NULL THEN 1 
            ELSE warnings + 1 
        END
        WHERE id = ?
        '''

        # Выполняем обновление
        result = await db.execute(query, (user_id,))
        await db.commit()

        if result.rowcount > 0:
            print(f"Выговор успешно добавлен пользователю с ID {user_id}.")
            return True
        else:
            print(f"Пользователь с ID {user_id} не найден.")
            return False

    except aiosqlite.Error as error:
        print("Ошибка при добавлении выговора:", error)
        return False

    finally:
        if db:
            try:
                await db.close()
            except aiosqlite.Error as close_error:
                print("Ошибка при закрытии соединения:", close_error)




async def remove_warning(user_id: int) -> bool:
    """
    Уменьшает количество выговоров пользователю по его ID.

    Параметры:
    - user_id (int): ID пользователя, которому нужно уменьшить выговор.

    Возвращает:
    - bool: True, если выговор был успешно уменьшен, иначе False.
    """
    db = None
    try:
        db = await aiosqlite.connect('data/base/base.db')

        # SQL-запрос для уменьшения количества выговоров
        query = '''
        UPDATE users
        SET warnings = CASE 
            WHEN warnings > 0 THEN warnings - 1 
            ELSE 0 
        END
        WHERE id = ?
        '''

        # Выполняем обновление
        result = await db.execute(query, (user_id,))
        await db.commit()

        if result.rowcount > 0:
            print(f"Выговор успешно уменьшен у пользователя с ID {user_id}.")
            return True
        else:
            print(f"Пользователь с ID {user_id} не найден.")
            return False

    except aiosqlite.Error as error:
        print("Ошибка при уменьшении выговора:", error)
        return False

    finally:
        if db:
            try:
                await db.close()
            except aiosqlite.Error as close_error:
                print("Ошибка при закрытии соединения:", close_error)
