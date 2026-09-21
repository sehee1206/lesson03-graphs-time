import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    page_icon="🎬",
    layout="wide"
)

@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"
    
    # 데이터 불러오기 (컬럼: 날짜, 순위, 영화코드, 영화명, 일관객, 누적관객, 스크린수, 상영횟수)
    df = pd.read_csv(url)
    
    # '날짜' 열을 YYYYMMDD 형태의 string에서 datetime으로 변환
    df['날짜'] = pd.to_datetime(df['날짜'].astype(str), format='%Y%m%d')
    
    # 숫자형 데이터 안전하게 변환
    numeric_cols = ['순위', '일관객', '누적관객', '스크린수', '상영횟수']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
    return df

try:
    df = load_data()
    data_loaded = True
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    data_loaded = False

st.title("🎬 영화 데이터 그래프 도감 1 - 시간")
st.markdown("""
KOBIS 1년치(365일) 일별 박스오피스 10위권 데이터를 기반으로 **시간의 흐름에 따른 영화 트렌드**를 분석하고 시각화하는 도감입니다.
""")

st.divider()

if data_loaded:
    st.header("1. 영화별 일별 관객수 변화 추이")
    st.caption("선택한 영화가 상영 기간 동안 일별로 얼마만큼의 관객을 모았는지 추적합니다.")

    # 영화 목록 추출 (관객수 총합 기준 내림차순 정렬)
    movie_list = (
        df.groupby('영화명')['일관객']
        .sum()
        .sort_values(ascending=False)
        .index
        .tolist()
    )

    # 드롭다운으로 영화 선택
    selected_movie = st.selectbox(
        "📈 관객수 변화를 확인하고 싶은 영화를 선택하세요:",
        options=movie_list,
        index=0
    )

    # 선택된 영화 데이터 필터링
    movie_df = df[df['영화명'] == selected_movie].sort_values('날짜')

    # Plotly 선 그래프 생성
    fig = px.line(
        movie_df,
        x='날짜',
        y='일관객',
        title=f"<b>[{selected_movie}]</b> 일별 관객수 추이",
        markers=True,
        labels={'날짜': '날짜', '일관객': '일관객 수(명)'},
        hover_data={'날짜': '|%Y-%m-%d', '일관객': ':,d'}
    )

    # 그래프 툴팁(마우스 호버) 및 디자인 커스텀
    fig.update_traces(
        hovertemplate="<b>날짜:</b> %{x|%Y-%m-%d}<br><b>일관객:</b> %{y:,}명<extra></extra>",
        line_color='#E50914',
        line_width=2.5,
        marker=dict(size=6)
    )

    fig.update_layout(
        xaxis_title="날짜",
        yaxis_title="일관객 수 (명)",
        hovermode="x unified",
        template="plotly_white",
        margin=dict(l=20, r=20, t=50, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)

    # '이 그래프로 알 수 있는 것' 안내 박스
    st.info(
        "💡 **이 그래프로 알 수 있는 것:** "
        "영화 개봉 초기 흥행 화력(개봉주 피크)과 주말/평일 간의 관객수 격차 패턴, "
        "그리고 장기 흥행(입소문 효과) 여부를 일별 관객수 흐름을 통해 한눈에 파악할 수 있습니다."
    )

    st.divider()

    # --- 두 번째 그래프 구역 ---
    st.header("2. 누적 관객 Top 5 영화의 일별 관객수 비교")
    st.caption("1년 동안 전체 관객수가 가장 많았던 상위 5개 영화의 일별 흥행 추이를 한눈에 비교합니다.")

    # 기간 내 일관객 합계 기준 Top 5 영화 선정
    top5_movies = (
        df.groupby('영화명')['일관객']
        .sum()
        .nlargest(5)
        .index
        .tolist()
    )

    # Top 5 영화 데이터 필터링
    top5_df = df[df['영화명'].isin(top5_movies)].sort_values('날짜')

    # Plotly 다중 선 그래프 생성 (영화별 색상 구분)
    fig_top5 = px.line(
        top5_df,
        x='날짜',
        y='일관객',
        color='영화명',
        title="<b>상위 5개 흥행작 일별 관객수 추이 비교</b>",
        markers=True,
        labels={'날짜': '날짜', '일관객': '일관객 수(명)', '영화명': '영화 제목'}
    )

    # 그래프 디자인 커스텀 및 툴팁 설정
    fig_top5.update_traces(
        hovertemplate="<b>%{fullData.name}</b><br>날짜: %{x|%Y-%m-%d}<br>일관객: %{y:,}명<extra></extra>",
        marker=dict(size=5)
    )

    fig_top5.update_layout(
        xaxis_title="날짜",
        yaxis_title="일관객 수 (명)",
        hovermode="x unified",
        template="plotly_white",
        legend=dict(
            title="영화 제목 (클릭 시 켜기/끄기)",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=20, r=20, t=60, b=20)
    )

    st.plotly_chart(fig_top5, use_container_width=True)

    # '이 그래프로 알 수 있는 것' 안내 박스
    st.info(
        "💡 **이 그래프로 알 수 있는 것:** "
        "연간 최상위 흥행작들의 개봉 시기별 관객 수 격차와 피크(Peak) 시점, "
        "동시기 경쟁 작품과의 흥행 규모 비교를 직관적으로 확인할 수 있습니다. "
        "오른쪽 상단 범례 항목을 클릭하여 특정 영화만 선택해서 볼 수 있습니다."
    )

    st.divider()

    st.header("3. 순위 변동 시뮬레이션 (추가 예정)")
    st.info("💡 **이 그래프로 알 수 있는 것:** 박스오피스 상위권 영화들의 랭킹 뒤바뀜과 차트 장기 집권 여부를 알 수 있습니다.")
