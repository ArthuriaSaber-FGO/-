import streamlit as st
import pandas as pd

st.set_page_config(page_title="회의실 예약 시스템", layout="wide")

# 세션 상태 초기화 (데이터베이스 대용)
if "reservations" not in st.session_state:
    st.session_state.reservations = [
        {"id": 1, "user": "김철수", "room": "A회의실", "date": "2026-09-25", "time": "14:00-15:00", "status": "예약완료"}
    ]
if "members" not in st.session_state:
    st.session_state.members = [
        {"id": "user1", "name": "김철수", "noshow": 0, "status": "정상"},
        {"id": "user2", "name": "이영희", "noshow": 2, "status": "블랙리스트"}
    ]
if "notices" not in st.session_state:
    st.session_state.notices = []
if "history" not in st.session_state:
    st.session_state.history = ["시스템 초기화 완료"]

# 관리자 로그인 상태 초기화
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

st.title("🏢 스마트 회의실 예약 및 관리 시스템")

# 사이드바 - 관리자 로그인 및 메뉴
st.sidebar.header("🔐 관리자 로그인")
if not st.session_state.is_admin:
    admin_id = st.sidebar.text_input("관리자 ID")
    admin_pw = st.sidebar.text_input("비밀번호", type="password")
    if st.sidebar.button("로그인"):
        # 기본 관리자 계정: admin / 1234
        if admin_id == "admin" and admin_pw == "1234":
            st.session_state.is_admin = True
            st.sidebar.success("로그인 성공!")
            st.rerun()
        else:
            st.sidebar.error("ID 또는 비밀번호가 틀렸습니다. (기본: admin / 1234)")
