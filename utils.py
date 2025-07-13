import sqlite3
import os
import re
import pandas as pd

DB_PATH = "blacklist.db"

def ensure_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blacklist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            id_number TEXT UNIQUE,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_records(records):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    for r in records:
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO blacklist (name, id_number, status)
                VALUES (?, ?, ?)
            ''', (r["name"], r["id_number"], r["status"]))
        except Exception as e:
            print(f"插入失敗：{r}, 錯誤：{e}")
    conn.commit()
    conn.close()

def search_blacklist(id_number):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM blacklist WHERE id_number = ?', (id_number,))
    result = cursor.fetchone()
    conn.close()
    return result

def parse_blacklist_file(file_path):
    ext = os.path.splitext(file_path)[1]
    records = []

    if ext.lower() == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        for line in lines:
            match = re.findall(r"姓名[:：]?(.*?)\s+身分證字號[:：]?(.*?)\s+狀態[:：]?(.*)", line)
            if match:
                name, id_number, status = match[0]
                records.append({
                    "name": name.strip(),
                    "id_number": id_number.strip(),
                    "status": status.strip()
                })

    elif ext.lower() in [".xls", ".xlsx"]:
        df = pd.read_excel(file_path)
        for _, row in df.iterrows():
            name = str(row.get("姓名", "")).strip()
            id_number = str(row.get("身分證字號", "")).strip()
            status = str(row.get("狀態", "")).strip()
            if name and id_number:
                records.append({
                    "name": name,
                    "id_number": id_number,
                    "status": status
                })

    else:
        raise Exception("不支援的檔案格式，請上傳 .txt 或 .xlsx")

    return records
