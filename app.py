import streamlit as st
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="전국 쓰레기봉투 가격 비교", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv('merged_trash_bag_population_data.csv')
    df_grouped = df.groupby(['시도명', '시군구명', '인구수', '쓰레기봉투 용량'])['가격'].mean().reset_index()
    df_pivoted = df_grouped.pivot_table(index=['시도명', '시군구명', '인구수'], columns='쓰레기봉투 용량', values='가격').reset_index()
    df_pivoted.columns.name = None
    df_pivoted = df_pivoted.rename(columns={'10L': 'price_10L', '20L': 'price_20L', '50L': 'price_50L'})
    return df_pivoted

df = load_data()
total_regions = len(df)

# 2. UI 구성 (사이드바 제거 및 상단 배치)
st.title("🗑️ 전국 쓰레기봉투 가격 비교(2026.5 기준)")
st.markdown("지자체를 선택하면 해당 지역의 가격 정보와 유사 인구 규모 지역을 비교해 드립니다.")

# 상단 선택창
selected_city = st.selectbox("조회할 지자체를 선택하세요:", df['시군구명'].sort_values().unique())

st.markdown("---")

# 3. 데이터 연산
target = df[df['시군구명'] == selected_city].iloc[0]
pop = target['인구수']

# 순위 계산
rank_10L = df['price_10L'].rank(ascending=False, method='min')[target.name]
rank_20L = df['price_20L'].rank(ascending=False, method='min')[target.name]
rank_50L = df['price_50L'].rank(ascending=False, method='min')[target.name]

# 유사 규모 지자체 필터링 (인구수 ±5%)
similar_df = df[(df['인구수'] >= pop * 0.95) & (df['인구수'] <= pop * 1.05)]
similar_df = similar_df[similar_df['시군구명'] != selected_city].copy()

# 4. 결과 출력
st.subheader(f"📍 {target['시도명']} {target['시군구명']} 가격 정보")
col1, col2, col3 = st.columns(3)
col1.metric("10L 가격", f"{int(target['price_10L'])}원")
col2.metric("20L 가격", f"{int(target['price_20L'])}원")
col3.metric("50L 가격", f"{int(target['price_50L'])}원")

st.markdown(f"""
### 📊 전국 가격 순위
{target['시도명']} {target['시군구명']}시는 전국 {total_regions}개 지자체 중 
**10L {int(rank_10L)}번째, 20L {int(rank_20L)}번째, 50L {int(rank_50L)}번째**로 비쌉니다. 
(상위 {(rank_10L/total_regions)*100:.1f}%, {(rank_20L/total_regions)*100:.1f}%, {(rank_50L/total_regions)*100:.1f}%)
""")

st.markdown("---")
st.subheader(f"👥 비슷한 인구 규모(±5%) 지자체 비교")
if not similar_df.empty:
    display_df = similar_df[['시도명', '시군구명', '인구수', 'price_10L', 'price_20L', 'price_50L']]
    display_df.columns = ['시도', '시군구', '인구수', '10L가격', '20L가격', '50L가격']
    st.dataframe(display_df.style.format("{:.0f}"), use_container_width=True)
else:
    st.write("해당 규모의 다른 지자체가 데이터에 없습니다.")
