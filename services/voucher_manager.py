# voucher_manager.py - منطق سندات القبض والصرف (منقول من Nuit Cosmetics للمحاسب)
# يعمل مع Place 2026 - يتطلب الجداول TBL004, TBL009, TBL010, TBL011, TBL012, TBL038
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

# ثوابت أنواع السندات
TYPE_RECEIPT = "3BCA1E9B-1EE2-460D-B552-252CDD568A55"   # قبض
TYPE_PAYMENT = "E61AEE0C-193F-498D-8827-5B0977321FF7"   # صرف
DEFAULT_CURRENCY = "48554FE9-C3F9-4BA8-B746-2026E0DEE92B"

def _row_val(row, key, default=None):
    if row is None: return default
    if isinstance(row, dict):
        v = row.get(key) or row.get(str(key).upper()) or row.get(str(key).lower())
        return v if v is not None else default
    if isinstance(key, int) and 0 <= key < len(row):
        return row[key]
    return default

def _get_db():
    """الحصول على الاتصال من Flask app."""
    try:
        from flask import g
        return getattr(g, 'db', None)
    except Exception:
        return None

def get_conn():
    """الاتصال بقاعدة البيانات - يستخدم get_db من app."""
    try:
        import app as app_module
        return app_module.get_db()
    except Exception:
        return None

def get_sub_accounts(conn=None) -> List[Dict[str, Any]]:
    """دليل الحسابات الفرعية (TBL004)."""
    db = conn or get_conn()
    if not db: return []
    try:
        cur = db.cursor()
        cur.execute("""
            SELECT CardGuide, AccountName, CardCode, MainAccount
            FROM TBL004
            WHERE CardGuide <> MainAccount AND AccountName IS NOT NULL
            ORDER BY CardCode
        """)
        cols = [c[0] for c in cur.description]
        rows = [dict(zip(cols, r)) for r in cur.fetchall()]
        return [{
            "CardGuide": str(r.get("CardGuide", "")),
            "AccountName": r.get("AccountName", ""),
            "CardCode": str(r.get("CardCode", "")),
            "DisplayName": f"{r.get('CardCode','')}-{r.get('AccountName','')}"
        } for r in rows]
    except Exception:
        return []
    # لا نغلق g.db — إدارة Flask
    # finally: ...

def get_next_bond_number(main_guide: str, conn=None) -> int:
    db = conn or get_conn()
    if not db: return 1
    try:
        cur = db.cursor()
        cur.execute("SELECT MAX(BondNumber) FROM TBL010 WHERE MainGuide = ?", (main_guide,))
        row = cur.fetchone()
        val = row[0] if row else 0
        return int(val or 0) + 1
    except Exception:
        return 1

def resolve_account_guid(val: str, conn=None) -> Optional[str]:
    """تحويل كود/اسم الحساب إلى CardGuide."""
    if not val or not str(val).strip(): return None
    val = str(val).strip()
    try:
        uuid.UUID(val)
        return val
    except ValueError:
        pass
    db = conn or get_conn()
    if not db: return None
    try:
        cur = db.cursor()
        cur.execute("SELECT TOP 1 CardGuide FROM TBL004 WHERE CardCode = ? OR AccountName = ? OR AccountName LIKE ?", (val, val, f"%{val}%"))
        row = cur.fetchone()
        if row: return str(row[0])
        return None
    except Exception:
        return None

def resolve_agent_guid(conn, agent_val: str) -> Optional[str]:
    """تحويل العميل إلى CardGuide من TBL016."""
    if not agent_val or not str(agent_val).strip(): return None
    val = str(agent_val).strip()
    if len(val) >= 30 and "-" in val:
        try:
            cur = conn.cursor()
            cur.execute("SELECT CardGuide FROM TBL016 WHERE CardGuide = ?", (val,))
            row = cur.fetchone()
            if row: return str(row[0])
        except: pass
    try:
        cur = conn.cursor()
        cur.execute("SELECT TOP 1 CardGuide FROM TBL016 WHERE AgentName = ? AND ISNULL(NotActive,0)=0", (val,))
        row = cur.fetchone()
        if row: return str(row[0])
        cur.execute("SELECT TOP 1 CardGuide FROM TBL016 WHERE AgentName LIKE ? AND ISNULL(NotActive,0)=0", (f"%{val}%",))
        row = cur.fetchone()
        if row: return str(row[0])
    except Exception:
        pass
    return None

