import dash
from dash import html, dcc, dash_table, Input, Output
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, MATCH
import pandas as pd
import config
from Team_1_page import get_Team_1_layout
from Team_2_page import get_Team_2_layout
from Team_3_page import get_Team_3_layout

def get_home_layout():
    df_groups = config.create_dataframe("schedule_groups", columns=["group_id", "group_name", "description"])
    df_members = config.create_dataframe("schedule_employees", columns=["employee_id", "name", "employee_code", "email", "group_id"])
    return html.Div([
        html.H1("📊 센터 일정관리 DB"),
        dcc.Tabs(id="home-tabs", value="groups", children=[
            dcc.Tab(label="🏢 그룹 & 인원", value="groups"),
            dcc.Tab(label="📌 프로젝트", value="projects"),
            dcc.Tab(label="📋 Main Task", value="main_task"),
            dcc.Tab(label="📝 Sub Task", value="sub_task"),
        ]),
        html.Div(id="home-tab-content", className="home-tab-content")
    ])

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
server = app.server

app.layout = dbc.Container([
    # Header 영역
    html.Div([
        html.H1("센터 일정 관리 앱", className="header-title")
    ], className="header"),

    # 메인 콘텐츠 영역 (사이드바와 페이지 콘텐츠)
    dbc.Row([
        dbc.Col([
            html.H2("생산 DT 센터"),
            dcc.Dropdown(
                id="page-selection",
                options=[
                    {"label": "Home", "value": "home"},
                    {"label": "Team_1", "value": "team1"},
                    {"label": "Team_2", "value": "team2"},
                    {"label": "Team_3", "value": "team3"}
                ],
                value="home",
                clearable=False
            ),
            html.Div(id="sidebar-member-list", className="sidebar-member-list")
        ], width=3),
        dbc.Col(html.Div(id="page-content", className="page-content"), width=9)
    ], className="main-row"),

    # Footer 영역
    html.Div([
        html.P("© 2025 센터 일정 관리. All rights reserved.")
    ], className="footer")
], fluid=True)

@app.callback(
    Output("page-content", "children"),
    Input("page-selection", "value")
)
def render_page(page):
    if page == "home":
        return get_home_layout()
    elif page == "team1":
        return get_Team_1_layout()
    elif page == "team2":
        return get_Team_2_layout()
    elif page == "team3":
        return get_Team_3_layout()
    else:
        return html.Div(f"{page} 페이지는 현재 구현되지 않았습니다.")

@app.callback(
    Output("home-tab-content", "children"),
    Input("home-tabs", "value")
)
def render_home_tab(tab_value):
    if tab_value == "groups":
        df_groups = config.create_dataframe("schedule_groups", columns=["group_id", "group_name", "description"])
        df_members = config.create_dataframe("schedule_employees", columns=["employee_id", "name", "employee_code", "email", "group_id"])
        return html.Div([
            html.H3("🏢 그룹 및 인원 목록"),
            html.Div([
                html.H4("인원 목록"),
                dash_table.DataTable(
                    data=df_members.to_dict('records'),
                    columns=[{"name": col, "id": col} for col in df_members.columns],
                    editable=True
                )
            ], className="member-table-container"),
            html.Div([
                html.H4("그룹 목록"),
                dash_table.DataTable(
                    data=df_groups.to_dict('records'),
                    columns=[{"name": col, "id": col} for col in df_groups.columns],
                    editable=True
                )
            ], className="group-table-container")
        ])
    elif tab_value == "projects":
        df_projects = config.create_dataframe("schedule_projects", columns=["project_id", "project_name", "group_id", "description", "start_date", "end_date", "duration"])
        return html.Div([
            html.H3("📌 프로젝트 목록"),
            dash_table.DataTable(
                data=df_projects.to_dict('records'),
                columns=[{"name": col, "id": col} for col in df_projects.columns],
                editable=True
            )
        ], className="project-table-container")
    elif tab_value == "main_task":
        df_main_task = config.create_dataframe("schedule_Main_Task", columns=["Main_Task_id", "project_id", "Main_Task_name", "Main_Task_start_date", "Main_Task_end_date", "duration", "description"])
        return html.Div([
            html.H3("📋 Main Task 목록"),
            dash_table.DataTable(
                data=df_main_task.to_dict('records'),
                columns=[{"name": col, "id": col} for col in df_main_task.columns],
                editable=True
            )
        ], className="main-task-table-container")
    elif tab_value == "sub_task":
        df_sub_task = config.create_dataframe("schedule_Sub_Task", columns=["Sub_Task_id", "project_id", "Main_Task_name", "offset_days", "Sub_Task_name", "description", "name", "calculated_start_date", "calculated_end_date", "duration"])
        return html.Div([
            html.H3("📝 Sub Task 목록"),
            dash_table.DataTable(
                data=df_sub_task.to_dict('records'),
                columns=[{"name": col, "id": col} for col in df_sub_task.columns],
                editable=True
            )
        ], className="sub-task-table-container")
    return html.Div("알 수 없는 탭")

