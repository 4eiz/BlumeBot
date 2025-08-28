import aiosqlite



# Добавление новой записи в таблицу requests
async def add_request(user_id, data):
    db = None
    try:
        db = await aiosqlite.connect('data/base/base.db')
        insert_query = '''
        INSERT INTO requests (user_id, data)
        VALUES (?, ?)
        '''
        await db.execute(insert_query, (user_id, data))
        await db.commit()
        print("Заявка успешно добавлена.")
    except aiosqlite.Error as error:
        print("Не удалось добавить новую запись в таблицу requests.", error)
    finally:
        if db:
            try:
                await db.close()
            except aiosqlite.Error as close_error:
                print("Ошибка при закрытии соединения.", close_error)



# Удаление записи по ID из таблицы requests
async def delete_request(user_id):
    db = None
    try:
        db = await aiosqlite.connect('data/base/base.db')
        delete_query = '''
        DELETE FROM requests
        WHERE user_id = ?
        '''
        await db.execute(delete_query, (user_id,))
        await db.commit()
        print(f"Заявка с ID {user_id} успешно удалена.")
    except aiosqlite.Error as error:
        print("Не удалось удалить запись из таблицы requests.", error)
    finally:
        if db:
            try:
                await db.close()
            except aiosqlite.Error as close_error:
                print("Ошибка при закрытии соединения.", close_error)


async def get_request(user_id):
    db = None
    try:
        db = await aiosqlite.connect('data/base/base.db')
        select_query = '''
        SELECT user_id, data FROM requests
        WHERE user_id = ?
        LIMIT 1
        '''
        cursor = await db.execute(select_query, (user_id,))
        result = await cursor.fetchone()
        await cursor.close()
        # print(f'Результат: {result}')
        
        if result:
            return result

    except aiosqlite.Error as error:
        print("Не удалось выполнить запрос к таблице requests.", error)
        return False
    finally:
        if db:
            try:
                await db.close()
            except aiosqlite.Error as close_error:
                print("Ошибка при закрытии соединения.", close_error)
