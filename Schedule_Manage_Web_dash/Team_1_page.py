import dash
from dash import html, dcc, dash_table
import pandas as pd
from datetime import datetime
import config

def load_main_task(project_id):
    df = config.create_dataframe("schedule_Main_Task", columns=["Main_Task_id", "project_id", "Main_Task_name", "Main_Task_start_date", "Main_Task_end_date", "duration", "description"])
    if not df.empty:
        df["Main_Task_start_date"] = pd.to_datetime(df["Main_Task_start_date"]).dt.date
        df["Main_Task_end_date"] = pd.to_datetime(df["Main_Task_end_date"]).dt.date
        df["duration"] = df["duration"].astype(int)
    return df[df["project_id"] == project_id]

def load_sub_task(project_id):
    df = config.create_dataframe("schedule_Sub_Task", columns=["Sub_Task_id", "project_id", "Main_Task_name", "offset_days", "Sub_Task_name", "description", "name", "calculated_start_date", "calculated_end_date", "duration"])
    if not df.empty:
        df["calculated_start_date"] = pd.to_datetime(df["calculated_start_date"]).dt.date
        df["calculated_end_date"] = pd.to_datetime(df["calculated_end_date"]).dt.date
        df["duration"] = df["duration"].astype(int)
    return df[df["project_id"] == project_id]

def get_Team_1_layout():
    projects_df = config.load_projects_by_group(1)
    tabs = [
        dcc.Tab(
            label=project["project_name"],
            value=str(project["project_id"]),
            children=[
                html.Div([
                    html.Button(
                        "프로젝트 삭제", 
                        id={'type': 'team1-delete-project-btn', 'index': project["project_id"]}, 
                        n_clicks=0, 
                        className="delete-btn"
                    ),
                    # 삭제 메시지 영역 분리
                    html.Div(
                        id={'type': 'team1-delete-message', 'index': project["project_id"]},
                        className="delete-message"
                    ),
                    html.Div([
                        html.H3("Main Task 관리"),
                        html.Button("행 추가", id={'type': 'team1-add-main-task-btn', 'index': project["project_id"]}, n_clicks=0, className="add-btn"),
                        dash_table.DataTable(
                            id={'type': 'team1-main-task-table', 'index': project["project_id"]},
                            columns=[
                                {"name": "Main_Task_id", "id": "Main_Task_id", "hideable": True},
                                {"name": "Main_Task_name", "id": "Main_Task_name", "editable": True},
                                {"name": "시작날짜", "id": "Main_Task_start_date", "type": "datetime", "editable": True},
                                {"name": "종료날짜", "id": "Main_Task_end_date", "type": "datetime", "editable": True},
                                {"name": "기간", "id": "duration", "type": "numeric", "editable": False},
                            ],
                            data=load_main_task(project["project_id"]).to_dict('records'),
                            editable=True,
                            row_deletable=True,
                        ),
                        html.Button("Main Task 저장", id={'type': 'team1-save-main-task-btn', 'index': project["project_id"]}, n_clicks=0),
                        html.Div(id={'type': 'team1-main-task-message', 'index': project["project_id"]}, className="main-task-message")
                        ], className="main-task-container"),
                    html.Div([
                        html.H3("Sub Task 관리"),
                        dash_table.DataTable(
                            id={'type': 'team1-sub-task-table', 'index': project["project_id"]},
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
                            data=load_sub_task(project["project_id"]).to_dict('records'),
                            editable=True,
                            row_deletable=True,
                        ),
                        html.Button(
                            "Sub Task 저장", 
                            id={'type': 'team1-save-sub-task-btn', 'index': project["project_id"]}, 
                            n_clicks=0
                        ),
                        html.Div(
                            id={'type': 'team1-sub-task-message', 'index': project["project_id"]},
                            className="sub-task-message"
                        )
                    ], className="sub-task-container"),
                ], className="project-container")
            ]
        )
        for project in projects_df.to_dict('records')
    ]
    layout = html.Div([
        html.H1("Team_1 일정관리"),
        html.Details([
            html.Summary("새 프로젝트 추가"),
            html.Div([
                html.Label("프로젝트 이름"),
                dcc.Input(id="team1-new-project-name", type="text", value="", className="input-margin"),
                html.Label("시작 날짜"),
                dcc.DatePickerSingle(id="team1-new-start-date", date=datetime.now().date()),
                html.Label("종료 날짜"),
                dcc.DatePickerSingle(id="team1-new-end-date", date=datetime.now().date()),
                html.Button("프로젝트 추가", id="team1-add-project-btn", n_clicks=0)
            ], className="new-project-container")
        ]),
        html.Div(id="team1-add-project-message"),
        dcc.Tabs(id="team1-project-tabs", value=tabs[0].value if tabs else 'none', children=tabs),
        dcc.Store(id="team1-project-data", data=projects_df.to_dict('records'))
    ])
    return layout
