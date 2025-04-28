# config.py
import os
from dotenv import load_dotenv
load_dotenv()

REQUIRED_ENV_VARS = ["dbhost", "user", "password", "database", "charset"]
missing_vars = [var for var in REQUIRED_ENV_VARS if var not in os.environ]

if missing_vars:
    raise ValueError(f"[ERROR] 다음 환경 변수가 설정되지 않았습니다. : {missing_vars}")

import pandas as pd
import pymysql
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger

# 데이터베이스 연결 함수
def connect_to_database():
    return pymysql.connect(
        host=os.getenv("dbhost"),
        user=os.getenv("user"),
        password=os.getenv("password"),
        db=os.getenv("database"),
        charset=os.getenv("charset"),
    )

# 특정 테이블에서 데이터를 읽어 DataFrame으로 반환
def create_dataframe(table_name, columns):
    conn = connect_to_database()
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM {table_name};")
            rows = cur.fetchall()
    finally:
        conn.close()
    return pd.DataFrame(rows, columns=columns)

# 그룹별 인원 데이터 반환
def get_member_data(group_id=None):
    df = create_dataframe("schedule_employees", columns=["employee_id", "name", "employee_code", "email", "group_id"])
    return df[df["group_id"] == group_id] if group_id else df

# 그룹 이름으로 그룹 id 조회
def get_group_id_by_name(group_name):
    conn = connect_to_database()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT group_id FROM schedule_groups WHERE group_name = %s", (group_name,))
            result = cur.fetchone()
    finally:
        conn.close()
    return result[0] if result else None

# 그룹 id에 따른 프로젝트 목록 반환 (날짜 형식도 변환)
def load_projects_by_group(group_id):
    df_project = create_dataframe("schedule_projects", columns=["project_id", "project_name", "group_id", "description", "start_date", "end_date", "duration"])
    df_project["start_date"] = pd.to_datetime(df_project["start_date"])
    df_project["end_date"] = pd.to_datetime(df_project["end_date"])
    return df_project[df_project["group_id"] == group_id]

# 프로젝트 삭제 (하위 데이터부터 삭제)
def delete_project(project_id):
    conn = connect_to_database()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM schedule_Sub_Task WHERE project_id = %s", (project_id,))
            cur.execute("DELETE FROM schedule_Main_Task WHERE project_id = %s", (project_id,))
            cur.execute("DELETE FROM schedule_projects WHERE project_id = %s", (project_id,))
        conn.commit()
        return "프로젝트가 삭제 되었습니다!"
    except Exception as e:
        return f"프로젝트 삭제 중 오류 발생 : {e}"
    finally:
        conn.close()

# APScheduler 스케줄러 (이메일 알림 기능)
_scheduler = None
def get_scheduler():
    global _scheduler
    if _scheduler is None:
        from day_email import notify_managers
        _scheduler = BackgroundScheduler()
        run_time = datetime.now() + timedelta(seconds=5)
        _scheduler.add_job(notify_managers, DateTrigger(run_date=run_time), id="day_notify_job_initial", replace_existing=True)
        _scheduler.add_job(notify_managers, CronTrigger(hour=6, minute=0), id="day_notify_job_daily", replace_existing=True)
        _scheduler.start()
    return _scheduler