else:
    st.sidebar.info("관리자로 로그인 중입니다.")
    if st.sidebar.button("로그아웃"):
        st.session_state.is_admin = False
        st.rerun()

    menu = st.sidebar.selectbox(
        "기능 선택",
        ["예약 관리 (CRUD)", "회원 정보 및 블랙리스트", "좌석/회의실 락(Lock) 컨트롤", "공지사항 및 경고 메시지", "히스토리 조회"]
    )

    # 1. 예약 관리 (CRUD)
    if menu == "예약 관리 (CRUD)":
        st.header("📌 회의실 예약 관리 (C, R, U, D)")
        
        tab1, tab2, tab3, tab4 = st.tabs(["Create (예약생성)", "Read (예약조회)", "Update (예약변경/연장)", "Delete (예약취소)"])
        
        with tab1:
            st.subheader("새 회의실 예약 생성 (Create)")
            with st.form("create_form"):
                user_name = st.text_input("예약자 이름")
                room_name = st.selectbox("회의실 선택", ["A회의실", "B회의실", "C회의실", "대회의실"])
                res_date = st.date_input("예약 날짜")
                res_time = st.text_input("예약 시간 (예: 10:00-11:00)")
                submitted = st.form_submit_button("예약 등록")
                if submitted and user_name:
                    new_id = len(st.session_state.reservations) + 1
                    st.session_state.reservations.append({
                        "id": new_id, "user": user_name, "room": room_name, 
                        "date": str(res_date), "time": res_time, "status": "예약완료"
                    })
                    st.session_state.history.append(f"[CREATE] {user_name}님이 {room_name} 예약 생성")
                    st.success("예약이 완료되었습니다!")
                    st.rerun()

        with tab2:
            st.subheader("예약 현황 조회 (Read)")
            if st.session_state.reservations:
                df = pd.DataFrame(st.session_state.reservations)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("등록된 예약이 없습니다.")

        with tab3:
            st.subheader("예약 정보 변경 및 시간 연장 (Update)")
            if st.session_state.reservations:
                res_ids = [r["id"] for r in st.session_state.reservations]
                selected_id = st.selectbox("수정할 예약 ID 선택", res_ids)
                target = next(r for r in st.session_state.reservations if r["id"] == selected_id)
                
                new_time = st.text_input("변경할 시간 (연장 포함)", value=target["time"])
                new_status = st.selectbox("상태 변경", ["예약완료", "시간연장됨", "강제배정"], index=0)
                
                if st.button("예약 수정 적용"):
                    target["time"] = new_time
                    target["status"] = new_status
                    st.session_state.history.append(f"[UPDATE] 예약 ID {selected_id} 수정됨")
                    st.success("예약 정보가 변경되었습니다.")
                    st.rerun()
            else:
                st.info("수정할 예약이 없습니다.")

        with tab4:
            st.subheader("예약 취소 및 삭제 (Delete)")
            if st.session_state.reservations:
                res_ids = [r["id"] for r in st.session_state.reservations]
                del_id = st.selectbox("삭제할 예약 ID 선택", res_ids, key="del_select")
                if st.button("예약 강제 취소/삭제"):
                    st.session_state.reservations = [r for r in st.session_state.reservations if r["id"] != del_id]
                    st.session_state.history.append(f"[DELETE] 예약 ID {del_id} 삭제됨")
                    st.warning("예약이 삭제되었습니다.")
                    st.rerun()
            else:
                st.info("삭제할 예약이 없습니다.")

    # 2. 회원 정보 및 노쇼/블랙리스트
    elif menu == "회원 정보 및 블랙리스트":
        st.header("👥 회원 정보 및 노쇼(No-Show) / 블랙리스트 관리")
        df_members = pd.DataFrame(st.session_state.members)
        st.dataframe(df_members, use_container_width=True)
        
        st.subheader("노쇼 회원 블랙리스트 지정")
        member_ids = [m["id"] for m in st.session_state.members]
        target_member = st.selectbox("대상 회원 ID", member_ids)
        action_type = st.radio("조치 선택", ["정상 해제", "블랙리스트 지정"])
        
        if st.button("회원 상태 변경"):
            for m in st.session_state.members:
                if m["id"] == target_member:
                    m["status"] = "정상" if action_type == "정상 해제" else "블랙리스트"
            st.session_state.history.append(f"[MEMBER] 회원 {target_member} 상태 변경: {action_type}")
            st.success("회원 상태가 업데이트되었습니다.")
            st.rerun()

    # 3. 임시 좌석/회의실 차단(Lock) 컨트롤
    elif menu == "좌석/회의실 락(Lock) 컨트롤":
        st.header("🔒 임시 회의실/좌석 차단 (Lock) 컨트롤")
        lock_room = st.selectbox("차단할 회의실 선택", ["A회의실", "B회의실", "C회의실", "대회의실"])
        lock_status = st.radio("제어 상태", ["사용 가능 (Unlock)", "임시 차단 (Lock)"])
        
        if st.button("상태 반영"):
            st.session_state.history.append(f"[LOCK] {lock_room} 상태 변경: {lock_status}")
            st.success(f"{lock_room}이(가) [{lock_status}] 상태로 설정되었습니다.")

    # 4. 공지사항 및 경고 메시지 발송
    elif menu == "공지사항 및 경고 메시지":
        st.header("📢 공지사항 및 경고 메시지 발송")
        msg = st.text_area("전송할 메시지 내용 입력")
        if st.button("전송하기"):
            if msg:
                st.session_state.notices.append(msg)
                st.session_state.history.append(f"[NOTICE] 공지/경고 발송: {msg}")
                st.success("메시지가 성공적으로 발송되었습니다!")
            else:
                st.warning("메시지 내용을 입력해주세요.")
        
        if st.session_state.notices:
            st.subheader("발송된 공지/경고 내역")
            for idx, n in enumerate(st.session_state.notices, 1):
                st.write(f"{idx}. {n}")

    # 5. 히스토리 조회
    elif menu == "히스토리 조회":
        st.header("📜 시스템 히스토리 조회")
        for h in reversed(st.session_state.history):
            st.text(h)

# 로그인 전 화면 안내 (들여쓰기 수정 완료)
if not st.session_state.is_admin:
    st.info("👈 좌측 사이드바에서 관리자 로그인(ID: **admin**, PW: **1234**)을 진행해주세요.")
    st.markdown("### 📋 구현된 기능 요약")
    st.markdown("- **관리자 로그인** (`Id`, `pw` 인증)")
    st.markdown("- **회원정보 확인** 및 **노쇼 관리 / 블랙리스트 지정**")
    st.markdown("- **예약 정보 CRUD** (생성, 조회, 변경/연장, 취소/삭제, 강제배정)")
    st.markdown("- **임시 좌석/회의실 차단(Lock) 컨트롤**")
    st.markdown("- **공지사항 및 경고 메시지 발송**, **히스토리 조회** 기능 포함")