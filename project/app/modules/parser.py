from app.models import Attack, Report
from app import MyIP, db
from app.modules import loggers
import base64
from private.ports import WEB_SERVER_PORT

logger = loggers.create_logger(__name__)
downloadURL = f"https://{MyIP}:{WEB_SERVER_PORT}/attack/download/"


def attack_query_to_json(attacks):
    filtered_attacks=[]
    for attack in attacks:
        _attack = {
            "attackId":attack.attackId,
            "program":attack.program,
            "version":attack.version,
            "port":attack.port,
            "fileName":attack.fileName,
            "usage":attack.usage
        }
        filtered_attacks.append(_attack)
    return filtered_attacks


def recv_to_json(recvData):
    filtered_attacks = []
    ports = recvData["ports"]
    for _port in ports:
        try:
            attacks = Attack.query.filter(Attack.program==_port["service_name"]).all()
        except:
            continue
        sub_filtered_attacks= attack_query_to_json(attacks)
        filtered_attacks.extend(sub_filtered_attacks)
    return filtered_attacks


def save_report_to_MySQL(pre_no, attack_start_time, reportData):
    new_no = pre_no+1
    reportType = reportData["type"]
    attack_id = reportData["attack_id"] # int
    if reportType=="pkt":
        port = reportData["port"] # int
        send_ip = reportData["send_ip"]
        recv_ip = reportData["recv_ip"]
        sendPkts = reportData["send"] # base64 encoded byte list
        recvPkts = reportData["recv"] # base64 encoded byte list

        decoded_sendPkts=[]
        decoded_recvPkts=[]

        # base64 decode
        for _pkt in sendPkts:
            _pkt = base64.b64decode(_pkt.decode('utf-8'))
            try:
                _pkt = _pkt.decode('ascii')
            except:
                pass
            decoded_sendPkts.append(_pkt)

        for _pkt in recvPkts:
            _pkt = base64.b64decode(_pkt.decode('utf-8'))
            try:
                _pkt = _pkt.decode('ascii')
            except:
                pass
            decoded_recvPkts.append(_pkt)
        
        # send, recv 비교
        if set(decoded_sendPkts)==set(decoded_recvPkts):
            result = "success"
        else:
            result = "fail"
        
        # list -> str
        decoded_sendPkts = str(decoded_sendPkts)
        decoded_recvPkts = str(decoded_recvPkts)

        log = f"{send_ip} sent\n{decoded_sendPkts}\n\n{recv_ip} received\n{decoded_recvPkts}"
    elif reportType=="malware":
        attackName = Attack.query.filter(Attack.attackId==attack_id).first().fileName
        infected = reportData["infected"] # bool
        if infected==True:
            log = f"Infected by {attackName}"
            result = "success"
        else:
            log = f"Not Infected by {attackName}"
            result = "fail"
    elif reportType=="kvm":
        log = reportData["log"]
        result = "kvm" # or null
    try:
        logger.info(f"New Report({reportType}) : {new_no}, {attack_id}, {log}, {attack_start_time}, {result}")
        
        # Insert into MySQL
        report = Report(no=new_no, attackId=attack_id, startTime=attack_start_time, log=log, result=result)
        db.session.add(report)
        db.session.commit()
        return "Insert SUCCESS"
    except:
        return "Insert ERROR"
