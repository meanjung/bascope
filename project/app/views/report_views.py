from flask import Blueprint, request, render_template

import base64


from app.models import Report
from app.modules import parser, loggers, statusCode
from app import db

logger = loggers.create_logger(__name__)



bp = Blueprint('report', __name__, url_prefix='/report')


@bp.route('/')
def report():
    reports = Report.query.with_entities(Report.no, Report.attackId, Report.startTime, Report.result).order_by(Report.no.desc())
    dict_report = {}
    for report in reports:
        report_no = report[0]
        report_attackId = report[1]
        report_startTime = report[2]
        report_result = report[3]
        logger.info(f"report_no:{report_no}, report_attackId:{report_attackId}, report_startTime:{report_startTime}, report_result:{report_result}")
        if report_no not in dict_report.keys():
            dict_report[report_no]=[[report_attackId], report_startTime, 0]
        else:
            dict_report[report_no][0].append(report_attackId)
        if report_result=="success":
            dict_report[report_no][2]+=1
    arranged_reports = []
    for d in dict_report.keys():
        attack_id_cnt = len(dict_report[d][0])
        arranged_reports.append({
            "no":d,
            "attack_id":dict_report[d][0],
            "start_time":dict_report[d][1],
            "result":f"{dict_report[d][2]} of {attack_id_cnt} succeed"
        })
    
    return render_template("report.html", sql_data = {
	    "data":arranged_reports
    })


@bp.route('/<int:reportNo>')
def show_one_report(reportNo):
    reports = Report.query.filter(Report.no==reportNo).all()
    arranged_reports = []
    for report in reports:
        arranged_reports.append({
            "no":report.no,
            "attack_id":report.attackId,
            "time":report.startTime,
            "log":report.log
        })
    return {
        "data":arranged_reports
    }