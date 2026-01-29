import streamlit as st
import pandas as pd
import requests
import io

# -------------------------------------------------------------
# [설정] 페이지 제목과 아이콘
# -------------------------------------------------------------
st.set_page_config(page_title="문샷 출석부", page_icon="📅")

# [설정] 구글 시트 링크
sheet_url = "https://docs.google.com/spreadsheets/d/1XqLy6uLi_S22wgBVM0lOsBGmQboQI_DA67MD7ipiUxw/export?format=csv&gid=663277277"

# -------------------------------------------------------------
# 데이터 불러오기 함수
# -------------------------------------------------------------
@st.cache_data(ttl=60)
def load_data():
    try:
        response = requests.get(sheet_url)
        response.raise_for_status()
        decoded_content = response.content.decode('utf-8')
        lines = decoded_content.splitlines()
        data = [line.split(',') for line in lines]
        return data
    except Exception as e:
        return None

# -------------------------------------------------------------
# 메인 앱 로직
# -------------------------------------------------------------
def main():
    st.title("📅 문샷 1기 출석부")

    raw_data = load_data()

    if not raw_data:
        st.error("데이터를 불러오는 데 실패했습니다.")
        return

    # 1. '성함'이 적힌 줄(Header) 찾기
    header_idx = -1
    for i, row in enumerate(raw_data):
        if len(row) > 0 and ("성함" in row[0] or "이름" in row[0]):
            header_idx = i
            break
            
    if header_idx != -1:
        # 2. 날짜가 있는 줄 찾기 (자동 감지 로직)
        # 우선 '성함'과 같은 줄(header_idx)을 확인해보고, 없으면 윗줄(header_idx-1)을 확인
        
        # [후보 1] 성함이 있는 줄 (가장 유력)
        row_candidate_1 = raw_data[header_idx]
        dates_1 = {}
        for idx, val in enumerate(row_candidate_1):
            if idx >= 4 and val.strip(): # E열(4)부터 데이터가 있는지 확인
                dates_1[val.strip()] = idx

        # [후보 2] 바로 윗줄 (혹시 날짜가 위에 병합되어 있는 경우)
        dates_2 = {}
        if header_idx > 0:
            row_candidate_2 = raw_data[header_idx - 1]
            for idx, val in enumerate(row_candidate_2):
                if idx >= 4 and val.strip():
                    dates_2[val.strip()] = idx
        
        # 최종 결정: 데이터가 더 많은 쪽을 선택
        if len(dates_1) >= len(dates_2) and len(dates_1) > 0:
            date_options = dates_1
            # st.caption("DEBUG: 성함과 같은 줄에서 날짜를 찾았습니다.")
        elif len(dates_2) > 0:
            date_options = dates_2
            # st.caption("DEBUG: 윗줄에서 날짜를 찾았습니다.")
        else:
            st.error("🚨 날짜를 찾지 못했습니다. (E열 이후가 비어있습니다)")
            # 디버깅을 위해 현재 읽은 줄을 화면에 보여줌 (문제 해결용)
            st.write("읽은 데이터(성함 줄):", raw_data[header_idx])
            return

        # 3. 날짜 선택 박스
        selected_date = st.selectbox("확인할 날짜를 선택하세요 👇", list(date_options.keys()))
        
        st.divider()

        if selected_date:
            col_idx = date_options[selected_date]
            attendees = []
            absentees = []
            
            # 4. 명단 분류 (성함 줄 다음부터 끝까지)
            for row in raw_data[header_idx+1:]:
                if not row: continue
                name = row[0].strip()
                
                # 종료 조건: 이름이 없거나 '참석 인원' 통계 줄
                if not name: break
                if "참석" in name and "인원" in name: break
                
                # 체크박스 확인
                check_val = "FALSE"
                if len(row) > col_idx:
                    check_val
