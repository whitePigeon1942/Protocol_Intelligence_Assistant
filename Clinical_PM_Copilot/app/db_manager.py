import sqlite3
import pandas as pd
import os
from datetime import datetime


class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """创建表结构（如果不存在）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sites (
                site_id TEXT PRIMARY KEY,
                site_name TEXT,
                province TEXT,
                planned_enrollment INTEGER
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS enrollment_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                site_id TEXT,
                week_start DATE,
                total_screened INTEGER,
                total_enrolled INTEGER,
                new_this_week INTEGER,
                completion_rate REAL,
                risk_level TEXT,
                FOREIGN KEY (site_id) REFERENCES sites(site_id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ae_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT,
                site_id TEXT,
                subject_id TEXT,
                ae_name TEXT,
                severity TEXT,
                event_type TEXT,
                onset_date DATE,
                resolution_date DATE,
                outcome TEXT,
                status TEXT,
                report_week DATE,
                FOREIGN KEY (site_id) REFERENCES sites(site_id)
            )
        ''')

        conn.commit()
        conn.close()
        print("✅ Database initialized successfully.")

    def save_enrollment_snapshot(self, df, week_start):
        """保存当周入组快照"""
        conn = sqlite3.connect(self.db_path)

        for _, row in df.iterrows():
            conn.execute('''
                INSERT OR REPLACE INTO sites (site_id, site_name, province, planned_enrollment)
                VALUES (?, ?, ?, ?)
            ''', (row['中心编号'], row['中心名称'], row.get('省份', ''), row['计划入组']))

        for _, row in df.iterrows():
            conn.execute('''
                INSERT INTO enrollment_history 
                (site_id, week_start, total_screened, total_enrolled, new_this_week, completion_rate, risk_level)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['中心编号'],
                week_start,
                row['累计筛选'],
                row['累计入组'],
                row['本周新增'],
                row['完成率_实际'],
                row['风险等级']
            ))

        conn.commit()
        conn.close()
        print(f"✅ Enrollment snapshot saved for week: {week_start}")

    def save_ae_snapshot(self, df, week_start):
        """保存当周AE快照"""
        conn = sqlite3.connect(self.db_path)
        for _, row in df.iterrows():
            onset = row['发生日期']
            resolution = row['解决日期'] if pd.notna(row['解决日期']) else None

            if pd.notna(onset):
                onset = onset.strftime('%Y-%m-%d')
            else:
                onset = None

            if resolution and pd.notna(resolution):
                resolution = resolution.strftime('%Y-%m-%d')
            else:
                resolution = None

            conn.execute('''
                INSERT OR REPLACE INTO ae_history 
                (event_id, site_id, subject_id, ae_name, severity, event_type, 
                 onset_date, resolution_date, outcome, status, report_week)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['事件ID'],
                row['中心编号'],
                row['受试者号'],
                row['AE名称'],
                row['严重程度'],
                row['事件类型'],
                onset,
                resolution,
                row['转归'],
                row['状态'],
                week_start
            ))
        conn.commit()
        conn.close()
        print(f"✅ AE snapshot saved for week: {week_start}")

    # ========== 新增方法：获取每周新增入组 ==========
    def get_weekly_new_enrollment(self, weeks=None):
        """
        返回每周新增入组总数（按 week_start 升序）
        weeks: 返回最近几周（若 None 则返回全部）
        """
        conn = sqlite3.connect(self.db_path)
        query = """
            SELECT week_start, SUM(new_this_week) as total_new
            FROM enrollment_history
            GROUP BY week_start
            ORDER BY week_start DESC
        """
        if weeks is not None:
            query += f" LIMIT {weeks}"
        df = pd.read_sql_query(query, conn)
        conn.close()
        if df.empty:
            return df
        df = df.sort_values('week_start').reset_index(drop=True)
        df['week_start'] = pd.to_datetime(df['week_start'])
        return df