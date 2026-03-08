-- =============================================================================
-- فاتورة التدريب — ايراد دورات تدريب (نفس آلية فاتورة الامتحان)
-- TBL020: نوع الفاتورة = ايراد دورات تدريب
-- TBL007: الصنف = ايرادات دورات
-- =============================================================================
-- جدول 20 (نوع الفاتورة): AA290AC4-ECD8-4EC0-851B-FC34DC65C9C7 = ايراد دورات تدريب
-- جدول 7 (الصنف):          4F08EC42-70EB-418F-A7C0-9D4C6447E345 = ايرادات دورات
-- المخزن:                  6F058E4B-69B5-43E9-9873-697091C98591
-- العملة:                   F128EEE5-B7EA-4C47-A804-CFD3E6ABEE8E
-- =============================================================================

DECLARE @BillTypeGuid   UNIQUEIDENTIFIER = 'AA290AC4-ECD8-4EC0-851B-FC34DC65C9C7'; -- TBL020: ايراد دورات تدريب
DECLARE @ProductGuid    UNIQUEIDENTIFIER = '4F08EC42-70EB-418F-A7C0-9D4C6447E345'; -- TBL007: ايرادات دورات
DECLARE @StoreGuid      UNIQUEIDENTIFIER = '6F058E4B-69B5-43E9-9873-697091C98591';
DECLARE @CurrencyGuid   UNIQUEIDENTIFIER = 'F128EEE5-B7EA-4C47-A804-CFD3E6ABEE8E';

DECLARE @BillGuid   UNIQUEIDENTIFIER = NEWID();
DECLARE @RowGuid    UNIQUEIDENTIFIER = NEWID();
DECLARE @BillNum    INT;
DECLARE @Amount     FLOAT = 500.00;   -- مثال: المبلغ
DECLARE @Notes      NVARCHAR(255) = N'ايراد دورات تدريب - Place Guide';

SELECT @BillNum = ISNULL(MAX(BillNumber), 0) + 1
FROM TBL022
WHERE MainGuide = @BillTypeGuid;

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
