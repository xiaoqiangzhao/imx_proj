import os
import sys
import json

class SubmitJobs:
    def __init__(self,json_file,block='soc_tb'):
        self.json_file = json_file
        self.project = os.getenv('PROJECT','')
        self.block = block
        self.workdir = os.getenv('DESIGN_DIR',os.path.dirname(os.path.abspath(sys.argv[0])))
        self.testlist = []
        with open(self.json_file,'r') as j:
            self.testlist = json.load(j)

        self.group = self.testlist[0]['groups']
        self.vector = self.testlist[0]['vec']
        print("project : "+self.project)
        print("workarea : "+self.workdir)
        print("json file : "+self.json_file)
        print("group : "+self.group)
        print("vector : "+self.vector)

    def generate_sh(self):
        self.so = 'testbench/blocks/soc_tb/tool_data/verilog/{lib_dir}/INCA_libs/worklib/cfg1/config/_sv_export.so'.format(lib_dir=self.group+'.linux26_64bit')
        self.shell_script = self.vector+".sh"
        compile_job_name = 'compile_'+self.group
        compile_job = "bsub -q priority -J {job_name} soc verilog -irun -block {block} -bc {bc} -session {session} -keeptemps -bbox -no_simulate \n".format(job_name='compile_'+self.group  , block=self.block, bc=self.group, session=self.group)

        with open(self.shell_script,'w') as f:
            f.write("#!/bin/sh\n")
            if os.path.isfile(os.path.join(self.workdir,self.so)):
                depend_str = ""
            else:
                f.write(compile_job)
                depend_str = '-w "ended({compile_job_name})"'.format(compile_job_name = compile_job_name)
            simulate_finish_depend = ""
            depend_list = []
            for test in self.testlist:
                job_name = "simulate_"+test['pat']
                depend_list.append("ended({job_name})".format(job_name=job_name))
                simulate_job = "bsub -q normal -J {job_name} soc verilog -irun -block {block} -session {session} -bc {bc} -vectors {vector} -test {test} -keeptemps -bbox -no_compile \n".format(job_name=job_name, block=self.block, bc=self.group, session=self.group, vector= self.vector, test= test['pat'])
                f.write(simulate_job)
            simulate_finish_depend = '-w "{depend}"'.format(depend=" && ".join(depend_list))
            cmd = "echo 'Finished'\n"
            analysis_output_job = "bsub -q priority {depend} {cmd}".format(depend=simulate_finish_depend , cmd = cmd)
            f.write(analysis_output_job)


if __name__ == "__main__":
    test = SubmitJobs('test.json')
    test.generate_sh()




