import sqlite3

def drop_tables():
    conn = sqlite3.connect('data/app.db')
    cursor = conn.cursor()
    
    tables_to_drop = ['tenants', 'collection_acl', 'api_keys', 'tenant_usage', 'query_feedbacks']
    
    for table in tables_to_drop:
        try:
            cursor.execute(f"DROP TABLE IF EXISTS {table}")
            print(f"Dropped table {table}")
        except Exception as e:
            print(f"Error dropping table {table}: {e}")
            
    conn.commit()
    conn.close()

if __name__ == "__main__":
    drop_tables()
