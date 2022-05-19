from flask import Blueprint, request
import json
import subprocess
import os
from app import MyIP
from app.modules import loggers, statusCode, cmd_setter

logger = loggers.create_logger(__name__)

bp = Blueprint('ssploit',__name__, url_prefix='/ssploit')

CURRENT_DIR = os.path.abspath(os.getcwd())

# def subprocess_open(command):
#     popen = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
#     (stdoutdata, stderrdata) = popen.communicate()
#     return stdoutdata, stderrdata

from private.ports import WEB_SERVER_PORT

downloadURL = f"http://{MyIP}:{WEB_SERVER_PORT}/ssploit/download"





# @bp.route('/filter', methods=['POST'])
# def ssploit_filter():
#     if request.method=='GET':
#         logger.warning(f"{loggers.RED}[SSPLOIT] NOT GET{loggers.END}")
#         return {"status":statusCode.METHOD_ERROR}
#     getFromFront = request.get_data().decode()
#     getFromFront = json.loads(getFromFront)
#     src_ip = getFromFront['src_ip']
#     dst_ip = getFromFront['dst_ip']
#     service = getFromFront['service']
#     #stdoutdata, stderrdata = subprocess_open(f'searchsploit {service}')
#     # print(stdoutdata.decode('utf-8'))
#     #print(stdoutdata)
#     #return {"stdout":stdoutdata}
#     r = os.popen(f'searchsploit {service} -j').read()
#     # searchsploit service --colour
#     r = json.loads(r)
#     results = r["RESULTS_EXPLOIT"]
#     results.extend(r["RESULTS_PAPER"])
#     return {
#         "results":results
#     }

# @bp.route('/edit', methods=['POST'])
# def ssploit_edit():
#     if request.method=='GET':
#         logger.warning(f"{loggers.RED}[SSPLOIT] NOT GET{loggers.END}")
#         return {"status":statusCode.METHOD_ERROR}
#     getFromFront = request.get_data().decode()
#     getFromFront = json.loads(getFromFront)
#     script_number = getFromFront['script_number']

#     # searchsploit에서 파일 위치 가져오기
#     ssploit_res = os.popen(f"searchsploit -p {script_number} -j").read()
#     ssploit_res = ssploit_res.split("\n")
#     for i in ssploit_res:
#         if "Path" in i:
#             ssploit_path = i
#             break
#     ssploit_path = ssploit_path.split(":")[1].replace(" ","")
#     new_path = CURRENT_DIR+"/temp/tmp.py"
    
#     # 해당 파일 temp 밑으로 복사
#     os.system(f"cp {ssploit_path} {new_path}")

#     code = os.popen(f"cat {ssploit_path}").read()
#     print(code)

#     return {
#         "code": code
#     }

# @bp.route("/save", methods=['POST'])
# def ssploit_save():
#     if request.method=='GET':
#         logger.warning(f"{loggers.RED}[SSPLOIT] NOT GET{loggers.END}")
#         return {"status":statusCode.METHOD_ERROR}
#     getFromFront = request.get_data().decode()
#     getFromFront = json.loads(getFromFront)
#     edited_code = getFromFront['edited']
#     usage = getFromFront["usage"]
#     attack_id = int(getFromFront["attack_id"])
#     src_ip = getFromFront["src_ip"]
#     dst_ip = getFromFront["dst_ip"]


#     tmp_path = CURRENT_DIR+"/temp/tmp.py"
#     f = open(tmp_path,"w")
#     f.write(edited_code)
#     f.close()
    
#     filename = os.popen(f'searchsploit {attack_id} -j').read()
#     filename = json.loads(filename)

#     return {
#         "attack_id": attack_id,
#         "filename":filename["RESULTS_EXPLOIT"][0]["Path"].split("/")[-1],
# 		"type": "exploit-db",
#         "src_ip": src_ip,
#         "dst_ip": dst_ip,
#         "usage": usage,
#         "code": downloadURL
# 	}


@bp.route("/download")
def ssploit_download():
    tmp_path = CURRENT_DIR+"/temp/tmp.py"
    fbytes = bytearray(open(tmp_path,'rb').read())
    f_size = cmd_setter.file_size(tmp_path)
    encoded = bytearray(f_size)

    for i in range(f_size):
        encoded[i] = fbytes[i]^ord('X')
    return encoded


