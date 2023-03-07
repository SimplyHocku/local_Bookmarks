import pathlib
import sqlite3


def connect_to_db(path_to_db):
    def upper_wrapper(function):
        def wrapper():
            with sqlite3.connect(path_to_db) as conn:
                cur = conn.cursor()
                result = function(cur)
                conn.commit()
                return result

        return wrapper

    return upper_wrapper


@connect_to_db(pathlib.Path("databases/default.db"))
def test(cursor):
    res = cursor.execute("""
    SELECT * from `Аниме`;
    """).fetchall()
    # print(res)
    return res


enter = test()
print(enter)
