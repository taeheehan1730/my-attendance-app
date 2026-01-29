import streamlit as st
import pandas as pd
import io
import requests

# 페이지 설정
st.set_page_config(page_title="문샷 출석부", page_icon="📅")

# 링크 설정
sheet_url = "https://docs.google.com/spreadsheets/d/1XqLy6uLi_S22wgBVM0lOsBGmQboQI_DA67MD7ipiUxw/export?format=csv&gid=663277277"

st.title("📅 문샷 1기 출석부")

@st.cache_data(ttl=60) # 60초마다 데이터 갱신 (빠른 속도 위해)
def load_data():
    try:
        response = requests.get(sheet_url)
        response.raise_for_status()
        decoded_content = response.content.decode('utf-8')
        
        # 튼튼하게 읽기
        lines = decoded_content.splitlines()
        data = [line.split(',') for line in lines]
        return data
    except Exception as e:
        return None

raw_data = load_data()

if raw_data:
    # 1. 제목 줄 찾기
    header_idx = -1
    for i, row in enumerate(raw_data):
        if len(row) > 0 and ("성함" in row[0] or "이름" in row[0]):
            header_idx = i
            break
            
    if header_idx != -1:
        header_row = raw_data[header_idx]
        
        # 2. 날짜 옵션 만들기
        date_options = {} # {날짜이름: 열번호}
        for idx, val in enumerate(header_row):
            if idx >= 4 and val.strip(): # E열(4)부터
                date_options[val.strip()] = idx
                
        # 3. 날짜 선택 박스
        selected_date = st.selectbox("확인할 날짜를 선택하세요", list(date_options.keys()))
        
        if selected_date:
            col_idx = date_options[selected_date]
            attendees = []
            absentees = []
            
            # 4. 명단 분류
            for row in raw_data[header_idx+1:]:
                if not row: continue
                name = row[0].strip()
                
                # 빈칸이면 종료 (요청하신 기능)
                if not name: break
                if "참석" in name and "인원" in name: break
                
                # 체크 확인
                check_val = "FALSE"
                if len(row) > col_idx:
                    check_val = row[col_idx].strip().upper()
                
                if check_val == "TRUE":
                    attendees.append(name)
                else:
                    absentees.append(name)
            
            # 5. 결과 화면 출력
            st.success(f"🔵 참석자: {len(attendees)}명")
            st.write(", ".join(attendees))
            
            st.error(f"🔴 불참자: {len(absentees)}명")
            st.write(", ".join(absentees))
            
    else:
        st.error("데이터에서 '이름' 열을 찾을 수 없습니다.")
else:
    st.error("데이터를 불러오지 못했습니다.")
