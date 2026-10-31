from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent / 'src'))
import altair as alt
import pandas as pd
import streamlit as st
from brand_visibility.pipeline import ROOT, DB, build, query

st.set_page_config(page_title='BrandScope | Visibility Intelligence', page_icon='◈', layout='wide')
st.markdown('''<style>
.stApp {background:#f6f8fc} [data-testid="stSidebar"] {background:#101d35}
[data-testid="stSidebar"] * {color:#e7edf8}
[data-testid="stMetric"] {background:white;border:1px solid #e3e9f3;border-radius:12px;padding:18px}
h1,h2,h3 {color:#152643} .block-container {padding-top:2.3rem}
</style>''', unsafe_allow_html=True)
if not DB.exists(): build()
all_data = query()
st.sidebar.title('◈ BrandScope')
st.sidebar.caption('COMMERCE INTELLIGENCE')
page = st.sidebar.radio('Workspace', ['Overview','Brand Insights','Pricing Analysis','Platform Analysis','Visibility & Ranking','Product Explorer','Data Quality'])
st.sidebar.divider()
filters = {col: st.sidebar.multiselect(label, sorted(all_data[col].dropna().unique())) for col,label in [('keyword','Search keyword'),('brand','Brand'),('platform','Platform'),('price_range','Price tier'),('source','Data source')]}
rating = st.sidebar.slider('Customer rating', 0., 5., (0.,5.), .1)
unrated = st.sidebar.checkbox('Include unrated products', True)
restrict = st.sidebar.checkbox('Limit price (excludes unknown prices)')
price = st.sidebar.slider('Price · INR', 0, max(1, int(all_data.price.max() or 1)), (0, max(1,int(all_data.price.max() or 1)))) if restrict else None
search = st.sidebar.text_input('Search product title')
if st.sidebar.button('Rebuild database from source files'):
    build(); st.rerun()
d = query(filters, search, rating, unrated, price)
st.caption('BRANDSCOPE  /  MARKET INTELLIGENCE')
st.title(page)
st.caption('Understand the shelf. Find your next opportunity.  •  Currency: INR  •  All metrics follow your filters')
if d.empty:
    st.info('No products match these filters. Clear a filter to broaden your view.'); st.stop()

def fmt(value, prefix='', suffix='', decimals=1):
    return 'Unavailable' if pd.isna(value) else f'{prefix}{value:,.{decimals}f}{suffix}'

def metrics(items):
    for col,(name,value) in zip(st.columns(len(items)),items): col.metric(name,value)

def chart(data, x, y, title, kind='bar', color=None):
    st.subheader(title)
    if data.empty or data[x].notna().sum() == 0 or data[y].notna().sum() == 0:
        st.info('This metric needs fields absent from the selected records.'); return
    base = alt.Chart(data)
    base = base.mark_circle(size=65, opacity=.55) if kind == 'scatter' else base.mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4, color='#5b63ed')
    types = lambda c: 'quantitative' if pd.api.types.is_numeric_dtype(data[c]) else 'nominal'
    enc = dict(x=alt.X(x,type=types(x)), y=alt.Y(y,type=types(y)), tooltip=list(data.columns))
    if color: enc['color'] = alt.Color(color,type='nominal')
    st.altair_chart(base.encode(**enc).properties(height=300), width='stretch')

def histogram(col,title):
    st.subheader(title)
    if not d[col].notna().any(): st.info('No observed values available.'); return
    st.altair_chart(alt.Chart(d.dropna(subset=[col])).mark_bar(color='#5b63ed').encode(x=alt.X(col+':Q',bin=alt.Bin(maxbins=30)),y='count()',tooltip=['count()']).properties(height=300),width='stretch')

def grouped(col):
    return d.groupby(col,as_index=False).agg(products=('title','size'),average_price=('price','mean'),average_rating=('rating','mean'),average_position=('position','mean'),visibility=('visibility_score','mean'),discount=('discount_pct','mean'))

metrics([('Products',f'{len(d):,}'),('Average price',fmt(d.price.mean(),'₹')),('Customer rating',fmt(d.rating.mean(),suffix=' / 5')),('Total known reviews',fmt(d.reviews.sum(min_count=1),decimals=0))])
st.caption(f'Price coverage {d.price.notna().mean():.0%} · Rating coverage {d.rating.notna().mean():.0%} · Ranking coverage {d.position.notna().mean():.0%} · Reviews coverage {d.reviews.notna().mean():.0%}')
st.divider()
if page == 'Overview':
    a,b = st.columns([1.4,1])
    with a: histogram('price','The price landscape')
    with b:
        chart(grouped('platform'),'platform','products','Platform presence')
    chart(grouped('keyword'),'keyword','products','Products by search keyword')
    histogram('reviews','Customer engagement distribution')
    st.subheader('Signals worth exploring')
    leader = grouped('brand').sort_values('products',ascending=False).iloc[0]
    st.info(f"{leader['brand']} accounts for {leader['products']/len(d):.1%} of selected listings. Compare its rating and pricing within the same keyword before adjusting positioning.")
    st.caption('Listing share describes this dataset, not market share or sales. The supplied model-style titles may represent synthetic training data.')
