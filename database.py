"""Central database layer for the OmniSearch OSINT ecosystem.

Every module writes to this single SQLite database, keyed by the same
target_id (UUID) so all artifacts stay linked to one root entity.
"""

import sqlite3

DB_PATH = "osint_root.db"


def get_connection():
    """Return a connection to the central database (creates the file)."""
    return sqlite3.connect(DB_PATH)


def init_db():
    """Create all tables if they do not exist yet."""
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Main targets table — the root of the rooting technique
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS targets (
        target_id TEXT PRIMARY KEY,
        input_query TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    # 2. FastPeopleSearch data (name -> address / phone / relatives)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fastpeoplesearch_data (
        target_id TEXT, full_name TEXT, age TEXT, current_phone TEXT,
        current_address TEXT, aliases TEXT, relatives TEXT
    )""")

    # 3. Whoxy domain data (reverse WHOIS)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS whoxy_data (
        target_id TEXT, owned_domain TEXT, registrar TEXT, registrant_email TEXT
    )""")

    # 4. IP location data
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS iplocation_data (
        target_id TEXT, ip_address TEXT, country TEXT, city TEXT,
        isp TEXT, vpn_proxy TEXT
    )""")

    # 5. Social media footprints
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS social_footprints (
        target_id TEXT, platform_name TEXT, profile_url TEXT
    )""")

    # 6. Image metadata / EXIF
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS image_metadata (
        target_id TEXT, image_path TEXT, camera_model TEXT,
        capture_time TEXT, gps_coordinates TEXT
    )""")

    # 7. Data breach audit
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cyber_leaks (
        target_id TEXT, leak_source TEXT, breach_date TEXT, exposed_data TEXT
    )""")

    # 8. Phone intelligence data (numverify)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS phone_intel_data (
        target_id TEXT, phone TEXT, valid TEXT, country TEXT,
        location TEXT, carrier TEXT, line_type TEXT
    )""")

    conn.commit()
    conn.close()
