import streamlit as st
from Team_1_page import Team_1_page
from Team_2_page import Team_2_page
from Team_3_page import Team_3_page
from config import get_member_data, get_scheduler, create_dataframe

# 페이지 레이아웃을 wide로 설정
st.set_page_config(layout="wide")


# 모든 그룹 불러오기 함수
def load_all_groups():
    return create_dataframe(
        None, "schedule_groups", columns=["group_id", "group_name", "description"]
    )


# 모든 인원 불러오기 함수
def load_all_members():
    return create_dataframe(
        None,
        "schedule_employees",
        columns=["employee_id", "name", "employee_code", "email", "group_id"],
    )


# 모든 프로젝트 불러오기 함수
def load_all_projects():
    return create_dataframe(
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


# 모든 Main Task 불러오기 함수
def load_all_Main_Task():
    return create_dataframe(
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


# 모든 Sub Task 불러오기 함수
def load_all_Sub_Task():
    return create_dataframe(
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


# 페이지별 내용 출력 함수
def render_content(page):
    # 페이지 선택 함수의 드롭박스와 매칭 후 페이지 로드
    if page == "Home":
        Home_page()
    elif page == "Team_1":
        Team_1_page()
    elif page == "Team_2":
        Team_2_page()
    elif page == "Team_3":
        Team_3_page()


# 페이지 선택 메뉴 함수
def select_page():
    # 사이드바 생성 및 제목 생성
    st.sidebar.title("센터 일정 관리")
    # 드롭박스 생성
    return st.sidebar.selectbox("일정 선택", ["Home", "Team_1", "Team_2", "Team_3"])


def display_sidebar_member_list(selected_page):
    """
    사이드바에 선택된 페이지(팀)의 명단을 표시합니다.
    """
    # 팀 이름과 페이지 매핑 (데이터 베이스의 (group_id)와 매칭)
    # 팀 이름을 키로, 페이지 아이디를 값으로 하는 딕셔너리
    team_mapping = {
        "Team_1": "1",
        "Team_2": "2",
        "Team_3": "3",
    }
    # 선택된 페이지의 팀 아이디를 가져오기
    selected_team = team_mapping.get(selected_page)

    if selected_team:

        # 명단 데이터 가져오기 (config의 get_member_data의 함수, group_id 인자)
        df_member = get_member_data(int(selected_team))

        # 명단이 존재할 때
        if not df_member.empty:
            st.sidebar.subheader(f"{selected_page} 팀 명단")
            # for _, row in ...: iterrows() 함수가 반환하는 튜플을 unpacking하여 변수에 할당하는 방법.
            #  _: 행의 인덱스를 나타내는 변수. _는 파이썬에서 일반적으로 사용하지 않는 변수를 나타내는 관용적 표현.행의 인덱스를 사용하지 않기 때문에 _로 표시했습니다.
            # row: 행의 데이터를 나타내는 변수. 각 행의 데이터를 포함하는 pandas Series 객체입니다.
            # iterrows(): 데이터프레임의 각 행을 반복하는 함수. 각 행을 튜플로 반환, 첫 번째 요소는 행의 인덱스, 두 번째 요소는 행의 데이터
            for _, row in df_member.iterrows():
                st.sidebar.write(f"- {row['name']}\n({row['email']})")
        else:
            st.sidebar.write(f"{selected_page} 팀에 등록된 명단이 없습니다.")


# 메인 함수
def main():
    # 페이지 선택
    page = select_page()
    # 페이지 출력
    render_content(page)
    # 사이드바에 명단 표시
    display_sidebar_member_list(page)

    # 스케줄러 시작하는 함수 (정해진 시간에 e-mail을 보내는 event발생)
    get_scheduler()


def Home_page():
    # 페이지 제목
    st.title("📊 센터 일정관리 DB")

    # 데이터 불러오기
    df_groups = load_all_groups()
    df_members = load_all_members()
    df_projects = load_all_projects()
    df_Main_Task = load_all_Main_Task()
    df_Sub_Task = load_all_Sub_Task()
    print("\ndf_groups\n", df_groups)
    print("\ndf_members\n", df_members)
    print("\ndf_projects\n", df_projects)
    print("\ndf_Main_Task\n", df_Main_Task)
    print("\ndf_Sub_Task\n", df_Sub_Task)

    # 🗂️ 4개 탭 생성
    tabs = st.tabs(["🏢 그룹 & 인원", "📌 프로젝트", "📋 Main Task", "📝 Sub Task"])

    # 1️⃣ 그룹 & 인원 탭
    with tabs[0]:

        # 탭의 소제목
        st.subheader("🏢 그룹 및 인원 목록")

        # 탭의 열, 비율 나누기
        col1, col2 = st.columns((1, 1))

        # 첫 번째 열(인원 테이블)
        with col1:
            st.write("**인원 목록**")
            if not df_members.empty:
                # st.data_editor()은 데이터 프레임을 편집 가능한 테이블의 형태로 출력
                # num_rows="dynamic"으로 설정하여 테이블의 행 수를 동적으로 조정
                df_members = st.data_editor(
                    df_members, num_rows="dynamic", key="member_editor", height=600
                )
            else:
                st.write("등록된 인원이 없습니다.")
        # 두 번째 열(그룹 테이블)
        with col2:
            st.write("**그룹 목록**")
            if not df_groups.empty:
                df_groups = st.data_editor(
                    df_groups, num_rows="dynamic", key="group_editor", height=600
                )
            else:
                st.write("등록된 그룹이 없습니다.")

    # 2️⃣ 프로젝트 탭
    with tabs[1]:
        st.subheader("📌 프로젝트 목록")
        if not df_projects.empty:
            df_projects = st.data_editor(
                df_projects, num_rows="dynamic", key="project_editor"
            )
        else:
            st.write("등록된 프로젝트가 없습니다.")

    # 3️⃣ Main Task 탭
    with tabs[2]:
        st.subheader("📋 Main Task 목록")
        if not df_Main_Task.empty:
            df_Main_Task = st.data_editor(
                df_Main_Task, num_rows="dynamic", key="Main_Task_editor"
            )
        else:
            st.write("등록된 Main Task가 없습니다.")

    # 4️⃣ Sub Task 탭
    with tabs[3]:
        st.subheader("📝 Sub Task 목록")
        if not df_Sub_Task.empty:
            df_Sub_Task = st.data_editor(
                df_Sub_Task, num_rows="dynamic", key="Sub_Task_editor"
            )
        else:
            st.write("등록된 Sub Task이 없습니다.")


# 프로그램 실행
if __name__ == "__main__":
    main()
