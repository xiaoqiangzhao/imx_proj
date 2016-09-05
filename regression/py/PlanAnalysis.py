import os
import sys
from collections import namedtuple
from openpyxl import load_workbook
import json

class XlsxParser:
    def __init__(self,xlsx_file,sheet_name='razor_test_plan'):
        self.xlsx_file = xlsx_file
        self.file_prefix = os.path.splitext(os.path.basename(self.xlsx_file))[0]
        self.json_file = self.file_prefix+".json"
        self.sheet_name = sheet_name  #this sheet name is used in Razor
        print(self.file_prefix)
        if not os.path.isfile(self.xlsx_file):
            print("No Such File Exists")
            sys.exit()

    def row2list(self,row):
        l = []
        for cell in row[0:9]:    ## only these colums needed for regression
            l.append(cell.value)
        return l

    def parser(self):
        self.wb = load_workbook(self.xlsx_file,keep_vba=False)
        self.ws = self.wb.__getitem__(self.sheet_name)
        self.rows = self.ws.rows
        self.headings = self.row2list(self.rows[0])
        self.testtuple = namedtuple('testtuple',self.headings)
        self.testlist = []
        for i in self.rows[1:]:
            self.testlist.append(self.testtuple(*self.row2list(i))._asdict())
        with open(self.json_file,'w') as f:
            json.dump(self.testlist,f)





if __name__ == "__main__":
    xlsx_file = "/home/b51816/my_git/repository/imx_proj/regression/testplan/iMX8QM_Security_Verification_Plan.xlsx"
    test = XlsxParser(xlsx_file)
    test.parser()
    # print(test.headings)
    # with open('./plan.json','w') as f:
        # json.dump(test.testlist,f)




