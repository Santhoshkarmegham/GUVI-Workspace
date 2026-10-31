import sys
from pathlib import Path
import unittest
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from brand_visibility.pipeline import clean, build, query
from streamlit.testing.v1 import AppTest

class ProjectTests(unittest.TestCase):
    def test_cleaning_preserves_unknowns_and_observed_rank(self):
        rows = pd.DataFrame({'keyword':['phone']*3, 'title':['Apple phone !!!']*3,'platform':['AMAZON','amazon','amazon'],'price':['₹1,000','₹1,000','-999'],'rating':[4,4,9],'reviews':['many','many','4'],'position':[1,1,None],'raw_price':[1250,1250,None]})
        d,a = clean(rows)
        self.assertEqual(len(d),2)
        self.assertEqual(a['duplicate_rows_removed'],1)
        self.assertEqual(d.iloc[0].discount_pct,20)
        self.assertEqual(d.iloc[0].visibility_score,100)
        self.assertTrue(pd.isna(d.iloc[1].price))
        self.assertTrue(pd.isna(d.iloc[0].reviews))
        self.assertEqual(d.iloc[0].brand,'Apple')

    def test_sql_filters(self):
        build()
        self.assertTrue(query({'platform':['Amazon']}).platform.eq('Amazon').all())
        self.assertEqual(len(query(search="' OR 1=1 --")),0)
        self.assertTrue(query(rating=(4,5),include_unrated=False).rating.between(4,5).all())
        self.assertTrue(query(price=(100,1000)).price.between(100,1000).all())

    def test_all_pages_and_empty_filters(self):
        app = AppTest.from_file(str(Path(__file__).resolve().parents[1]/'app.py')).run(timeout=30)
        self.assertEqual(len(app.exception),0)
        for page in ['Brand Insights','Pricing Analysis','Platform Analysis','Visibility & Ranking','Product Explorer','Data Quality']:
            app.sidebar.radio[0].set_value(page).run(timeout=30)
            self.assertEqual(len(app.exception),0,str(app.exception))
        app.sidebar.text_input[0].set_value('no such product xyz').run()
        self.assertEqual(len(app.exception),0)
        self.assertIn('No products match',app.info[0].value)

if __name__ == '__main__': unittest.main()
