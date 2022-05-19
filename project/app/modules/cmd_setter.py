from app.models import Attack
from app import MyIP
import os

import json
import logging
import logging.config
import pathlib
log_config = (pathlib.Path(__file__).parent.resolve().parents[1].joinpath("log_config.json"))
config = json.load(open(str(log_config)))
logging.config.dictConfig(config)
logger = logging.getLogger(__name__)

from private.ports import WEB_SERVER_PORT

downloadURL = f"http://{MyIP}:{WEB_SERVER_PORT}/attack/download"


def file_size(file_route):
    return os.path.getsize(file_route)



def product_command(src_ip, dst_ip, attack_id_list):
    pwd = os.getcwd()
    
    command = []
    for attack_id in attack_id_list:
        attack_id = int(attack_id)
        # file_name, dst_port, usage, type = Attack.query.filter(Attack.attackId==attack_id).with_entities(Attack.fileName, Attack.port, Attack.usage, Attack.type).first()
        attackInfo = Attack.query.filter(Attack.attackId==attack_id).first()
        
        file_name = attackInfo.fileName
        dst_port = attackInfo.port
        usage = attackInfo.usage
        type = attackInfo.type

        # logger.info(f"\n[CMD_SETTER] product - file_name : {file_name}, dst_port :{dst_port}, usage : {usage}, type:{type}")

        # file_route = f"{downloadURL}/crypt/{attack_id}"
        file_route = f"{pwd}/attack_files/{file_name}"
        down_route = f"{downloadURL}/crypt/{attack_id}"
        f_size = file_size(file_route)
        if type=="mal":
            command.append({
                "type":"product_malware",
                "src_ip":dst_ip,
                "download": down_route,
                "attack_id":attack_id,
                "file_size":f_size
            })
        else:
            command.append({
                "type":"defense",
                "src_ip": dst_ip,
                "attack_id":attack_id,
                "port":dst_port
            })
            command.append({
                "type":"product_packet",
                "malware":False,
                "src_ip":src_ip,
                "dst_ip":dst_ip,
                "dst_port":dst_port,
                "download":down_route, # 암호화 된
                "file_size":f_size, # bytes
                "attack_id":attack_id,
                "usage":usage
            })
        
    return command




def target_command(src_ip, dst_ip, attack_id_list):
    command = []
    pwd = os.getcwd()
    for attack_id in attack_id_list:
        attack_id = int(attack_id)
        # file_name, dst_port, usage = Attack.query.filter(Attack.attackId==attack_id).with_entities(Attack.fileName, Attack.port, Attack.usage).first()
        attackInfo = Attack.query.filter(Attack.attackId==attack_id).first()
        
        file_name = attackInfo.fileName
        dst_port = attackInfo.port
        usage = attackInfo.usage

        file_route = f"{pwd}/attack_files/{file_name}"
        down_route = f"{downloadURL}/crypt/{attack_id}"
        f_size = file_size(file_route)

        logger.info("\n[CMD_SETTER] target - {file_name}, dst_port :{dst_port}, usage : {usage}, file_route : {file_route}, down_route : {down_route}, f_size : {f_size}")

        command.append({
            "type":"target",
            "src_ip":src_ip,
            "dst_ip":dst_ip,
            "dst_port":dst_port,
            "download":down_route, # 암호화 안 된
            "file_size":f_size, # bytes,
            "attack_id":attack_id,
            "usage":usage
        })
    return command



def malware_command(src_ip, attack_id_list):
    command = []
    pwd = os.getcwd()
    for attack_id in attack_id_list:
        attack_id = int(attack_id)
        # file_name, usage = Attack.query.filter(Attack.attackId==attack_id).with_entities(Attack.fileName, Attack.port, Attack.usage).first()
        
        attackInfo = Attack.query.filter(Attack.attackId==attack_id).first()
        
        file_name = attackInfo.fileName
        usage = attackInfo.usage

        file_route = f"{pwd}/attack_files/{file_name}"
        down_route = f"{downloadURL}/{attack_id}"
        f_size = file_size(file_route)

        logger.info("\n[CMD_SETTER] malware - file_name : {file_name}, usage : {usage}, file_route : {file_route}, down_route : {down_route}, f_size : {f_size}")

        command.append({
            "type":"endpoint",
            "src_ip":src_ip,
            "download":down_route, # 암호화 안 된
            "file_size":f_size,
            "attack_id":attack_id,
            "usage":usage,
            "filename": file_name,
        })
    return command
         

