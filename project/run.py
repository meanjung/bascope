#!/usr/bin/env python3
from app import create_app

# LOGGING
import json
import logging
import logging.config
log_config = json.load(open('log_config.json'))
logging.config.dictConfig(log_config)
logger = logging.getLogger(__name__)


if __name__=="__main__":
    # APP
    run_app = create_app()
    logger.info("\n[INIT] APP CONNECTED")
    
    run_app.run(host="0.0.0.0")

#######################################
####실행 방법 
######################################
# 이 파일을 만들고 python run.py 하거나
# 이 파일 지우고 flask run --host 0.0.0.0
