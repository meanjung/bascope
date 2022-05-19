from flask import Blueprint, request, send_file, current_app
from app.models import Attack, Report
from flask_mail import Mail, Message
from private import email_info

import os, bson, json
import time
import datetime

from app.modules import loggers, statusCode, parser, sckt_utils, cmd_setter
logger = loggers.create_logger(__name__)

from app import MyIP
from private.ports import WEB_SERVER_PORT

CURRENT_DIR = os.path.abspath(os.getcwd())
downloadURL = f"http://{MyIP}:{WEB_SERVER_PORT}/ssploit/download"


bp = Blueprint('attack', __name__, url_prefix='/attack')


@bp.route('/filter', methods=['GET', 'POST'])
def attack_filter():
    if request.method=='GET':
        type1 = request.args.get('type1') # product, endpoint, malware, product_packet
        src_ip = request.args.get('src_ip')
        dst_ip = request.args.get('dst_ip')
        
        if type1=='product':### 보안 장비 점검
            type2 = request.args.get('type2') # atk_packet, atk+malware
            type2 = "mal" if type2=="atk_malware" else "cve"
            attacks = Attack.query.filter(Attack.type==type2).all()
            all_attacks = parser.attack_query_to_json(attacks)
            logger.info(f"[ATTACK] PRODUCT : {all_attacks}")
            return {"result":all_attacks}

        elif type1=='endpoint':### 타겟 점검
            # 포트 스캔 (제거)
            # sckt = sckt_utils.create_socket()
            # command = {
            #     "type":"web",
            #     "command":[{
            #         "type":"scan",
            #         "src_ip":src_ip,
            #         "dst_ip":dst_ip
            #     }]
            # }
            # sckt_utils.send_with_size(sckt, bson.dumps(command))
            # recvData = sckt_utils.recv_data(sckt)
            # recvData = bson.loads(recvData)
            # logger.info(f"[ATTACK] ENDPOINT \"scan_result\" : {recvData}")
            # sckt.close()

            # filtered_attacks = parser.recv_to_json(recvData)
            # res = {"result":filtered_attacks}
            # logger.info(f"[ATTACK] ENDPOINT \"filtered_attacks\" : {res}")

            attacks = Attack.query.filter(Attack.type=="cve").all()
            all_attacks = parser.attack_query_to_json(attacks)
            return {"result":all_attacks}

        elif type1=="malware":### endpoint 솔루션
            attacks = Attack.query.filter(Attack.type=="mal").all()
            all_attacks = parser.attack_query_to_json(attacks)

            logger.info(f"[ATTACK] MALWARE \"result\" : {all_attacks}")
            
            return {"result":all_attacks}
    else:
        getFromFront = request.get_data().decode()
        logger.info(f"data from front : {getFromFront}")
        
        getFromFront = json.loads(getFromFront)
        type1=getFromFront['type1']
        src_ip = getFromFront['src_ip']
        dst_ip = getFromFront['dst_ip']
        service = getFromFront['service']

        logger.info(f"type1:{type1}, src_ip:{src_ip}, dst_ip:{dst_ip}, service:{service}")

        r = os.popen(f'searchsploit {service} -j').read()
        r = json.loads(r)
        
        results = r["RESULTS_EXPLOIT"]
        if "RESULTS_PAPER" in r:
            results.extend(r["RESULTS_PAPER"])
        return {
            "results":results
        }


