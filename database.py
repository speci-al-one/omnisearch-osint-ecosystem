import sqlite3

def init_db():
    # Connects to the local SQLite database file (creates it if it doesn't exist)
    conn = sqlite3.connect("core_db/osint_root.db")
    cursor = conn.cursor()
    
    print("[*] Initializing Central OSINT Database Tables...")

    # 1. Main Targets Table (The Root of the Rooting Technique)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS targets (
        target_id TEXT PRIMARY KEY,
        input_query TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    
    # 2. FastPeopleSearch Data Module Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fastpeoplesearch_data (
        target_id TEXT NOT NULL,
        full_name TEXT,
        age TEXT,
        current_phone TEXT,
        current_address TEXT,
        aliases TEXT,
        relatives TEXT,
        FOREIGN KEY (target_id) REFERENCES targets(target_id)
    )""")
    
    # 3. Whoxy Domain Data Module Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS whoxy_data (
        target_id TEXT NOT NULL,
        owned_domain TEXT,
        registrar TEXT,
        registrant_email TEXT,
        FOREIGN KEY (target_id) REFERENCES targets(target_id)
    )""")
    
    # 4. IPLocation Network Data Module Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS iplocation_data (
        target_id TEXT NOT NULL,
        ip_address TEXT,
        country TEXT,
        city TEXT,
        isp TEXT,
        vpn_proxy TEXT,
        FOREIGN KEY (target_id) REFERENCES targets(target_id)
    )""")
    
    conn.commit()
    conn.close()
    print("[+] Database Architecture Built Successfully!")

if __name__ == "__main__":
    init_db()

