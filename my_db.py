#!/usr/bin/env python3


import time
import threading
import sqlite3

import my_log
from utils import asunc_run



LOCK = threading.Lock()

CON = None
CUR = None
COM_COUNTER = 0
DAEMON_RUN = True
DAEMON_TIME = 2


@asunc_run
def sync_daemon():
    global COM_COUNTER
    while DAEMON_RUN:
        time.sleep(DAEMON_TIME)
        try:
            with LOCK:
                if COM_COUNTER > 0:
                    CON.commit()
                    COM_COUNTER = 0
        except Exception as error:
            my_log.log2(f'my_msg_counter:sync_daemon {error}')


def init():
    '''init db'''
    global CON, CUR
    try:
        CON = sqlite3.connect('db/main.db', check_same_thread=False)
        CUR = CON.cursor()

        CUR.execute('''
            CREATE TABLE IF NOT EXISTS msg_counter (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                access_time REAL,
                model_used TEXT
            )
        ''')
        # Creating indexes separately
        CUR.execute('CREATE INDEX IF NOT EXISTS idx_access_time ON msg_counter (access_time)')
        CUR.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON msg_counter (user_id)')
        CUR.execute('CREATE INDEX IF NOT EXISTS idx_model_used ON msg_counter (model_used)')

        CON.commit()
        sync_daemon()
    except Exception as error:
        my_log.log2(f'my_msg_counter:init {error}')


def close():
    global DAEMON_RUN
    DAEMON_RUN = False
    time.sleep(DAEMON_TIME + 2)
    with LOCK:
        try:
            CON.commit()
            CON.close()
        except Exception as error:
            my_log.log2(f'my_msg_counter:close {error}')


def add_msg(user_id: str, model_used: str, timestamp: float = None):
    '''add msg counter record to db'''
    global COM_COUNTER
    with LOCK:
        try:
            access_time = timestamp if timestamp else time.time()
            
            # Проверка наличия записи
            CUR.execute('''
                SELECT COUNT(*) FROM msg_counter
                WHERE user_id = ? AND access_time = ? AND model_used = ?
            ''', (user_id, access_time, model_used))
            
            if CUR.fetchone()[0] == 0:
                # Если записи нет, добавляем новую
                CUR.execute('''
                    INSERT INTO msg_counter (user_id, access_time, model_used)
                    VALUES (?, ?, ?)
                ''', (user_id, access_time, model_used))
                COM_COUNTER += 1

        except Exception as error:
            my_log.log2(f'my_msg_counter:add {error}')


def count_msgs(user_id: str, model: str, access_time: float):
    '''Count the number of messages sent by a user since a specified access time.

    access_time - seconds before now (60*60*24*30 - 30 days)

    print(count_msgs('user1', 'all', 60*60*24*30)) - print all messages sent by user1 in the last 30 days
    '''
    access_time = time.time() - access_time
    with LOCK:
        try:
            if model == 'all':
                CUR.execute('''
                    SELECT COUNT(*) FROM msg_counter
                    WHERE user_id = ? AND access_time > ?
                ''', (user_id, access_time))
            else:
                CUR.execute('''
                    SELECT COUNT(*) FROM msg_counter
                    WHERE user_id = ? AND model_used = ? AND access_time > ?
                ''', (user_id, model, access_time))
            return CUR.fetchone()[0]
        except Exception as error:
            my_log.log2(f'my_msg_counter:count {error}')
            return 0


def count_msgs_all():
    '''count all messages'''
    with LOCK:
        try:
            CUR.execute('''
                SELECT COUNT(*) FROM msg_counter
            ''')
            return CUR.fetchone()[0]
        except Exception as error:
            my_log.log2(f'my_msg_counter:count_all {error}')
            return 0


def get_model_usage(days: int):
    access_time = time.time() - days * 24 * 60 * 60
    with LOCK:
        try:
            CUR.execute('''
                SELECT model_used, COUNT(*) FROM msg_counter
                WHERE access_time > ?
                GROUP BY model_used
            ''', (access_time,))
            results = CUR.fetchall()
            model_usage = {}
            for row in results:
                model = row[0]
                usage_count = row[1]
                model_usage[model] = usage_count
            return model_usage
        except Exception as error:
            my_log.log2(f'my_msg_counter:get_model_usage {error}')
            return {}


def get_total_msg_users() -> int:
    with LOCK:
        try:
            CUR.execute('''
                SELECT COUNT(DISTINCT user_id) FROM msg_counter
            ''')
            return CUR.fetchone()[0]
        except Exception as error:
            my_log.log2(f'my_msg_counter:get_total_msg_users {error}')
            return 0


def get_total_msg_users_in_days(days: int) -> int:
    access_time = time.time() - days * 24 * 60 * 60
    with LOCK:
        try:
            CUR.execute('''
                SELECT COUNT(DISTINCT user_id) FROM msg_counter
                WHERE access_time > ?
            ''', (access_time,))
            return CUR.fetchone()[0]
        except Exception as error:
            my_log.log2(f'my_msg_counter:get_total_msg_users_in_days {error}')
            return 0


def count_new_user_in_days(days: int) -> int:
    '''Посчитать сколько юзеров не имеют ни одного сообщения раньше чем за days дней'''
    access_time = time.time() - days * 24 * 60 * 60
    with LOCK:
        try:
            # Найти всех пользователей, которые имели сообщения позже заданного времени
            CUR.execute('''
                SELECT user_id
                FROM msg_counter
                WHERE access_time > ?
                GROUP BY user_id
            ''', (access_time,))
            recent_users = set(row[0] for row in CUR.fetchall())

            if not recent_users:
                return 0

            # Найти всех пользователей, которые не имели сообщения раньше заданного времени
            recent_users_str = ','.join('?' for _ in recent_users)
            CUR.execute(f'''
                SELECT COUNT(DISTINCT user_id)
                FROM msg_counter
                WHERE user_id IN ({recent_users_str})
                AND access_time <= ?
            ''', (*recent_users, access_time))

            found_users = set(row[0] for row in CUR.fetchall())
            new_users_count = len(recent_users - found_users)
            return new_users_count
        except Exception as error:
            my_log.log2(f'my_msg_counter:count_new_user_in_days {error}')
            return 0


if __name__ == '__main__':
    pass
    init()
    print(get_total_msg_users_in_days(30))
    print(count_new_user_in_days(30))

    # for x in range(10000000):
    #     uid = random.choice(('user1','user2', 'user3', 'user4', 'user5', 'user6', 'user7', 'user8', 'user9', 'user10'))
    #     model = random.choice(('model1','model2', 'model3', 'model4', 'model5', 'model6', 'model7', 'model8', 'model9', 'model10'))
    #     add_msg(uid, model)
    #     print(x, end='\r\r\r\r\r')

    # for x in range(10000000):
    #     a = count_msgs('user1', 'all', 10000)
    #     b = count_msgs('user1', 'model5', 10000)
    #     c = count_msgs_all()
    #     print(x, end='\r\r\r\r\r')

    # print(count_msgs('test', 'gpt4o', 1000000))

    close()
