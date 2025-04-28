# 환경 변수 로드
import os
from dotenv import load_dotenv

# .env 파일을 로드하여 환경 변수를 설정
load_dotenv()

# 필수 환경 변수를 정의
REQUIRED_ENV_VARS = ["smtp_server", "smtp_port", "email_address", "email_password"]

missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"[ERROR] 다음 환경 변수가 설정되지 않았습니다. : {missing_vars}")

import pymysql
from datetime import datetime, timedelta
from config import connect_to_database

# 이메일 본문을 텍스트로 작성하기 위한 모듈
from email.mime.text import MIMEText

# 복합적인 이메일(텍스트+첨부파일) 작성하기 위한 모듈
from email.mime.multipart import MIMEMultipart

# SMTP서버와 통신하여 이메일 전송하는 모듈
import smtplib

# 이메일 전송을 위한 정보
SMTP_SERVER = os.getenv("smtp_server")
SMTP_PORT = os.getenv("smtp_port")
EMAIL_ADDRESS = os.getenv("email_address")
EMAIL_PASSWORD = os.getenv("email_password")


# 알림이 필요한 관리자 정보 호출
def get_managers_to_notify():
    try:
        conn = connect_to_database()
    except Exception as e:
        print(f"멤버 조회 실패 {e}")
    cur = conn.cursor()

    # 현재 날짜의 하루 후 날짜 계산
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    # 세부계획의 계산된 시작 날짜가 내일인 경우 담당자와 이름이 같은 직원 이메일 선택
    query = """
    SELECT
        dp.name,
        e.email,
        dp.calculated_start_date,
        dp.Sub_Task_name,
        dp.Main_Task_name
    FROM
        schedule_Sub_Task dp
    JOIN
        schedule_employees e ON dp.name = e.name
    WHERE
        DATE(dp.calculated_start_date) = %s
"""
    try:
        cur.execute(query, (tomorrow,))
        results = cur.fetchall()
    except Exception as e:
        print(f"쿼리 실행 실패: {e}")
        results = []
    cur.close()

    return results


# 이메일 전송 함수
def send_email(to_email, subject, body):
    try:
        # MIMEMultipart 객체 생성
        message = MIMEMultipart()
        # 이메일 발신 주소
        message["From"] = EMAIL_ADDRESS
        # 이메일 수신 주소
        message["To"] = to_email
        # 이메일 제목
        message["Subject"] = subject

        # 이메일 본문 설정
        message.attach(MIMEText(body, "plain", "utf-8"))

        # SMTP서버 연결 및 로그인
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            # 이메일 계정 로그인
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            # 이메일 전송
            server.send_message(message)

        print(f"Email sent to {to_email}")
    except smtplib.SMTPAuthenticationError:
        print("이메일 로그인 실패: 아이디 또는 비밀번호 확인 필요")
    except smtplib.SMTPException as e:
        print(f"SMTP 오류 발생: {e}")


# 이메일 전송 함수
def notify_managers():
    try:
        # 알림이 필요한 관리자 정보(데이터 프레임) 호출
        names = get_managers_to_notify()

        # 각 관리자에게 이메일전송 (아래 변수들은 데이터 프레임에 있음)
        for name, email, calculated_start_date, Main_Task_name, Sub_Task_name in names:
            subject = f"프로젝트 '{Sub_Task_name}' 시작알림"
            body = f"안녕하세요 {name}님, '{Main_Task_name}' 프로젝트가 {calculated_start_date}에 시작될 예정입니다.\n주요내용 : {Sub_Task_name} 준비 부탁드립니다. 감사합니다."
            send_email(email, subject, body)
    except Exception as e:
        print(f"Error in notify_managers : {e}")
