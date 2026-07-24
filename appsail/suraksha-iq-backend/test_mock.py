from app.core.mock_data import get_mock_app

app = get_mock_app()
zcql = app.zcql()

r1 = zcql.execute_query('SELECT * FROM Crime LIMIT 5')
print('Simple select:', len(r1))

r2 = zcql.execute_query("SELECT * FROM Crime WHERE status = 'open' LIMIT 3")
print('Filtered by status:', len(r2))

r3 = zcql.execute_query("SELECT * FROM Crime WHERE status = 'open' AND crime_type = 'theft' LIMIT 3")
print('Filtered by status AND type:', len(r3))

r4 = zcql.execute_query('SELECT COUNT(ROWID) FROM District')
print('Count districts:', r4[0]['District']['COUNT(ROWID)'])

r5 = zcql.execute_query("SELECT * FROM Crime WHERE title LIKE '%theft%' LIMIT 3")
print('LIKE search:', len(r5))

r6 = zcql.execute_query('SELECT * FROM Crime ORDER BY CREATEDTIME DESC LIMIT 3')
dates = [x['Crime']['CREATEDTIME'][:10] for x in r6 if 'Crime' in x]
print('Ordered:', dates)

r7 = zcql.execute_query("SELECT * FROM Crime WHERE district_id = 'bangalore-urban' LIMIT 3")
print('By district:', len(r7))

# Test find_all_with_filters style query
r8 = zcql.execute_query("SELECT * FROM Crime WHERE 1=1 AND status = 'open' AND crime_type = 'cybercrime' LIMIT 10, 20")
print('find_all_with_filters style:', len(r8))

# Test find_by_district style
r9 = zcql.execute_query("SELECT * FROM Crime WHERE district_id = 'bangalore-urban' ORDER BY CREATEDTIME DESC LIMIT 1, 5")
print('find_by_district style:', len(r9))

# Test FIR count by status
r10 = zcql.execute_query("SELECT COUNT(ROWID) FROM FIR WHERE status = 'open'")
print('Count open FIRs:', r10[0]['FIR']['COUNT(ROWID)'])
