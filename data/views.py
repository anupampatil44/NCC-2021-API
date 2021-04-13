import json
import os
import re

from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response

from judge.views import exec
from rest_framework.permissions import IsAuthenticated  # <-- Here
# hello world of DRF -

path_users_code = 'code_related/usersCode/'
standard_data = 'code_related/standard/'


class HelloView(APIView):
    # permission_classes = (IsAuthenticated,)
    def get(self, request):
        content = {'message': 'Hello, World!'}
        return Response(content)


def change_file_content(content, extension, code_file):
    if extension != 'py':
        sandbox_header = '#include"../../../include/sandbox.h"\n'
        try:
            # Inject the function call for install filters in the user code file
            # Issue with design this way (look for a better solution (maybe docker))
            # multiple main strings
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

    else:
        with open(code_file, 'w+') as f:
            f.write('import temp\n')
            f.write(content)
            f.close()




@api_view(['POST',])
def coderun(request):
    # {
    #     "username":"dummy",
    #     "qno":1,
    #     "code": "\"hello\"",
    #     "lang": "py",
    #     "ici": false,
    #     "ci":"NA"
    # }

    data=request.data
    print(request.data)
    user_question_path = path_users_code + '{}/question{}/'.format(data["username"], data["qno"])
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
        username=data["username"],
        qno=data["qno"],
        lang=data["lang"],
        custominput=data["ici"],
        run=True,

    )[0]

    # exp_op_path = standard + "output/question{}/expected_output7.txt".format(que_no)

    op_path = user_question_path + "output7.txt"
    err_path = user_question_path + "error.txt"

    op_f = open(op_path, 'r')
    err_f = open(err_path, 'r')
    # exp_f = open(exp_op_path, 'r')

    errcodes = ['CTE', 'RTE', 'AC', 'TLE']

    if status in errcodes:
        if status == "CTE":
            err_text = err_f.read()
            if (data["lang"] != "py"):
                err_text = re.sub('data/.*?:', '', err_text)  # regular expression
                err_text = re.sub('install_filters\(\);', '', err_text)
            else:
                err_text = re.sub('File(.*?)(\.cpp:|\.py",|\.c:)', '', err_text)
            actual = err_text
        else:
            actual = ""
    else:
        if status == 'AC':
            status = 'OK'
        actual = op_f.read()

    op_f.close()
    err_f.close()
    response_data = {}
    response_data["status"] = status
    response_data["output"] = actual
    print("response:\n",response_data)
    return Response(response_data)