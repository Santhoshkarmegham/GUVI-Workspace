from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from audible_insights.data import load, identity, duration, genres
from audible_insights.recommend import Recommender
from streamlit.testing.v1 import AppTest

class ProjectTests(unittest.TestCase):
    def test_cleaned_catalogue(self):
        d=load()
        self.assertFalse(d.key.duplicated().any())
        self.assertTrue(d.rating.dropna().between(0,5).all())
        self.assertEqual(identity(' A  Book '),'a book')
        self.assertEqual(duration('2 hours and 3 minutes'),123)
        self.assertEqual(genres(',#1 in Science Fiction,#2 in Audible Audiobooks & Originals (See Top 100)'),['Science Fiction'])

    def test_ranking_excludes_seed_and_respects_filters(self):
        d=load().head(100)
        m=Recommender(d)
        for method in ['Content','Cluster','Hybrid']:
            r=m.recommend(book_id=0,method=method,eligible=range(20))
            self.assertNotIn(0,r.index)
            self.assertTrue(all(i<20 for i in r.index))
        self.assertTrue(m.recommend(text='').empty)

    def test_app_pages(self):
        app=AppTest.from_file(str(Path(__file__).resolve().parents[1]/'app.py')).run(timeout=30)
        self.assertFalse(app.exception)
        for page in ['Recommendations','Catalogue Insights','Data Quality']:
            app.sidebar.radio[0].set_value(page).run(timeout=30)
            self.assertFalse(app.exception,str(app.exception))

if __name__=='__main__': unittest.main()
