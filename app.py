import streamlit as st
import pandas as pd
import requests
import io

# -------------------------------------------------------------
# [설정] 페이지 제목과 아이콘
# -------------------------------------------------------------
st.set_page_config(page_title="문샷 출석부", page_icon="📅")

# [설정] 구글 시트 링크 (수정할 필요 없음)
# 선생님의 시트 ID와 GID를 포함한 CSV 변환 링크입니다.
sheet_url = "https://docs.google.com/spreadsheets/d/1XqLy6uLi_S22wgBVM0lOsBGmQboQI_DA67MD7ipiUxw/export?format=csv&gid=663277277"

# -------------------------------------------------------------
# 데이터 불러오기 함수 (캐싱 적용으로 속도 향상)
# -------------------------------------------------------------
@st.cache_data(ttl=60) # 60초마다 데이터 새로고침
def load_data():
    try:
        response = requests.get(sheet_url)
        response.raise_for_status()
        decoded_content = response.content.decode('utf-8')
        
        # 데이터 읽기 (줄바꿈 기준으로 나눔)
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
        st.error("데이터를 불러오는 데 실패했습니다. 인터넷 연결을 확인하세요.")
        return

    # 1. '성함'이 적힌 줄(Header) 찾기
    header_idx = -1
    for i, row in enumerate(raw_data):
        if len(row) > 0 and ("성함" in row[0] or "이름" in row[0]):
            header_idx = i
            break
            
    if header_idx != -1 and header_idx > 0:
        # [중요 수정] 날짜는 '성함' 줄보다 한 줄 위에 있습니다! (header_idx - 1)
        date_row = raw_data[header_idx - 1]
        
        # 2. 날짜 옵션 만들기 (날짜 이름과 열 번호 짝짓기)
        date_options = {} 
        for idx, val in enumerate(date_row):
            # E열(인덱스 4)부터, 내용이 비어있지 않은 칸만 날짜로 인식
            if idx >= 4 and val.strip(): 
                date_options[val.strip()] = idx
                
        # 날짜가 잘 찾아졌는지 확인
        if not date_options:
            st.warning("날짜 형식을 찾지 못했습니다. 3행에 날짜가 있는지 확인해주세요.")
            return

        # 3. 날짜 선택 박스 (Selectbox)
        selected_date = st.selectbox("확인할 날짜를 선택하세요 👇", list(date_options.keys()))
        
        # 구분선
        st.divider()

        if selected_date:
            col_idx = date_options[selected_date] # 선택한 날짜의 열 번호
            
            attendees = [] # 참석자 명단
            absentees = [] # 불참자 명단
            
            # 4. 명단 분류 시작 (성함 줄 바로 다음부터 끝까지)
            for row in raw_data[header_idx+1:]:
                # 줄이 비어있으면 건너뜀
                if not row: continue
                
                # 이름 가져오기
                name = row[0].strip()
                
                # [요청하신 기능] 이름이 없거나, '참석 인원' 통계 줄이 나오면 멈춤(break)
                if not name: break
                if "참석" in name and "인원" in name: break
                
                # 체크박스 값 확인 (TRUE / FALSE)
                check_val = "FALSE"
                # 데이터 길이가 짧아도 에러 안 나게 처리
                if len(row) > col_idx:
                    check_val = row[col_idx].strip().upper()
                
                if check_val == "TRUE":
                    attendees.append(name)
                else:
                    absentees.append(name)
            
            # 5. 결과 화면 출력 (깔끔한 디자인)
            col1, col2 = st.columns(2)
            
            with col1:
                st.success(f"🔵 참석 ({len(attendees)}명)")
                if attendees:
                    st.write("\n".join([f"- {name}" for name in attendees]))
                else:
                    st.write("없음")
            
            with col2:
                st.error(f"🔴 불참 ({len(absentees)}명)")
                if absentees:
                    st.write("\n".join([f"- {name}" for name in absentees]))
                else:
                    st.write("없음")
            
    else:
        st.error("엑셀 파일에서 '성함' 또는 '이름' 칸을 찾을 수 없습니다.")

if __name__ == "__main__":
    main()
