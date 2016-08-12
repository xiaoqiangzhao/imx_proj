
def IsTableExist(cursor,table_name):
    cursor.execute('select name from sqlite_master where type="table" and name = ?',(table_name,))
    table=cursor.fetchall()
    if table:
        print("Table %s Exist" % table_name)
        return True
    else:
        return False