@app.callback(
    Output("sidebar-member-list", "children"),
    Input("page-selection", "value")
)
def update_sidebar_members(selected_page):
    team_mapping = {"team1": 1, "team2": 2, "team3": 3}
    if selected_page in team_mapping:
        df_member = config.get_member_data(team_mapping[selected_page])
        if not df_member.empty:
            members = [html.Div(f"- {row['name']} ({row['email']})") for _, row in df_member.iterrows()]
            return [html.H5(f"{selected_page} 팀 명단")] + members
        return f"{selected_page} 팀에 등록된 명단이 없습니다."
    return "홈 페이지의 명단은 없습니다."

config.get_scheduler()

@app.callback(
    Output({'type': 'team1-delete-message', 'index': MATCH}, 'children'),
    Input({'type': 'team1-delete-project-btn', 'index': MATCH}, 'n_clicks'),
    State({'type': 'team1-delete-project-btn', 'index': MATCH}, 'id'),
    prevent_initial_call=True
)
def delete_project_callback(n_clicks, btn_id):
    if n_clicks:
        project_id = btn_id['index']
        message = config.delete_project(project_id)
        return message
    return ""


@app.callback(
    [Output("team1-add-project-message", "children"),
     Output("team1-project-data", "data")],
    Input("team1-add-project-btn", "n_clicks"),
    [State("team1-new-project-name", "value"),
     State("team1-new-start-date", "date"),
     State("team1-new-end-date", "date")],
    prevent_initial_call=True
)
def add_project_callback(n_clicks, new_project_name, new_start_date, new_end_date):
    if n_clicks:
        if new_project_name.strip():
            conn = config.connect_to_database()
            cur = conn.cursor()
            try:
                group_id = 1  # Team_1 그룹
                cur.execute(
                    """
                    INSERT INTO schedule_projects (project_name, start_date, end_date, group_id)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (new_project_name, new_start_date, new_end_date, group_id)
                )
                conn.commit()
                message = f"'{new_project_name}' 프로젝트가 추가되었습니다!"
                # 신규 데이터를 불러와 dcc.Store에 업데이트
                projects_df = config.load_projects_by_group(group_id)
                data = projects_df.to_dict('records')
            except Exception as e:
                message = f"프로젝트 추가 중 오류 발생: {e}"
                data = dash.no_update
            finally:
                cur.close()
                conn.close()
            return message, data
        else:
            return "프로젝트 이름을 입력하세요.", dash.no_update
    return dash.no_update, dash.no_update

@app.callback(
    Output({'type': 'team1-main-task-message', 'index': MATCH}, 'children'),
    Input({'type': 'team1-save-main-task-btn', 'index': MATCH}, 'n_clicks'),
    [State({'type': 'team1-main-task-table', 'index': MATCH}, 'data'),
     State({'type': 'team1-save-main-task-btn', 'index': MATCH}, 'id')],
    prevent_initial_call=True
)
def save_main_task_callback(n_clicks, table_data, btn_id):
    project_id = btn_id['index']
    if n_clicks:
        conn = config.connect_to_database()
        cur = conn.cursor()
        try:
            for row in table_data:
                main_task_id = row.get("Main_Task_id")
                if main_task_id:
                    # 기존 행 업데이트
                    cur.execute("""
                        UPDATE schedule_Main_Task
                        SET Main_Task_name=%s,
                            Main_Task_start_date=%s,
                            Main_Task_end_date=%s,
                            duration=%s,
                            description=%s
                        WHERE Main_Task_id=%s
                    """, (row["Main_Task_name"],
                          row["Main_Task_start_date"],
                          row["Main_Task_end_date"],
                          row["duration"],
                          row.get("description", ""),
                          main_task_id))
                else:
                    # 신규 행 INSERT
                    cur.execute("""
                        INSERT INTO schedule_Main_Task (project_id, Main_Task_name, Main_Task_start_date, Main_Task_end_date, duration, description)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (project_id,
                          row["Main_Task_name"],
                          row["Main_Task_start_date"],
                          row["Main_Task_end_date"],
                          row["duration"],
                          row.get("description", "")))
            conn.commit()
            message = "Main Task가 저장되었습니다."
        except Exception as e:
            message = f"Main Task 저장 중 오류 발생: {e}"
        finally:
            cur.close()
            conn.close()
        return message
    return ""

