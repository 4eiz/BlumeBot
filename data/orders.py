import aiosqlite


async def add_order_to_db(title, description, required_skills, size, specialty, created_by, price=None, deadline=None):
    """
    Добавляет новый заказ в базу данных и возвращает его ID.
    """

    db = None
    try:
        db = await aiosqlite.connect('data/base/base.db')
        insert_query = '''
        INSERT INTO orders (title, description, required_skills, size, price, deadline, specialty, status, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'open', ?)
        '''
        cursor = await db.execute(insert_query, (
            title, 
            description, 
            required_skills, 
            size, 
            price, 
            deadline,
            specialty,
            created_by
        ))
        await db.commit()
        order_id = cursor.lastrowid  # Получаем ID последней вставленной строки
        print(f"Заказ успешно добавлен. ID: {order_id}")
        return order_id  # Возвращаем ID заказа
    except aiosqlite.Error as error:
        print("Не удалось добавить заказ в таблицу orders.", error)
        return None  # Возвращаем None в случае ошибки
    finally:
        if db:
            try:
                await db.close()
            except aiosqlite.Error as close_error:
                print("Ошибка при закрытии соединения.", close_error)



async def get_orders_for_user(user_id: int):
    """
    Ищет заказы для пользователя по его стеку технологий, предпочитаемому размеру заказа и специализации (роли),
    с проверкой на отклонённые заказы. Возвращает список подходящих заказов.

    Параметры:
    - user_id (int): ID пользователя.

    Возвращает:
    - list of dicts: Список заказов, которые соответствуют условиям пользователя и не отклонены им ранее.
    """
    db = None
    try:
        db = await aiosqlite.connect('data/base/base.db')

        # Получаем данные о пользователе
        user_query = '''
        SELECT stack, preferred_orders, role, specialty
        FROM users
        WHERE id = ?
        '''
        cursor = await db.execute(user_query, (user_id,))
        user = await cursor.fetchone()
        await cursor.close()

        if not user:
            print(f"Пользователь с ID {user_id} не найден.")
            return []

        user_stack, preferred_orders, user_role, user_specialty = user

        # Разделяем стек технологий и предпочитаемые размеры заказов
        tech_list = [tech.strip().lower() for tech in user_stack.split(',')] if user_stack else []
        preferred_order_sizes = preferred_orders.split(',') if preferred_orders else []

        matching_orders = []

        if user_role == 'admin':
            # Запрос для получения всех открытых заказов для администраторов с исключением отклоненных
            orders_query = '''
            SELECT o.id, o.title, o.description, o.required_skills, o.size, o.price, o.deadline, o.status, o.created_at
            FROM orders o
            LEFT JOIN order_assignments oa ON o.id = oa.order_id AND oa.user_id = ? AND oa.status = 'rejected'
            WHERE o.status = 'open' AND oa.order_id IS NULL
            '''
            cursor = await db.execute(orders_query, (user_id,))
            orders = await cursor.fetchall()
            await cursor.close()

            # Преобразуем кортежи в словари
            matching_orders.extend([
                {
                    "id": order[0],
                    "title": order[1],
                    "description": order[2],
                    "required_skills": order[3],
                    "size": order[4],
                    "price": order[5],
                    "deadline": order[6],
                    "status": order[7],
                    "created_at": order[8]
                }
                for order in orders
            ])
        else:
            # Запрос для получения заказов для обычных пользователей
            orders_query = '''
            SELECT o.id, o.title, o.description, o.required_skills, o.size, o.price, o.deadline, o.status, o.created_at
            FROM orders o
            LEFT JOIN order_assignments oa ON o.id = oa.order_id AND oa.user_id = ? AND oa.status = 'rejected'
            WHERE o.status = 'open' AND o.size IN ({}) AND o.specialty = ? AND oa.order_id IS NULL
            '''
            
            # Создаем подстановку для предпочитаемых размеров заказов
            size_placeholders = ','.join(['?'] * len(preferred_order_sizes))
            orders_query = orders_query.format(size_placeholders)

            # Выполняем запрос с подстановкой предпочитаемых размеров заказов и роли
            cursor = await db.execute(orders_query, (user_id, *preferred_order_sizes, user_specialty))
            orders = await cursor.fetchall()
            await cursor.close()

            # Преобразуем кортежи в список словарей
            all_orders = [
                {
                    "id": order[0],
                    "title": order[1],
                    "description": order[2],
                    "required_skills": order[3],
                    "size": order[4],
                    "price": order[5],
                    "deadline": order[6],
                    "status": order[7],
                    "created_at": order[8]
                }
                for order in orders
            ]

            # Получаем список отклоненных заказов для пользователя
            rejected_orders_query = '''
            SELECT order_id FROM order_assignments
            WHERE user_id = ? AND status = 'rejected'
            '''
            cursor = await db.execute(rejected_orders_query, (user_id,))
            rejected_orders = await cursor.fetchall()
            await cursor.close()

            # Преобразуем список отклоненных заказов в множество для быстрого поиска
            rejected_order_ids = {order[0] for order in rejected_orders}

            # Фильтруем заказы: исключаем те, которые отклонены пользователем
            for order in all_orders:
                if order["id"] not in rejected_order_ids:
                    # Проверяем, что все технологии из стека пользователя есть в требуемых навыках
                    required_skills_list = [skill.strip().lower() for skill in order["required_skills"].split(',')] if order["required_skills"] else []
                    
                    missing_skills = [skill for skill in required_skills_list if skill not in tech_list]

                    if not missing_skills:
                        matching_orders.append(order)
                    else:
                        print(f"Заказ с ID {order['id']} не подходит. Требуемые навыки: {required_skills_list}. У пользователя есть: {tech_list}. Отсутствуют навыки: {missing_skills}.")
                else:
                    print(f"Заказ с ID {order['id']} отклонён пользователем ранее.")

        
        if not matching_orders:
            print(f"Для пользователя с ID {user_id} не найдено подходящих заказов.")

        return matching_orders

    except aiosqlite.Error as error:
        print("Ошибка при поиске заказов для пользователя:", error)
        return []
    
    finally:
        if db:
            try:
                await db.close()
            except aiosqlite.Error as close_error:
                print("Ошибка при закрытии соединения:", close_error)






