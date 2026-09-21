import streamlit as st
import pandas as pd

st.set_page_config(page_title="회의실 예약 시스템", layout="wide")

# 세션 상태 초기화 (풍부한 예시 데이터 3명 및 예약 내역 포함)
if "reservations" not in st.session_state:
    st.session_state.reservations = [
        {"id": 1, "user": "김철수", "room": "4인실", "date": "2026-09-25", "time": "14:00-15:00", "status": "예약완료"},
        {"id": 2, "user": "이영희", "room": "6인실", "date": "2026-09-26", "time": "10:00-12:00", "status": "예약완료"},
        {"id": 3, "user": "박민수", "room": "8인실", "date": "2026-09-27", "time": "13:00-15:00", "status": "예약완료"}
    ]
if "room_max" not in st.session_state:
    st.session_state.room_max = {
        "4인실": 4,
        "6인실": 4,
        "8인실": 2,
        "대회의실": 1
    }
if "room_counts" not in st.session_state:
    st.session_state.room_counts = {
        "4인실": 3,  # 김철수 예약으로 1개 차감 반영
        "6인실": 3,  # 이영희 예약으로 1개 차감 반영
        "8인실": 1,  # 박민수 예약으로 1개 차감 반영
        "대회의실": 1
    }
if "room_locks" not in st.session_state:
    st.session_state.room_locks = {
        "4인실": 0,
        "6인실": 0,
        "8인실": 0,
        "대회의실": 0
    }

# 예시 회원 3명 (김철수: 정상, 이영희: 노쇼 누적 및 블랙리스트, 박민수: 주의 대상)
if "member_status" not in st.session_state:
    st.session_state.member_status = {
        "김철수": {"noshow": 0, "is_blacklist": False},
        "이영희": {"noshow": 3, "is_blacklist": True},
        "박민수": {"noshow": 1, "is_blacklist": False}
    }

if "notices" not in st.session_state:
    st.session_state.notices = ["[공지] 추석 연휴 기간 회의실 이용 안내", "[경고] 노쇼 3회 이상 회원 자동 차단 시스템 가동"]
if "history" not in st.session_state:
    st.session_state.history = [
        "시스템 초기화 완료",
        "[예약 생성] 예약자: 김철수 | 회의실: 4인실 | 일시: 2026-09-25 14:00-15:00",
        "[예약 생성] 예약자: 이영희 | 회의실: 6인실 | 일시: 2026-09-26 10:00-12:00",
        "[예약 생성] 예약자: 박민수 | 회의실: 8인실 | 일시: 2026-09-27 13:00-15:00",
        "[블랙리스트 지정] 회원 '이영희' 블랙리스트 등록됨 (노쇼 누적: 3회)"
    ]

# 관리자 로그인 상태 초기화 (기본값: False)
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

# 로그인이 안 되어 있을 때: 메인 화면 중앙에 로그인 창 배치
if not st.session_state.is_admin:
    st.markdown("<h1 style='text-align: center;'>🏢 스마트 회의실 예약 및 관리 시스템</h1>", unsafe_allow_html=True)
    st.write("")
    st.write("")
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        st.markdown("### 🔐 관리자 로그인")
        admin_id = st.text_input("관리자 ID")
        admin_pw = st.text_input("비밀번호", type="password")
        
        if st.button("로그인", use_container_width=True):
            if admin_id == "admin" and admin_pw == "1234":
                st.session_state.is_admin = True
                st.success("로그인 성공!")
                st.rerun()
            else:
                st.error("ID 또는 비밀번호가 틀렸습니다. (기본: admin / 1234)")