@app.callback(
    Output({'type': 'team1-sub-task-message', 'index': MATCH}, 'children'),
    Input({'type': 'team1-save-sub-task-btn', 'index': MATCH}, 'n_clicks'),
    [State({'type': 'team1-sub-task-table', 'index': MATCH}, 'data'),
     State({'type': 'team1-save-sub-task-btn', 'index': MATCH}, 'id')],
    prevent_initial_call=True
)
def save_sub_task_callback(n_clicks, table_data, btn_id):
    project_id = btn_id['index']
    if n_clicks:
        conn = config.connect_to_database()
        cur = conn.cursor()
        try:
            for row in table_data:
                sub_task_id = row.get("Sub_Task_id")
                if sub_task_id:
                    # 기존 행 업데이트
                    cur.execute("""
                        UPDATE schedule_Sub_Task
                        SET Main_Task_name=%s,
                            offset_days=%s,
                            Sub_Task_name=%s,
                            description=%s,
                            name=%s,
                            calculated_start_date=%s,
                            calculated_end_date=%s,
                            duration=%s
                        WHERE Sub_Task_id=%s
                    """, (row["Main_Task_name"],
                          row["offset_days"],
                          row["Sub_Task_name"],
                          row["description"],
                          row["name"],
                          row["calculated_start_date"],
                          row["calculated_end_date"],
                          row["duration"],
                          sub_task_id))
                else:
                    # 신규 행 INSERT
                    cur.execute("""
                        INSERT INTO schedule_Sub_Task (project_id, Main_Task_name, offset_days, Sub_Task_name, description, name, calculated_start_date, calculated_end_date, duration)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (project_id,
                          row["Main_Task_name"],
                          row["offset_days"],
                          row["Sub_Task_name"],
                          row["description"],
                          row["name"],
                          row["calculated_start_date"],
                          row["calculated_end_date"],
                          row["duration"]))
            conn.commit()
            message = "Sub Task가 저장되었습니다."
        except Exception as e:
            message = f"Sub Task 저장 중 오류 발생: {e}"
        finally:
            cur.close()
            conn.close()
        return message
    return ""

@app.callback(
    Output({'type': 'team1-main-task-table', 'index': MATCH}, 'data'),
    Input({'type': 'team1-add-main-task-btn', 'index': MATCH}, 'n_clicks'),
    State({'type': 'team1-main-task-table', 'index': MATCH}, 'data'),
    prevent_initial_call=True
)
def add_main_task_callback(n_clicks, current_data):
    if n_clicks:
        # 빈 행 정의 (필요한 컬럼에 대해 기본값 설정)
        new_row = {
            "Main_Task_id": None,  # 신규 행이므로 id는 None
            "Main_Task_name": "",
            "Main_Task_start_date": "",
            "Main_Task_end_date": "",
            "duration": 0,
            "description": ""
        }
        current_data.append(new_row)
        return current_data
    return current_data


if __name__ == "__main__":
    app.run_server(debug=True)