@bp.route('/start', methods=['POST'])
def attack_start():
    getFromFront = request.get_data().decode()
    getFromFront = json.loads(getFromFront)

    # logger.info(f"[ATTACK] data from front : {getFromFront}")

    attackType = getFromFront['type'] # 'product' or 'endpoint'
    src_ip = getFromFront['src_ip']
    try:
        dst_ip = getFromFront['dst_ip']
    except:
        pass
    attack_id_list = getFromFront["cve_id"]
    attack_cnt = len(attack_id_list)

    command = {"type":"web"}

    if attackType=="product": # (attack & defense) & remote malware
        _command = cmd_setter.product_command(src_ip, dst_ip, attack_id_list)
    elif attackType=="endpoint": # target
        _command = cmd_setter.target_command(src_ip, dst_ip, attack_id_list)
    elif attackType=="malware": # local malware
        _command = cmd_setter.malware_command(dst_ip, attack_id_list)
    
    command["command"]=_command

    logger.info(f"[ATTACK] attack info : {attackType}, {src_ip}, {dst_ip}, {attack_id_list}")
    logger.info(f"[ATTACK] command : {command}")

    sckt = sckt_utils.create_socket()
    # send command to tcp server
    sckt_utils.send_with_size(sckt, bson.dumps(command))
    
    try:
        pre_no = Report.query.order_by(Report.no.desc()).first().no
    except:
        pre_no = -1
    now = datetime.datetime.now()
    attack_start_time = now.strftime('%Y-%m-%d %H:%M:%S')

    for i in range(attack_cnt): # recv reports from tcp server
        reportData = sckt_utils.recv_data(sckt) # json
        reportData = bson.loads(reportData)
        to_MySQL_result = parser.save_report_to_MySQL(pre_no, attack_start_time, reportData)
        if to_MySQL_result == "Insert ERROR":
            logger.warning(f"{loggers.RED}[ATTACK] ERROR while inserting report into MySQL{loggers.END}")
        time.sleep(1)
    sckt.close()

    ### popup alert

    return {
        "status": statusCode.OK
    }

@bp.route('/edit', methods=['POST'])
def product_packet_edit():
    if request.method=='GET':
        logger.warning(f"{loggers.RED}[ATTACK] NOT GET{loggers.END}")
        return {"status":statusCode.METHOD_ERROR}
    getFromFront = request.get_data().decode()
    getFromFront = json.loads(getFromFront)
    script_number = getFromFront['script_number']

    # searchsploit에서 파일 위치 가져오기
    ssploit_res = os.popen(f"searchsploit -p {script_number} -j").read()
    ssploit_res = ssploit_res.split("\n")
    for i in ssploit_res:
        if "Path" in i:
            ssploit_path = i
            break
    ssploit_path = ssploit_path.split(":")[1].replace(" ","")
    new_path = CURRENT_DIR+"/temp/tmp.py"
    
    # 해당 파일 temp 밑으로 복사
    os.system(f"cp {ssploit_path} {new_path}")

    code = os.popen(f"cat {ssploit_path}").read()
    logger.info(f"code to edit : {code}")

    return {
        "code": code
    }

@bp.route("/save", methods=['POST'])
def product_packet_save():
    if request.method=='GET':
        logger.warning(f"{loggers.RED}[ATTACK] NOT GET{loggers.END}")
        return {"status":statusCode.METHOD_ERROR}
    getFromFront = request.get_data().decode()
    getFromFront = json.loads(getFromFront)
    edited_code = getFromFront['edited']
    usage = getFromFront["usage"]
    attack_id = int(getFromFront["attack_id"])
    src_ip = getFromFront["src_ip"]
    dst_ip = getFromFront["dst_ip"]
    target_port = int(getFromFront["tport"])

    # print("[---] edited_code : ", edited_code)
    # logger.info(f"attack_id:{attack_id}, src_ip:{src_ip}, dst_ip:{dst_ip}, usage:{usage}")


    tmp_path = CURRENT_DIR+"/temp/tmp.py"
    f = open(tmp_path,"w")
    f.write(edited_code)
    f.close()
    
    filename = os.popen(f'searchsploit {attack_id} -j').read()
    filename = json.loads(filename)
    # logger.info(f"filename:{filename}")

    _command = {
        "type":"web",
        "command":[
            {
                "type" : "defense",
                "src_ip" : dst_ip,
                "attack_id" : attack_id,
                "port": target_port,  # 7777 로 하드코딩
            },
            {
                "attack_id": attack_id, # exploit-db 번호
                "filename": filename["RESULTS_EXPLOIT"][0]["Path"].split("/")[-1],
                "type": "product_packet", # exploit-db 대신 product_packet 사용
                "src_ip": src_ip,
                "dst_ip": dst_ip,
                "usage": usage,
                "download": downloadURL, # X로 암호화된 api,
                "dst_port": target_port,
            }
        ]
    }


    sckt = sckt_utils.create_socket()
    # send command to tcp server
    sckt_utils.send_with_size(sckt, bson.dumps(_command))

    reportData = sckt_utils.recv_data(sckt) # json
    reportData = bson.loads(reportData)
    logger.info(f"[ATTACK] SSPLOIT \"report\" : {reportData}")
    sckt.close()

    try:
        pre_no = Report.query.order_by(Report.no.desc()).first().no
    except:
        pre_no = -1
    now = datetime.datetime.now()
    attack_start_time = now.strftime('%Y-%m-%d %H:%M:%S')

    to_MySQL_result = parser.save_report_to_MySQL(pre_no, attack_start_time, reportData)
    if to_MySQL_result == "Insert ERROR":
        logger.warning(f"{loggers.RED}[ATTACK] ERROR while inserting report into MySQL{loggers.END}")
    
    return {
        "status": statusCode.OK
    }

    # filtered_attacks = parser.recv_to_json(recvData)
    # res = {"result":filtered_attacks}
    # logger.info(f"[ATTACK] ENDPOINT \"filtered_attacks\" : {res}")


    

    # return {
    #     "attack_id": attack_id,
    #     "filename":filename["RESULTS_EXPLOIT"][0]["Path"].split("/")[-1],
	# 	"type": "exploit-db",
    #     "src_ip": src_ip,
    #     "dst_ip": dst_ip,
    #     "usage": usage,
    #     "code": downloadURL
	# }

