import json
import os
import re
from datetime import datetime

from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response

from judge.views import exec
from data.models import Question, Userdata, Submission
from rest_framework.permissions import IsAuthenticated  # <-- Here
# hello world of DRF -

# starttime = datetime.datetime(2021, 2, 1, 18, 0,0)


path_users_code = 'code_related/usersCode/'
standard_data = 'code_related/standard/'


class HelloView(APIView):
    # permission_classes = (IsAuthenticated,)
    def get(self, request):
        content = {'message': 'Hello, World!'}
        return Response(content)


def change_file_content(content, extension, code_file):
    print("current path:",os.getcwd())
    if extension != 'py':
        sandbox_header = '#include"{}/{}/sandbox.h"\n'.format(os.getcwd(),"judge")
        try:
            # Add the function call for install filters in the user code file
            # multiple main strings for identifying & inserting before and after main method in the c and cpp files.
            before_main = content.split('main')[0] + 'main'
            after_main = content.split('main')[1]
            index = after_main.find('{') + 1
            main = before_main + after_main[:index] + 'install_filters();' + after_main[index:]
            print(code_file)
            with open(code_file, 'w+') as f:
                f.write(sandbox_header)
                f.write(main)
                f.close()

        except IndexError:
            with open(code_file, 'w+') as f:
                f.write(content)
                f.close()

    else: #for python codes, direclty import the file with the filter call
        with open(code_file, 'w+') as f:
            f.write('import temp\n')
            f.write(content)
            f.close()





class coderun(APIView):
    # {
    #     "username":"dummy",
    #     "qno":1,
    #     "code": "print(\"hello\")",
    #     "lang": "py",
    #     "ici": false,
    #     "ci":"NA"
    # }
    def post(self,request):
        data=request.data
        user_question_path = path_users_code + '{}/question{}/'.format(request.user.username, data["qno"])
        code_file_path = user_question_path + 'code.{}'.format(data["lang"])
        if not os.path.exists(user_question_path):
            os.system('mkdir ' + user_question_path)
        print(data["ici"])
        if (data["ici"] == True):
            with open(user_question_path + "custominput.txt", 'w+') as cin:
                cin.write(data["ci"])

        code_f = open(code_file_path, 'w+')
        code_f.write(data["code"])
        code_f.close()

        change_file_content(data["code"], data["lang"], code_file_path)

        status = exec(
            username=request.user.username,
            qno=data["qno"],
            lang=data["lang"],
            custominput=data["ici"],
            run=True,

        )[0]
        print("status val: ",status)


        op_path = user_question_path + "output0.txt"
        err_path = user_question_path + "error.txt"

        op_f = open(op_path, 'r')
        err_f = open(err_path, 'r')

        errcodes = ['CTE', 'RTE', 'AT', 'TLE']
        actual=""
        if status in errcodes:
            if status == "CTE":
                err_text = err_f.read()
                if (data["lang"] != "py"):
                    err_text = re.sub('data/.*?:', '', err_text)  # regular expression
                    err_text = re.sub('install_filters\(\);', '', err_text)
                    err_text = re.sub('File(.*?)(\.cpp:|\.py",|\.c:)', '', err_text)
                    err_text = re.sub('code_related(.*?)(\.cpp:|\.py",|\.c:)', '', err_text)
                else:
                    err_text = re.sub('File(.*?)(\.cpp:|\.py",|\.c:)', '', err_text)
                    err_text = re.sub('code_related(.*?)(\.cpp:|\.py",|\.c:)', '', err_text)
                actual = err_text
            else:
                actual = ""
        else:
            if status == 'AC':
                status = 'OK'
            actual = op_f.read()
        print("output: ",actual)

        op_f.close()
        err_f.close()
        response_data = {}
        response_data["status"] = status
        response_data["output"] = actual
        print("response:\n",response_data)
        return Response(response_data)






