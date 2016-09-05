import os
import sys
import sqlite3
from get_files import get_files
from contextlib import contextmanager
from jay_wraps import time_cost
from jay_sqlite3 import IsTableExist

@contextmanager
def opendatabase(db):
    # print("connect to "+db)
    mx_conn = sqlite3.connect(db)
    mx_cursor = mx_conn.cursor()
    try:
        yield mx_cursor
    finally:
        # print("close and commit "+db)
        mx_cursor.close()
        mx_conn.commit()
        mx_conn.close()
class jay_file_manager(object):
    def __init__(self, *args):
        self.project = os.getenv('PROJECT','jay_files')
        self.workdir = os.getenv('DESIGN_DIR',os.path.dirname(os.path.abspath(sys.argv[0])))
        self.cwp = os.path.dirname(os.path.abspath(os.path.realpath(sys.argv[0])))
        self.filelist = self.project + ".list"
        self.filelist = os.path.join(self.cwp,self.filelist)
        self.file_search = get_files(list_name = self.filelist, path = self.workdir)
        self.database = self.project + ".db"
        self.database = os.path.join(self.cwp,self.database)
        if args:
            self.filetarget = args
        else:
            self.filetarget = ['c','h','v','vh','sv','pl','py','pm','vhd', 's', 'sh', 'arg']
        print("target file type are : "+" ".join(self.filetarget))
        print("target project is : " + self.project)
        print("target directory : "+self.workdir)
        print("current directory : "+self.cwp)

    @time_cost
    def generate_file_list(self, replace = True):
        self.file_search.search_files(*self.filetarget, replace = replace)

    @time_cost
    def initial_tables(self):
        with opendatabase(self.database) as cursor:
            for table_name in self.filetarget :
                if IsTableExist(cursor, table_name):
                    cursor.execute('drop table %s'% table_name)
                print("Create Table %s" %table_name)
                cursor.execute('create table %s (id integer primary key autoincrement, path tinytext, filename tinytext)' % table_name)

    @time_cost
    def list2db(self):
        with opendatabase(self.database) as cursor:
            with open(self.filelist,'r') as fd:
                for line in fd:
                    line=line.strip()
                    (path, filename) = (os.path.dirname(line), os.path.basename(line))
                    workdir_list = self.workdir.split('/')
                    path_list = path.split('/')
                    relative_path = '/'.join(path_list[len(workdir_list):])
                    # print(relative_path)
                    cursor.execute('insert into %s (path, filename) values (?,?)' % os.path.splitext(line)[1][1:], (relative_path, filename))

    # @time_cost
    def search_file(self, table, name, precise = True, limits = []):
        final_result = []
        if precise:
            search_operate = '='
            search_name = name
        else:
            search_operate = 'like'
            search_name = '%'+name+'%'
        with opendatabase(self.database) as cursor:
            # print('select * from %s filename %s %s' %(table , search_operate, search_name))
            cursor.execute('select * from %s where filename %s ?' % (table ,search_operate), (search_name,))
            results = cursor.fetchall()
            # print(results.__len__())
        if results.__len__() :
            for item in results:
                if not limits:
                    final_result.append(os.path.join(os.path.abspath(self.workdir),item[1],item[2]))
                else:
                    key_words = item[1].split('/')
                    key_match = True
                    for limit in limits:
                        if not limit in key_words:
                            key_match = False
                            break
                    if key_match:
                        final_result.append(os.path.join(os.path.abspath(self.workdir),item[1],item[2]))
        return final_result



if __name__=='__main__':
    test = jay_file_manager()
    # test.generate_file_list()
    # test.initial_tables()
    # test.list2db()
    # test.search_file('c','soc_api', False,['arm_gnu',])
    test.search_file('s','cache', False,[])




# with opendatabase("./test.db") as cursor:
     # cursor.execute('create table testtable ( row varchar(20) primary key,n_p tinytext, start_addr blob, end_addr blob,hex_s_a varchar(40),hex_e_a varchar(40), region varchar(40))')

