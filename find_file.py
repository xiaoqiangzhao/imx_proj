#! /home/b51816/localpython/python3/bin/python3
from jay_file_manager import jay_file_manager
import os, sys
from optparse import OptionParser

ff = jay_file_manager()
parser = OptionParser()
parser.add_option("-u","--update", action="store_true", dest = "update_db", default = False, help = "force to update the database for current project or directory")
parser.add_option("-n","--name", action="store", dest = "name", help = "target file name")
parser.add_option("-s","--specific", action="store", dest="limit", help ="help to locate specific results ")
(options, args) = parser.parse_args()

if options.update_db :
    ff.generate_file_list()
    ff.initial_tables()
    ff.list2db()

limits = []
results = []
if options.name:
    if options.limit:
        limits = options.limit.split(',')
    file_extention = os.path.splitext(options.name)[1][1:]
    if file_extention in ff.filetarget:
        results = results + ff.search_file(file_extention, options.name, False, limits)
    else:
        for table in ff.filetarget:
            results = results + ff.search_file(table, options.name, False, limits)

    for i in range(len(results)):
        print("%d : %s" %(i,results[i]))
    select = input("Please choose one to open:")
    select = int(select)
    if select in range(len(results)):
        os.system("gvim %s" %(results[select]))
    else:
        print("illeagel choose")
        sys.exit()
