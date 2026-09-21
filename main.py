import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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
            
    # 월과 요일 데이터 추출
    df['월'] = df['날짜'].dt.month.map(lambda x: f"{x}월")
    
    # 요일 한글 이름 및 순서 정의
    weekday_map = {0: '월요일', 1: '화요일', 2: '수요일', 3: '목요일', 4: '금요일', 5: '토요일', 6: '일요일'}
    df['요일'] = df['날짜'].dt.weekday.map(weekday_map)
    
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
    fig1 = px.line(
        movie_df,
        x='날짜',
        y='일관객',
        title=f"<b>[{selected_movie}]</b> 일별 관객수 추이",
        markers=True,
        labels={'날짜': '날짜', '일관객': '일관객 수(명)'},
        hover_data={'날짜': '|%Y-%m-%d', '일관객': ':,d'}
    )

    fig1.update_traces(
        hovertemplate="<b>날짜:</b> %{x|%Y-%m-%d}<br><b>일관객:</b> %{y:,}명<extra></extra>",
        line_color='#E50914',
        line_width=2.5,
        marker=dict(size=6)
    )

    fig1.update_layout(
        xaxis_title="날짜",
        yaxis_title="일관객 수 (명)",
        hovermode="x unified",
        template="plotly_white",
        margin=dict(l=20, r=20, t=50, b=20)
    )

    st.plotly_chart(fig1, use_container_width=True)

    st.info(
        "💡 **이 그래프로 알 수 있는 것:** "
        "영화 개봉 초기 흥행 화력(개봉주 피크)과 주말/평일 간의 관객수 격차 패턴, "
        "그리고 장기 흥행(입소문 효과) 여부를 일별 관객수 흐름을 통해 한눈에 파악할 수 있습니다."
    )

    st.divider()

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

    fig_top5 = px.line(
        top5_df,
        x='날짜',
        y='일관객',
        color='영화명',
        title="<b>상위 5개 흥행작 일별 관객수 추이 비교</b>",
        markers=True,
        labels={'날짜': '날짜', '일관객': '일관객 수(명)', '영화명': '영화 제목'}
    )

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

    st.info(
        "💡 **이 그래프로 알 수 있는 것:** "
        "연간 최상위 흥행작들의 개봉 시기별 관객 수 격차와 피크(Peak) 시점, "
        "동시기 경쟁 작품과의 흥행 규모 비교를 직관적으로 확인할 수 있습니다. "
        "오른쪽 상단 범례 항목을 클릭하여 특정 영화만 선택해서 볼 수 있습니다."
    )

    st.divider()

    st.header("3. 날짜별 10위권 전체 관객수 추이 (총 극장 관객 규모)")
    st.caption("일별 박스오피스 10위권 영화들의 관객수 합계를 집계하여 전체 영화 시장의 활성도를 나타냅니다.")

    # 날짜별 10위권 일관객 합계 데이터 생성
    daily_total = (
        df.groupby('날짜')['일관객']
        .sum()
        .reset_index()
        .sort_values('날짜')
    )

    # 일관객 합계가 가장 컸던 상위 3일 추출
    top3_days = daily_total.nlargest(3, '일관객').sort_values('일관객', ascending=False)

    # Plotly 영역 그래프 (Area Chart) 생성
    fig_area = px.area(
        daily_total,
        x='날짜',
        y='일관객',
        title="<b>날짜별 박스오피스 Top 10 관객수 합계 추이 및 최고 피크일 Top 3</b>",
        labels={'날짜': '날짜', '일관객': '총 일관객 수(명)'}
    )

    fig_area.update_traces(
        fillcolor='rgba(229, 9, 20, 0.25)',
        line_color='#E50914',
        line_width=2,
        hovertemplate="<b>날짜:</b> %{x|%Y-%m-%d}<br><b>10위권 총관객:</b> %{y:,}명<extra></extra>"
    )

    # 관객수 Top 3 피크 날짜에 주석(Annotation) 및 점 포인트 추가
    rank_medals = ["🥇 1위", "🥈 2위", "🥉 3위"]
    for idx, (_, row) in enumerate(top3_days.iterrows()):
        date_str = row['날짜'].strftime('%Y-%m-%d')
        audience_cnt = int(row['일관객'])
        medal = rank_medals[idx]

        fig_area.add_trace(
            go.Scatter(
                x=[row['날짜']],
                y=[audience_cnt],
                mode='markers',
                marker=dict(size=12, color='#B20710', symbol='diamond'),
                name=f"{medal} ({date_str})",
                hovertemplate=f"<b>{medal} 피크일</b><br>날짜: {date_str}<br>총관객: {audience_cnt:,}명<extra></extra>"
            )
        )

        fig_area.add_annotation(
            x=row['날짜'],
            y=audience_cnt,
            text=f"<b>{medal}</b><br>{date_str}<br>{audience_cnt:,}명",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor="#B20710",
            ax=0,
            ay=-45,
            bgcolor="#FFFFFF",
            bordercolor="#B20710",
            borderwidth=1.5,
            borderpad=4,
            opacity=0.95
        )

    fig_area.update_layout(
        xaxis_title="날짜",
        yaxis_title="총 일관객 수 (명)",
        hovermode="x unified",
        template="plotly_white",
        showlegend=False,
        margin=dict(l=20, r=20, t=60, b=20)
    )

    st.plotly_chart(fig_area, use_container_width=True)

    st.info(
        "💡 **이 그래프로 알 수 있는 것:** "
        "설·추석 연휴, 여름 휴가철, 크리스마스 등 영화 시장 전체의 최전성기(Peak) 날짜를 직관적으로 파악할 수 있으며, "
        "일별 총 관객 흐름을 통해 전체 극장가의 성수기와 비수기 주기적 패턴을 밝혀낼 수 있습니다."
    )

    st.divider()

    st.header("4. 월별 총 관객수 분포 (시즌별 관객 집중도)")
    st.caption("12개월 각 월의 박스오피스 10위권 관객 합계를 막대 그래프로 살펴봅니다.")

    # 월별 순서 정렬을 위한 카테고리 설정
    month_order = [f"{m}월" for m in range(1, 13)]
    monthly_sum = (
        df.groupby('월')['일관객']
        .sum()
        .reindex(month_order)
        .reset_index()
    )

    fig_bar = px.bar(
        monthly_sum,
        x='월',
        y='일관객',
        title="<b>월별 총 관객수 (1월 ~ 12월)</b>",
        color='일관객',
        color_continuous_scale='Reds',
        text_auto='.2s',
        labels={'월': '월', '일관객': '총 관객 수(명)'}
    )

    fig_bar.update_traces(
        hovertemplate="<b>%{x}</b><br>총 관객수: %{y:,}명<extra></extra>",
        marker_line_color='rgb(8,48,107)',
        marker_line_width=1.5,
        opacity=0.85
    )

    fig_bar.update_layout(
        xaxis_title="월",
        yaxis_title="총 관객 수 (명)",
        template="plotly_white",
        coloraxis_showscale=False,
        margin=dict(l=20, r=20, t=50, b=20)
    )

    st.plotly_chart(fig_bar, use_container_width=True)

    st.info(
        "💡 **이 그래프로 알 수 있는 것:** "
        "연중 어느 달에 영화관을 찾는 총 관객이 가장 많은지(성수기 월)와 가장 적은지(비수기 월)의 월별 시즌성을 명확히 비교할 수 있습니다."
    )

    st.divider()

    st.header("5. 월 × 요일별 일관객 합계 히트맵")
    st.caption("월(1월~12월)과 요일(월~일)의 조합에 따른 일관객 합계를 색상의 짙기로 표현한 패턴 분석 그래프입니다.")

    # 요일 순서 지정 (월요일 ~ 일요일)
    weekday_order = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
    
    # 피벗 테이블 생성 (행: 월, 열: 요일)
    heatmap_pivot = (
        df.groupby(['월', '요일'])['일관객']
        .sum()
        .unstack(level='요일')
    )

    # 월 및 요일 순서에 맞춰 재정렬
    heatmap_pivot = heatmap_pivot.reindex(index=month_order, columns=weekday_order)

    # Plotly Heatmap 생성
    fig_heatmap = go.Figure(
        data=go.Heatmap(
            z=heatmap_pivot.values,
            x=weekday_order,
            y=month_order,
            colorscale='YlOrRd',
            reversescale=False,
            colorbar=dict(title="관객수 합계(명)"),
            hovertemplate="<b>%{y} %{x}</b><br>총 관객수: %{z:,}명<extra></extra>"
        )
    )

    fig_heatmap.update_layout(
        title="<b>월 × 요일별 관객수 분포 히트맵 (짙은 색일수록 관객이 많음)</b>",
        xaxis_title="요일",
        yaxis_title="월",
        template="plotly_white",
        xaxis=dict(tickangle=0),
        yaxis=dict(autorange="reversed"), # 1월이 위로 오도록 설정
        margin=dict(l=20, r=20, t=50, b=20)
    )

    st.plotly_chart(fig_heatmap, use_container_width=True)

    st.info(
        "💡 **이 그래프로 알 수 있는 것:** "
        "주말(토/일) 및 특정 월(휴가철/명절 연휴 등)에 관객이 얼마나 집중되는지 '월×요일' 2차원 교차 패턴으로 시각화하여, "
        "연중 어느 달의 무슨 요일에 극장가가 가장 붐비는지를 한눈에 쉽게 찾을 수 있습니다."
    )
