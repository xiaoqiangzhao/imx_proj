#! /home/b51816/localpython/python3/bin/python3
import sys
import re
import os
import sqlite3
import getopt
from xlsx import Workbook
# from openpyxl import load_workbook
###  strinfo_hex_in_v = re.compile('32\'h')
#### start of function find_help()
def find_help():
   print('''
#################################################################
Author:  Jay Zhao.
Email:   zq496547199@126.com 
Phone:   13501675484
version: 1.0
Options: 
             -f : choose xlsx file
             -u : force update database, when this option is opened
                  one legal xlsx file should be identified
             --dir  : set work area; default is /home/b51816/my_git/repository/imx_proj/imx_db
             --name : locate memory or IP by name
             --addr : locate memory or IP by address
             --help : print help
Example: jay_memory_locate.py -f xxx.xlsx -u   ### update db
         jay_memory_locate.py --name=SNVS --addr=02010000 ### find all IP section 
                      with name of SNVS or with memory allocated including 0x02010000
Notice:  v-style like 32'hxxxxxxxx is not supported in current version
################################################################''')
   sys.exit()
#### end of function find_help()

name = False
xlsx_file = False
update = False
addr = False
table = False
work_dir = "/home/b51816/my_git/repository/imx_proj/imx_db"
s_a = 0 # Start Address
e_a = 1 # End Address
region = 2 # Region
n_p =3  # NIC PORT
try:
   opts,args = getopt.getopt(sys.argv[1:],"f:ut:",["name=","addr=","dir=","help"])
except getopt.GetoptError:
   print("Bad Options")

class ArgError(BaseException):
   pass

for o,a in opts:
   if o in ("-f"):
      xlsx_file = a
   if o in ("-u"):
      update = True
   if o in ("--name"):
      name = a
   if o in ("--addr"):
      addr = a
   if o in ("-t"):
      table = a
   if o in ("--dir"):
      work_dir = a
   if o in ("--help"):
      find_help()

if update and (not xlsx_file):
   raise ArgError("no xlsc specified for updating database")
if (not update) and (not name) and(not addr):
   raise ArgError("neither name or address specified")
if xlsx_file and ( not os.path.isfile(xlsx_file)):
   raise ArgError("no such file found for %s" % xlsx_file)
if xlsx_file and os.path.isfile(xlsx_file):
   xlsx_file = os.path.abspath(xlsx_file)
#### change work dir
os.chdir(work_dir)

#### define updata_db
def IsTableExist(cursor,table):
   cursor.execute('select name from sqlite_master where type="table" and name = ?',(table,))
   table=cursor.fetchall()
   print(table)
   if table:
      return True
   else:
      return False

proj_name = os.getenv('PROJECT','jay_proj')  ### get from ENV or default
proj_db = proj_name+'.db'
proj_aips = proj_name+'_aips_map'
def update_db(xlsx_table):

   print("connecting database: %s" % os.path.abspath(proj_db))
   mx_conn = sqlite3.connect(proj_db)
   mx_cursor = mx_conn.cursor()

   for i_t in xlsx_table:
      up_table =i_t.replace(' ','_')
      print(up_table)
      if IsTableExist(mx_cursor,up_table):  ### check if table exist
         print("table %s already exist, delete and re-generate" % up_table)
         mx_cursor.execute('drop table %s'% up_table)

      mx_cursor.execute('create table %s ( row varchar(20) primary key,n_p tinytext, start_addr blob, end_addr blob,hex_s_a varchar(40),hex_e_a varchar(40), region varchar(40))'% up_table )
      mx = Workbook(xlsx_file)
      aips_sheet = mx[i_t]
      mx_cursor.execute('insert into %s (row,n_p,region) values (?,?,?)'% up_table,('id',xlsx_file,i_t))  ## special row to indicate xlsx file and sheet
      for row,cells in aips_sheet.rowsIter():
         if re.match(r'^[\d_A-F]+$',cells[s_a].value):
            if cells[region].value:
               set_region=cells[region].value
            int_s_a=int(cells[s_a].value.replace("_",''),16)
            int_e_a=int(cells[e_a].value.replace("_",''),16)

            mx_cursor.execute('insert into %s (row,n_p,start_addr,end_addr,hex_s_a,hex_e_a,region) values (?,?,?,?,?,?,?)'%up_table,(row,cells[n_p].value,int_s_a ,int_e_a ,cells[s_a].value,cells[e_a].value, set_region))
   mx_cursor.rowcount
   mx_cursor.close()
   mx_conn.commit()
   mx_conn.close()
#### end of definition of update_db
if xlsx_file and update and (os.path.isfile(xlsx_file)):
   update_db(['AIPS Maps','Main Map'])
def search_item(db,table,name=False,addr=False):
   my_conn = sqlite3.connect(db)
   my_cursor = my_conn.cursor()
   my_cursor.execute('select n_p,region from %s where row="id"'%table)
   my_results = my_cursor.fetchall()
   valid_xlsx = my_results[0][0]
   valid_sheet = my_results[0][1]
   print ("----------------------------------------------------------------")
   print ("Reference DataBase: "+os.path.abspath(db))
   print ("Reference XLSX    : "+valid_xlsx)
   print ("Reference Sheet   : "+valid_sheet)
   if name:
      target = "%"+name+"%"   ### to use place-holder we need to add wildchar to plain text
      my_cursor.execute('select n_p,hex_s_a,hex_e_a,region from %s where n_p like ? or region like ?'% table,(target,target))
      my_results=my_cursor.fetchall()
      print ("----------------------------------------------------------------")
      print ("Below are results for: "+name)
      if my_results:
         print ("----------------------------------------------------------------")
         for i in my_results:
            print(i)
         print ("----------------------------------------------------------------")
      else:
         print ("----------------------------------------------------------------")
         print ("---- No such item named %s in sheet %s" %(name,valid_sheet,))
         print ("----------------------------------------------------------------")
         search_item(proj_db,'AIPS_MAPS',name,addr)   ### if not found in Main_Map, try AIPS_MAPS
   if addr:
      search_addr = addr.replace('_','')
      search_addr = search_addr.replace('h','')  ### for usage in vim, v-style hex data
      if not re.match('^0x',search_addr):
         search_addr = "0x"+search_addr   
      my_cursor.execute('select n_p,hex_s_a,hex_e_a,region from %s where start_addr <=? and end_addr >= ? '% table,(int(search_addr,16),int(search_addr,16)))
      my_results=my_cursor.fetchall()
      print ("Below are results for: "+search_addr)
      if my_results:
         print ("----------------------------------------------------------------")
         for i in my_results:
            print(i)
            if table =="Main_Map" and i[3]=="Registers":
               search_item(proj_db,'AIPS_MAPS',name,addr)  ### if found Registers, search deeper in AIPS_MAPS
      else:
         print ("----------------------------------------------------------------")
         print ("---- No such item match address %s in %s" %(search_addr,valid_sheet,))
         print ("----------------------------------------------------------------")
   my_cursor.close()
   my_conn.commit()
   my_conn.close()
if name or addr:
   search_item(proj_db,'Main_Map',name,addr)