async def get_users_for_order(technologies: str, order_size: str, role: str):
    """
    Ищет пользователей по указанным технологиям, размеру заказа и специализации (роли).
    Возвращает список ID пользователей, у которых в стеке есть все указанные технологии,
    в предпочитаемых размерах заказов присутствует указанный размер заказа, а роль совпадает с указанной.
    Пользователи с ролью 'admin' добавляются независимо от стека и размера заказа.
    """
    
    db = None
    try:
        # Разделяем технологии на отдельные слова
        tech_list = technologies.split(',')

        db = await aiosqlite.connect('data/base/base.db')
        
        # Создаем SQL запрос
        query = '''
        SELECT id, stack, preferred_orders, role, specialty
        FROM users
        WHERE (preferred_orders LIKE ? AND specialty = ?) OR role = 'admin'
        '''
        
        cursor = await db.execute(query, (f'%{order_size}%', role))
        users = await cursor.fetchall()

        matching_users = []

        # Проходим по найденным пользователям и проверяем их стек и роль
        for user in users:
            user_id, stack, preferred_orders, user_role, user_specialty = user
            
            # Добавляем администраторов вне зависимости от их стека и размеров заказов
            if user_role == 'admin':
                matching_users.append(user_id)
                continue

            # Проверяем, что у пользователя роль совпадает и в стеке есть все переданные технологии
            user_stack = stack.split(',') if stack else []
            if all(tech.strip() in user_stack for tech in tech_list):
                matching_users.append(user_id)

        await cursor.close()
        return matching_users
    
    except aiosqlite.Error as error:
        print("Ошибка при поиске пользователей:", error)
        return []
    
    finally:
        if db:
            try:
                await db.close()
            except aiosqlite.Error as close_error:
                print("Ошибка при закрытии соединения:", close_error)



