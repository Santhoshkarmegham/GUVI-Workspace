from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import unittest
from brickview.database import initialize, connect
from brickview.queries import QUERIES

class DatabaseChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls): initialize()

    def test_queries_and_relationships(self):
        with connect() as con:
            self.assertEqual(con.execute('PRAGMA foreign_key_check').fetchall(), [])
            for name, sql in QUERIES.items():
                with self.subTest(query=name):
                    self.assertTrue(con.execute(sql).description)
            total, distinct = con.execute('SELECT COUNT(*), COUNT(DISTINCT listing_id) FROM listing_details').fetchone()
            self.assertEqual(total, distinct)

    def test_crud_and_foreign_keys(self):
        con = connect()
        try:
            con.execute("INSERT INTO agents(agent_id,name) VALUES ('TEST_AGENT','Test')")
            con.execute("UPDATE agents SET name='Updated' WHERE agent_id='TEST_AGENT'")
            self.assertEqual(con.execute("SELECT name FROM agents WHERE agent_id='TEST_AGENT'").fetchone()[0], 'Updated')
            with self.assertRaises(Exception):
                con.execute("INSERT INTO buyers(buyer_id,sale_id) VALUES (-1,'MISSING_SALE')")
            con.execute("DELETE FROM agents WHERE agent_id='TEST_AGENT'")
        finally:
            con.rollback(); con.close()


class AllTableCrudChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls): initialize()
    def test_all_required_tables(self):
        con = connect()
        try:
            samples = [
                ('agents', 'agent_id', 'TEST_A', {'agent_id':'TEST_A','name':'Test'}, 'name','Changed'),
                ('listings', 'listing_id', 'TEST_L', {'listing_id':'TEST_L','city':'Test','property_type':'House','price':100,'area_sqft':10,'listed_date':'2024-01-01','agent_id':'TEST_A'}, 'price',110),
                ('property_attributes', 'attribute_id', -1, {'attribute_id':-1,'listing_id':'TEST_L'}, 'bedrooms',2),
                ('sales', 'sale_id', 'TEST_S', {'sale_id':'TEST_S','listing_id':'TEST_L','sale_price':105,'sale_date':'2024-02-01','days_on_market':31}, 'sale_price',108),
                ('buyers', 'buyer_id', -1, {'buyer_id':-1,'sale_id':'TEST_S','buyer_type':'Investor'}, 'buyer_type','End User'),
                ('india_housing', 'id', -1, {'id':-1,'city':'Test'}, 'city','Changed'),
            ]
            for table, pk, key, row, field, changed in samples:
                with self.subTest(table=table):
                    con.execute(f'INSERT INTO {table} ({",".join(row)}) VALUES ({",".join("?" for _ in row)})', list(row.values()))
                    con.execute(f'UPDATE {table} SET {field}=? WHERE {pk}=?', (changed,key))
                    self.assertEqual(con.execute(f'SELECT {field} FROM {table} WHERE {pk}=?',(key,)).fetchone()[0],changed)
            for table, pk, key, *_ in reversed(samples):
                con.execute(f'DELETE FROM {table} WHERE {pk}=?',(key,))
                self.assertIsNone(con.execute(f'SELECT * FROM {table} WHERE {pk}=?',(key,)).fetchone())
        finally:
            con.rollback(); con.close()

if __name__ == '__main__': unittest.main()
