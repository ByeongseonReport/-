import streamlit as st
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="전국 쓰레기봉투 가격 비교", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv('merged_trash_bag_population_data.csv')
    # 그룹화 및 피벗 테이블 생성
    df_grouped = df.groupby(['시도명', '시군구명', '인구수', '쓰레기봉투 용량'])['가격'].mean().reset_index()
    df_pivoted = df_grouped.pivot_table(index=['시도명', '시군구명', '인구수'], columns='쓰레기봉투 용량', values='가격').reset_index()
    df_pivoted.columns.name = None
    df_pivoted = df_pivoted.rename(columns={'10L': 'price_10L', '20L': 'price_20L', '50L': 'price_50L'})
    return df_pivoted

df = load_data()
total_regions = len(df)

# 2. UI 구성
st.title("🗑️ 전국 쓰레기봉투 가격 비교")
st.sidebar.header("검색 설정")
selected_city = st.sidebar.selectbox("살고 있는 시·군·구를 선택하세요. (가나다순)", df['시군구명'].sort_values().unique())

# 3. 데이터 연산 및 로직
target = df[df['시군구명'] == selected_city].iloc[0]
pop = target['인구수']

# 순위 계산 (실시간)
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
    
    # 🔥 [이 부분을 새로 추가해 주세요] 숫자 컬럼들을 강제로 숫자형(numeric)으로 변환합니다.
    num_cols = ['인구수', '10L가격', '20L가격', '50L가격']
    display_df[num_cols] = display_df[num_cols].apply(pd.to_numeric, errors='coerce')

    st.dataframe(
        display_df.style.format({
            '인구수': '{:,.0f}',
            '10L가격': '{:,.0f}',
            '20L가격': '{:,.0f}',
            '50L가격': '{:,.0f}'
        }), 
        use_container_width=True
)
else:
    st.write("해당 규모의 다른 지자체가 데이터에 없습니다.")
