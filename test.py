import psycopg2

con = psycopg2.connect(
    database="default",
    user="postgres",
    password="hocku23",
    host="/home/hocku/PycharmProjects/local_Bookmarks/databases",
    port="5432"
)

con.execute("SELECT * FROM 'Чика1'")