async def get_order_by_id(order_id: int):
    """
    Получает информацию о заказе по его ID.

    Параметры:
    - order_id (int): ID заказа.

    Возвращает:
    - dict: Информация о заказе, содержащая:
        - id (int): ID заказа.
        - title (str): Название заказа.
        - description (str): Описание заказа.
        - required_skills (str): Стек технологий, необходимых для выполнения заказа.
        - size (str): Размер заказа.
        - price (float): Стоимость заказа.
        - deadline (int): Дедлайн для выполнения заказа (в днях).
        - status (str): Статус заказа ('open', 'in_progress', 'completed', 'rejected').
        - created_at (str): Дата и время создания заказа.
        - created_by (int): ID пользователя, который создал заказ.
    """
    
    db = None
    try:
        db = await aiosqlite.connect('data/base/base.db')
        
        # Запрос для получения информации о заказе
        order_query = '''
        SELECT id, title, description, required_skills, size, price, deadline, status, created_at, created_by
        FROM orders
        WHERE id = ?
        '''
        
        cursor = await db.execute(order_query, (order_id,))
        order = await cursor.fetchone()
        await cursor.close()

        if order:
            # Создаем словарь с результатами
            order_dict = {
                "id": order[0],
                "title": order[1],
                "description": order[2],
                "required_skills": order[3],
                "size": order[4],
                "price": order[5],
                "deadline": order[6],
                "status": order[7],
                "created_at": order[8],
                "created_by": order[9]
            }
            return order_dict
        else:
            print(f"Заказ с ID {order_id} не найден.")
            return None

    except aiosqlite.Error as error:
        print("Ошибка при получении заказа по ID:", error)
        return None
    
    finally:
        if db:
            try:
                await db.close()
            except aiosqlite.Error as close_error:
                print("Ошибка при закрытии соединения:", close_error)



async def assign_order_to_user(order_id: int, user_id: int):
    """
    Назначает заказ пользователю. Добавляет новую запись в таблицу order_assignments.
    Перед этим проверяет, есть ли у пользователя более двух активных заказов (status='in_progress').
    
    Параметры:
    - order_id (int): ID заказа.
    - user_id (int): ID пользователя.
    
    Возвращает:
    - bool: True, если назначение успешно, False в случае ошибки или если у пользователя больше двух активных заказов.
    """
    db = None
    try:
        db = await aiosqlite.connect('data/base/base.db')
        
        # Проверяем количество активных заказов у пользователя
        active_orders_query = '''
        SELECT COUNT(*)
        FROM order_assignments
        WHERE user_id = ? AND status = 'in_progress'
        '''
        cursor = await db.execute(active_orders_query, (user_id,))
        result = await cursor.fetchone()
        active_orders_count = result[0]
        await cursor.close()

        # Если у пользователя больше двух активных заказов, возвращаем False
        if active_orders_count >= 2:
            print(f"Пользователь с ID {user_id} имеет {active_orders_count} активных заказов.")
            return False

        # Создаем SQL-запрос для назначения заказа
        query = '''
        INSERT INTO order_assignments (order_id, user_id)
        VALUES (?, ?)
        '''
        
        await db.execute(query, (order_id, user_id))
        await db.commit()
        
        return True
    
    except aiosqlite.Error as error:
        print("Ошибка при назначении заказа пользователю:", error)
        return False
    
    finally:
        if db:
            try:
                await db.close()
            except aiosqlite.Error as close_error:
                print("Ошибка при закрытии соединения:", close_error)




async def reject_order(user_id: int, order_id: int):
    """
    Обновляет статус выполнения заказа на 'rejected' для конкретного пользователя.
    
    Параметры:
    - user_id (int): ID пользователя.
    - order_id (int): ID заказа.
    
    Возвращает:
    - bool: True, если обновление успешно, False в случае ошибки.
    """
    db = None
    try:
        db = await aiosqlite.connect('data/base/base.db')
        
        # Обновляем статус и флаг активности
        query = '''
        UPDATE order_assignments
        SET status = 'rejected', is_active = 0
        WHERE order_id = ? AND user_id = ? AND is_active = 1
        '''
        
        await db.execute(query, (order_id, user_id))
        await db.commit()
        
        return True
    
    except aiosqlite.Error as error:
        print("Ошибка при отказе от заказа:", error)
        return False
    
    finally:
        if db:
            try:
                await db.close()
            except aiosqlite.Error as close_error:
                print("Ошибка при закрытии соединения:", close_error)



async def update_order_status(order_id: int, new_status: str):
    """
    Обновляет статус заказа.

    Параметры:
    - order_id (int): ID заказа, который нужно обновить.
    - new_status (str): Новый статус заказа ('open', 'in_progress', 'completed', 'rejected').

    Возвращает:
    - bool: True, если статус был успешно обновлен, иначе False.
    """
    if new_status not in ('open', 'in_progress', 'completed', 'rejected'):
        print(f"Недопустимый статус: {new_status}")
        return False

    db = None
    try:
        db = await aiosqlite.connect('data/base/base.db')
        
        # SQL-запрос для обновления статуса заказа
        query = '''
        UPDATE orders
        SET status = ?
        WHERE id = ?
        '''
        
        # Выполняем обновление статуса
        await db.execute(query, (new_status, order_id))
        await db.commit()

        print(f"Статус заказа с ID {order_id} успешно обновлен на {new_status}.")
        return True

    except aiosqlite.Error as error:
        print("Ошибка при обновлении статуса заказа:", error)
        return False

    finally:
        if db:
            try:
                await db.close()
            except aiosqlite.Error as close_error:
                print("Ошибка при закрытии соединения:", close_error)