# 암호화 된
@bp.route('/download/crypt/<int:attackIdx>/', methods=['GET'])
def attack_download_enc(attackIdx):
    attackInfo = Attack.query.filter(Attack.attackId==attackIdx).first()
    f_name = attackInfo.fileName

    pwd = os.getcwd()
    file_route = f"{pwd}/attack_files/{f_name}" # 공격 파일 경로

    logger.info(f"[ATTACK] local file route : {file_route}")
    
    file_bytes = bytearray(open(file_route, 'rb').read())
    f_size = cmd_setter.file_size(file_route)
    encoded = bytearray(f_size)

    for i in range(f_size):
        encoded[i] = file_bytes[i]^ord('X')
    
    logger.info(f"[ATTACK] encoded content of encrypted file({attackIdx}) : {encoded}")

    return encoded



# 암호화 안 된
@bp.route('/download/<int:attackIdx>/', methods=['GET'])
def attack_download(attackIdx):
    attackInfo = Attack.query.filter(Attack.attackId==attackIdx).first()
    file_name = attackInfo.fileName

    pwd = os.getcwd()
    file_route = f"{pwd}/attack_files/{file_name}" # 공격 파일 경로

    logger.info(f"[ATTACK] local file route : {file_route}")

    if os.path.isfile(file_route):
        return send_file(file_route,
            attachment_filename=f"{file_route}",# 다운받아지는 파일 이름 -> 경로 지정할 수 있나?
            as_attachment=True)
    else:
        return {"status":statusCode.SERVER_ERROR}


@bp.route('/mail', methods=['POST'])
def attack_mail():
    if request.method=='GET':
        logger.warning(f"{loggers.RED}[ATTACK] NOT GET{loggers.END}")
        return {"status":statusCode.METHOD_ERROR}
    
    sender_email = email_info.email
    sender_pw = email_info.passwd

    logger.info(f"[ATTACK] sender_email :{sender_email}, sender_pw :{sender_pw}")
    # logger.info(f"[ATTACK] /mail - request.form : {request.form}")
    # logger.info(f"[ATTACK] /mail - request.files : {request.files}")
    
    recver_email = request.form.getlist('recver_email')[0]
    file_title = request.form.getlist('title')[0]
    file_body = request.form.getlist('body')[0]
    file_name = request.files.getlist('attachment')[0]
    fileName = file_name.filename
    
    logger.info(f"[ATTACK] recver_email : {recver_email}, file_title : {file_title}, file_body : {file_body}, fileName : {fileName}")
    

    # hard coding OK...
    smtp_type = sender_email.split('@')[1]

    current_app.config['MAIL_SERVER']=f"smtp.{smtp_type}" # smtp.naver.com / smtp.gmail.com / smtp.daum.net
    current_app.config['MAIL_PORT']=465
    current_app.config['MAIL_USERNAME']=sender_email
    current_app.config['MAIL_PASSWORD']=sender_pw
    current_app.config['MAIL_USE_TLS']=False
    current_app.config['MAIL_USE_SSL']=True

    mail = Mail(current_app)
    msg = Message(subject=file_title, sender=sender_email, recipients=[recver_email])
    msg.body = f"{file_body}"
    with current_app.open_resource(f"../attack_files/{fileName}") as fp:
        msg.attach(f"{fileName}", "text/plain", fp.read())
    mail.send(msg)
    return {"status":statusCode.OK}



    
