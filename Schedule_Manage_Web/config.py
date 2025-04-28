# 환경 변수 로드
import os
from dotenv import load_dotenv

# .env 파일을 로드하여 환경 변수를 설정
load_dotenv()

# 필수 환경 변수를 정의
REQUIRED_ENV_VARS = ["dbhost", "user", "password", "database", "charset"]

# 필수 환경 변수 중 설정되지 않은 변수 찾기
missing_vars = [
var for var in REQUIRED_ENV_VARS if not os.getenv(var) and os.getenv(var) != ""
]
if missing_vars:
    raise ValueError(f"[ERROR] 다음 환경 변수가 설정되지 않았습니다. : {missing_vars}")

import streamlit as st
import pandas as pd
import pymysql
from datetime import datetime, timedelta

#APScheduler는 파이썬에서 작업을 예약하고 실행할 수 있는 라이브러리
from apscheduler.schedulers.background import BackgroundScheduler

# CronTrigger는 작업을 특정 주기마다 실행하는 트리거
# DateTrigger은 작업을 특정 시간에만 실행하는 트리거
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger

# 데이터베이스 연결 정보
conn = pymysql.connect(
host=os.getenv("dbhost"),
user=os.getenv("user"),
password=os.getenv("password"),
db=os.getenv("database"),
charset=os.getenv("charset"),
)

_scheduler = None

# 메일 보내는 스케줄러
def get_scheduler():
# 전역 변수 _scheduler를 사용
    global _scheduler

    if _scheduler is None:
        # day_email 모듈에서 notify_managers 함수 사용
        from day_email import notify_managers

        # BackgroundScheduler 인스턴스를 생성 (APScheduler 라이브러리에서 제공하는 스케줄러 클래스)
        _scheduler = BackgroundScheduler()

        # 5초 뒤에 실행할 시간을 계산합니다.
        run_time = datetime.now() + timedelta(seconds=5)

        # DateTrigger를 사용하여 5초 뒤에 실행하도록 설정합니다.
        _scheduler.add_job(
            notify_managers,
            DateTrigger(run_time),
            id="day_notify_job",
            replace_existing=True,
        )

        # notify_managers 함수를 15시 38분에 실행
        # replace_existing=True 기존에 동일한 아이디의 작업이 있는 경우, 새로운 작업으로 대체.
        # id를 이용한 작업 관리 예
        # 작업을 삭제하는 경우:_scheduler.remove_job("day_notify_job")
        # 작업을 일시 중지하는 경우:_scheduler.pause_job("day_notify_job")
        # 작업을 재개하는 경우:_scheduler.resume_job("day_notify_job")
        _scheduler.add_job(
            notify_managers,
            CronTrigger(hour=6, minute=00),
            id="day_notify_job",
            replace_existing=True,
        )

        _scheduler.start()
    return _scheduler


def connect_to_database():  # SQL 연결 함수
    conn = pymysql.connect(
        host=os.getenv("dbhost"),
        user=os.getenv("user"),
        password=os.getenv("password"),
        db=os.getenv("database"),
        charset=os.getenv("charset"),
        )
    return conn

# 데이터베이스의 특정 테이블에서 데이터를 가져와 pandas DataFrame으로 반환하는 함수
def create_dataframe(conn, table_name, columns):
    # connect_to_database()를 호출하여 데이터베이스에 연결
    conn = connect_to_database()
    # 질의를 실행하기 위한 커서 객체를 생성
    cur = conn.cursor()
    # 든 데이터를 가져오는 SQL 질의를 실행
    cur.execute(f"SELECT * FROM {table_name};")
    # SQL 질의의 결과를 모두 rows 변수에 저장
    rows = cur.fetchall()
    cur.close()
    return pd.DataFrame(rows, columns=columns)

# 명단 데이터 가져오기 함수
def get_member_data(group_id=None):
    # 데이터 가져오기
    df = create_dataframe(
    conn,
    "schedule_employees",
    columns=["employee_id", "name", "employee_code", "email", "group_id"],
    )


# 팀 이름이 주어지면 해당 팀으로 필터링
    if group_id:
        return df[df["group_id"] == group_id]
    # 팀 이름이 주어지지 않으면 모든 팀의 데이터 반환
    else:
        return df
    
# 그룹 이름에 맞는 그룹 id 불러오는 함수
def get_group_id_by_name(group_name):
    conn = connect_to_database()
    cur = conn.cursor()
    query = "SELECT group_id FROM schedule_groups WHERE group_name = %s"
    cur.execute(query, (group_name,))
    result = cur.fetchone()
    cur.close()
    return result[0] if result else None

# 그룹 id에 맞는 프로젝트 데이터 불러오는 함수
def load_projects_by_group(group_id):
    df_project = create_dataframe(
        None,
        "schedule_projects",
        columns=[
        "project_id",
        "project_name",
        "group_id",
        "description",
        "start_date",
        "end_date",
        "duration",
        ],
    )
    # 날짜 데이터를 판다스 날짜 형식으로 변환
    df_project["start_date"] = pd.to_datetime(df_project["start_date"])
    df_project["end_date"] = pd.to_datetime(df_project["end_date"])
    # 그룹 id에 맞는 프로젝트만 반환
    return df_project[df_project["group_id"] == group_id]

# 프로젝트 삭제하는 함수
def delete_project(project_id):
    conn = connect_to_database()
    cur = conn.cursor()

    # 가장 자식 데이터부터 삭제 디테일 플랜 -> 스테이지 -> 프로젝트
    try:
        # 프로젝트와 관련된 데이터 삭제(세부계획, 스테이지)
        cur.execute(
            "DELETE FROM schedule_Sub_Task WHERE project_id = %s", (project_id,)
        )
        # 프로젝트와 관련된 스테이지 삭제
        cur.execute(
            "DELETE FROM schedule_Main_Task WHERE project_id = %s", (project_id,)
        )
        # 프로젝트 삭제
        cur.execute("DELETE FROM schedule_projects WHERE project_id = %s", (project_id,))
        st.success(f"프로젝트가 삭제 되었습니다!")
        conn.commit()

    except Exception as e:
        st.error(f"프로젝트 삭제 중 오류 발생 : {e}")
    finally:
        cur.close()
