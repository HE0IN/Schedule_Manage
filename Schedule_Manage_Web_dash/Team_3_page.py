# Team_3_page.py
import dash
from dash import html, dcc, dash_table, Input, Output, State
import pandas as pd
from datetime import datetime, timedelta
import config
import pymysql

# DB에서 Main Task, Sub Task 데이터를 불러오는 헬퍼 함수
def load_main_task(project_id):
    df = config.create_dataframe(None, "schedule_Main_Task", columns=["Main_Task_id", "project_id", "Main_Task_name", "Main_Task_start_date", "Main_Task_end_date", "duration", "description"])
    if not df.empty:
        df["Main_Task_start_date"] = pd.to_datetime(df["Main_Task_start_date"]).dt.date
        df["Main_Task_end_date"] = pd.to_datetime(df["Main_Task_end_date"]).dt.date
        df["duration"] = df["duration"].astype(int)
    return df[df["project_id"] == project_id]

def load_sub_task(project_id):
    df = config.create_dataframe(None, "schedule_Sub_Task", columns=["Sub_Task_id", "project_id", "Main_Task_name", "offset_days", "Sub_Task_name", "description", "name", "calculated_start_date", "calculated_end_date", "duration"])
    if not df.empty:
        df["calculated_start_date"] = pd.to_datetime(df["calculated_start_date"]).dt.date
        df["calculated_end_date"] = pd.to_datetime(df["calculated_end_date"]).dt.date
        df["duration"] = df["duration"].astype(int)
    return df[df["project_id"] == project_id]

# Team_3 페이지 레이아웃 생성 함수
def get_Team_3_layout():
    # 초기 프로젝트 데이터 (Team_3은 group_id=3)
    projects_df = config.load_projects_by_group(3)
    tabs = []
    # 각 프로젝트에 대해 탭 생성
    for project in projects_df.to_dict('records'):
        project_id = project["project_id"]
        tab = dcc.Tab(
            label=project["project_name"],
            value=str(project_id),
            children=[
                html.Div([
                    html.Button("프로젝트 삭제", id={'type': 'team3-delete-project-btn', 'index': project_id}, n_clicks=0, style={'float': 'right'}),
                    html.Div([
                        html.H3("Main Task 관리"),
                        dash_table.DataTable(
                            id={'type': 'team3-main-task-table', 'index': project_id},
                            columns=[
                                {"name": "Main_Task_id", "id": "Main_Task_id", "hideable": True},
                                {"name": "Main_Task_name 이름", "id": "Main_Task_name", "editable": True},
                                {"name": "시작날짜", "id": "Main_Task_start_date", "type": "datetime", "editable": True},
                                {"name": "종료날짜", "id": "Main_Task_end_date", "type": "datetime", "editable": True},
                                {"name": "기간", "id": "duration", "type": "numeric", "editable": False},
                            ],
                            data=load_main_task(project_id).to_dict('records'),
                            editable=True,
                            row_deletable=True,
                        ),
                        html.Button("Main Task 저장", id={'type': 'team3-save-main-task-btn', 'index': project_id}, n_clicks=0),
                        html.Div(id={'type': 'team3-main-task-message', 'index': project_id})
                    ], style={'width': '45%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                    html.Div([
                        html.H3("Sub Task 관리"),
                        dash_table.DataTable(
                            id={'type': 'team3-sub-task-table', 'index': project_id},
                            columns=[
                                {"name": "Sub_Task_id", "id": "Sub_Task_id", "hideable": True},
                                {"name": "스테이지 이름", "id": "Main_Task_name", "editable": True},
                                {"name": "차이나는 날짜", "id": "offset_days", "type": "numeric", "editable": True},
                                {"name": "디테일 이름", "id": "Sub_Task_name", "editable": True},
                                {"name": "설명", "id": "description", "editable": True},
                                {"name": "담당자 이름", "id": "name", "editable": True},
                                {"name": "계산된 시작 날짜", "id": "calculated_start_date", "type": "datetime", "editable": True},
                                {"name": "계산된 종료 날짜", "id": "calculated_end_date", "type": "datetime", "editable": True},
                                {"name": "기간", "id": "duration", "type": "numeric", "editable": False},
                            ],
                            data=load_sub_task(project_id).to_dict('records'),
                            editable=True,
                            row_deletable=True,
                        ),
                        html.Button("Sub Task 저장", id={'type': 'team3-save-sub-task-btn', 'index': project_id}, n_clicks=0),
                        html.Div(id={'type': 'team3-sub-task-message', 'index': project_id})
                    ], style={'width': '45%', 'display': 'inline-block', 'marginLeft': '5%', 'verticalAlign': 'top'}),
                ], style={'padding': '10px'})
            ]
        )
        tabs.append(tab)
    layout = html.Div([
        html.H1("Team_3 일정관리"),
        html.Details([
            html.Summary("새 프로젝트 추가"),
            html.Div([
                html.Label("프로젝트 이름"),
                dcc.Input(id="team3-new-project-name", type="text", value="", style={'margin': '5px'}),
                html.Label("시작 날짜"),
                dcc.DatePickerSingle(id="team3-new-start-date", date=datetime.now().date()),
                html.Label("종료 날짜"),
                dcc.DatePickerSingle(id="team3-new-end-date", date=datetime.now().date()),
                html.Button("프로젝트 추가", id="team3-add-project-btn", n_clicks=0)
            ], style={'margin': '10px'})
        ]),
        html.Div(id="team3-add-project-message"),
        dcc.Tabs(id="team3-project-tabs", value=tabs[0].value if tabs else 'none', children=tabs),
        dcc.Store(id="team3-project-data", data=projects_df.to_dict('records'))
    ])
    return layout

# (참고: 각 버튼 및 DataTable에 대해 별도의 콜백을 등록하여
#  - 새 프로젝트 추가 시 DB에 INSERT 후 dcc.Store 및 탭 업데이트
#  - 프로젝트 삭제 시 DB에서 삭제하고 화면 새로고침
#  - Main Task, Sub Task 저장 시 각 테이블의 변경 데이터를 DB에 반영
# 원본 Streamlit 로직과 동일한 기능을 구현할 수 있습니다.)