class code_submit(APIView):
    # {
    #
    #     "qno":1,
    #     "code": "print(\"hello\")",
    #     "lang": "py",
    #
    #
    # }

    permission_classes = (IsAuthenticated,)

    def post(self,request):
        usert = request.user
        data=request.data

        que = Question.objects.get(pk=data["qno"])
        username=request.user.username
        user=Userdata.objects.get(username=usert)
        code=data["code"]
        lang=data["lang"]
        user_question_path = '{}/{}/question{}/'.format(path_users_code, username, data["qno"])
        if not os.path.exists(user_question_path):
            os.system('mkdir ' + user_question_path)
        print("qno:",data["qno"])
        code_file_path = os.getcwd()+'/'+user_question_path + "code{}.{}".format( 1,data["lang"])

        #adding the seccomp filtering code dependency to the code file:
        change_file_content(data["code"], data["lang"], code_file_path)

        testcase_values = exec(
            username=username,
            qno=data["qno"],
            lang=lang,
            test_cases=que.no_of_testcases,
        )

        code_f = open(code_file_path, 'w+')
        code_f.seek(0)
        code_f.write(code)
        code_f.close()



        sub = Submission(code=data["code"], user_id_fk=usert, question_id_fk=que, attempt=1) #modify attempt var later on

        error_text = ""

        epath = path_users_code + '/{}/question{}/error.txt'.format(username, data["qno"])
        if os.path.exists(epath):
            ef = open(epath, 'r')
            error_text = ef.read()
            if (data["lang"] != "py"):
                error_text = re.sub('data/.*?:', '', error_text)  # regular expression
                error_text = re.sub('install_filters\(\);', '', error_text)
                error_text = re.sub('File(.*?)(\.cpp:|\.py",|\.c:)', '', error_text)
                error_text = re.sub('code_related(.*?)(\.cpp:|\.py",|\.c:|\.iostream:)', '', error_text)
                error_text = re.sub('/usr(.*?)(\.cpp:|\.py",|\.c:|\.iostream:)', '', error_text)
            else:
                error_text = re.sub('File(.*?)(\.cpp:|\.py",|\.c:)', '', error_text)
                error_text = re.sub('code_related(.*?)(\.cpp:|\.py",|\.c:|\.iostream:)', '', error_text)
                error_text = re.sub('/usr/(.*?)(\.cpp:|\.py",|\.c:|\.ostream:)', '', error_text)

            ef.close()

        no_of_pass = 0
        iter = 0
        tle = 0
        wa = 0
        ac = 0
        cte = 0
        for i in testcase_values:
            if i == 'AC':
                no_of_pass += 1
                ac += 1

            elif (i == 'TLE'):
                tle += 1
            elif (i == 'WA'):
                wa += 1
            elif (i == "CTE"):
                cte += 1
            iter += 1

        sub.accuracy = (no_of_pass / que.no_of_testcases) * 100

        subscore=0
        status = ''  # overall Status
        if (ac == que.no_of_testcases):
            status += 'AC'
        elif (wa > 0 and tle == 0 and cte == 0):
            status += 'WA'
        elif (tle > 0 and cte == 0):
            status += 'TLE'
        else:
            status += "CTE"

        if status == 'AC':

            sub.score=subscore=100

            # if this is the first ac submission for the question then update the latest_ac_time variable
            if not Submission.objects.filter(user_id_fk=usert,question_id_fk=que).exists():
                user.latest_ac_time=datetime.now()
                user.totalScore += 100
                user.correctly_solved+=1
            else:
                query=Submission.objects.filter(user_id_fk=usert,question_id_fk=que).order_by('-score')[0].score
                if(query<100):  #100 is max. marks per question
                    inc=100-query
                    user.latest_ac_time = datetime.now()
                    user.totalScore += inc
                    user.correctly_solved += 1



            que.total_attempts+=1
            que.correct_attempts+=1
            if not Submission.objects.filter(user_id_fk=usert,question_id_fk=que).exists():
                user.attempted+=1

        else:
            if(user.junior==True):
                print("in junior")
                correcttc=0
                for i in testcase_values:
                    if i=="AC":
                        correcttc+=1
                tempscore=int((correcttc/que.no_of_testcases)*100)
                print("tempscore",tempscore)
                sub.score = subscore =tempscore
                if ((Submission.objects.filter(user_id_fk=usert,question_id_fk=que).exists()) and Submission.objects.filter(user_id_fk=usert,question_id_fk=que).order_by('-score')[0].score<tempscore):
                    q=Submission.objects.filter(user_id_fk=usert,question_id_fk=que).order_by('-score')[0]
                    increment=tempscore-q.score
                    user.totalScore+=increment
                    que.total_attempts += 1
                    user.latest_ac_time = datetime.now()

                else:
                    if(not Submission.objects.filter(user_id_fk=usert,question_id_fk=que).exists()):
                        user.totalScore+=tempscore
                        que.total_attempts += 1

            else:
                que.total_attempts += 1

            if not Submission.objects.filter(user_id_fk=usert, question_id_fk=que).exists():
                user.attempted += 1
                user.latest_ac_time = datetime.now()



        sub.status=status
        sub.language=data["lang"]
        sub.save()
        user.save()
        que.save()
        testcases={'status':status,"submission_score":subscore,"test_case_status":testcase_values,"console_out":error_text}
        print("testcase_values:",testcase_values)
        return Response(testcases)






