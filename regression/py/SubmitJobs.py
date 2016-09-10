import os
import sys
import json
from termcolor import colored

info_color = {'PASS':'green','FAILED':'red','COMPILE_ERROR':'yellow','NO_ARG':'blue','MAKE_ERROR_OR_NOT_RUN':'magenta','RUNNING':'cyan'}

BASE_DIR = '/proj/imx6sll/design/workarea/b51816/JAY_HOME/my_git/repository/imx_proj/regression'

class SubmitJobs:
    def __init__(self,json_file,block='soc_tb'):
        self.json_file = json_file
        self.project = os.getenv('PROJECT','')
        self.block = block
        self.workdir = os.getenv('DESIGN_DIR',os.path.dirname(os.path.abspath(sys.argv[0])))
        self.bom = os.path.basename(self.workdir)
        self.cwp = BASE_DIR
        with open(self.json_file,'r') as j:
            self.testdict = json.load(j)
        self.vectors = self.testdict.keys()
        if not os.path.isdir(os.path.join(self.cwp,'RunShell')):
            os.chdir(self.cwp)
            os.system("mkdir RunShell")
        if not os.path.isdir(os.path.join(self.cwp,'RunShell',self.bom)):
            os.chdir(os.path.join(self.cwp,'RunShell'))
            os.system("mkdir {bom_dir}".format(bom_dir=self.bom))
        self.shell_dir = os.path.join(self.cwp,'RunShell',self.bom)


        print("#################################################")
        print("project : "+self.project)
        print("workarea : "+self.workdir)
        print("json file : "+self.json_file)

    def show_vectors(self):
        print(colored("\n".join(self.vectors),'green'))

    def analysis_log(self,vector):
        pass_text = 'Simulation completed Successfully'
        fail_text = 'Simulation completed with Errors'
        compile_error_text = 'An error occurred during parsing'
        block_size = 2048   ## get last 2048 bytes text from log file
        log_dir = os.path.join(self.workdir,'testbench/blocks/soc_tb/vectors/{vector}/logfiles'.format(vector=vector))
        os.chdir(log_dir)

        if not vector in self.testdict:
            print("No Such Vector {vector}".format(vector=vector))
            sys.exit()

        with_arg_test = []
        no_arg_test = []
        make_error_or_not_run_test = []
        pass_test = []
        fail_test = []
        compile_error_test = []
        running_test = []
        test_checked = self.check_testlist(self.testdict[vector],vector)
        with_arg_test = test_checked['test_with_arg']
        no_arg_test = test_checked['test_no_arg']
        for test in with_arg_test:
            start_seek = 0
            test_logfile = test['pat']+'verilog_{group}.log'.format(group=test['groups'])
            if not os.path.isfile(test_logfile):
                test['Status'] = "MAKE_ERROR_OR_NOT_RUN"
                make_error_or_not_run_test.append(test)
                continue
            test['review'] = test_logfile
            with open(test_logfile,'r') as log:
                log.seek(0,2)  ## get the size
                log_size = log.tell()
                if log_size > block_size:
                    start_seek = log_size - block_size
                log.seek(start_seek,0)
                log_text = log.read()
                if log_text.count(pass_text):
                    test['Status'] = 'PASS'
                    pass_test.append(test)
                elif log_text.count(fail_text):
                    test['Status'] = 'FAILED'
                    fail_test.append(test)
                elif log_text.count(compile_error_text):
                    test['Status'] = 'COMPILE_ERROR'
                    compile_error_test.append(test)
                else:
                    test['Status'] = 'RUNNING'
                    running_test.append(test)
        result = {'PASS':pass_test,'FAILED':fail_test,'COMPILE_ERROR':compile_error_test,'RUNNING':running_test,'NO_ARG':no_arg_test,'MAKE_ERROR_OR_NOT_RUN':make_error_or_not_run_test}
        with open(vector+".json",'w') as f:
            json.dump(result,f)
        return result



    def show_results(self,vector,status='all'):
        log_dir = os.path.join(self.workdir,'testbench/blocks/soc_tb/vectors/{vector}/logfiles'.format(vector=vector))
        os.chdir(log_dir)
        json_file = vector+".json"
        if not os.path.isfile(json_file):
            print("JSON file for this vector not available, you may use analysis_log to generate one")
            return
        with open(json_file,'r') as f:
            results = json.load(f)
            if  status in results:
                print(colored('{:*^40s}'.format(status),info_color[status]))
                for test in results[status]:
                    print(colored("  {pattern}".format(pattern=test['pat']),info_color[status]))
            else:
                for i in results:
                    if results[i]:
                        # format_text = format()
                        print(colored('{:*^40s}'.format(i),info_color[i]))
                        for test in results[i]:
                            print(colored("  {pattern}".format(pattern=test['pat']),info_color[i]))


    def check_testlist(self,testlist,vector):
        arg_dir = os.path.join(self.workdir,'testbench/blocks/soc_tb/vectors/{vector}/stimulus/arg'.format(vector=vector))
        test_no_arg = []
        test_with_arg = []
        for test in testlist:
            arg_file = os.path.join(arg_dir,'{test}.arg'.format(test=test['pat']))
            if os.path.isfile(arg_file):
                test_with_arg.append(test)
            else:
                test['Status'] = 'NO_ARG'
                test_no_arg.append(test)
        return {'test_with_arg':test_with_arg,'test_no_arg':test_no_arg}

    def generate_sh(self,vector,priority=999):   #assume 999 the lowest priority
        # os.chdir(os.path.join(self.cwp,'RunShell',self.bom))
        if not vector in self.testdict:
            print("No Such Vector {vector}".format(vector=vector))
            sys.exit()
        self.vector = vector
        test_checked = self.check_testlist(self.testdict[self.vector],self.vector)
        self.testlist = test_checked['test_with_arg']
        test_no_arg = test_checked['test_no_arg']
        if test_no_arg:
            print("#################################################")
            print("Below Patterns Not Found:")
            for test in test_no_arg:
                print("    "+test['pat'])
            print("#################################################")

        self.group = self.testlist[0]['groups']  ## take the first to sample group info
        self.priority = priority
        self.so = 'testbench/blocks/soc_tb/tool_data/verilog/{lib_dir}/INCA_libs/worklib/cfg1/config/_sv_export.so'.format(lib_dir=self.group+'.linux26_64bit')
        self.shell_script = os.path.join(self.shell_dir,"runsim_"+vector+".sh")
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
                if test['priority'] > self.priority:  ## skip the test with lower priority
                    continue
                job_name = "simulate_"+test['pat']
                depend_list.append("ended({job_name})".format(job_name=job_name))
                simulate_job = "bsub -q priority -J {job_name} {depend_str} soc verilog -irun -block {block} -session {session} -bc {bc} -vectors {vector} -test {test} -keeptemps -bbox -no_compile  -no_save_db\n".format(job_name=job_name, block=self.block, bc=self.group, session=self.group, vector= self.vector, test= test['pat'], depend_str = depend_str)
                f.write(simulate_job)
            simulate_finish_depend = '-w "{depend}"'.format(depend=" && ".join(depend_list))
            cmd = "echo '{vector} Finished' | mail -s Submit jay.zhao@nxp.com".format(vector=vector)
            analysis_output_job = "bsub -q priority  {depend} {cmd}".format(depend=simulate_finish_depend , cmd = cmd)
            f.write(analysis_output_job)
        os.system("chmod 750 {shell_script}".format(shell_script=self.shell_script))


if __name__ == "__main__":
    test = SubmitJobs('/home/b51816/my_git/repository/imx_proj/regression/py/iMX8QM_Security_Verification_Plan.json')
    test.generate_sh('scu_sec_snvs')
    test.generate_sh('scu_sec_romcp')
    # results = test.analysis_log('scu_sec_snvs')
    results = test.analysis_log('scu_sec_romcp')
    test.show_results('scu_sec_romcp','PASS')
    # for i in results:
        # if results[i]:
            # # print(colored("################################################",info_color[i]))
            # print(colored(i,info_color[i]))
            # for test in results[i]:
                # print("    {name}".format(name=test['pat']))




