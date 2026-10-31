PRAGMA foreign_keys = ON;
CREATE TABLE agents (
 agent_id TEXT PRIMARY KEY, name TEXT NOT NULL, phone TEXT, email TEXT,
 commission_rate REAL CHECK(commission_rate BETWEEN 0 AND 100), deals_closed INTEGER,
 rating REAL, experience_years INTEGER, avg_closing_days REAL
);
CREATE TABLE listings (
 listing_id TEXT PRIMARY KEY, city TEXT NOT NULL, property_type TEXT NOT NULL,
 price REAL NOT NULL CHECK(price>=0), area_sqft REAL CHECK(area_sqft>0),
 listed_date TEXT NOT NULL CHECK(date(listed_date) IS NOT NULL), agent_id TEXT REFERENCES agents(agent_id), latitude REAL, longitude REAL
);
CREATE TABLE property_attributes (
 attribute_id INTEGER PRIMARY KEY, listing_id TEXT UNIQUE NOT NULL REFERENCES listings(listing_id),
 bedrooms INTEGER, bathrooms INTEGER, floor_number INTEGER, total_floors INTEGER,
 year_built INTEGER, is_rented INTEGER CHECK(is_rented IN (0,1)), tenant_count INTEGER,
 furnishing_status TEXT, metro_distance_km REAL, parking_available INTEGER CHECK(parking_available IN (0,1)), power_backup INTEGER CHECK(power_backup IN (0,1))
);
CREATE TABLE sales (
 sale_id TEXT PRIMARY KEY, listing_id TEXT UNIQUE NOT NULL REFERENCES listings(listing_id),
 sale_price REAL CHECK(sale_price>=0), sale_date TEXT CHECK(date(sale_date) IS NOT NULL), days_on_market REAL CHECK(days_on_market>=0)
);
CREATE TABLE buyers (
 buyer_id INTEGER PRIMARY KEY, sale_id TEXT NOT NULL REFERENCES sales(sale_id),
 buyer_type TEXT, payment_mode TEXT, loan_taken INTEGER CHECK(loan_taken IN (0,1)), loan_provider TEXT, loan_amount REAL CHECK(loan_amount>=0)
);
CREATE INDEX idx_listings_city ON listings(city);
CREATE INDEX idx_listings_agent ON listings(agent_id);
CREATE INDEX idx_sales_date ON sales(sale_date);
CREATE INDEX idx_buyers_sale ON buyers(sale_id);
CREATE VIEW listing_details AS
 SELECT l.*, a.name AS agent_name, p.bedrooms, p.bathrooms, p.furnishing_status,
 p.metro_distance_km, p.is_rented, p.parking_available, p.power_backup, p.year_built,
 s.sale_price, s.sale_date, s.days_on_market
 FROM listings l LEFT JOIN agents a USING(agent_id)
 LEFT JOIN property_attributes p USING(listing_id) LEFT JOIN sales s USING(listing_id);
