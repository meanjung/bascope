from flask import Blueprint, request
from app import redis_client


from app.modules import loggers, statusCode
logger = loggers.create_logger(__name__)

bp = Blueprint('agent', __name__, url_prefix='/agent')

@bp.route('/add', methods=['POST'])
def add_agent():
    if request.method=='GET':
        logger.warning(f'{loggers.RED}[AGENT] NOT GET{loggers.END}')
        return {"status":statusCode.METHOD_ERROR}
    agent_ip = request.get_json()['ip']
    redis_client.sadd("agents",agent_ip)
    logger.info(f"{loggers.GREEN}[AGENT] ADD agent_ip :{agent_ip}{loggers.END}")
    return {"status":statusCode.OK}

@bp.route('/del', methods=['POST'])
def del_agent():
    if request.method=='GET':
        logger.warning(f'{loggers.RED}[AGENT] Not GET{loggers.END}')
        return {"status":statusCode.METHOD_ERROR}
    agent_ip = request.get_json()['ip']
    redis_client.srem("agents", agent_ip)
    logger.info(f"{loggers.GREEN}[AGENT] DEL agent_ip :{agent_ip}{loggers.END}")
    return {"status":statusCode.OK}


@bp.route('/show')
def show_agent():
    all_agents = redis_client.smembers("agents")
    # all_agents = {b'2.2.2.2', b'1.1.1.1'}
    all_agents = [a.decode() for a in all_agents]
    # ['2.2.2.2', '1.1.1.1']
    logger.info(f'[AGENT] all agents: {all_agents}')
    return {"status":statusCode.OK}