def save_voucher_transaction(data: Dict[str, Any], conn=None) -> Dict[str, Any]:
    """حفظ سند قبض أو صرف."""
    db = conn or get_conn()
    if not db: return {"success": False, "message": "لا يوجد اتصال بقاعدة البيانات"}
    try:
        cur = db.cursor()
        v_type = data.get("type", "DISB")
        main_guide = TYPE_RECEIPT if v_type == "RECP" else TYPE_PAYMENT
        is_receipt = (v_type == "RECP")
        card_guide = str(uuid.uuid4()).upper()
        bond_number = get_next_bond_number(main_guide, db)
        try:
            bond_date = datetime.strptime(data.get("date", ""), "%Y-%m-%d")
        except:
            bond_date = datetime.now()
        notes = data.get("notes") or ""
        ref = data.get("ref") or ""
        header_acct = resolve_account_guid(data.get("mainAccount") or data.get("mainAcct"), db)
        if not header_acct:
            return {"success": False, "message": "الحساب الرئيسي غير صحيح"}
        currency = data.get("currency") or DEFAULT_CURRENCY
        agent_guide = resolve_agent_guid(db, data.get("agent"))
        try:
            cur.execute("""
                INSERT INTO TBL010 (CardGuide, MainGuide, BondNumber, BondDate, CurrencyGuide, Rate, AccountGuide, DocumentNumber, Notes, AgentGuide)
                VALUES (?, ?, ?, ?, ?, 1, ?, ?, ?, ?)
            """, (card_guide, main_guide, bond_number, bond_date, currency, header_acct, ref, notes, agent_guide))
        except Exception as col_err:
            if "AgentGuide" in str(col_err):
                cur.execute("""
                    INSERT INTO TBL010 (CardGuide, MainGuide, BondNumber, BondDate, CurrencyGuide, Rate, AccountGuide, DocumentNumber, Notes)
                    VALUES (?, ?, ?, ?, ?, 1, ?, ?, ?)
                """, (card_guide, main_guide, bond_number, bond_date, currency, header_acct, ref, notes))
            else:
                raise
        for item in data.get("items", []):
            line_acct = resolve_account_guid(item.get("account"), db)
            if not line_acct:
                raise ValueError(f"حساب غير صحيح: {item.get('account')}")
            amount = float(item.get("db") or 0) + float(item.get("cr") or 0)
            debit = 0 if is_receipt else amount
            credit = amount if is_receipt else 0
            cur.execute("""
                INSERT INTO TBL038 (MainGuide, AccountGuide, CurrencyGuide, DebitRate, CreditRate, Notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (card_guide, line_acct, currency, debit, credit, item.get("desc") or notes))
        db.commit()
        return {"success": True, "message": "تم حفظ السند بنجاح", "BondNumber": bond_number, "CardGuide": card_guide}
    except Exception as e:
        if db: db.rollback()
        return {"success": False, "message": str(e)}

def get_recent_transactions(limit: int = 30, conn=None) -> List[Dict[str, Any]]:
    """آخر السندات من TBL010."""
    db = conn or get_conn()
    if not db: return []
    try:
        cur = db.cursor()
        cur.execute("""
            SELECT TOP (?) t10.CardGuide, t10.BondNumber, t10.BondDate, t10.MainGuide, t10.Notes,
                (SELECT ISNULL(SUM(DebitRate + CreditRate), 0) FROM TBL038 WHERE MainGuide = t10.CardGuide) AS Total,
                t9.EntryName
            FROM TBL010 t10
            LEFT JOIN TBL009 t9 ON t10.MainGuide = t9.CardGuide
            ORDER BY t10.BondDate DESC, t10.BondNumber DESC
        """, (min(max(1, int(limit)), 100),))
        cols = [c[0] for c in cur.description]
        out = []
        for row in cur.fetchall():
            r = dict(zip(cols, row))
            dt = r.get("BondDate")
            dt_str = dt.strftime("%Y-%m-%d") if hasattr(dt, "strftime") else str(dt or "")[:10]
            out.append({
                "CardGuide": str(r.get("CardGuide", "")),
                "BondNumber": r.get("BondNumber"),
                "BondDate": dt_str,
                "type_name": r.get("EntryName") or "سند",
                "Notes": r.get("Notes") or "",
                "total": float(r.get("Total") or 0),
            })
        return out
    except Exception:
        return []

def get_cashflow_config(user_id: str, conn=None) -> Optional[Dict]:
    """جلب ConfigJson من CashflowUserConfig."""
    db = conn or get_conn()
    if not db: return None
    try:
        cur = db.cursor()
        cur.execute("SELECT ConfigJson FROM CashflowUserConfig WHERE UserId = ?", (str(user_id or "").strip(),))
        row = cur.fetchone()
        if not row: return None
        raw = row[0] if isinstance(row, (tuple, list)) else (row.get("ConfigJson") if isinstance(row, dict) else None)
        if not raw: return None
        import json
        return json.loads(raw) if isinstance(raw, str) else raw
    except Exception:
        return None

def save_cashflow_config(user_id: str, config: Dict, conn=None) -> bool:
    """حفظ ConfigJson في CashflowUserConfig (يتطلب تشغيل scripts/create_cashflow_config_table.sql)."""
    db = conn or get_conn()
    if not db: return False
    try:
        import json
        uid = str(user_id or "").strip()
        js = json.dumps(config or {}, ensure_ascii=False)
        cur = db.cursor()
        try:
            cur.execute("UPDATE CashflowUserConfig SET ConfigJson = ?, UpdatedAt = GETDATE() WHERE UserId = ?", (js, uid))
            if cur.rowcount and cur.rowcount > 0:
                db.commit()
                return True
            cur.execute("INSERT INTO CashflowUserConfig (UserId, ConfigJson, UpdatedAt) VALUES (?, ?, GETDATE())", (uid, js))
            db.commit()
            return True
        except Exception as tbl_err:
            if "CashflowUserConfig" in str(tbl_err) or "Invalid object" in str(tbl_err):
                pass  # Table may not exist
            raise
    except Exception:
        try: db.rollback()
        except: pass
        return False

def search_agents_quick(search_text: str, conn=None) -> List[Dict[str, Any]]:
    """بحث العملاء من TBL016."""
    db = conn or get_conn()
    if not db: return []
    try:
        cur = db.cursor()
        pat = f"%{(search_text or '').strip()}%"
        cur.execute("""
            SELECT TOP 50 CardGuide, AgentName, CardNumber, Phone
            FROM TBL016
            WHERE (AgentName LIKE ? OR ISNULL(CAST(CardNumber AS NVARCHAR(50)), N'') LIKE ?) AND ISNULL(NotActive, 0) = 0
            ORDER BY AgentName
        """, (pat, pat))
        cols = [c[0] for c in cur.description]
        return [{"CardGuide": str(d.get("CardGuide","")), "AgentName": d.get("AgentName") or "", "CardNumber": str(d.get("CardNumber") or ""), "Phone": str(d.get("Phone") or "")}
                for d in (dict(zip(cols, r)) for r in cur.fetchall())]
    except Exception:
        return []
