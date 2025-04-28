# day_email.py
import os
from dotenv import load_dotenv
load_dotenv()

REQUIRED_ENV_VARS = ["smtp_server", "smtp_port", "email_address", "email_password"]
missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"[ERROR] 다음 환경 변수가 설정되지 않았습니다. : {missing_vars}")

from datetime import datetime, timedelta
from config import connect_to_database
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

SMTP_SERVER = os.getenv("smtp_server")
SMTP_PORT = int(os.getenv("smtp_port"))
EMAIL_ADDRESS = os.getenv("email_address")
EMAIL_PASSWORD = os.getenv("email_password")

# 내일 시작할 프로젝트 관련 관리자 정보를 조회
def get_managers_to_notify():
    conn = connect_to_database()
    try:
        with conn.cursor() as cur:
            tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            query = """
            SELECT dp.name, e.email, dp.calculated_start_date, dp.Sub_Task_name, dp.Main_Task_name
            FROM schedule_Sub_Task dp
            JOIN schedule_employees e ON dp.name = e.name
            WHERE DATE(dp.calculated_start_date) = %s
            """
            cur.execute(query, (tomorrow,))
            results = cur.fetchall()
    except Exception as e:
        print(f"쿼리 실행 실패: {e}")
        results = []
    finally:
        conn.close()
    return results

# 이메일 전송 함수
def send_email(to_email, subject, body):
    try:
        message = MIMEMultipart()
        message["From"] = EMAIL_ADDRESS
        message["To"] = to_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain", "utf-8"))
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(message)
        print(f"Email sent to {to_email}")
    except smtplib.SMTPAuthenticationError:
        print("이메일 로그인 실패: 아이디 또는 비밀번호 확인 필요")
    except smtplib.SMTPException as e:
        print(f"SMTP 오류 발생: {e}")

# 관리자에게 이메일 알림 발송
def notify_managers():
    try:
        managers = get_managers_to_notify()
        for name, email, calculated_start_date, main_task_name, sub_task_name in managers:
            subject = f"프로젝트 '{sub_task_name}' 시작알림"
            body = (f"안녕하세요 {name}님, '{main_task_name}' 프로젝트가 {calculated_start_date}에 시작될 예정입니다.\n"
                    f"주요내용 : {sub_task_name} 준비 부탁드립니다. 감사합니다.")
            send_email(email, subject, body)
    except Exception as e:
        print(f"Error in notify_managers : {e}")