async def set_order_status_open(order_id: int):
    """
    Устанавливает статус заказа на 'open'.

    Параметры:
    - order_id (int): ID заказа, который нужно обновить.

    Возвращает:
    - bool: True, если статус был успешно обновлен, иначе False.
    """
    db = None
    try:
        db = await aiosqlite.connect('data/base/base.db')
        
        # SQL-запрос для обновления статуса на 'open'
        query = '''
        UPDATE orders
        SET status = 'open'
        WHERE id = ?
        '''
        
        # Выполняем обновление статуса
        await db.execute(query, (order_id,))
        await db.commit()

        print(f"Статус заказа с ID {order_id} успешно обновлен на 'open'.")
        return True

    except aiosqlite.Error as error:
        print("Ошибка при обновлении статуса заказа на 'open':", error)
        return False

    finally:
        if db:
            try:
                await db.close()
            except aiosqlite.Error as close_error:
                print("Ошибка при закрытии соединения:", close_error)



async def set_order_status_in_progress(order_id: int):
    """
    Устанавливает статус заказа на 'in_progress', если текущий статус 'open'.

    Параметры:
    - order_id (int): ID заказа, который нужно обновить.

    Возвращает:
    - bool: True, если статус был успешно обновлен, иначе False.
    """
    db = None
    try:
        db = await aiosqlite.connect('data/base/base.db')
        
        # Сначала получаем текущий статус заказа
        query_status = '''
        SELECT status FROM orders WHERE id = ?
        '''
        cursor = await db.execute(query_status, (order_id,))
        order = await cursor.fetchone()
        await cursor.close()

        if not order:
            print(f"Заказ с ID {order_id} не найден.")
            return False
        
        current_status = order[0]

        # Проверяем, является ли статус 'open'
        if current_status != 'open':
            print(f"Невозможно обновить статус заказа с ID {order_id}. Текущий статус: {current_status}.")
            return False

        # Если статус 'open', обновляем его на 'in_progress'
        update_query = '''
        UPDATE orders
        SET status = 'in_progress'
        WHERE id = ?
        '''
        await db.execute(update_query, (order_id,))
        await db.commit()

        print(f"Статус заказа с ID {order_id} успешно обновлен на 'in_progress'.")
        return True

    except aiosqlite.Error as error:
        print("Ошибка при обновлении статуса заказа на 'in_progress':", error)
        return False

    finally:
        if db:
            try:
                await db.close()
            except aiosqlite.Error as close_error:
                print("Ошибка при закрытии соединения:", close_error)




async def reject_order_assignment(order_id: int, user_id: int):
    """
    Проверяет наличие записи с order_id и user_id в таблице order_assignments.
    Если запись существует, обновляет статус на 'rejected' и is_active = 0.
    Если записи нет, создает новую с этими значениями.

    Параметры:
    - order_id (int): ID заказа.
    - user_id (int): ID пользователя.

    Возвращает:
    - bool: True, если операция прошла успешно, False в случае ошибки.
    """
    db = None
    try:
        db = await aiosqlite.connect('data/base/base.db')

        # Сначала проверим, есть ли такая запись в таблице
        check_query = '''
        SELECT 1 FROM order_assignments
        WHERE order_id = ? AND user_id = ?
        '''
        cursor = await db.execute(check_query, (order_id, user_id))
        record_exists = await cursor.fetchone()
        await cursor.close()

        if record_exists:
            # Если запись существует, обновляем её
            update_query = '''
            UPDATE order_assignments
            SET status = 'rejected', is_active = 0
            WHERE order_id = ? AND user_id = ?
            '''
            await db.execute(update_query, (order_id, user_id))
            print(f"Заказ с ID {order_id} для пользователя с ID {user_id} был обновлен до 'rejected'.")
        else:
            # Если записи нет, добавляем новую
            insert_query = '''
            INSERT INTO order_assignments (order_id, user_id, status, is_active)
            VALUES (?, ?, 'rejected', 0)
            '''
            await db.execute(insert_query, (order_id, user_id))
            print(f"Добавлена новая запись: заказ с ID {order_id} для пользователя с ID {user_id} был отклонен.")

        # Сохраняем изменения
        await db.commit()
        return True

    except aiosqlite.Error as error:
        print("Ошибка при отклонении заказа:", error)
        return False

    finally:
        if db:
            try:
                await db.close()
            except aiosqlite.Error as close_error:
                print("Ошибка при закрытии соединения:", close_error)