elif page == 'Brand Insights':
    g = grouped('brand')
    metrics([('Brands',str(len(g))),('Most listed brand',g.loc[g.products.idxmax(),'brand']),('Average visibility',fmt(d.visibility_score.mean()))])
    for y,t in [('products','Share of the shelf'),('average_rating','Customer rating by brand'),('visibility','Search visibility by brand')]: chart(g,'brand',y,t)
    chart(d[d.position.le(10)].groupby('brand').size().reset_index(name='products'),'brand','products','Brands in the top 10 search positions')
elif page == 'Pricing Analysis':
    known = d.discount_pct.dropna()
    metrics([('Highest price',fmt(d.price.max(),'₹')),('Lowest price',fmt(d.price.min(),'₹')),('Discounted · known prices',fmt(known.gt(0).mean()*100,suffix='%') if len(known) else 'Unavailable')])
    histogram('price','Price distribution')
    chart(d[['price','position','brand']],'price','position','Price vs search position','scatter','brand')
    chart(d[['price','rating','brand']],'price','rating','Price vs customer rating','scatter','brand')
    chart(grouped('price_range'),'price_range','products','Price tier mix')
    for col in ['brand','platform']: chart(grouped(col),col,'discount',f'Observed discount by {col}')
elif page == 'Platform Analysis':
    g = grouped('platform')
    metrics([('Platforms',str(len(g))),('Best rated',g.loc[g.average_rating.idxmax(),'platform'] if g.average_rating.notna().any() else 'Unavailable'),('Lowest average price',g.loc[g.average_price.idxmin(),'platform'] if g.average_price.notna().any() else 'Unavailable')])
    for y,t in [('products','Listings per platform'),('average_price','Average price by platform'),('average_rating','Customer ratings by platform'),('average_position','Average search position by platform')]: chart(g,'platform',y,t)
    chart(d.groupby(['platform','brand']).size().reset_index(name='products'),'platform','products','Brand mix per platform',color='brand')
elif page == 'Visibility & Ranking':
    ranked = d[d.position.notna()]
    metrics([('Ranked listings',str(len(ranked))),('Average visibility',fmt(ranked.visibility_score.mean())),('Top 10 · ranked listings',fmt(ranked.position.le(10).mean()*100,suffix='%') if len(ranked) else 'Unavailable')])
    st.info('Search position comes only from API results. Visibility = 100 / position. Customer rating remains a separate metric. Lower position means better placement.')
    histogram('position','Search position distribution')
    for x,t in [('rating','Customer rating vs search position'),('reviews','Reviews vs search position')]: chart(d[[x,'position','brand']],x,'position',t,'scatter','brand')
    chart(grouped('brand'),'brand','visibility','Average visibility by brand')
elif page == 'Product Explorer':
    st.subheader('Explore every listing')
    sort = st.selectbox('Sort by',['rating','price','reviews','position','visibility_score','title'])
    ascending = st.checkbox('Ascending',sort == 'position')
    st.dataframe(d.sort_values(sort,ascending=ascending,na_position='last'), hide_index=True, width='stretch')
    st.download_button('Download filtered CSV',d.to_csv(index=False),'brand_products_filtered.csv','text/csv')
    selected = st.selectbox('Inspect a listing',d.index,format_func=lambda i: f'{d.loc[i,"title"]} · {d.loc[i,"platform"]}')
    st.json(d.loc[selected].where(d.loc[selected].notna(),None).to_dict())
    chart(d[['price','rating','brand']],'price','rating','Price and customer satisfaction','scatter','brand')
else:
    audit = json.loads((ROOT/'reports/cleaning_audit.json').read_text())
    st.subheader('Cleaning audit · full dataset')
    st.json(audit)
    st.markdown('''Missing or invalid prices, ratings and reviews remain unknown and are excluded only from that metric’s mean. Listings are retained. Delivery gaps become **Unknown**. Platform case and title punctuation are standardized. Duplicates use keyword, title, platform, price, source, snapshot and position. Price outliers are flagged using keyword-level 1.5×IQR and retained. Brand extraction uses a documented dictionary; unmatched titles become Unknown.

The provided CSV has no original prices, observation dates or search positions. Discounts and visibility remain unavailable unless observed through API records. API snapshots are separate listing observations; filter by source when comparing coverage. Cross-keyword pricing mixes product categories and should be interpreted carefully.''')
    st.download_button('Download cleaned dataset',(ROOT/'data/processed/clean_products.csv').read_bytes(),'clean_products.csv','text/csv')
