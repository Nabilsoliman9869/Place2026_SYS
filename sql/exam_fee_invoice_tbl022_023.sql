-- =============================================================================
-- فاتورة تحصيل رسوم امتحان تدريب — إدخال في TBL022 + TBL023
-- منسوخ من نمط Nuit Cosmetics (main.py: create_sales_invoice / warehouse APIs)
-- الثوابت:
--   نمط الفاتورة (MainGuide): 4590AFCC-3215-4213-9625-A59BD4EFAA3E = رسوم امتحان تدريب
--   الصنف (ProductGuide):       F6776237-EFD0-48C1-B906-013B118B592E
--   المخزن (StoreGuide):       6F058E4B-69B5-43E9-9873-697091C98591
--   العملة (CurrencyGuide):     F128EEE5-B7EA-4C47-A804-CFD3E6ABEE8E
-- =============================================================================

DECLARE @BillTypeGuid   UNIQUEIDENTIFIER = '4590AFCC-3215-4213-9625-A59BD4EFAA3E'; -- رسوم امتحان تدريب
DECLARE @ProductGuid    UNIQUEIDENTIFIER = 'F6776237-EFD0-48C1-B906-013B118B592E'; -- الصنف
DECLARE @StoreGuid      UNIQUEIDENTIFIER = '6F058E4B-69B5-43E9-9873-697091C98591'; -- المخزن
DECLARE @CurrencyGuid   UNIQUEIDENTIFIER = 'F128EEE5-B7EA-4C47-A804-CFD3E6ABEE8E'; -- العملة

DECLARE @BillGuid   UNIQUEIDENTIFIER = NEWID();
DECLARE @RowGuid    UNIQUEIDENTIFIER = NEWID();
DECLARE @BillNum    INT;
DECLARE @Amount     FLOAT = 100.00;   -- مثال: المبلغ
DECLARE @Notes      NVARCHAR(255) = N'رسوم امتحان تحديد المستوى - Place Guide';

-- 1) رقم الفاتورة التالي لهذا النمط
SELECT @BillNum = ISNULL(MAX(BillNumber), 0) + 1
FROM TBL022
WHERE MainGuide = @BillTypeGuid;

-- 2) إدراج رأس الفاتورة TBL022 (نمط Nuit + حقول إلزامية في Schema)
INSERT INTO TBL022 (
    CardGuide, BillNumber, BillDate, MainGuide, StoreGuide, Notes,
    InsertedIn, DoneIn, CurrencyGuide, PayMethod, AgentGuide,
    BillNumber2, OrderNumber, Rate, Discount, LocalAdministrativeTax, TaxValue,
    DownPayment, ChangeValue, Paid, RoundValue, LockRelations, Security, Posted
)
VALUES (
    @BillGuid, @BillNum, GETDATE(), @BillTypeGuid, @StoreGuid, @Notes,
    GETDATE(), GETDATE(), @CurrencyGuid, 1, NULL,
    0, 0, 1.0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 1
);

-- 3) إدراج بند الفاتورة TBL023 (صنف واحد = رسوم الامتحان، الكمية 1، المبلغ = السعر)
INSERT INTO TBL023 (
    RowGuide, MainGuide, ProductGuide, Quantity, ExtraQuantity, Unit,
    TotalValue, TotalValue2, TotalCost, DiscountValue, Discount0, Discount1, Discount2, Discount3,
    ExtraValue, TaxValue, BillTax, Weight, Value, Length, Width, Hieght,
    UnitQuantity, SalesPrice, Quantity2, UnitQuantity2, InsertedIn,
    RecordSecurity
)
VALUES (
    @RowGuid, @BillGuid, @ProductGuid, 1, 0, 0,
    @Amount, @Amount, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    1, @Amount, 0, 0, GETDATE(),
    0
);

SELECT @BillGuid AS CardGuide, @BillNum AS BillNumber, @Amount AS TotalValue;