async def get_active_orders_for_user(user_id: int):
    """
    Получает все активные заказы пользователя, где статус 'in_progress' и is_active=1.
    
    Параметры:
    - user_id (int): ID пользователя, для которого нужно найти активные заказы.
    
    Возвращает:
    - list of dicts: Список активных заказов, где каждый словарь содержит информацию о заказе.
    """
    db = None
    try:
        db = await aiosqlite.connect('data/base/base.db')

        query = '''
        SELECT oa.order_id, o.title, o.description, o.price, o.created_at, o.size
        FROM order_assignments oa
        JOIN orders o ON oa.order_id = o.id
        WHERE oa.user_id = ? AND oa.status = 'in_progress' AND oa.is_active = 1
        '''

        cursor = await db.execute(query, (user_id,))
        active_orders = await cursor.fetchall()
        await cursor.close()

        # Преобразование результатов в список словарей
        orders_list = [
            {
                "id": order[0],
                "title": order[1],
                "description": order[2],
                "price": order[3],
                "created_at": order[4],
                "size": order[5]
            }
            for order in active_orders
        ]

        return orders_list

    except aiosqlite.Error as error:
        print(f"Ошибка при получении активных заказов для пользователя {user_id}:", error)
        return []
    
    finally:
        if db:
            await db.close()



async def complete_order(order_id: int):
    """
    Завершает заказ, обновляя статус в таблице orders на 'completed', 
    обновляет запись в таблице order_assignments (status = 'completed', is_active = 0),
    автоматически находя пользователя, который выполняет заказ (status = 'in_progress' и is_active = 1),
    и обновляет баланс пользователя с учетом варнов (если 3 и более варнов, снимается 10%).

    Параметры:
    - order_id (int): ID заказа.

    Возвращает:
    - bool: True, если обновление прошло успешно, False в случае ошибки.
    """
    db = None
    try:
        db = await aiosqlite.connect('data/base/base.db')

        # Находим пользователя с активным выполнением заказа
        find_user_query = '''
        SELECT user_id
        FROM order_assignments
        WHERE order_id = ? AND status = 'in_progress' AND is_active = 1
        '''
        cursor = await db.execute(find_user_query, (order_id,))
        result = await cursor.fetchone()
        await cursor.close()

        # Проверка, найден ли пользователь
        if not result:
            print(f"Не найден пользователь с активным заказом ID {order_id}.")
            return False

        user_id = result[0]

        # Получаем количество варнов у пользователя
        get_warnings_query = '''
        SELECT warnings
        FROM users
        WHERE id = ?
        '''
        cursor = await db.execute(get_warnings_query, (user_id,))
        warnings_result = await cursor.fetchone()
        await cursor.close()

        # Проверка количества варнов
        if not warnings_result:
            print(f"Не удалось получить количество варнов пользователя с ID {user_id}.")
            return False

        warnings = warnings_result[0] if warnings_result[0] is not None else 0

        # Получаем стоимость заказа
        get_order_price_query = '''
        SELECT price
        FROM orders
        WHERE id = ?
        '''
        cursor = await db.execute(get_order_price_query, (order_id,))
        price_result = await cursor.fetchone()
        await cursor.close()

        # Проверка стоимости заказа
        if not price_result or price_result[0] is None:
            print(f"Не удалось получить стоимость заказа с ID {order_id}.")
            return False

        price = price_result[0]

        # Вычисляем финальную сумму (если 3 и более варнов, снимаем 10%)
        if warnings >= 3:
            final_price = price * 0.9  # Убираем 10%
        else:
            final_price = price

        # Обновляем баланс пользователя
        update_user_balance_query = '''
        UPDATE users
        SET total_earnings = total_earnings + ?
        WHERE id = ?
        '''
        await db.execute(update_user_balance_query, (final_price, user_id))

        # Обновляем статус заказа в таблице orders
        update_order_query = '''
        UPDATE orders
        SET status = 'completed'
        WHERE id = ?
        '''
        await db.execute(update_order_query, (order_id,))

        # Обновляем статус и активность в таблице order_assignments
        update_assignment_query = '''
        UPDATE order_assignments
        SET status = 'completed', is_active = 0
        WHERE order_id = ? AND user_id = ?
        '''
        await db.execute(update_assignment_query, (order_id, user_id))

        # Фиксируем изменения
        await db.commit()

        print(f"Заказ с ID {order_id} успешно завершен для пользователя с ID {user_id}. Финальная сумма: {final_price}")
        return True

    except aiosqlite.Error as error:
        print("Ошибка при завершении заказа:", error)
        return False

    finally:
        if db:
            try:
                await db.close()
            except aiosqlite.Error as close_error:
                print("Ошибка при закрытии соединения:", close_error)




