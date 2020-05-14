import sqlite3

class DBConnection:
    insert_query = 'INSERT INTO links (term, ind, href) VALUES ("%s", "%d", "%s")'
    select_query = 'SELECT href FROM links WHERE term="%s" and ind="%d"'
    update_query = 'UPDATE links SET href="%s" where term="%s"'

    def __init__(self, db=':memory:'):
        self.conn = sqlite3.connect(db)
        c = self.conn.cursor()
        # Create table command
        try:
            c.execute('''CREATE TABLE links
                         (id int primary key autoincrement, term text not null, ind int, href text)''')
            self.conn.commit()
        except sqlite3.OperationalError:
            pass

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.conn.close()

