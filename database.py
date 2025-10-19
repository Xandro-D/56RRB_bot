import sqlite3
import time


class ModerationDatabase:
    def __init__(self, db_path="moderation.db"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS warnings (
            user_id INTEGER PRIMARY KEY,
            warnings INTEGER DEFAULT 0
        )
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS strikes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            expires_at INTEGER
        )
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS role_cooldown (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            expires_at INTEGER
        )
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS promote_cooldown (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            expires_at INTEGER
        )
        """)
        self.conn.commit()

    # ---------- Warnings ----------
    def add_warning(self, user_id: int):
        self.cursor.execute("""
        INSERT INTO warnings (user_id, warnings)
        VALUES (?, 1)
        ON CONFLICT(user_id)
        DO UPDATE SET warnings = warnings + 1
        """, (user_id,))
        self.conn.commit()

    def remove_warning(self, user_id: int):
        self.cursor.execute("""
        UPDATE warnings
        SET warnings = CASE WHEN warnings > 0 THEN warnings - 1 ELSE 0 END
        WHERE user_id = ?
        """, (user_id,))
        self.conn.commit()

    def get_warnings(self, user_id: int) -> int:
        self.cursor.execute("SELECT warnings FROM warnings WHERE user_id = ?", (user_id,))
        row = self.cursor.fetchone()
        return row[0] if row else 0

    def reset_warnings(self, user_id: int):
        self.cursor.execute("UPDATE warnings SET warnings = 0 WHERE user_id = ?", (user_id,))
        self.conn.commit()

    # ---------- Strikes ----------

    def remove_expired_strikes(self):
        now = int(time.time())
        self.cursor.execute("SELECT id, user_id FROM strikes WHERE expires_at <= ?", (now,))
        expired = self.cursor.fetchall()
        for strike_id, user_id in expired:
            print(f"Strike {strike_id} for user {user_id} expired and was removed.")
        self.cursor.execute("DELETE FROM strikes WHERE expires_at <= ?", (now,))
        self.conn.commit()

    def add_strike(self, user_id: int, duration_seconds: int):
        expires_at = int(time.time()) + duration_seconds
        self.cursor.execute("INSERT INTO strikes (user_id, expires_at) VALUES (?, ?)", (user_id, expires_at))
        self.conn.commit()

    def remove_strike(self, user_id: int):
        self.remove_expired_strikes()
        self.cursor.execute("""
        SELECT id FROM strikes WHERE user_id = ? ORDER BY expires_at ASC LIMIT 1
        """, (user_id,))
        row = self.cursor.fetchone()
        if row:
            strike_id = row[0]
            self.cursor.execute("DELETE FROM strikes WHERE id = ?", (strike_id,))
            self.conn.commit()
            print(f"Strike {strike_id} for user {user_id} was manually removed.")

    def get_strikes(self, user_id: int) -> int:
        self.remove_expired_strikes()
        self.cursor.execute("SELECT COUNT(*) FROM strikes WHERE user_id = ?", (user_id,))
        row = self.cursor.fetchone()
        return row[0] if row else 0

    def reset_strikes(self, user_id: int):
        self.cursor.execute("SELECT id FROM strikes WHERE user_id = ?", (user_id,))
        strikes = self.cursor.fetchall()
        for strike_id in strikes:
            print(f"Strike {strike_id[0]} for user {user_id} was removed via reset.")
        self.cursor.execute("DELETE FROM strikes WHERE user_id = ?", (user_id,))
        self.conn.commit()


    # Role cooldown ---------------------------------------------
    def remove_expired_role_cooldown(self):
        now = int(time.time())
        self.cursor.execute("SELECT id, user_id FROM role_cooldown WHERE expires_at <= ?", (now,))
        self.cursor.execute("DELETE FROM role_cooldown WHERE expires_at <= ?", (now,))
        self.conn.commit()

    def add_role_cooldown(self, user_id: int, duration_seconds: int):
        expires_at = int(time.time()) + duration_seconds
        self.cursor.execute("INSERT INTO role_cooldown (user_id, expires_at) VALUES (?, ?)", (user_id, expires_at))
        self.conn.commit()

    def get_role_cooldown(self, user_id: int) -> int:
        self.remove_expired_role_cooldown()
        self.cursor.execute("SELECT COUNT(*) FROM role_cooldown WHERE user_id = ?", (user_id,))
        row = self.cursor.fetchone()
        return row[0] if row else 0

    def get_role_cooldown_remaining(self, user_id: int) -> int:
        self.remove_expired_role_cooldown()
        now = int(time.time())
        self.cursor.execute(
            "SELECT expires_at FROM role_cooldown WHERE user_id = ? ORDER BY expires_at DESC LIMIT 1",
            (user_id,)
        )
        row = self.cursor.fetchone()
        if not row:
            return 0
        expires_at = row[0]
        return max(0, expires_at - now)

    def reset_role_cooldown(self, user_id: int):
        self.cursor.execute("SELECT id FROM role_cooldown WHERE user_id = ?", (user_id,))
        role_cooldown = self.cursor.fetchall()
        for strike_id in role_cooldown:
            print(f"Strike {strike_id[0]} for user {user_id} was removed via reset.")
        self.cursor.execute("DELETE FROM role_cooldown WHERE user_id = ?", (user_id,))
        self.conn.commit()
    # Role cooldown end  ---------------------------------------------

    # Start promote cooldown
    def remove_expired_promote_cooldown(self):
        now = int(time.time())
        self.cursor.execute("SELECT id, user_id FROM promote_cooldown WHERE expires_at <= ?",(now,) )
        self.cursor.execute("DELETE FROM promote_cooldown WHERE expires_at <= ?",(now,))
        self.conn.commit()

    def add_promote_cooldown(self, user_id:int, duration_seconds:int):
        self.remove_expired_promote_cooldown()
        expires_at = int(time.time()) + duration_seconds
        self.cursor.execute("INSERT INTO promote_cooldown (user_id, expires_at) VALUES (?, ?)",(user_id,expires_at,))
        self.conn.commit()

    def get_promote_cooldown(self,user_id:int) -> int:
        self.remove_expired_promote_cooldown()
        self.cursor.execute("SELECT COUNT(*) FROM promote_cooldown WHERE user_id= ? ",(user_id,))
        row = self.cursor.fetchone()
        return row[0] if row else 0

    # Returns remaining time in seconds
    def get_promote_cooldown_remaining(self,user_id:int) -> int:
        self.remove_expired_promote_cooldown()
        now = int(time.time())
        self.cursor.execute("SELECT expires_at FROM promote_cooldown WHERE user_id = ? ORDER BY expires_at DESC LIMIT 1",
                            (user_id,))
        row = self.cursor.fetchone()
        if not row:
            return 0
        expires_at = row[0]
        return max(0,expires_at - now)

    def reset_promote_cooldown(self,user_id:int):
        self.remove_expired_promote_cooldown()
        self.cursor.execute("DELETE FROM promote_cooldown WHERE user_id = ?",(user_id,))
        self.conn.commit()


    # ---------- General ----------
    def close(self):
        self.conn.close()