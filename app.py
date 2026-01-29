import streamlit as st
import urllib.request
import csv
import io

# -------------------------------------------------------------
# [설정] 페이지 설정
# -------------------------------------------------------------
st.set_page_config(page_title="문샷 출석부", page_icon="📅")

# [설정] 구글 시트 링크
sheet_url = "https://docs.google.com/spreadsheets/d/1XqLy6uLi_S22wgBVM0lOsBGmQboQI_DA67MD7ipiUxw/export?format=csv&gid=663277277"

# -------------------------------------------------------------
# 데이터 불러오기
# -------------------------------------------------------------
@st.cache_data(ttl=60)
def load_data():
    try:
        response = urllib.request.urlopen(sheet_url)
        csv_data = response.read().decode('utf-8')
        f = io.StringIO(csv_data)
        reader = csv.reader(f)
        data = list(reader)
        return data
    except Exception as e:
        return None

# -------------------------------------------------------------
# 메인 화면 로직
# -------------------------------------------------------------
def main():
    st.title("📅 문샷 1기 출석부")

    with st.spinner('데이터를 불러오는 중...'):
        raw_data = load_data()

    if not raw_data:
        st.error("데이터를 불러오지 못했습니다.")
        return

    # 1. 헤더 찾기
    header_idx = -1
    for i, row in enumerate(raw_data):
        if len(row) > 0 and ("성함" in row[0] or "이름" in row[0]):
            header_idx = i
            break
            
    if header_idx != -1:
        # 2. 날짜 찾기
        row_candidate = raw_data[header_idx]
        dates = {}
        for idx, val in enumerate(row_candidate):
            if idx >= 4 and val.strip(): dates[val.strip()] = idx
        
        # 만약 같은 줄에 없으면 윗줄 확인
        if not dates and header_idx > 0:
            row_candidate = raw_data[header_idx - 1]
            for idx, val in enumerate(row_candidate):
                if idx >= 4 and val.strip(): dates[val.strip()] = idx
        
        if not dates:
            st.error("날짜를 찾을 수 없습니다.")
            return

        # 3. 날짜 선택
        # 리스트를 뒤집어서([::-1]) 최신 날짜가 맨 위에 오게 하면 더 편합니다
        date_list = list(dates.keys())
        selected_date = st.selectbox("확인할 날짜를 선택하세요 👇", date_list)
        
        st.divider()

        if selected_date:
            col_idx = dates[selected_date]
            attendees = []
            absentees = []
            
            # 4. 명단 분류
            for row in raw_data[header_idx+1:]:
                if not row: continue
                name = row[0].strip()
                if not name: break
                if "참석" in name and "인원" in name: break
                
                check_val = "FALSE"
                if len(row) > col_idx:
                    check_val = row[col_idx].strip().upper()
                
                if check_val == "TRUE":
                    attendees.append(name)
                else:
                    absentees.append(name)
            
            # 5. 가로형 명단 만들기 (" / " 로 연결)
            attend_str = " / ".join(attendees) if attendees else "없음"
            absent_str = " / ".join(absentees) if absentees else "없음"
            
            # 6. 화면 출력 (보기 좋게 꾸미기)
            st.subheader(f"📌 {selected_date} 현황")
            
            col1, col2 = st.columns(2)
            with col1:
                st.success(f"🔵 참석 ({len(attendees)}명)")
                st.write(attend_str) # 가로로 출력됨
            
            with col2:
                st.error(f"🔴 불참 ({len(absentees)}명)")
                st.write(absent_str) # 가로로 출력됨
            
            st.divider()
            
            # 7. [복사 기능] 클립보드 복사용 텍스트 박스
            st.caption("📋 아래 박스 우측 상단의 '복사 아이콘'을 누르면 전체 내용이 복사됩니다.")
            
            # 카카오톡 등에 붙여넣기 좋은 포맷으로 텍스트 생성
            copy_text = f"""[문샷 1기 출석 결과]
📅 날짜: {selected_date}

🔵 참석자 ({len(attendees)}명)
{attend_str}

🔴 불참자 ({len(absentees)}명)
{absent_str}"""
            
            # 복사 버튼이 달린 코드 블록 생성
            st.code(copy_text, language='text')

    else:
        st.error("'성함' 열을 찾을 수 없습니다.")

if __name__ == "__main__":
    main()
