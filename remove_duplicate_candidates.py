# -*- coding: utf-8 -*-
"""
إزالة تكرار المرشحين/المتدربين من قاعدة البيانات.
يعتمد على: نفس الاسم (بعد تطبيع) أو نفس البريد الإلكتروني.
يُبقي سجلاً واحداً (أقل CandidateID) وينقل إليه التسجيلات والتقييمات ثم يحذف المكرّرين.
شغّل: python remove_duplicate_candidates.py
"""
import os
import sys
import json

try:
    import pyodbc
except ImportError:
    print("ثبّت pyodbc: pip install pyodbc")
    sys.exit(1)

BASE = os.path.dirname(os.path.abspath(__file__))


def get_connection():
    config_path = os.path.join(BASE, "db_config.json")
    if not os.path.exists(config_path):
        print("لا يوجد db_config.json")
        sys.exit(1)
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    server = config.get("server", ".")
    port = config.get("port", "1433")
    database = config.get("database", "Place2026DB")
    username = config.get("username", "")
    password = config.get("password", "")
    use_trusted = config.get("use_trusted", False)
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server},{port};DATABASE={database};"
        + ("Trusted_Connection=yes;" if use_trusted else f"UID={username};PWD={password};")
    )
    return pyodbc.connect(conn_str, timeout=15)


def main():
    conn = get_connection()
    conn.autocommit = False
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT CandidateID, FullName, Email FROM Candidates")
        rows = cursor.fetchall() or []
        # تطبيع: الاسم (حذف فراغات، صغير) والبريد (حذف فراغات، صغير)
        def norm_name(s):
            return (s or "").strip().lower()
        def norm_email(s):
            if not s or not str(s).strip():
                return None
            return str(s).strip().lower()
        by_name = {}
        by_email = {}
        for r in rows:
            cid, name, email = r[0], r[1], r[2]
            n = norm_name(name)
            e = norm_email(email)
            if n:
                by_name.setdefault(n, []).append(cid)
            if e:
                by_email.setdefault(e, []).append(cid)
        # تجميع كل المكرّرين: نفس الاسم أو نفس البريد
        to_merge = {}
        for n, ids in by_name.items():
            if len(ids) > 1:
                for i in ids:
                    to_merge[i] = to_merge.get(i, set()) | set(ids)
        for e, ids in by_email.items():
            if len(ids) > 1:
                for i in ids:
                    to_merge[i] = to_merge.get(i, set()) | set(ids)
        # تحويل إلى مجموعات متصلة: كل مجموعة نُبقي فيها أصغر CandidateID
        merged = []
        seen = set()
        for cid, group in to_merge.items():
            if cid in seen:
                continue
            keep = min(group)
            remove = sorted(group - {keep})
            if remove:
                merged.append((keep, remove))
                seen |= group
        if not merged:
            print("لا يوجد تكرار (اسم أو بريد) في جدول المرشحين.")
            return
        print("عدد المجموعات المكررة:", len(merged))
        for keep, remove_list in merged:
            for dup in remove_list:
                for table in ["Enrollments", "PlacementTests", "Matches", "TraineeSheetData"]:
                    try:
                        cursor.execute(f"UPDATE {table} SET CandidateID=? WHERE CandidateID=?", (keep, dup))
                        if cursor.rowcount:
                            print(f"  تحديث {table}: {cursor.rowcount} صف من {dup} إلى {keep}")
                    except Exception as e:
                        if "Invalid object name" not in str(e):
                            print(f"  تحذير {table}:", e)
                try:
                    cursor.execute("DELETE FROM Candidates WHERE CandidateID=?", (dup,))
                    print("  حذف مرشح مكرر CandidateID=", dup)
                except Exception as e:
                    print("  خطأ عند حذف", dup, ":", e)
        conn.commit()
        print("تم إزالة التكرار بنجاح.")
    except Exception as e:
        conn.rollback()
        print("خطأ:", e)
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()
