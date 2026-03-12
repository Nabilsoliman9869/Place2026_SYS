# كود SQL — التدفق النقدي (Smart CashFlow)

## 1. حسابات الرأس والتفاصيل (TBL004)

### جلب دليل الحسابات الفرعية
```sql
SELECT CardGuide, AccountName, CardCode, MainAccount
FROM TBL004
WHERE CardGuide <> MainAccount AND AccountName IS NOT NULL
ORDER BY CardCode;
```

### استخراج CardGuide من كود أو اسم الحساب
```sql
SELECT TOP 1 CardGuide 
FROM TBL004 
WHERE CardCode = @val 
   OR AccountName = @val 
   OR AccountName LIKE '%' + @val + '%';
```

---

## 2. أنماط السندات (TBL009)

### GUIDs الثابتة المستخدمة في الكود

| النوع | GUID | الاسم |
|-------|------|-------|
| قبض | `3BCA1E9B-1EE2-460D-B552-252CDD568A55` | سند قبض |
| صرف | `E61AEE0C-193F-498D-8827-5B0977321FF7` | سند صرف |
| قيد يومية | `4E2840D9-BFA3-4D9E-BB18-46B699169045` | قيد يومية |

### جلب أنماط السندات من TBL009
```sql
SELECT CardGuide, EntryName
FROM TBL009
WHERE CardGuide IN (
    '3BCA1E9B-1EE2-460D-B552-252CDD568A55',  -- قبض
    'E61AEE0C-193F-498D-8827-5B0977321FF7',  -- صرف
    '4E2840D9-BFA3-4D9E-BB18-46B699169045'   -- قيد
);
```

### التأكد من وجود أنماط السندات (إنشاءها إن لم تكن موجودة)
```sql
-- إدراج أنواع القيود إذا لم تكن موجودة
IF NOT EXISTS (SELECT 1 FROM TBL009 WHERE CardGuide = '3BCA1E9B-1EE2-460D-B552-252CDD568A55')
INSERT INTO TBL009 (CardGuide, EntryName) VALUES ('3BCA1E9B-1EE2-460D-B552-252CDD568A55', N'سند قبض');

IF NOT EXISTS (SELECT 1 FROM TBL009 WHERE CardGuide = 'E61AEE0C-193F-498D-8827-5B0977321FF7')
INSERT INTO TBL009 (CardGuide, EntryName) VALUES ('E61AEE0C-193F-498D-8827-5B0977321FF7', N'سند صرف');

IF NOT EXISTS (SELECT 1 FROM TBL009 WHERE CardGuide = '4E2840D9-BFA3-4D9E-BB18-46B699169045')
INSERT INTO TBL009 (CardGuide, EntryName) VALUES ('4E2840D9-BFA3-4D9E-BB18-46B699169045', N'قيد يومية');
```

---

## 3. إرسال السندات — سند قبض أو صرف (TBL010 + TBL038)

### 3.1 الرقم التالي للسند
```sql
SELECT MAX(BondNumber) 
FROM TBL010 
WHERE MainGuide = @main_guide;  -- قبض أو صرف
```

### 3.2 إدراج رأس السند (TBL010)
```sql
INSERT INTO TBL010 (
    CardGuide, MainGuide, BondNumber, BondDate, 
    CurrencyGuide, Rate, AccountGuide, DocumentNumber, Notes, AgentGuide
)
VALUES (
    @card_guide,      -- UUID جديد
    @main_guide,      -- 3BCA1E9B... (قبض) أو E61AEE0C... (صرف)
    @bond_number,     -- الرقم التالي
    @bond_date,
    @currency,        -- 48554FE9-C3F9-4BA8-B746-2026E0DEE92B افتراضياً
    1,
    @account_guide,   -- حساب الرأس (الصندوق/البنك)
    @ref,             -- المرجع/رقم الشيك
    @notes,
    @agent_guide      -- العميل/المستفيد من TBL016 (اختياري)
);
```

### 3.3 إدراج تفاصيل السند (TBL038)
```sql
-- لكل سطر في التفاصيل:
INSERT INTO TBL038 (
    MainGuide,     -- CardGuide من TBL010 (رابط بالسند)
    AccountGuide,  -- الحساب من TBL004
    CurrencyGuide,
    DebitRate,     -- مدين (صرف = المبلغ، قبض = 0)
    CreditRate,    -- دائن (قبض = المبلغ، صرف = 0)
    Notes
)
VALUES (
    @card_guide,
    @line_account_guide,
    @currency,
    @debit,   -- قبض: 0  |  صرف: المبلغ
    @credit,  -- قبض: المبلغ  |  صرف: 0
    @desc
);
```

---

## 4. إرسال قيد يومية (TBL011 + TBL012)

### 4.1 الرقم التالي للقيد
```sql
SELECT MAX(EntryNumber) FROM TBL011;
```

### 4.2 إدراج رأس القيد (TBL011)
```sql
INSERT INTO TBL011 (
    CardGuide, EntryNumber, Rate, EntryDate, 
    CurrencyGuide, Notes
)
VALUES (
    @card_guide,
    @entry_number,
    1,
    @entry_date,
    @currency,
    @notes
);
```

### 4.3 إدراج تفاصيل القيد (TBL012)
```sql
INSERT INTO TBL012 (
    MainGuide, AccountGuide, CurrencyGuide, Description,
    Debit, Credit, DebitRate, CreditRate
)
VALUES (
    @card_guide,
    @account_guide,
    @currency,
    @desc,
    @debit,
    @credit,
    @debit,   -- Rate=1
    @credit
);
```

---

## 5. العملة (TBL001)

```sql
SELECT CardGuide, CurrencyName, Rate 
FROM TBL001 
ORDER BY CurrencyName;
```

**العملة الافتراضية:** `48554FE9-C3F9-4BA8-B746-2026E0DEE92B` (ريال سعودي)

---

## 6. العميل/المستفيد (TBL016)

```sql
-- بالاسم بالضبط
SELECT TOP 1 CardGuide 
FROM TBL016 
WHERE AgentName = @val AND ISNULL(NotActive, 0) = 0;

-- بالاسم تقريبي
SELECT TOP 1 CardGuide 
FROM TBL016 
WHERE AgentName LIKE '%' + @val + '%' AND ISNULL(NotActive, 0) = 0;
```

---

## 7. ملخص الجداول المستخدمة

| الجدول | الاستخدام |
|--------|-----------|
| **TBL004** | حسابات الرأس والتفاصيل (دليل الحسابات) |
| **TBL009** | أنماط السندات (قبض، صرف، قيد) |
| **TBL010** | رأس سند قبض/صرف |
| **TBL011** | رأس قيد يومية |
| **TBL012** | تفاصيل قيد يومية (مدين/دائن) |
| **TBL016** | العملاء/الموردون (المستفيد في الرأس) |
| **TBL038** | تفاصيل سند قبض/صرف |
| **TBL001** | العملات |
