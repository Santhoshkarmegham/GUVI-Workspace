"""Initial data explorer for the Real Estate Investment Advisor project."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent / 'src'))
from investment_advisor.config import RAW_DATA_FILE
from investment_advisor.data import load_housing_data
import streamlit as st

st.set_page_config(page_title='Real Estate Investment Advisor', page_icon='🏡', layout='wide')
st.title('Real Estate Investment Advisor')
st.caption('Predicting Property Profitability & Future Value')
st.info('Project setup: explore the supplied dataset below. Model training and MLflow integration are pending.')
source = RAW_DATA_FILE
if not source.exists():
    st.error('Place india_housing_prices.csv in data/raw/.'); st.stop()
@st.cache_data
def load(path):
    return load_housing_data(path)
data = load(source)
cities = st.sidebar.multiselect('City', sorted(data.City.dropna().unique()))
types = st.sidebar.multiselect('Property type', sorted(data.Property_Type.dropna().unique()))
filtered = data
if cities: filtered = filtered[filtered.City.isin(cities)]
if types: filtered = filtered[filtered.Property_Type.isin(types)]
a,b,c = st.columns(3)
a.metric('Property records', f'{len(filtered):,}')
b.metric('Cities', filtered.City.nunique())
c.metric('Average price · INR lakhs', f'{filtered.Price_in_Lakhs.mean():,.2f}' if len(filtered) else 'Unavailable')
st.subheader('Property records')
st.dataframe(filtered, hide_index=True, width='stretch')
st.download_button('Download filtered records', filtered.to_csv(index=False), 'housing_filtered.csv', 'text/csv')
