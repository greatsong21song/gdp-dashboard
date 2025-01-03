import streamlit as st
import pandas as pd
import math
from pathlib import Path

# 브라우저의 탭 바에 나타나는 제목과 파비콘을 설정합니다.
st.set_page_config(
    page_title='GDP dashboard',
    page_icon=':earth_americas:', # 이것은 이모지 단축코드입니다. URL도 사용할 수 있습니다.
)

# -----------------------------------------------------------------------------
# 유용한 함수들을 선언합니다.
@st.cache_data
def get_gdp_data():
    """GDP 데이터를 CSV 파일에서 가져옵니다.
    파일을 매번 읽지 않도록 캐싱을 사용합니다. 만약 파일 대신 HTTP 엔드포인트에서
    읽는다면, TTL 인자를 사용하여 캐시의 최대 수명을 설정하는 것이 좋습니다: 
    @st.cache_data(ttl='1d')
    """
    # 디스크의 CSV 대신, 여기서 HTTP 엔드포인트를 읽을 수도 있습니다.
    DATA_FILENAME = Path(__file__).parent/'data/gdp_data.csv'
    raw_gdp_df = pd.read_csv(DATA_FILENAME)
    MIN_YEAR = 1960
    MAX_YEAR = 2023

    # 위의 데이터는 다음과 같은 열을 가지고 있습니다:
    # - Country Name (국가명)
    # - Country Code (국가 코드)
    # - [관심 없는 데이터]
    # - 1960년 GDP
    # - 1961년 GDP
    # - 1962년 GDP
    # - ...
    # - 2022년 GDP
    #
    # ...하지만 나는 이렇게 바꾸고 싶습니다:
    # - Country Name (국가명)
    # - Country Code (국가 코드)
    # - Year (연도)
    # - GDP
    #
    # 그래서 모든 연도 열을 두 개의 열로 피벗합니다: Year와 GDP
    gdp_df = raw_gdp_df.melt(
        ['Country Code'],
        [str(x) for x in range(MIN_YEAR, MAX_YEAR + 1)],
        'Year',
        'GDP',
    )
    # 연도를 문자열에서 정수로 변환
    gdp_df['Year'] = pd.to_numeric(gdp_df['Year'])
    return gdp_df

gdp_df = get_gdp_data()

# -----------------------------------------------------------------------------
# 실제 페이지를 그립니다
# 페이지 상단에 나타나는 제목을 설정합니다.
'''
# :서울고등학교_세계시민교육: GDP dashboard
[World Bank Open Data](https://data.worldbank.org/) 웹사이트의 GDP 데이터를 둘러보세요. 
보시다시피 현재 데이터는 2023년까지만 있고, 특정 연도의 데이터 포인트가 종종 누락되어 있습니다.
하지만 그래도 이는 훌륭한(그리고 *무료*라는 점을 언급했나요?) 데이터 소스입니다.
'''

# 여백 추가
''
''

min_value = gdp_df['Year'].min()
max_value = gdp_df['Year'].max()
from_year, to_year = st.slider(
    '어느 연도에 관심이 있으신가요?',
    min_value=min_value,
    max_value=max_value,
    value=[min_value, max_value])

countries = gdp_df['Country Code'].unique()
if not len(countries):
    st.warning("최소한 한 국가를 선택하세요")

selected_countries = st.multiselect(
    '어느 국가들을 보고 싶으신가요?',
    countries,
    ['DEU', 'FRA', 'GBR', 'BRA', 'MEX', 'JPN', 'KOR', 'CHN', 'USA'])

''
''
''

# 데이터 필터링
filtered_gdp_df = gdp_df[
    (gdp_df['Country Code'].isin(selected_countries))
    & (gdp_df['Year'] <= to_year)
    & (from_year <= gdp_df['Year'])
]

st.header('시간에 따른 GDP', divider='gray')
''
st.line_chart(
    filtered_gdp_df,
    x='Year',
    y='GDP',
    color='Country Code',
)

''
''

first_year = gdp_df[gdp_df['Year'] == from_year]
last_year = gdp_df[gdp_df['Year'] == to_year]

st.header(f'{to_year}년의 GDP', divider='gray')
''

cols = st.columns(4)
for i, country in enumerate(selected_countries):
    col = cols[i % len(cols)]
    with col:
        first_gdp = first_year[first_year['Country Code'] == country]['GDP'].iat[0] / 1000000000
        last_gdp = last_year[last_year['Country Code'] == country]['GDP'].iat[0] / 1000000000
        if math.isnan(first_gdp):
            growth = '해당없음'
            delta_color = 'off'
        else:
            growth = f'{last_gdp / first_gdp:,.2f}배'
            delta_color = 'normal'
        st.metric(
            label=f'{country} GDP',
            value=f'{last_gdp:,.0f}B',
            delta=growth,
            delta_color=delta_color
        )
