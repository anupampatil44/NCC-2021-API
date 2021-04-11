import os
import resource
import subprocess

path_users_code = 'code_related/usersCode/'
standard_data = 'code_related/standard/'

signals = {
    0: 'AC',  # Correct ans

    1: 'CTE',  # compile time error
    127: 'CTE',
    # 256: 'C.T.E',

    # All of these codes(exit codes of a process) are of the format 128 + signal code generated by child process

    159: 'AT',  # 31 SIGSYS (When system call doent match)
    135: 'AT',  # Bus error 7 int x[10000000000000]

    136: 'RTE',  # SIGFPE sig -> 8 floating point exception
    139: 'RTE',  # (128 + 11) -> 11 SIGSEGV (Invalid memory reference)

    137: 'TLE',  # SIGKILL 9  (Time limit exceeded or resource violation killed by setprlimit)

    'wa': 'WA',  # Wrong answer
}

#comparing the output of the ideal answer to the user's code answer
def compare(user_out, e_out):
    user = open(user_out, "r")
    expected = open(e_out, "r")

    lines_user = user.read()
    lines_user=lines_user.rstrip()
    lines_expected = expected.read()
    lines_expected=lines_expected.rstrip()
    user.close()
    expected.close()

    if lines_user == lines_expected:
        return 0
    else:
        return 'wa'

def get_quota(qno, test_case_no,lang):
    if test_case_no == 7:
        test_case_no = 6
    if(lang=="py"):
        descrip_path = standard_data + 'quotas/question{}/pyquota{}.txt'.format(qno, test_case_no)
    else:
        descrip_path = standard_data + 'quotas/question{}/quota{}.txt'.format(qno, test_case_no)

    descrip_f = open(descrip_path)

    lines = descrip_f.readlines()
    time = lines[0].strip()
    mem = lines[1].strip()  # memory

    quota = {
        'time': int(time),
        'mem': int(mem),
    }
    return quota



def initialize_quota(quota):
    cpu_time = quota['time']
    mem = quota['mem']

    def setlimits():
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_time, cpu_time))
        resource.setrlimit(resource.RLIMIT_AS, (mem, mem))
        # resource.setrlimit(resource.RLIMIT_STACK, (1310720, 1310720))

    return setlimits



def compile_code(user_question_path, code_file_path, err_file): #for c and cpp codes only
    lang = code_file_path.split('.')[1]
    print("User err path:", err_file)
    if lang == 'c':
        rc = os.system(
            "gcc" + " -o " + user_question_path + 'exe ' + code_file_path + ' -lseccomp ' + '-lm 2>' + err_file)
    else:
        rc = os.system(
            "g++" + " -o " + user_question_path + 'exe ' + code_file_path + ' -lseccomp ' + '-lm 2>' + err_file)

    return rc  # return 0 for success and 1 for error



def run_in_sandbox(exec_path, lang, ipf, opf, errf, quota):
    if lang == 'py':
        child = subprocess.Popen(
            ['python3 ' + exec_path], preexec_fn=initialize_quota(quota),
            stdin=ipf, stdout=opf, stderr=errf, shell=True
        )
    else:
        child = subprocess.Popen(
            ['./' + exec_path], preexec_fn=initialize_quota(quota),
            stdin=ipf, stdout=opf, stderr=errf, shell=True
        )

    child.wait()
    rc = child.returncode

    if rc < 0:
        return 128 - rc
    else:
        return rc


def run_test_case(test_case_no,user_que_path,code_file_path,lang,qno,custominput):
    if custominput=="true":
        input_file=user_que_path+"custominput.txt"
    else:
        input_file=standard_data+'input/question{}/input{}.txt'.format(qno,test_case_no)

    input_file=open(input_file,'r')

    user_output=user_que_path+'output{}.txt'.format(test_case_no)
    user_op_file=open(user_output,"w+")

    quota=get_quota(qno,test_case_no,lang)

    error_path=user_que_path+'error.txt'
    error_file=open(error_path,'w+')

    if lang == 'py':
        exec_file = code_file_path

    else:
        exec_file = user_que_path + 'exe'

    process_code = run_in_sandbox(
        exec_file,
        lang,
        input_file,
        user_op_file,
        error_file,
        quota)

    input_file.close()
    user_op_file.close()
    error_file.close()

    e_output_file = standard_data + 'output/question{}/expected_output{}.txt'.format(qno, test_case_no)

    if process_code == 0:
        result_value = compare(user_op_file, e_output_file)
        return result_value

    return process_code


def exec(username, qno, lang, test_cases=0, custominput="false", attempts=None, run=False):
    user_question_path = path_users_code + '{}/question{}/'.format(username, qno)
    if run:
        code_file=user_question_path+'code.{}'.format(lang)
    else:
        code_file = user_question_path + 'code{}.{}'.format(attempts,lang)

    py_sandbox='judge/pysand.py'

    with open(user_question_path + 'temp.py', 'w+') as file:
        sand = open(py_sandbox, 'r')
        file.write(sand.read())
        sand.close()

    error_file=user_question_path+'error.txt'

    result_codes=[]


    if(lang!='py'):
        compilestat=compile_code(user_question_path, code_file, error_file)
        if(compilestat!=0):
            result_codes=["CTE"]*test_cases
            return result_codes


    if run:
        process_code = run_test_case(
            test_case_no=7, # 7 corresponds to the sample input testcase
            user_que_path=user_question_path,
            code_file_path=code_file,
            lang=lang,
            qno=qno,
            custominput=custominput,
        )
        print("pc", process_code)
        result_codes.append(signals[process_code])

    else:
        for i in range(1, test_cases+1):
            process_code = run_test_case(
                test_case_no=i,
                user_que_path=user_question_path,
                code_file_path=code_file,
                lang=lang,
                qno=qno,
                custominput=custominput,
            )
            print("pc", process_code)
            result_codes.append(signals[process_code])
            # clean_up(user_question_path)

    return result_codes
