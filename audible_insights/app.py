from pathlib import Path
import sys
import json
sys.path.insert(0,str(Path(__file__).resolve().parent/'src'))
import streamlit as st
from audible_insights.data import load
from audible_insights.config import AUDIT
from audible_insights.recommend import Recommender

st.set_page_config(page_title='Audible Insights',page_icon='🎧',layout='wide')
st.title('Audible Insights')
st.caption('Intelligent Book Recommendations · Discover, compare and explore your next listen')
@st.cache_data
def catalogue(): return load()
@st.cache_resource
def model(): return Recommender(catalogue())
books=catalogue()
page=st.sidebar.radio('Explore',['Book Explorer','Recommendations','Catalogue Insights','Data Quality'])
search=st.sidebar.text_input('Search title or author')
genre_options=sorted(set(g for value in books.genres for g in value.split(' | ')))
genre=st.sidebar.selectbox('Genre',['All']+genre_options)
minimum=st.sidebar.slider('Minimum rating',0.,5.,0.,.1)
unknown=st.sidebar.checkbox('Include unknown ratings',True)
filtered=books[(books.rating.ge(minimum)) | (books.rating.isna() & unknown)].copy()
if search: filtered=filtered[filtered.title.str.contains(search,case=False,regex=False)|filtered.author.str.contains(search,case=False,regex=False)]
if genre!='All': filtered=filtered[filtered.genres.map(lambda s:genre in s.split(' | '))]
a,b,c,d=st.columns(4)
a.metric('Books',f'{len(filtered):,}'); b.metric('Authors',f'{filtered.author.nunique():,}')
c.metric('Average rating',f'{filtered.rating.mean():.2f}' if filtered.rating.notna().any() else 'Unavailable')
d.metric('With descriptions',f'{filtered.description.ne("").mean():.0%}' if len(filtered) else '0%')

def value(v):
    import pandas as pd
    return 'Unknown' if pd.isna(v) else f'{v:,.2f}' if isinstance(v,float) else str(v)

def details(row):
    st.subheader(row.title)
    st.write('By **'+row.author+'**')
    x,y,z=st.columns(3)
    x.metric('Rating / 5',value(row.rating)); y.metric('Reviews',value(row.reviews)); z.metric('Listed price · currency unspecified',value(row.price))
    st.write('**Genres:** '+row.genres)
    st.write('**Listening time:** '+(row.listening_time or 'Unknown'))
    st.write('**Description**')
    st.write(row.description or 'No description supplied for this book.')
    with st.expander('Source details and category ranks'):
        st.write('Source: '+row.source)
        st.write(row.ranks_and_genre or 'No ranking information supplied.')

if page=='Data Quality':
    st.subheader('Source merging and cleaning')
    st.json(json.loads(AUDIT.read_text()))
    st.caption('Ratings and prices are catalogue observations without observation dates. No user-history evaluation or publication-year analysis is supported by these files.')
elif filtered.empty:
    st.info('No matching books. Broaden your sidebar filters.')
elif page=='Book Explorer':
    st.subheader('Find a book')
    order=st.selectbox('Sort by',['title','rating','reviews','price'])
    st.dataframe(filtered[['book_id','title','author','rating','reviews','price','listening_time','genres']].sort_values(order,ascending=order=='title',na_position='last'),hide_index=True,width='stretch')
    selected=st.selectbox('View full book details',filtered.index,format_func=lambda i:books.loc[i,'title']+' — '+books.loc[i,'author'])
    details(books.loc[selected])
    st.download_button('Download filtered catalogue',filtered.to_csv(index=False),'books_filtered.csv','text/csv')
elif page=='Recommendations':
    st.caption('Content uses TF-IDF cosine similarity. Cluster restricts results to a content cluster. Hybrid combines 80% similarity, 15% rating and 5% log review popularity. Scores are not confidence probabilities.')
    mode=st.radio('Starting point',['A book I like','My interests'],horizontal=True)
    selected=None; text=''
    if mode=='A book I like': selected=st.selectbox('Favourite book',filtered.index,format_func=lambda i:books.loc[i,'title']+' — '+books.loc[i,'author'])
    else: text=st.text_input('Describe your interests',placeholder='Space exploration, science fiction, mysteries…')
    method=st.selectbox('Recommendation model',['Content','Cluster','Hybrid'])
    count=st.slider('Number of recommendations',1,20,5)
    if st.button('Find recommendations'):
        with st.spinner('Matching books…'): results=model().recommend(book_id=selected,text=text,method=method,limit=count,eligible=filtered.index)
        if results.empty: st.info('No content matches found. Try other interests or broader filters.')
        for _,row in results.iterrows():
            with st.expander(f'{row.title} — {row.author} · score {row.score:.3f}'):
                details(row)
else:
    st.subheader('Most common genres · books can have multiple genres')
    st.bar_chart(filtered.genres.str.split(' | ',regex=False).explode().value_counts().head(15))
    st.subheader('Customer rating distribution')
    st.bar_chart(filtered.rating.dropna().round(1).value_counts().sort_index())
    st.subheader('Authors with the most catalogue entries')
    st.bar_chart(filtered.author.value_counts().head(15))
    st.subheader('Rating and review counts')
    st.scatter_chart(filtered.dropna(subset=['rating','reviews']),x='reviews',y='rating')
    st.caption('Genre counts describe this catalogue, not sales. Publication dates and user interactions are not present.')
