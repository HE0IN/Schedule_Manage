import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import timedelta
from config import (
    connect_to_database,
    create_dataframe,
    get_group_id_by_name,
    delete_project,
    load_projects_by_group,
)


def Team_3_page():
    st.title("Team_3 일정관리")

    # 예를 들어, 'Team_3'의 group_id가 1이이라면
    if "projects_Team_3" not in st.session_state:
        # group_id가 1인 프로젝트를 로드하여 세션 상태에 저장
        st.session_state["projects_Team_3"] = load_projects_by_group(3)

    # '새 프로젝트 추가'라는 제목의 확장자를 생성
    with st.expander("새 프로젝트 추가"):
        # 확장자 내부 입력받는 폼 생성
        with st.form("add_project_form"):

            # 신규 프로젝트 입력 요소
            new_project_name = st.text_input("프로젝트 이름", "")
            new_start_date = st.date_input("시작 날짜")
            new_end_date = st.date_input("종료 날짜")
            submitted = st.form_submit_button("프로젝트 추가")

            # 신규 프로젝트 id 지정
            group_id = get_group_id_by_name("Team_3")
            if group_id is None:
                group_id = 3  # 혹은 기본값 지정

            # 프로젝트 추가 버튼이 눌린경우
            if submitted:
                # 신규 프로젝트 이름이 비어있지 않다면 (.strip() 함수는 문자열 앞 뒤 공백제거)
                if new_project_name.strip():
                    conn = connect_to_database()
                    cur = conn.cursor()
                    # 데이터베이스에 신규 프로젝트 데이터 삽입
                    cur.execute(
                        """
                        INSERT INTO schedule_projects (project_name, start_date, end_date, group_id)
                        VALUES (%s, %s, %s, %s);
                        """,
                        (new_project_name, new_start_date, new_end_date, group_id),
                    )
                    # 변경 사항을 데이터베이스에 저장
                    conn.commit()
                    cur.close()
                    # 성공 메세지
                    st.success(f"'{new_project_name}' 프로젝트가 추가되었습니다!")
                    # 프로젝트 세션 업데이트
                    st.session_state["projects_Team_3"] = load_projects_by_group(3)
                else:
                    st.error("프로젝트 이름을 입력하세요.")

    # 세션에 저장된 프로젝트 데이터프레임을 변수로 저장
    df_project = st.session_state["projects_Team_3"]

    # project_name 기준 반복문으로 탭 생성
    if not df_project.empty:
        project_tabs = st.tabs(
            [row["project_name"] for _, row in df_project.iterrows()]
        )
    else:
        st.write("프로젝트가 없습니다.")
        project_tabs = []

    # zip() 함수는 요소를 병렬로 묶어서 동시에 반복
    # enumerate() 함수는 반복 횟수를 나타내는 idx 인덱스 생성 -> 탭별 id
    for idx, (tab, (_, project)) in enumerate(zip(project_tabs, df_project.iterrows())):

        with tab:

            # 프로젝트 삭제 버튼(10:1 비율로 컬럼나누어서 위치 조정, 오른쪽 끝)
            col_header, col_btn = st.columns([10, 1])

            # 프로젝트 삭제 버튼(생성)
            with col_btn:
                if st.button("프로젝트 삭제", key=f"delete_{project['project_id']}"):
                    # 삭제 함수 실행
                    delete_project(project["project_id"])
                    # 세션에 저장된 프로젝트 데이터 프레임 업데이트
                    st.session_state["projects_Team_3"] = load_projects_by_group(3)

            # 프로젝트 삭제 버튼 누르면 삭제(한 번 누르면 DB에서 삭제, 두 번 누르면 화면에서 탭이 사라짐.
            # 두 번 눌러야 사라지는 이유는 누르는 순간에 DB삭제와 화면 새로고침이 동시에 되지 않기 때문)

            # Main Task 데이터 로드
            df_Main_Task = create_dataframe(
                None,
                "schedule_Main_Task",
                columns=[
                    "Main_Task_id",
                    "project_id",
                    "Main_Task_name",
                    "Main_Task_start_date",
                    "Main_Task_end_date",
                    "duration",
                    "description",
                ],
            )
            # Sub Task 데이터 로드
            df_Sub_Task = create_dataframe(
                None,
                "schedule_Sub_Task",
                columns=[
                    "Sub_Task_id",
                    "project_id",
                    "Main_Task_name",
                    "offset_days",
                    "Sub_Task_name",
                    "description",
                    "name",
                    "calculated_start_date",
                    "calculated_end_date",
                    "duration",
                ],
            )

            try:
                # df_Main_Task 데이터프레임의 'Main_Task_start_date' 열을 datetime 형식으로 변환
                df_Main_Task["Main_Task_start_date"] = pd.to_datetime(
                    df_Main_Task["Main_Task_start_date"]
                )
                # df_Main_Task 데이터프레임의 'Main_Task_end_date' 열을 datetime 형식으로 변환
                df_Main_Task["Main_Task_end_date"] = pd.to_datetime(
                    df_Main_Task["Main_Task_end_date"]
                )
                # 'Main_Task_start_date'와 'Main_Task_end_date'의 차이를 계산하여 'duration' 열을 생성
                df_Main_Task["duration"] = (
                    df_Main_Task["Main_Task_end_date"]
                    - df_Main_Task["Main_Task_start_date"]
                ).dt.days
                # df_Main_Task 데이터프레임에서 'project_id'가 project["project_id"]와 일치하는 행을 필터링
                filtered_Main_Task = df_Main_Task[
                    df_Main_Task["project_id"] == project["project_id"]
                ]
                # filtered_Main_Task 데이터프레임의 인덱스를 초기화
                filtered_Main_Task = filtered_Main_Task.reset_index(drop=True)
            except KeyError as e:
                st.error(f"필요한 컬럼 {e.args[0]}가 데이터 프레임에 없습니다.")
                st.stop()

            # df_Sub_Task 데이터프레임에서 'project_id'가 project["project_id"]와 일치하는 행을 필터링
            try:
                filtered_Sub_Task = df_Sub_Task[
                    df_Sub_Task["project_id"] == project["project_id"]
                ]
                filtered_Sub_Task = filtered_Sub_Task.reset_index(drop=True)
            except KeyError as e:
                st.error(f"필요한 컬럼 {e.args[0]}가 데이터 프레임에 없습니다.")
                st.stop()

            # 컬럼 나누어서 테이블배치
            col1, col2 = st.columns([3, 5])
            with col1:
                st.subheader("Main Task 관리")
                with st.form(key=f"main_task_form_{project['project_id']}_{idx}"):
                    # Main_Task_placeholder = st.empty()는 스트림릿에서 빈 영역을 생성하는 함수
                    # 이 함수는 이후에 다른 요소를 추가하거나 수정할 수 있는 빈 영역을 생성
                    Main_Task_placeholder = st.empty()

                    # 삭제를 위한 원본 데이터 미리 저장
                    # (원본 데이터와 비교해서 수정 내역이 있으면 입력, 삭제 적용하기 위해서)
                    Main_Task_original_key = (
                        f"original_Main_Task_{project['project_id']}"
                    )
                    updated_data_key = f"updated_Main_Task_{project['project_id']}"

                    if updated_data_key in st.session_state:
                        current_data = st.session_state[updated_data_key]
                    else:
                        current_data = filtered_Main_Task.copy()
                        st.session_state[Main_Task_original_key] = current_data.copy()

                    # filtered_Main_Task로 필터링 된 Main_Task데이터를 테이블로 생성
                    edited_Main_Task = Main_Task_placeholder.data_editor(
                        current_data,
                        column_config={
                            "Main_Task_id": {"hidden": True},
                            "project_id": {"hidden": True},
                            "Main_Task_name": {"type": "text", "name": "스테이지 이름"},
                            "Main_Task_start_date": {
                                "type": "date",
                                "name": "시작날짜",
                            },
                            "Main_Task_end_date": {"type": "date", "name": "종료날짜"},
                            "duration": {"type": "int", "name": "기간"},
                            "description": {"hidden": True},
                        },
                        num_rows="dynamic",
                        key=f"Main_Task_editor_{project['project_id']}_{idx}",
                        height=500,
                    )

                    submit_main = st.form_submit_button("Main Task 저장")
                    if submit_main:
                        conn = connect_to_database()
                        cur = conn.cursor()

                        Main_Task_original_ids = set(
                            st.session_state[Main_Task_original_key][
                                "Main_Task_id"
                            ].tolist()
                        )
                        # 수정된 데이터의 Main_Task_id를 세트로 저장
                        Main_Task_edited_ids = set(
                            edited_Main_Task["Main_Task_id"].tolist()
                        )
                        # 삭제된 Main_Task_id를 원본 데이터의 Main_Task_id와 수정된 데이터의 Main_Task_id를 비교하여 차이를 찾기
                        deleted_Main_Task_ids = (
                            Main_Task_original_ids - Main_Task_edited_ids
                        )

                        # 삭제된 Main_Task_id를 데이터베이스에서 삭제
                        for Main_Task_id in deleted_Main_Task_ids:
                            cur.execute(
                                "DELETE FROM schedule_Main_Task WHERE Main_Task_id = %s",
                                (Main_Task_id,),
                            )

                        # edited_Main_Task의 모든 행을 반복
                        for _, row in edited_Main_Task.iterrows():
                            # row 내부의 NaN의 값을 None으로 변환(SQL삽입 시 NULL처리 가능하도록, NaN값은 MySQL에서 처리 불가능)
                            row = row.where(pd.notnull(row), None)
                            # start_date와 end_date값을 date_time형식으로 변환
                            start_date = pd.to_datetime(row["Main_Task_start_date"])
                            end_date = pd.to_datetime(row["Main_Task_end_date"])
                            # 두 날짜간의 차이를 계산하여 duration(기간, 일 수) 저장
                            duration = (end_date - start_date).days
                            # 'duration' 열에 duration 계산 값 저장
                            row["duration"] = duration
                            # MySQL 쿼리 실행하여 데이터를 테이블에 삽입
                            cur.execute(
                                """
                                INSERT INTO schedule_Main_Task (
                                    Main_Task_id, project_id, Main_Task_name, Main_Task_start_date, Main_Task_end_date, duration, description
                                )
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                                ON DUPLICATE KEY UPDATE
                                    Main_Task_name = VALUES(Main_Task_name),
                                    Main_Task_start_date = VALUES(Main_Task_start_date),
                                    Main_Task_end_date = VALUES(Main_Task_end_date),
                                    duration = VALUES(duration),
                                    description = VALUES(description)
                                """,
                                (
                                    row["Main_Task_id"],
                                    project["project_id"],
                                    row["Main_Task_name"],
                                    row["Main_Task_start_date"],
                                    row["Main_Task_end_date"],
                                    row["duration"],
                                    row["description"],
                                ),
                            )
                        conn.commit()
                        cur.close()
                        st.success("Main Task 정보가 저장되었습니다.")

                        # 변경된 데이터베이스를 다시 연결하여 받아오는 코드
                        conn = connect_to_database()
                        df_Main_Task_updated = create_dataframe(
                            conn,
                            "schedule_Main_Task",
                            columns=[
                                "Main_Task_id",
                                "project_id",
                                "Main_Task_name",
                                "Main_Task_start_date",
                                "Main_Task_end_date",
                                "duration",
                                "description",
                            ],
                        )
                        df_Main_Task_updated = df_Main_Task_updated[
                            df_Main_Task_updated["project_id"] == project["project_id"]
                        ].reset_index(drop=True)

                        st.session_state[updated_data_key] = df_Main_Task_updated.copy()

            with col2:
                st.subheader("Sub Task 관리")
                with st.form(key=f"sub_task_form_{project['project_id']}_{idx}"):

                    Sub_Task_placeholder = st.empty()

                    # 삭제를 위한 원본 데이터 미리 저장
                    Sub_Task_original_key = f"original_Sub_Task_{project['project_id']}"
                    updated_sub_data_key = f"updated_Sub_Task_{project['project_id']}"

                    if updated_sub_data_key in st.session_state:
                        current_sub_data = st.session_state[updated_sub_data_key]
                    else:
                        current_sub_data = filtered_Sub_Task.copy()
                        st.session_state[Sub_Task_original_key] = (
                            current_sub_data.copy()
                        )

                    # 데이터 편집 UI
                    edited_Sub_Task = Sub_Task_placeholder.data_editor(
                        current_sub_data,
                        column_config={
                            "Sub_Task_id": {"hidden": True},
                            "project_id": {"hidden": True},
                            "Main_Task_name": {"type": "text", "name": "스테이지 이름"},
                            "offset_days": {"type": "int", "name": "차이나는 날짜"},
                            "Sub_Task_name": {"type": "text", "name": "디테일 이름"},
                            "description": {"type": "text", "name": "설명"},
                            "name": {"type": "text", "name": "담당자 이름"},
                            "calculated_start_date": {
                                "type": "date",
                                "name": "계산된 시작 날짜",
                            },
                            "calculated_end_date": {
                                "type": "date",
                                "name": "계산된 종료 날짜",
                            },
                            "duration": {"type": "int", "name": "기간"},
                        },
                        column_order=[
                            "Main_Task_name",
                            "offset_days",
                            "Sub_Task_name",
                            "description",
                            "name",
                            "duration",
                            "calculated_start_date",
                            "calculated_end_date",
                        ],
                        num_rows="dynamic",
                        key=f"Sub_Task_editor_{project['project_id']}_{idx}",
                        height=500,
                    )

                    submit_sub = st.form_submit_button("Sub Task 저장")
                    if submit_sub:
                        conn = connect_to_database()
                        cur = conn.cursor()

                        Sub_Task_original_ids = set(
                            st.session_state[Sub_Task_original_key][
                                "Sub_Task_id"
                            ].tolist()
                        )

                        # 불러올 때 데이터와 수정 된 데이터 비교
                        Sub_Task_edited_ids = set(
                            edited_Sub_Task["Sub_Task_id"].tolist()
                        )
                        deleted_Sub_Task_ids = (
                            Sub_Task_original_ids - Sub_Task_edited_ids
                        )

                        # 삭제 기능
                        for Sub_Task_id in deleted_Sub_Task_ids:
                            cur.execute(
                                "DELETE FROM schedule_Sub_Task WHERE Sub_Task_id = %s",
                                (Sub_Task_id,),
                            )

                        for _, row in edited_Sub_Task.iterrows():
                            row = row.where(pd.notnull(row), None)

                            if not row["Main_Task_name"]:
                                continue

                            matching_Main_Task = filtered_Main_Task[
                                filtered_Main_Task["Main_Task_name"]
                                .str.strip()
                                .str.lower()
                                == row["Main_Task_name"].strip().lower()
                            ]

                            Main_Task_start_date = pd.to_datetime(
                                matching_Main_Task.iloc[0]["Main_Task_start_date"]
                            )
                            calculated_start_date = Main_Task_start_date + timedelta(
                                days=int(row.get("offset_days") or 0)
                            )
                            calculated_end_date = calculated_start_date + timedelta(
                                days=int(row.get("duration") or 0)
                            )
                            cur.execute(
                                """
                                            INSERT INTO schedule_Sub_Task (
                                                Sub_Task_id, project_id, Main_Task_name, offset_days, Sub_Task_name, description, name,
                                                calculated_start_date, calculated_end_date, duration
                                            )
                                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                            ON DUPLICATE KEY UPDATE
                                                Main_Task_name = VALUES(Main_Task_name),
                                                offset_days = VALUES(offset_days),
                                                Sub_Task_name = VALUES(Sub_Task_name),
                                                description = VALUES(description),
                                                name = VALUES(name),
                                                calculated_start_date = VALUES(calculated_start_date),
                                                calculated_end_date = VALUES(calculated_end_date),
                                                duration = VALUES(duration);

                                            """,
                                (
                                    row["Sub_Task_id"],
                                    project["project_id"],
                                    row["Main_Task_name"],
                                    int(row.get("offset_days", 0) or 0),
                                    row["Sub_Task_name"],
                                    row["description"],
                                    row["name"],
                                    calculated_start_date,
                                    calculated_end_date,
                                    int(row.get("duration", 0) or 0),
                                ),
                            )
                        conn.commit()
                        cur.close()
                        st.success("Sub Task 정보가 저장되었습니다.")

                        # --- 저장 후 즉시 최신 데이터를 조회하여 원본 업데이트 및 data_editor 재생성 ---
                        conn = connect_to_database()
                        df_Sub_Task_updated = create_dataframe(
                            conn,
                            "schedule_Sub_Task",
                            columns=[
                                "Sub_Task_id",
                                "project_id",
                                "Main_Task_name",
                                "offset_days",
                                "Sub_Task_name",
                                "description",
                                "name",
                                "calculated_start_date",
                                "calculated_end_date",
                                "duration",
                            ],
                        )
                        df_Sub_Task_updated = df_Sub_Task_updated[
                            df_Sub_Task_updated["project_id"] == project["project_id"]
                        ].reset_index(drop=True)

                        st.session_state[updated_sub_data_key] = (
                            df_Sub_Task_updated.copy()
                        )