# 로그인 성공 후 화면 (사이드바 및 기능 메뉴)
else:
    st.title("🏢 스마트 회의실 예약 및 관리 시스템")
    
    st.sidebar.header("🔐 관리자 메뉴")
    st.sidebar.info("관리자로 로그인 중입니다.")
    if st.sidebar.button("로그아웃"):
        st.session_state.is_admin = False
        st.rerun()

    menu = st.sidebar.selectbox(
        "기능 선택",
        ["예약 관리", "회원 정보 및 블랙리스트", "좌석/회의실 락(Lock) 컨트롤", "공지사항 및 경고 메시지", "히스토리 조회"]
    )

    # 1. 예약 관리 
    if menu == "예약 관리":
        st.header("📌 회의실 예약 관리")
        
        tab1, tab2, tab3, tab4 = st.tabs(["예약하기", "예약조회", "예약변경/연장", "예약취소"])
        
        with tab1:
            st.subheader("새 회의실 예약 생성")
            
            with st.form("create_form", clear_on_submit=True):
                user_name = st.text_input("예약자 이름 (예: 김철수, 이영희 등)")
                
                is_black = False
                if user_name in st.session_state.member_status and st.session_state.member_status[user_name]["is_blacklist"]:
                    is_black = True
                    st.error("🚨 블랙리스트에 등록된 사용자는 예약을 생성할 수 없습니다.")
                
                room_options = [
                    f"4인실 ({st.session_state.room_counts['4인실']})",
                    f"6인실 ({st.session_state.room_counts['6인실']})",
                    f"8인실 ({st.session_state.room_counts['8인실']})",
                    f"대회의실 ({st.session_state.room_counts['대회의실']})"
                ]
                selected_room_option = st.selectbox("회의실 선택", room_options)
                
                res_date = st.date_input("예약 날짜")
                res_time = st.text_input("예약 시간 (예: 10:00-15:00)")
                submitted = st.form_submit_button("예약 등록")
                
                if submitted:
                    if not user_name:
                        st.warning("예약자 이름을 입력해주세요.")
                    elif is_black:
                        st.error("블랙리스트 회원은 예약을 등록할 수 없습니다.")
                    else:
                        clean_room_name = selected_room_option.split(" ")[0]
                        
                        if st.session_state.room_counts[clean_room_name] <= 0:
                            st.error(f"선택하신 {clean_room_name}은(는) 남은 방이 없거나 모두 차단되어 예약할 수 없습니다.")
                        else:
                            try:
                                start_str, end_str = res_time.split("-")
                                start_h, start_m = map(int, start_str.strip().split(":"))
                                end_h, end_m = map(int, end_str.strip().split(":"))
                                
                                total_start_mins = start_h * 60 + start_m
                                total_end_mins = end_h * 60 + end_m
                                duration_hours = (total_end_mins - total_start_mins) / 60
                                
                                if duration_hours <= 0:
                                    st.error("시작 시간은 종료 시간보다 빨라야 합니다.")
                                elif duration_hours > 5:
                                    st.error(f"최대 예약 가능 시간은 5시간입니다. (현재 신청 시간: {duration_hours}시간)")
                                else:
                                    st.session_state.room_counts[clean_room_name] -= 1
                                    new_id = len(st.session_state.reservations) + 1
                                    st.session_state.reservations.append({
                                        "id": new_id, "user": user_name, "room": clean_room_name, 
                                        "date": str(res_date), "time": res_time, "status": "예약완료"
                                    })
                                    
                                    if user_name not in st.session_state.member_status:
                                        st.session_state.member_status[user_name] = {"noshow": 0, "is_blacklist": False}
                                        
                                    st.session_state.history.append(f"[예약 생성] 예약자: {user_name} | 회의실: {clean_room_name} | 일시: {res_date} {res_time}")
                                    st.success("예약이 완료되었습니다! 잔여 개수가 즉시 차감되었습니다.")
                                    st.rerun()
                            except Exception:
                                st.error("시간 형식이 올바르지 않습니다. 예시와 같이 입력해주세요 (예: 10:00-15:00)")

        with tab2:
            st.subheader("예약 현황 조회")
            if st.session_state.reservations:
                df = pd.DataFrame(st.session_state.reservations)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("등록된 예약이 없습니다.")

        with tab3:
            st.subheader("예약 정보 변경 및 시간 연장")
            if st.session_state.reservations:
                res_labels = [f"ID: {r['id']} | 예약자: {r['user']} ({r['room']})" for r in st.session_state.reservations]
                selected_label = st.selectbox("수정할 예약 선택", res_labels)
                
                selected_id = int(selected_label.split("|")[0].replace("ID:", "").strip())
                target = next(r for r in st.session_state.reservations if r["id"] == selected_id)
                
                room_options = [
                    f"4인실 ({st.session_state.room_counts['4인실']})",
                    f"6인실 ({st.session_state.room_counts['6인실']})",
                    f"8인실 ({st.session_state.room_counts['8인실']})",
                    f"대회의실 ({st.session_state.room_counts['대회의실']})"
                ]
                current_room_index = 0
                for idx, opt in enumerate(room_options):
                    if target["room"] in opt:
                        current_room_index = idx
                        break
                        
                new_room_option = st.selectbox("변경할 회의실 선택 (좌석 현황 포함)", room_options, index=current_room_index)
                new_time = st.text_input("변경할 시간 (관리자 권한: 시간 제한 없음)", value=target["time"])
                new_status = st.selectbox("상태 변경", ["예약완료", "시간연장됨", "강제배정"], index=0)
                
                if st.button("예약 수정 적용"):
                    try:
                        start_str, end_str = new_time.split("-")
                        start_h, start_m = map(int, start_str.strip().split(":"))
                        end_h, end_m = map(int, end_str.strip().split(":"))
                        
                        duration_hours = ((end_h * 60 + end_m) - (start_h * 60 + start_m)) / 60
                        
                        if duration_hours <= 0:
                            st.error("시작 시간은 종료 시간보다 빨라야 합니다.")
                        else:
                            target_new_room = new_room_option.split(" ")[0]
                            old_room = target["room"]
                            
                            if old_room != target_new_room:
                                if st.session_state.room_counts[target_new_room] <= 0:
                                    st.error(f"이동하려는 {target_new_room}은(는) 남은 방이 없습니다.")
                                    st.stop()
                                else:
                                    st.session_state.room_counts[old_room] += 1
                                    st.session_state.room_counts[target_new_room] -= 1
                                    target["room"] = target_new_room
                            
                            target["time"] = new_time
                            target["status"] = new_status
                            st.session_state.history.append(f"[예약 수정] 예약 ID {selected_id} ({target['user']}님) 정보 변경됨")
                            st.success("예약 정보가 관리자 권한으로 변경되었습니다.")
                            st.rerun()
                    except Exception:
                        st.error("시간 형식이 올바르지 않습니다. (예: 10:00-15:00)")
            else:
                st.info("수정할 예약이 없습니다.")

        with tab4:
            st.subheader("예약 취소 및 삭제")
            if st.session_state.reservations:
                res_ids = [r["id"] for r in st.session_state.reservations]
                del_id = st.selectbox("삭제할 예약 ID 선택", res_ids, key="del_select")
                if st.button("예약 강제 취소/삭제"):
                    target_res = next((r for r in st.session_state.reservations if r["id"] == del_id), None)
                    if target_res:
                        room_type = target_res["room"]
                        if room_type in st.session_state.room_counts:
                            st.session_state.room_counts[room_type] += 1
                            
                    st.session_state.reservations = [r for r in st.session_state.reservations if r["id"] != del_id]
                    st.session_state.history.append(f"[예약 삭제] 예약 ID {del_id} ({target_res['user']}님) 취소됨")
                    st.warning("예약이 삭제되었습니다.")
                    st.rerun()
            else:
                st.info("삭제할 예약이 없습니다.")

    # 2. 회원 정보 및 노쇼/블랙리스트
    elif menu == "회원 정보 및 블랙리스트":
        st.header("👥 회원 및 노쇼/블랙리스트 관리")
        
        st.subheader("🚫 샘플 회원별 노쇼 및 블랙리스트 현황 (3명)")
        if st.session_state.member_status:
            member_list_data = []
            for name, info in st.session_state.member_status.items():
                member_list_data.append({
                    "회원 이름": name,
                    "누적 노쇼 횟수": f"{info['noshow']}회",
                    "블랙리스트 여부": "등록됨 (예약 차단)" if info['is_blacklist'] else "정상 회원"
                })
            df_members = pd.DataFrame(member_list_data)
            st.dataframe(df_members, use_container_width=True)
        else:
            st.info("등록된 회원 정보가 없습니다.")
        
        st.markdown("---")
        st.subheader("노쇼(No-Show) 처리 및 블랙리스트 관리")
        
        input_name = st.text_input("대상 회원 이름 입력 (예: 김철수, 이영희, 박민수)")
        action_mode = st.radio("관리 작업 선택", ["노쇼 1회 추가", "블랙리스트 지정", "정상 회원으로 해제"])
        
        if st.button("회원 조치 적용"):
            if not input_name:
                st.warning("회원 이름을 입력해주세요.")
            else:
                if input_name not in st.session_state.member_status:
                    st.session_state.member_status[input_name] = {"noshow": 0, "is_blacklist": False}
                
                target_info = st.session_state.member_status[input_name]
                
                if action_mode == "노쇼 1회 추가":
                    target_info["noshow"] += 1
                    st.session_state.history.append(f"[노쇼 발생] 회원 '{input_name}' 노쇼 1회 추가됨 (누적: {target_info['noshow']}회)")
                    st.success(f"'{input_name}'님의 노쇼 횟수가 1회 추가되었습니다. (총 누적: {target_info['noshow']}회)")
                    st.rerun()
                elif action_mode == "블랙리스트 지정":
                    target_info["is_blacklist"] = True
                    st.session_state.history.append(f"[블랙리스트 지정] 회원 '{input_name}' 블랙리스트 등록됨 (노쇼 누적: {target_info['noshow']}회)")
                    st.success(f"'{input_name}'님이 블랙리스트에 등록되었습니다.")
                    st.rerun()
                else:  # 정상 회원 해제
                    target_info["is_blacklist"] = False
                    target_info["noshow"] = 0
                    st.session_state.history.append(f"[블랙리스트 해제] 회원 '{input_name}' 정상 회원으로 복구됨")
                    st.success(f"'{input_name}'님이 정상 회원으로 해제되었습니다.")
                    st.rerun()

    # 3. 임시 좌석/회의실 락(Lock) 컨트롤
    elif menu == "좌석/회의실 락(Lock) 컨트롤":
        st.header("🔒 임시 회의실/좌석 차단 (Lock) 컨트롤")
        st.write("각 회의실별로 차단할 방 개수를 자유롭게 설정한 뒤 일괄 반영할 수 있습니다.")
        
        with st.form("lock_form"):
            new_locks = {}
            for room_name in ["4인실", "6인실", "8인실", "대회의실"]:
                max_limit = st.session_state.room_max[room_name]
                current_locked = st.session_state.room_locks[room_name]
                
                st.markdown(f"### 🚪 {room_name}")
                st.text(f"전체 방 개수: {max_limit}개")
                
                new_locks[room_name] = st.number_input(
                    f"{room_name} 차단할 방 개수 설정", 
                    min_value=0, 
                    max_value=max_limit, 
                    value=current_locked, 
                    step=1,
                    key=f"lock_{room_name}"
                )
                st.markdown("---")
                
            submitted_locks = st.form_submit_button("모든 설정 상태 일괄 반영")
            
            if submitted_locks:
                for room_name, new_val in new_locks.items():
                    max_limit = st.session_state.room_max[room_name]
                    st.session_state.room_locks[room_name] = new_val
                    st.session_state.room_counts[room_name] = max_limit - new_val
                    
                st.session_state.history.append("[회의실 락 변경] 모든 회의실 차단 개수 설정이 일괄 변경됨")
                st.success("모든 회의실의 차단 상태가 예약 시스템에 실시간으로 반영되었습니다!")
                st.rerun()

    # 4. 공지사항 및 경고 메시지 발송
    elif menu == "공지사항 및 경고 메시지":
        st.header("📢 공지사항 및 경고 메시지 발송")
        msg = st.text_area("전송할 메시지 내용 입력")
        if st.button("전송하기"):
            if msg:
                st.session_state.notices.append(msg)
                st.session_state.history.append(f"[공지 발송] 내용: {msg}")
                st.success("메시지가 성공적으로 발송되었습니다!")
            else:
                st.warning("메시지 내용을 입력해주세요.")
        
        if st.session_state.notices:
            st.subheader("발송된 공지/경고 내역")
            for idx, n in enumerate(st.session_state.notices, 1):
                st.write(f"{idx}. {n}")

    # 5. 히스토리 조회
    elif menu == "히스토리 조회":
        st.header("📜 시스템 히스토리 조회 (로그 타임라인)")
        st.info("예약 생성, 삭제, 노쇼 발생, 블랙리스트 지정 등의 모든 활동 이력이 실시간으로 기록됩니다.")
        for h in reversed(st.session_state.history):
            st.text(h)