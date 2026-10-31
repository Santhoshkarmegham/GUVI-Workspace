from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent / 'src'))
import sqlite3
import pandas as pd
import altair as alt
import streamlit as st
from brickview.database import initialize, connect, TABLES
from brickview.queries import QUERIES

st.set_page_config(page_title='BrickView', page_icon='🏠', layout='wide')
initialize()
st.title('🏠 BrickView')
st.caption('A simple real estate analytics dashboard • Python + SQLite + Streamlit')

def read(sql, params=()):
    with connect() as con:
        return pd.read_sql_query(sql, con, params=params)

def show(df):
    sort_column = st.selectbox('Sort table by', list(df.columns), key='table_sort_' + page)
    descending = st.checkbox('Descending', key='table_desc_' + page)
    df = df.sort_values(sort_column, ascending=not descending, na_position='last')
    size = st.selectbox('Rows per page', [25, 50, 100], key='table_size_' + page)
    pages = max(1, (len(df) + size - 1) // size)
    number = st.number_input('Page number', min_value=1, max_value=pages, value=1, key=f'table_page_{page}_{pages}')
    st.caption(f'{len(df):,} rows • page {number} of {pages}')
    st.dataframe(df.iloc[(number-1)*size:number*size], hide_index=True, width='stretch')
    st.download_button('Download CSV', df.to_csv(index=False), 'brickview.csv', 'text/csv')

page = st.sidebar.radio('Page', ['Dashboard', 'Agent dashboard', 'SQL explorer', 'Manage records', 'India housing', 'Data notes'])
if page == 'Dashboard':
    clauses, params = [], []
    for label, col in [('City', 'city'), ('Property type', 'property_type'), ('Agent', 'agent_name')]:
        values = read(f'SELECT DISTINCT {col} FROM listing_details WHERE {col} IS NOT NULL ORDER BY {col}')[col].tolist()
        selected = st.sidebar.multiselect(label, values)
        if selected:
            clauses.append(f'{col} IN ({",".join("?" for _ in selected)})'); params.extend(selected)
    bounds = read('SELECT MIN(price) lo, MAX(price) hi, MIN(listed_date) first, MAX(listed_date) last FROM listings').iloc[0]
    if pd.isna(bounds.lo):
        st.info('Add listings to see the dashboard.'); st.stop()
    low, high = float(bounds.lo), float(bounds.hi)
    price = st.sidebar.slider('Listing price (source currency)', low, max(high, low+1), (low, high))
    dates = st.sidebar.date_input('Listed date range', (pd.to_datetime(bounds['first']).date(), pd.to_datetime(bounds['last']).date()))
    clauses.append('price BETWEEN ? AND ?'); params.extend(price)
    if len(dates) == 2:
        clauses.append('listed_date BETWEEN ? AND ?'); params.extend(map(str, dates))
    status = st.sidebar.selectbox('Status', ['All', 'Unsold', 'Sold'])
    if status != 'All': clauses.append('sale_price IS ' + ('NULL' if status == 'Unsold' else 'NOT NULL'))
    df = read('SELECT * FROM listing_details WHERE ' + ' AND '.join(clauses), params)
    if df.empty: st.info('No listings match these filters.'); st.stop()
    sold = df[df.sale_price.notna()]
    cols = st.columns(4)
    for col, label, value in zip(cols, ['Listings', 'Average listing price', 'Recorded sales', 'Average days to sell'], [f'{len(df):,}', f'{df.price.mean():,.0f}', f'{len(sold):,}', f'{sold.days_on_market.mean():.1f}' if len(sold) else '—']): col.metric(label, value)
    a,b = st.columns(2)
    with a:
        st.subheader('Average price by city'); st.bar_chart(df.groupby('city').price.mean())
    with b:
        st.subheader('Property types')
        counts = df.groupby('property_type').size().reset_index(name='listings')
        st.altair_chart(alt.Chart(counts).mark_arc().encode(theta='listings:Q', color='property_type:N', tooltip=['property_type', 'listings']), width='stretch')
    st.subheader('Listings by month')
    st.line_chart(df.assign(month=df.listed_date.str[:7]).groupby('month').size())
    if len(sold):
        st.subheader('Sales by month'); st.line_chart(sold.assign(month=sold.sale_date.str[:7]).groupby('month').size())
    st.subheader('Listing locations')
    points = df[['latitude','longitude']].dropna()
    points = points[points.latitude.between(-90,90) & points.longitude.between(-180,180)]
    if len(points): st.map(points)
    st.caption('Coordinates are shown as supplied; city and coordinate consistency is not verified.')
    st.subheader('Filtered listings'); show(df)
elif page == 'Agent dashboard':
    agents = read('SELECT agent_id, name FROM agents ORDER BY name')
    if agents.empty:
        st.info('Add an agent to see performance.'); st.stop()
    agent = st.selectbox('Agent', agents.agent_id, format_func=lambda value: agents.set_index('agent_id').loc[value, 'name'])
    stats = read('SELECT COUNT(*) listings, COUNT(sale_price) sales, SUM(sale_price) revenue, AVG(days_on_market) average_days FROM listing_details WHERE agent_id=?', (agent,)).iloc[0]
    for col, label in zip(st.columns(4), stats.index):
        col.metric(label.replace('_',' ').title(), '—' if pd.isna(stats[label]) else f'{stats[label]:,.1f}')
    st.subheader('Recorded sales revenue by agent')
    st.bar_chart(read(QUERIES['Top agents by revenue']).set_index('agent_name')['revenue'])
    st.subheader('Selected agent listings')
    show(read('SELECT listing_id, city, property_type, price, sale_price, days_on_market FROM listing_details WHERE agent_id=?', (agent,)))
elif page == 'SQL explorer':
    st.caption('These queries use the full database. Dashboard filters do not apply.')
    name = st.selectbox('Choose an analysis', list(QUERIES))
    st.code(QUERIES[name], language='sql')
    result = read(QUERIES[name])
    numeric = result.select_dtypes(include='number').columns.tolist()
    if numeric and len(result) > 1:
        value = st.selectbox('Chart value', numeric)
        label = st.selectbox('Chart category', [c for c in result.columns if c != value])
        st.bar_chart(result.set_index(label)[value])
    show(result)
elif page == 'Manage records':
    table = st.selectbox('Table', TABLES)
    with connect() as con: info = con.execute(f'PRAGMA table_info({table})').fetchall()
    columns = [r[1] for r in info]
    pk = next((r[1] for r in info if r[5]), columns[0])
    st.caption('Foreign keys are enforced. Delete dependent buyer, sale, or attribute records before their parent records. Blank optional fields are saved as NULL.')
    search = st.text_input(f'Find by {pk} (blank shows all)')
    show(read(f'SELECT * FROM {table}' + (f' WHERE {pk} = ?' if search else ''), (search,) if search else ()))
    operation = st.radio('Action', ['Add', 'Update', 'Delete'], horizontal=True)
    existing = None
    if operation != 'Add':
        key = st.text_input(f'{pk} of record to {operation.lower()}', key='record_key')
        records = read(f'SELECT * FROM {table} WHERE {pk} = ?', (key,))
        if records.empty: st.info('Enter an existing record ID.'); st.stop()
        existing = records.iloc[0]
    with st.form('record_form'):
        values = {}
        if operation != 'Delete':
            for cid, col, typ, required, default, primary in info:
                value = '' if existing is None or pd.isna(existing[col]) else str(existing[col])
                values[col] = st.text_input(col + (' *' if required or primary or col == pk else ''), value, disabled=(operation == 'Update' and col == pk))
        else: st.write(f'Delete {table} record {key}?')
        submitted = st.form_submit_button(operation + ' record')
    if submitted:
        try:
            converted = {}
            for _, col, typ, required, _, primary in info:
                if operation == 'Delete': break
                raw = values[col].strip()
                if not raw and (required or primary or col == pk): raise ValueError(f'{col} is required')
                converted[col] = None if not raw else int(raw) if 'INT' in typ.upper() else float(raw) if any(t in typ.upper() for t in ['REAL','FLOAT']) else raw
            with connect() as con:
                if operation == 'Add': con.execute(f'INSERT INTO {table} ({",".join(columns)}) VALUES ({",".join("?" for _ in columns)})', [converted[c] for c in columns])
                elif operation == 'Update':
                    edit = [c for c in columns if c != pk]
                    con.execute(f'UPDATE {table} SET ' + ','.join(c+'=?' for c in edit) + f' WHERE {pk}=?', [converted[c] for c in edit]+[key])
                else: con.execute(f'DELETE FROM {table} WHERE {pk}=?', (key,))
            st.success('Saved. Refresh the page to see the updated table.')
        except (ValueError, sqlite3.Error) as error: st.error(str(error))
elif page == 'India housing':
    st.caption('Separate dataset • prices are in INR lakhs (1 lakh = 100,000 INR). No joins to the other listings.')
    city = st.selectbox('City', ['All'] + read('SELECT DISTINCT city FROM india_housing ORDER BY city').city.tolist())
    where, args = ('', ()) if city == 'All' else (' WHERE city=?', (city,))
    st.bar_chart(read('SELECT city, AVG(price_in_lakhs) average_lakhs FROM india_housing'+where+' GROUP BY city', args).set_index('city'))
    show(read('SELECT * FROM india_housing'+where, args))
    st.caption('Table is paginated; download includes all matching rows.')
else:
    st.markdown('''- Sources are copied into `data/raw/`; the database is built once on first run.
- Original field names are standardized to lowercase; Sqft → area_sqft, Date_Listed → listed_date, Date_Sold → sale_date.
- Sales have no source Sale_ID. Their unique Listing_ID becomes sale_id, matching buyers.sale_id.
- Multiple buyer records can refer to one sale. Buyer queries count buyer records; sales queries count sales.
- Agent deals_closed is a source summary and may differ from recorded sales in this dataset.
- Listing currency is unspecified; no currency conversion is assumed.
- These are descriptive comparisons, not evidence that amenities cause higher prices.
- Days on market is preserved from the supplied data and can be fractional.
- Changes made through Manage records persist in the local SQLite file.''')
    show(pd.DataFrame([{'table':t, 'rows':read(f'SELECT COUNT(*) n FROM {t}').iloc[0,0]} for t in TABLES]))
