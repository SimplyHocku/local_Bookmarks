import sqlite3


def convert_date(values):
    day = values[2]
    month = values[1]
    year = values[0]
    return f"{day}.{month}.{year}"


def get_info_from_db_for_edit(cur_bd, table_name, record_name):
    with sqlite3.connect(cur_bd) as conn:
        cur = conn.cursor()
        res = cur.execute("""
                    SELECT * FROM `{table_name}`
                    WHERE `name` = ?
                    """.format(table_name=table_name),
                          (record_name,)).fetchall()
        return res