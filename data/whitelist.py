import aiosqlite

async def add_to_whitelist(user_id):
    db = None
    try:
        db = await aiosqlite.connect('data/base/base.db')
        insert_query = '''
        INSERT INTO whitelist (user_id)
        VALUES (?)
        '''
        await db.execute(insert_query, (user_id,))
        await db.commit()
        print("Пользователь успешно добавлен в whitelist.")
    except aiosqlite.Error as error:
        # print("Ошибка при добавлении пользователя в whitelist:", error)
        pass
    finally:
        if db:
            try:
                await db.close()
            except aiosqlite.Error as close_error:
                print("Ошибка при закрытии соединения.", close_error)



async def remove_from_whitelist(user_id):
    db = None
    try:
        db = await aiosqlite.connect('data/base/base.db')
        delete_query = '''
        DELETE FROM whitelist WHERE user_id = ?
        '''
        await db.execute(delete_query, (user_id,))
        await db.commit()
        print("Пользователь успешно удалён из whitelist.")
    except aiosqlite.Error as error:
        # print("Ошибка при удалении пользователя из whitelist:", error)
        pass
    finally:
        if db:
            try:
                await db.close()
            except aiosqlite.Error as close_error:
                print("Ошибка при закрытии соединения.", close_error)


async def is_in_whitelist(user_id):
    db = None
    try:
        db = await aiosqlite.connect('data/base/base.db')
        select_query = '''
        SELECT 1 FROM whitelist WHERE user_id = ?
        '''
        cursor = await db.execute(select_query, (user_id,))
        result = await cursor.fetchone()

        if result:
            return True
        
        return False
    except aiosqlite.Error as error:
        # print("Ошибка при проверке whitelist:", error)
        return False
    finally:
        if db:
            try:
                await db.close()
            except aiosqlite.Error as close_error:
                print("Ошибка при закрытии соединения.", close_error)
