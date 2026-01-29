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
# 데이터 불러오기 (설치 필요 없는 기본 도구 사용)
# -------------------------------------------------------------
@st.cache_data(ttl=60)
def load_data():
    try:
        # requests 대신 urllib 사용 (별도 설치 불필요)
        response = urllib.request.urlopen(sheet_url)
        csv_data = response.read().decode('utf-8')
        
        # CSV 모듈로 안전하게 읽기
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

    # 데이터 로딩 표시
    with st.spinner('데이터를 불러오는 중...'):
        raw_data = load_data()

    if not raw_data:
        st.error("데이터를 불러오지 못했습니다. 잠시 후 다시 시도해주세요.")
        return

    # 1. '성함'이 적힌 줄 찾기
    header_idx = -1
    for i, row in enumerate(raw_data):
        if len(row) > 0 and ("성함" in row[0] or "이름" in row[0]):
            header_idx = i
            break
            
    if header_idx != -1:
        # 2. 날짜가 있는 줄 찾기 (같은 줄 vs 윗줄 자동 감지)
        row_candidate_1 = raw_data[header_idx] # 성함 줄
        
        dates_1 = {}
        for idx, val in enumerate(row_candidate_1):
            if idx >= 4 and val.strip(): dates_1[val.strip()] = idx

        dates_2 = {}
        if header_idx > 0:
            row_candidate_2 = raw_data[header_idx - 1] # 윗줄
            for idx, val in enumerate(row_candidate_2):
                if idx >= 4 and val.strip(): dates_2[val.strip()] = idx
        
        # 날짜 데이터가 더 많은 쪽을 선택
        if len(dates_1) >= len(dates_2) and len(dates_1) > 0:
            date_options = dates_1
        elif len(dates_2) > 0:
            date_options = dates_2
        else:
            st.error("날짜를 찾을 수 없습니다.")
            st.write("확인된 데이터:", raw_data[header_idx])
            return

        # 3. 날짜 선택 메뉴
        selected_date = st.selectbox("확인할 날짜를 선택하세요 👇", list(date_options.keys()))
        st.divider()

        if selected_date:
            col_idx = date_options[selected_date]
            attendees = []
            absentees = []
            
            # 4. 명단 분류
            for row in raw_data[header_idx+1:]:
                if not row: continue
                name = row[0].strip()
                
                # 이름이 없거나 통계 줄이면 종료
                if not name: break
                if "참석" in name and "인원" in name: break
                
                # 체크박스 확인
                check_val = "FALSE"
                if len(row) > col_idx:
                    check_val = row[col_idx].strip().upper()
                
                if check_val == "TRUE":
                    attendees.append(name)
                else:
                    absentees.append(name)
            
            # 5. 결과 보여주기
            col1, col2 = st.columns(2)
            with col1:
                st.success(f"🔵 참석 ({len(attendees)}명)")
                if attendees:
                    # 보기 좋게 줄바꿈으로 출력
                    st.text("\n".join(attendees))
                else:
                    st.text("-")
            
            with col2:
                st.error(f"🔴 불참 ({len(absentees)}명)")
                if absentees:
                    st.text("\n".join(absentees))
                else:
                    st.text("-")
            
    else:
        st.error("엑셀 파일 형식을 인식하지 못했습니다. ('성함' 열 없음)")

if __name__ == "__main__":
    main()
