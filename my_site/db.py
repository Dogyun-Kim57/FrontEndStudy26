import sqlite3

DB_NAME = "site.db"

def get_conn():
    # DB 연결을 가져오는 함수
    return sqlite3.connect(DB_NAME)

def init_db():
    # 앱 최초 실행 시 테이블 생성
    conn = get_conn()
    cur = conn.cursor()

    # users 테이블: 회원 정보
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uid TEXT UNIQUE NOT NULL,
        pw_hash TEXT NOT NULL,
        created_at TEXT DEFAULT (datetime('now'))
    )
    """)

    # posts 테이블: 게시글
    cur.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    conn.commit()
    conn.close()