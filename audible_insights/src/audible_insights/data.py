"""Normalize title/author identity and merge sources one-to-one."""
import json
import re
import unicodedata
import pandas as pd
from .config import RAW, CLEAN, AUDIT

def identity(value):
    return ' '.join(unicodedata.normalize('NFKC',str(value)).casefold().split())

def genres(value):
    parts = re.split(r',?\s*#\s*[\d,]+\s+in\s+',str(value))
    return sorted(set(re.sub(r'\s*\([^)]*\)', '', p).strip(' ,') for p in parts[1:] if not p.startswith('Audible Audiobooks & Originals')))

def prepare():
    frames=[]; counts={}
    for name,source in [('Audible_Catlog.csv','Basic'),('Audible_Catlog_Advanced_Features.csv','Advanced')]:
        d=pd.read_csv(RAW/name)
        counts[source]={'input_rows':len(d)}
        d=d.rename(columns={'Book Name':'title','Author':'author','Rating':'rating','Number of Reviews':'reviews','Price':'price','Description':'description','Listening Time':'listening_time','Ranks and Genre':'ranks_and_genre'})
        for c in ['title','author']:
            d[c]=d[c].fillna('').astype(str).str.replace(r'\s+',' ',regex=True).str.strip()
        d=d[d.title.ne('') & d.author.ne('')].copy()
        d['key']=d.title.map(identity)+'|'+d.author.map(identity)
        for c in ['rating','reviews','price']:
            d[c]=pd.to_numeric(d[c],errors='coerce').astype(float)
        d.loc[~d.rating.between(0,5),'rating']=float('nan')
        d.loc[d.reviews.lt(0) | d.reviews.mod(1).ne(0),'reviews']=float('nan')
        d.loc[d.price.le(0),'price']=float('nan')
        # Retain the first source occurrence; fill its missing cells from later duplicates.
        unique=d.groupby('key',sort=False).first()
        counts[source]['duplicate_keys_collapsed']=len(d)-len(unique)
        frames.append(unique)
    basic,advanced=frames
    joined=advanced.combine_first(basic)
    joined['source']=['Both' if k in basic.index and k in advanced.index else 'Advanced' if k in advanced.index else 'Basic' for k in joined.index]
    for c in ['description','listening_time','ranks_and_genre']:
        if c not in joined: joined[c]=''
        joined[c]=joined[c].fillna('').astype(str)
    joined['genres']=joined.ranks_and_genre.map(lambda v:' | '.join(genres(v)))
    joined['genres']=joined.genres.replace('','Unknown')
    joined=joined.reset_index().sort_values(['title','author']).reset_index(drop=True)
    joined['book_id']=range(len(joined))
    joined['duration_minutes']=joined.listening_time.map(duration)
    CLEAN.parent.mkdir(parents=True,exist_ok=True); AUDIT.parent.mkdir(parents=True,exist_ok=True)
    joined.to_csv(CLEAN,index=False)
    report={'sources':counts,'merged_books':len(joined),'overlapping_books':int(joined.source.eq('Both').sum()),'missing_values':joined.isna().sum().to_dict(),'rules':['Identity is normalized title plus author; editions may be combined.','Advanced fields take precedence; basic fills missing values. Source dates are unknown.','Invalid ratings and non-positive prices remain unknown.','Currency is unspecified in supplied files.','No user interactions or publication dates are provided.']}
    AUDIT.write_text(json.dumps(report,indent=2)+'\n')
    return joined

def duration(value):
    hours=re.search(r'(\d+)\s*hour',value,re.I); minutes=re.search(r'(\d+)\s*min',value,re.I)
    return int(hours[1])*60+int(minutes[1]) if hours and minutes else int(hours[1])*60 if hours else int(minutes[1]) if minutes else float('nan')

def load():
    if not CLEAN.exists(): return prepare()
    return pd.read_csv(CLEAN).fillna({'description':'','listening_time':'','ranks_and_genre':'','genres':'Unknown'})
