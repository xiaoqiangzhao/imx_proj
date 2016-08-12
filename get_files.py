#! /home/b51816/local/bin/python3
import os
import sys
class get_files(object):
   '''
   example:
      my_get_files = get_files(
         path="my_path",            ##  set search path
         list_name = "file_list"    ##  set output file
         replace = True             ##  replace the file if existing  or add to the end when set to False
         )
      my_get_files.search_files(
         path="my_path",            ##  override search path
         list_name = "file_list"    ##  override output file
         replace = True             ##  override replace
         )
   '''

   def __init__(self,**kwargs):
      self._path = os.getcwd()
      self._list_name = "file_list"
      self.replace = True
      if "path" in kwargs:
         self._path = kwargs["path"]
      if "list_name" in kwargs:
         self._list_name = kwargs["list_name"]
      if "replace" in kwargs:
         if not kwargs["replace"] in (True, False):
            raise ValueError("replace arg should be True or False")
         self.replace = kwargs["replace"]



   def search_files(self,*args,**kwargs):
      if not args:
         raise ValueError("no args specified")

      if "path" in kwargs:
         self._path = kwargs["path"]
      if "list_name" in kwargs:
         self._list_name = kwargs["list_name"]
      if "replace" in kwargs:
         if not kwargs["replace"] in (True, False):
            raise ValueError("replace arg should be True or False")
         self.replace = kwargs["replace"]

      if self.replace:
         search_mode = " > "
      else:
         search_mode = " >> "
      cmd = ("find %s -follow -name '*.%s' "%(self._path,args[0],))
      print("search directory: %s" %(self._path,))
      print("search target:")
      for t in args:
         cmd = cmd + '-o -name  "*.' + t +'" '
         print(t)
      cmd = cmd + search_mode + self._list_name
      print("search cmd:\n"+cmd)
      os.system(cmd)

   def search_multi_dir(self, *args, **kwargs):
      if not args:
         raise ValueError("no args specified")

      if "paths" in kwargs:
         paths = kwargs["paths"]
         if not (isinstance(paths,list)):   ## check if paths is a list
            raise ValueError("the arg for paths should be a list")
      if "list_name" in kwargs:
         self._list_name = kwargs["list_name"]
      if "replace" in kwargs:
         if not kwargs["replace"] in (True, False):
            raise ValueError("replace arg should be True or False")
         self.replace = kwargs["replace"]
      first_path = paths.pop(0)
      self.search_files(*args, path = first_path, replace = self.replace)
      for p in paths:
         self.search_files(*args, path = p, replace = False)


   pass

if __name__=='__main__':
   test_c = get_files(list_name="file_list_1",path="./")
   # test_c.search_files("sv","py",replace = True)
   test_c.search_files("sv","py",replace = False, path = os.path.dirname(os.path.abspath(sys.argv[0])))
#   test_c.search_multi_dir("sv", "py", replace = True, paths = ["/proj/ult1/design/workarea/b51816/ULT1_TO1P1_PROD/blocks/gpcv2/testbench", os.path.dirname(os.path.abspath(sys.argv[0]))])
