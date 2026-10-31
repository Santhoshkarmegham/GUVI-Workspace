"""Each query is visible and runnable in the SQL explorer."""
QUERIES = {
'Average listing price by city': 'SELECT city, COUNT(*) listings, AVG(price) average_price FROM listings GROUP BY city ORDER BY average_price DESC',
'Price per square foot by type': 'SELECT property_type, AVG(price / NULLIF(area_sqft,0)) price_per_sqft FROM listings GROUP BY property_type',
'Furnishing and price': 'SELECT furnishing_status, COUNT(*) listings, AVG(price) average_price FROM listing_details GROUP BY furnishing_status',
'Metro distance and price': "SELECT CASE WHEN metro_distance_km<=1 THEN 'Within 1 km' WHEN metro_distance_km<=5 THEN '1–5 km' ELSE 'Over 5 km' END distance, COUNT(*) listings, AVG(price) average_price FROM listing_details WHERE metro_distance_km IS NOT NULL GROUP BY distance",
'Rented versus non-rented': 'SELECT is_rented, COUNT(*) listings, AVG(price) average_price FROM listing_details GROUP BY is_rented',
'Bedrooms, bathrooms and price': 'SELECT bedrooms, bathrooms, COUNT(*) listings, AVG(price) average_price FROM listing_details GROUP BY bedrooms, bathrooms',
'Parking, backup and sale price': 'SELECT parking_available, power_backup, COUNT(sale_price) sales, AVG(sale_price) average_sale_price FROM listing_details WHERE sale_price IS NOT NULL GROUP BY parking_available, power_backup',
'Year built and price': 'SELECT year_built, AVG(price) average_price FROM listing_details GROUP BY year_built ORDER BY year_built',
'Highest priced cities': 'SELECT city, AVG(price) average_price FROM listings GROUP BY city ORDER BY average_price DESC LIMIT 10',
'Price buckets': "SELECT CASE WHEN price<500000 THEN 'Under 500k' WHEN price<1000000 THEN '500k–1m' WHEN price<2000000 THEN '1m–2m' ELSE '2m+' END bucket, COUNT(*) listings FROM listings GROUP BY bucket",
'Days on market by city': 'SELECT city, COUNT(*) sales, AVG(days_on_market) average_days FROM listing_details WHERE sale_price IS NOT NULL GROUP BY city',
'Fastest selling property types': 'SELECT property_type, AVG(days_on_market) average_days FROM listing_details WHERE sale_price IS NOT NULL GROUP BY property_type ORDER BY average_days',
'Sold above listing price': 'SELECT 100.0*SUM(sale_price>price)/NULLIF(COUNT(*),0) percent_above_list FROM listing_details WHERE sale_price IS NOT NULL',
'Sale-to-list ratio by city': 'SELECT city, AVG(sale_price/NULLIF(price,0)) sale_to_list_ratio FROM listing_details WHERE sale_price IS NOT NULL GROUP BY city',
'Sales taking over 90 days': 'SELECT listing_id, city, days_on_market FROM listing_details WHERE days_on_market>90 ORDER BY days_on_market DESC',
'Metro distance and selling time': 'SELECT ROUND(metro_distance_km) metro_km, COUNT(*) sales, AVG(days_on_market) average_days FROM listing_details WHERE sale_price IS NOT NULL GROUP BY metro_km ORDER BY metro_km',
'Monthly sales trend': "SELECT substr(sale_date,1,7) month, COUNT(*) sales, SUM(sale_price) revenue FROM sales GROUP BY month ORDER BY month",
'Unsold listings': 'SELECT listing_id, city, property_type, price FROM listing_details WHERE sale_price IS NULL',
'Agents by closed sales': 'SELECT a.agent_id, a.name, COUNT(s.sale_id) recorded_sales FROM agents a LEFT JOIN listings l USING(agent_id) LEFT JOIN sales s USING(listing_id) GROUP BY a.agent_id ORDER BY recorded_sales DESC',
'Top agents by revenue': 'SELECT agent_id, agent_name, SUM(sale_price) revenue FROM listing_details WHERE sale_price IS NOT NULL GROUP BY agent_id ORDER BY revenue DESC',
'Fastest closing agents': 'SELECT agent_id, agent_name, COUNT(*) sales, AVG(days_on_market) average_days FROM listing_details WHERE sale_price IS NOT NULL GROUP BY agent_id ORDER BY average_days',
'Experience and deals': 'SELECT agent_id, name, experience_years, deals_closed FROM agents ORDER BY experience_years',
'Ratings and closing speed': 'SELECT a.rating, COUNT(s.sale_id) recorded_sales, AVG(s.days_on_market) average_days FROM agents a JOIN listings l USING(agent_id) JOIN sales s USING(listing_id) GROUP BY a.rating ORDER BY a.rating',
'Average commission by agent': 'SELECT a.agent_id, a.name, COUNT(s.sale_id) sales, AVG(s.sale_price*a.commission_rate/100.0) average_commission FROM agents a LEFT JOIN listings l USING(agent_id) LEFT JOIN sales s USING(listing_id) GROUP BY a.agent_id',
'Agents with active listings': 'SELECT agent_id, agent_name, COUNT(*) active_listings FROM listing_details WHERE sale_price IS NULL GROUP BY agent_id ORDER BY active_listings DESC',
'Buyer type distribution': 'SELECT buyer_type, COUNT(*) buyers, 100.0*COUNT(*)/(SELECT COUNT(*) FROM buyers) percentage FROM buyers GROUP BY buyer_type',
'Loan uptake by city': 'SELECT l.city, COUNT(*) buyer_records, 100.0*AVG(b.loan_taken) loan_uptake_percent FROM buyers b JOIN sales s USING(sale_id) JOIN listings l USING(listing_id) GROUP BY l.city ORDER BY loan_uptake_percent DESC',
'Loan amount by buyer type': 'SELECT buyer_type, AVG(loan_amount) average_loan_amount FROM buyers GROUP BY buyer_type',
'Payment modes': 'SELECT payment_mode, COUNT(*) buyers FROM buyers GROUP BY payment_mode ORDER BY buyers DESC',
'Loan status and closing time': 'SELECT b.loan_taken, COUNT(*) buyer_records, AVG(s.days_on_market) average_days FROM buyers b JOIN sales s USING(sale_id) GROUP BY b.loan_taken',
}

QUERIES['Experience and deals correlation'] = '''
SELECT (AVG(1.0*experience_years*deals_closed)-AVG(experience_years)*AVG(deals_closed)) /
 NULLIF(SQRT((AVG(1.0*experience_years*experience_years)-AVG(experience_years)*AVG(experience_years))*
 (AVG(1.0*deals_closed*deals_closed)-AVG(deals_closed)*AVG(deals_closed))),0) AS pearson_correlation
FROM agents WHERE experience_years IS NOT NULL AND deals_closed IS NOT NULL
'''