async def get_user_by_order(order_id: int):
    """
    Получает ID пользователя, который взял заказ по ID заказа.

    Параметры:
    - order_id (int): ID заказа.

    Возвращает:
    - user_id (int): ID пользователя, который взял заказ, или None, если заказ не найден или пользователь не назначен.
    """
    db = None
    try:
        # Подключаемся к базе данных
        db = await aiosqlite.connect('data/base/base.db')

        # SQL-запрос для получения ID пользователя по ID заказа
        query = '''
        SELECT user_id
        FROM order_assignments
        WHERE order_id = ? AND is_active = 1
        '''

        # Выполняем запрос
        async with db.execute(query, (order_id,)) as cursor:
            result = await cursor.fetchone()

        # Если результат найден, возвращаем user_id
        if result:
            return result[0]  # Возвращаем ID пользователя
        else:
            print(f"Заказ с ID {order_id} не найден или не назначен.")
            return None

    except aiosqlite.Error as error:
        print(f"Ошибка при получении ID пользователя для заказа {order_id}: {error}")
        return None

    finally:
        # Закрываем подключение к базе данных
        if db:
            await db.close()



async def update_order_price(order_id: int, new_price: float):
    """
    Обновляет цену заказа по его ID.

    Параметры:
    - order_id (int): ID заказа, который нужно обновить.
    - new_price (float): Новая цена заказа.

    Возвращает:
    - bool: True, если цена была успешно обновлена, иначе False.
    """
    db = None
    try:
        # Подключаемся к базе данных
        db = await aiosqlite.connect('data/base/base.db')

        # SQL-запрос для обновления цены заказа
        query = '''
        UPDATE orders
        SET price = ?
        WHERE id = ?
        '''

        # Выполняем запрос для обновления цены
        await db.execute(query, (new_price, order_id))
        await db.commit()

        print(f"Цена заказа с ID {order_id} успешно обновлена на {new_price}.")
        return True

    except aiosqlite.Error as error:
        print(f"Ошибка при обновлении цены заказа с ID {order_id}: {error}")
        return False

    finally:
        # Закрываем подключение к базе данных
        if db:
            await db.close()


async def reject_order(order_id: int):
    """
    Обновляет статус заказа на 'rejected' и удаляет запись о назначении заказа в order_assignments,
    если статус назначения 'in_progress'.

    Параметры:
    - order_id (int): ID заказа, который необходимо отклонить.

    Возвращает:
    - bool: True, если обновление прошло успешно и записи были удалены, иначе False.
    """
    db = None
    try:
        db = await aiosqlite.connect('data/base/base.db')

        # Обновляем статус заказа на 'rejected' в таблице orders
        update_order_query = '''
        UPDATE orders
        SET status = 'rejected'
        WHERE id = ?
        '''
        await db.execute(update_order_query, (order_id,))

        # Удаляем запись о назначении заказа, если статус 'in_progress'
        delete_assignment_query = '''
        DELETE FROM order_assignments
        WHERE order_id = ? AND status = 'in_progress'
        '''
        await db.execute(delete_assignment_query, (order_id,))

        # Сохраняем изменения
        await db.commit()

        print(f"Заказ с ID {order_id} отклонен, и записи с активным выполнением удалены.")
        return True

    except aiosqlite.Error as error:
        print("Ошибка при отклонении заказа:", error)
        return False

    finally:
        if db:
            try:
                await db.close()
            except aiosqlite.Error as close_error:
                print("Ошибка при закрытии соединения:", close_error)
