-- Database Schema Export
-- Run this to create missing tables

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL093' AND xtype='U')
BEGIN
CREATE TABLE [TBL093] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [MainGuide] uniqueidentifier  NULL,
    [CardDate] datetime  NULL,
    [CardNumber] int  NOT NULL,
    [CardNumber2] int  NOT NULL,
    [NumberValue] float  NOT NULL,
    [NumberValue2] float  NOT NULL,
    [NumberValue3] float  NOT NULL,
    [NumberValue4] float  NOT NULL,
    [AgentGuide] uniqueidentifier  NULL,
    [AgentGuide2] uniqueidentifier  NULL,
    [StoreGuide] uniqueidentifier  NULL,
    [ItemGuide] uniqueidentifier  NULL,
    [Item01] uniqueidentifier  NULL,
    [JobGuide] uniqueidentifier  NULL,
    [ProjectGuide] uniqueidentifier  NULL,
    [BranchGuide] uniqueidentifier  NULL,
    [RelatedArchive] uniqueidentifier  NULL,
    [Category01] uniqueidentifier  NULL,
    [Category02] uniqueidentifier  NULL,
    [Category03] uniqueidentifier  NULL,
    [Category04] uniqueidentifier  NULL,
    [Category05] uniqueidentifier  NULL,
    [BooleanValue01] bit  NOT NULL,
    [ByteValue01] tinyint  NOT NULL,
    [TypeID] smallint  NOT NULL,
    [Notes] nvarchar(255)  NULL,
    [Notes2] nvarchar(255)  NULL,
    [Attachment] image  NULL,
    [CurrencyGuide] uniqueidentifier  NULL,
    [rate] float  NOT NULL,
    [text_1] nvarchar(MAX)  NULL,
    [Discount] float  NOT NULL,
    [notes3] nvarchar(MAX)  NULL,
    [notes4] nvarchar(MAX)  NULL,
    [notes5] nvarchar(MAX)  NULL,
    [Quantity1] float  NOT NULL,
    [price1] float  NOT NULL,
    [Total] float  NOT NULL,
    [Additions] float  NOT NULL,
    [Custominvoice1] nvarchar(MAX)  NULL,
    [Custominvoice2] nvarchar(MAX)  NULL,
    [Custominvoice3] nvarchar(MAX)  NULL,
    [Custominvoice4] nvarchar(MAX)  NULL,
    [Custominvoice5] nvarchar(MAX)  NULL,
    [Billdiscount] float  NOT NULL,
    [Tax] float  NOT NULL,
    [Discountrate] float  NOT NULL,
    [netafterdiscount] float  NOT NULL,
    [Taxrate] float  NOT NULL,
    [net_after_tax] float  NOT NULL,
    [costsenter2] uniqueidentifier  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL121' AND xtype='U')
BEGIN
CREATE TABLE [TBL121] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [RecordGuide] uniqueidentifier  NOT NULL,
    [TypeID] smallint  NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [AgentGuide] uniqueidentifier  NULL,
    [AccountGuide] uniqueidentifier  NULL,
    [CurrencyGuide] uniqueidentifier  NULL,
    [OperationBill] uniqueidentifier  NULL,
    [BillGuide] uniqueidentifier  NULL,
    [CardDate] datetime  NULL,
    [RecordActivated] bit  NOT NULL,
    [Value] float  NOT NULL,
    [ValueRate] float  NOT NULL,
    [Debit] float  NOT NULL,
    [Credit] float  NOT NULL,
    [DebitRate] float  NOT NULL,
    [CreditRate] float  NOT NULL,
    [RelatedAdministration] uniqueidentifier  NULL,
    [ContraAccount] uniqueidentifier  NULL,
    [CostCenter] uniqueidentifier  NULL,
    [Project] uniqueidentifier  NULL,
    [Branch] uniqueidentifier  NULL,
    [ProductGuide] uniqueidentifier  NULL,
    [Category01] uniqueidentifier  NULL,
    [Category02] uniqueidentifier  NULL,
    [Category03] uniqueidentifier  NULL,
    [Category04] uniqueidentifier  NULL,
    [Category05] uniqueidentifier  NULL,
    [Description] nvarchar(255)  NULL,
    [Notes] nvarchar(255)  NULL,
    [SourceBill] uniqueidentifier  NULL,
    [IntValue01] bit  NOT NULL,
    [BitValue01] bit  NOT NULL,
    [BitValue02] bit  NOT NULL,
    [BondGuide] uniqueidentifier  NULL,
    [RecordExcluded] bit  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL104' AND xtype='U')
BEGIN
CREATE TABLE [TBL104] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [TypeID] smallint  NOT NULL,
    [Text01] nvarchar(200)  NULL,
    [Number01] float  NOT NULL,
    [Text02] nvarchar(MAX)  NULL,
    [Text03] nvarchar(MAX)  NULL,
    [Text04] nvarchar(MAX)  NULL,
    [Text05] nvarchar(MAX)  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL072' AND xtype='U')
BEGIN
CREATE TABLE [TBL072] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [Term] nvarchar(255)  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL024' AND xtype='U')
BEGIN
CREATE TABLE [TBL024] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [AccountID] uniqueidentifier  NOT NULL,
    [CurrencyGuide] uniqueidentifier  NOT NULL,
    [ContraAccount] uniqueidentifier  NULL,
    [Discount] float  NOT NULL,
    [Extra] float  NOT NULL,
    [DiscountToSave] float  NOT NULL,
    [ExtraToSave] float  NOT NULL,
    [CostCenter] uniqueidentifier  NULL,
    [Description] ntext  NULL,
    [OperationBond] uniqueidentifier  NULL,
    [NotEffectPrice] bit  NOT NULL,
    [NotEffectTax] bit  NOT NULL,
    [RecordType] smallint  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL131' AND xtype='U')
BEGIN
CREATE TABLE [TBL131] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [PeriodGuide] uniqueidentifier  NULL,
    [DueAfter] int  NOT NULL,
    [DueDate] datetime  NOT NULL,
    [AccountGuide] uniqueidentifier  NULL,
    [DiscountValue] float  NOT NULL,
    [DiscountRatio] float  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='ERPTypes' AND xtype='U')
BEGIN
CREATE TABLE [ERPTypes] (
    [ERPID] int IDENTITY(1,1) NOT NULL,
    [ERPName] nvarchar(50)  NULL,
    [ERPConnection] nvarchar(MAX)  NULL,
    [CompanyID] int  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL011' AND xtype='U')
BEGIN
CREATE TABLE [TBL011] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [RowGuide] uniqueidentifier  NULL,
    [EntryNumber] int  NOT NULL,
    [Posted] tinyint  NOT NULL,
    [Security] tinyint  NOT NULL,
    [EntryDate] datetime  NOT NULL,
    [DoneIn] datetime  NOT NULL,
    [CurrencyGuide] uniqueidentifier  NOT NULL,
    [BillGuide] uniqueidentifier  NULL,
    [BondGuide] uniqueidentifier  NULL,
    [Project] uniqueidentifier  NULL,
    [Branch] uniqueidentifier  NULL,
    [CostCenter] uniqueidentifier  NULL,
    [InsertedIn] datetime  NOT NULL,
    [MainBillGuide] uniqueidentifier  NULL,
    [TypeID] smallint  NOT NULL,
    [Rate] float  NOT NULL,
    [Notes] nvarchar(255)  NULL,
    [CardImage] image  NULL,
    [ByUser] uniqueidentifier  NULL,
    [ByGroup] uniqueidentifier  NULL,
    [CheckID] smallint  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL073' AND xtype='U')
BEGIN
CREATE TABLE [TBL073] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [InsertedIn] datetime  NOT NULL,
    [InDate] datetime  NOT NULL,
    [TypeGuide] uniqueidentifier  NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [Category01] uniqueidentifier  NULL,
    [Category02] uniqueidentifier  NULL,
    [Category03] uniqueidentifier  NULL,
    [Category04] uniqueidentifier  NULL,
    [Category05] uniqueidentifier  NULL,
    [BitValue01] bit  NOT NULL,
    [Notes] nvarchar(255)  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL105' AND xtype='U')
BEGIN
CREATE TABLE [TBL105] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [AgentGuide] uniqueidentifier  NOT NULL,
    [ItemGuide] uniqueidentifier  NULL,
    [GroupGuide] uniqueidentifier  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL050' AND xtype='U')
BEGIN
CREATE TABLE [TBL050] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [NotActive] bit  NOT NULL,
    [CardCode] nvarchar(255)  NOT NULL,
    [Security] tinyint  NOT NULL,
    [BronchName] nvarchar(255)  NOT NULL,
    [LatinName] nvarchar(255)  NULL,
    [DefaultAccount] uniqueidentifier  NULL,
    [BranchNotes2] nvarchar(255)  NULL,
    [BranchNotes3] nvarchar(255)  NULL,
    [MainBronch] uniqueidentifier  NULL,
    [Notes] ntext  NULL,
    [CardImage] image  NULL,
    [ByUser] uniqueidentifier  NULL,
    [ByGroup] uniqueidentifier  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL065' AND xtype='U')
BEGIN
CREATE TABLE [TBL065] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [PriceType] tinyint  NOT NULL,
    [GroupGuide] uniqueidentifier  NOT NULL,
    [Permission] int  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL139' AND xtype='U')
BEGIN
CREATE TABLE [TBL139] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardID] uniqueidentifier  NULL,
    [CardID2] uniqueidentifier  NULL,
    [CardID3] uniqueidentifier  NULL,
    [CardID4] uniqueidentifier  NULL,
    [Number01] float  NOT NULL,
    [Number02] float  NOT NULL,
    [Number03] float  NOT NULL,
    [Number04] float  NOT NULL,
    [Number05] float  NOT NULL,
    [Number06] float  NOT NULL,
    [TypeID] int  NOT NULL,
    [Int01] int  NOT NULL,
    [Int02] int  NOT NULL,
    [Bit01] int  NOT NULL,
    [Bit02] int  NOT NULL,
    [Date1] datetime  NULL,
    [Date2] datetime  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL022' AND xtype='U')
BEGIN
CREATE TABLE [TBL022] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [StoreGuide] uniqueidentifier  NOT NULL,
    [BillDate] datetime  NOT NULL,
    [DateValue01] datetime  NULL,
    [PayMethod] smallint  NOT NULL,
    [LockRelations] bit  NOT NULL,
    [TaxMethod] uniqueidentifier  NULL,
    [DoneIn] datetime  NOT NULL,
    [InsertedIn] datetime  NOT NULL,
    [CurrencyGuide] uniqueidentifier  NOT NULL,
    [BillNumber] int  NOT NULL,
    [BillNumber2] int  NOT NULL,
    [OrderNumber] int  NOT NULL,
    [Rate] float  NOT NULL,
    [Discount] float  NOT NULL,
    [LocalAdministrativeTax] float  NOT NULL,
    [TaxValue] float  NOT NULL,
    [DownPayment] float  NOT NULL,
    [DownPaymentNotes] nvarchar(255)  NULL,
    [ChangeValue] float  NOT NULL,
    [Notes] nvarchar(255)  NULL,
    [AgentGuide] uniqueidentifier  NULL,
    [MainBillGuide] uniqueidentifier  NULL,
    [POSGuide] uniqueidentifier  NULL,
    [PostToAccount] uniqueidentifier  NULL,
    [ProductsAccount] uniqueidentifier  NULL,
    [CommissionAccount] uniqueidentifier  NULL,
    [CreditCard] uniqueidentifier  NULL,
    [Paid] float  NOT NULL,
    [Security] tinyint  NOT NULL,
    [CustomerName] nvarchar(255)  NULL,
    [Posted] tinyint  NOT NULL,
    [CardImage] image  NULL,
    [ContraGuide] uniqueidentifier  NULL,
    [ContraStore] uniqueidentifier  NULL,
    [CashAccount] uniqueidentifier  NULL,
    [ReturnDate] datetime  NULL,
    [Returned] bit  NULL,
    [CostCenter] uniqueidentifier  NULL,
    [BillNotes2] nvarchar(255)  NULL,
    [BillNotes3] nvarchar(255)  NULL,
    [BillNotes4] nvarchar(255)  NULL,
    [BillNotes5] nvarchar(255)  NULL,
    [RelatedArchive] uniqueidentifier  NULL,
    [GeneratedBill] int  NULL,
    [IntValue01] int  NULL,
    [Project] uniqueidentifier  NULL,
    [Branch] uniqueidentifier  NULL,
    [Category01] uniqueidentifier  NULL,
    [Category02] uniqueidentifier  NULL,
    [CurrentStage] uniqueidentifier  NULL,
    [CalculatingField] uniqueidentifier  NULL,
    [RoundValue] float  NOT NULL,
    [ByUser] uniqueidentifier  NULL,
    [ByGroup] uniqueidentifier  NULL,
    [CheckID01] int  NULL,
    [APIReply] nvarchar(MAX)  NULL,
    [PrintCount] int  NULL,
    [APIReplyText] nvarchar(MAX)  NULL,
    [SourceBill] uniqueidentifier  NULL,
    [APIQrCode] nvarchar(MAX)  NULL,
    [Category03] uniqueidentifier  NULL,
    [Category04] uniqueidentifier  NULL,
    [Category05] uniqueidentifier  NULL,
    [ReserveDate] datetime  NULL,
    [CheckID] int  NULL,
    [AddressID] uniqueidentifier  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL106' AND xtype='U')
BEGIN
CREATE TABLE [TBL106] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [AgentGuide] uniqueidentifier  NOT NULL,
    [CardName] nvarchar(255)  NOT NULL,
    [Coding] nvarchar(4000)  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL165' AND xtype='U')
BEGIN
CREATE TABLE [TBL165] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [Category01] uniqueidentifier  NULL,
    [TypeID] smallint  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Clients' AND xtype='U')
BEGIN
CREATE TABLE [Clients] (
    [ClientID] int IDENTITY(1,1) NOT NULL,
    [CompanyName] nvarchar(100)  NOT NULL,
    [Industry] nvarchar(100)  NULL,
    [ContactPerson] nvarchar(100)  NULL,
    [Email] nvarchar(100)  NULL,
    [Phone] nvarchar(50)  NULL,
    [Address] nvarchar(200)  NULL,
    [CreatedAt] datetime  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL132' AND xtype='U')
BEGIN
CREATE TABLE [TBL132] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardName] nvarchar(255)  NOT NULL,
    [TypeID] int  NOT NULL,
    [TypeGuide] uniqueidentifier  NULL,
    [Color] int  NOT NULL,
    [LatinName] nvarchar(255)  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL074' AND xtype='U')
BEGIN
CREATE TABLE [TBL074] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [PriceType] tinyint  NOT NULL,
    [LastCalulatedDate] datetime  NOT NULL,
    [ItemUnit] tinyint  NOT NULL,
    [CurrencyGuide] uniqueidentifier  NULL,
    [ItemGuide] uniqueidentifier  NOT NULL,
    [PriceValue] float  NOT NULL,
    [PriceRate] float  NOT NULL,
    [AgentGuide] uniqueidentifier  NULL,
    [DiscountRation] float  NOT NULL,
    [ExtraRatio] float  NOT NULL,
    [CostCenterGuide] uniqueidentifier  NULL,
    [ProjectGuide] uniqueidentifier  NULL,
    [BranchGuide] uniqueidentifier  NULL,
    [CategoryGuide01] uniqueidentifier  NULL,
    [CategoryGuide02] uniqueidentifier  NULL,
    [CategoryGuide03] uniqueidentifier  NULL,
    [CategoryGuide04] uniqueidentifier  NULL,
    [CategoryGuide05] uniqueidentifier  NULL,
    [StoreGuide] uniqueidentifier  NULL,
    [BillRowGuide] uniqueidentifier  NULL,
    [ExpiryDate] datetime  NULL,
    [PatchCode] nvarchar(250)  NULL,
    [RelatedUnit] uniqueidentifier  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL146' AND xtype='U')
BEGIN
CREATE TABLE [TBL146] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [MethodGuide] uniqueidentifier  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='SubTax' AND xtype='U')
BEGIN
CREATE TABLE [SubTax] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [SubTaxCode] nvarchar(255)  NULL,
    [SubTaxName] nvarchar(255)  NULL,
    [SubTaxNameAR] nvarchar(255)  NULL,
    [TaxID] nvarchar(255)  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL066' AND xtype='U')
BEGIN
CREATE TABLE [TBL066] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [SerialCode] nvarchar(255)  NOT NULL,
    [ExpiryDate] datetime  NULL,
    [EstablishDate] datetime  NULL,
    [Notes] nvarchar(255)  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL107' AND xtype='U')
BEGIN
CREATE TABLE [TBL107] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [CardName] nvarchar(255)  NOT NULL,
    [CostCenter] uniqueidentifier  NULL,
    [Project] uniqueidentifier  NULL,
    [Branch] uniqueidentifier  NULL,
    [Category01] uniqueidentifier  NULL,
    [Category02] uniqueidentifier  NULL,
    [Notes] nvarchar(255)  NULL,
    [Notes2] nvarchar(255)  NULL,
    [Notes3] nvarchar(255)  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='ClientRequests' AND xtype='U')
BEGIN
CREATE TABLE [ClientRequests] (
    [RequestID] int IDENTITY(1,1) NOT NULL,
    [ClientID] int  NULL,
    [JobTitle] nvarchar(100)  NOT NULL,
    [NeededCount] int  NULL,
    [Status] nvarchar(50)  NULL,
    [Gender] nvarchar(20)  NULL,
    [Location] nvarchar(100)  NULL,
    [AgeFrom] int  NULL,
    [AgeTo] int  NULL,
    [SalaryFrom] decimal  NULL,
    [SalaryTo] decimal  NULL,
    [Benefits] nvarchar(MAX)  NULL,
    [EnglishLevel] nvarchar(50)  NULL,
    [ThirdLanguage] nvarchar(50)  NULL,
    [ComputerLevel] nvarchar(50)  NULL,
    [Requirements] nvarchar(MAX)  NULL,
    [SoftSkills] nvarchar(MAX)  NULL,
    [Smoker] nvarchar(20)  NULL,
    [AppearanceLevel] nvarchar(50)  NULL,
    [PhysicalTraits] nvarchar(MAX)  NULL,
    [CreatedAt] datetime  NULL,
    [RequestDate] datetime  NULL,
    [PreferredNationality] nvarchar(50)  NULL,
    [SupplyType] nvarchar(50)  NULL,
    [TechnicalSkills] nvarchar(MAX)  NULL,
    [Insurance] nvarchar(50)  NULL,
    [Nationality] nvarchar(50)  NULL,
    [ShiftType] nvarchar(50)  NULL,
    [WorkingConditions] nvarchar(MAX)  NULL,
    [EducationLevel] nvarchar(100)  NULL,
    [ExperienceYears] int  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL017' AND xtype='U')
BEGIN
CREATE TABLE [TBL017] (
    [ID] tinyint  NOT NULL,
    [PriceColumnName] nvarchar(255)  NOT NULL,
    [PriceTerm] nvarchar(255)  NOT NULL,
    [PricePercent] float  NOT NULL,
    [PriceOrder] int  NOT NULL,
    [PriceFunction] nvarchar(MAX)  NULL,
    [DetailingByCostCenter] bit  NOT NULL,
    [DetailingByProject] bit  NOT NULL,
    [DetailingByBranch] bit  NOT NULL,
    [DetailingByCategory01] bit  NOT NULL,
    [DetailingByCategory02] bit  NOT NULL,
    [DetailingByCategory03] bit  NOT NULL,
    [DetailingByCategory04] bit  NOT NULL,
    [DetailingByCategory05] bit  NOT NULL,
    [DetailingByPatchCode] bit  NOT NULL,
    [DetailingByExpiryDate] bit  NOT NULL,
    [TypeID] int  NOT NULL,
    [DetailingByUnit] bit  NOT NULL,
    [DetailingByVariableUnit] bit  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL133' AND xtype='U')
BEGIN
CREATE TABLE [TBL133] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [AccountGuide] uniqueidentifier  NULL,
    [CostCenterGuide] uniqueidentifier  NULL,
    [ProjectGuide] uniqueidentifier  NULL,
    [BranchGuide] uniqueidentifier  NULL,
    [StoreGuide] uniqueidentifier  NULL,
    [GroupGuide] uniqueidentifier  NULL,
    [AgentsGroupGuide] uniqueidentifier  NULL,
    [FormType] nvarchar(MAX)  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL000' AND xtype='U')
BEGIN
CREATE TABLE [TBL000] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [InformationFor] nvarchar(255)  NOT NULL,
    [InformationValue] ntext  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL067' AND xtype='U')
BEGIN
CREATE TABLE [TBL067] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [CardName] nvarchar(255)  NOT NULL,
    [LatinName] nvarchar(255)  NULL,
    [Notes] nvarchar(255)  NULL,
    [CategoryType] tinyint  NOT NULL,
    [Security] tinyint  NOT NULL,
    [MainGuide] uniqueidentifier  NULL,
    [ByGroup] uniqueidentifier  NULL,
    [ByUser] uniqueidentifier  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL147' AND xtype='U')
BEGIN
CREATE TABLE [TBL147] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [TypeID] int  NOT NULL,
    [Text01] nvarchar(250)  NULL,
    [Number01] float  NOT NULL,
    [Number02] float  NOT NULL,
    [Bit01] bit  NOT NULL,
    [Bit02] bit  NOT NULL,
    [Int01] int  NOT NULL,
    [Int02] int  NOT NULL,
    [Notes] ntext  NULL,
    [BillGuide] uniqueidentifier  NULL,
    [CreditCardGuide] uniqueidentifier  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL012' AND xtype='U')
BEGIN
CREATE TABLE [TBL012] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [RowGuide] uniqueidentifier  NOT NULL,
    [AccountGuide] uniqueidentifier  NOT NULL,
    [CurrencyGuide] uniqueidentifier  NOT NULL,
    [Debit] float  NOT NULL,
    [Credit] float  NOT NULL,
    [DebitRate] float  NOT NULL,
    [CreditRate] float  NOT NULL,
    [EntryDetailsNotes2] nvarchar(255)  NULL,
    [EntryDetailsNotes3] nvarchar(255)  NULL,
    [EntryDetailsNotes4] nvarchar(255)  NULL,
    [EntryDetailsNotes5] nvarchar(255)  NULL,
    [ContraAccount] uniqueidentifier  NULL,
    [CostCenter] uniqueidentifier  NULL,
    [Description] nvarchar(255)  NULL,
    [Project] uniqueidentifier  NULL,
    [Branch] uniqueidentifier  NULL,
    [AgentGuide] uniqueidentifier  NULL,
    [Checked] tinyint  NOT NULL,
    [RowDate] datetime  NULL,
    [CalcDate] datetime  NULL,
    [Category01] uniqueidentifier  NULL,
    [Category02] uniqueidentifier  NULL,
    [Category03] uniqueidentifier  NULL,
    [Category04] uniqueidentifier  NULL,
    [Category05] uniqueidentifier  NULL,
    [NoMerge] bit  NOT NULL,
    [CreditCard] uniqueidentifier  NULL,
    [EntryDetailsNotes6] nvarchar(255)  NULL,
    [EntryDetailsNotes7] nvarchar(255)  NULL,
    [EntryDetailsNotes8] nvarchar(255)  NULL,
    [EntryDetailsNotes9] nvarchar(255)  NULL,
    [ItemGuide] uniqueidentifier  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL025' AND xtype='U')
BEGIN
CREATE TABLE [TBL025] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [Security] tinyint  NOT NULL,
    [CardName] nvarchar(255)  NOT NULL,
    [CurrencyGuide] uniqueidentifier  NULL,
    [AccountID] uniqueidentifier  NULL,
    [TaxAccountID] uniqueidentifier  NULL,
    [TaxNotes] nvarchar(255)  NULL,
    [TaxRatio] float  NOT NULL,
    [CostCenter] uniqueidentifier  NULL,
    [Project] uniqueidentifier  NULL,
    [Branch] uniqueidentifier  NULL,
    [CommissionRatio] float  NOT NULL,
    [Notes] ntext  NULL,
    [CardImage] image  NULL,
    [CashPaymentMethod] tinyint  NULL,
    [CashUser] nvarchar(255)  NULL,
    [CashPass] nvarchar(255)  NULL,
    [CashID] nvarchar(255)  NULL,
    [ByGroup] uniqueidentifier  NULL,
    [ByUser] uniqueidentifier  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL001' AND xtype='U')
BEGIN
CREATE TABLE [TBL001] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [CurrencyName] nvarchar(255)  NOT NULL,
    [LatinName] nvarchar(255)  NULL,
    [Security] tinyint  NOT NULL,
    [Rate] float  NOT NULL,
    [CurrencyShortcut] nvarchar(255)  NULL,
    [CurrencyPartName] nvarchar(255)  NULL,
    [PartLatinName] nvarchar(255)  NULL,
    [Partity] float  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Items' AND xtype='U')
BEGIN
CREATE TABLE [Items] (
    [ItemID] int IDENTITY(1,1) NOT NULL,
    [ItemInternalID] nvarchar(50)  NULL,
    [ItemName] nvarchar(255)  NULL,
    [ItemNameAr] nvarchar(255)  NULL,
    [ItemType] nvarchar(5)  NULL,
    [ItemParentCode] nvarchar(20)  NULL,
    [ItemCode] nvarchar(50)  NULL,
    [ItemActiveFrom] date  NULL,
    [ItemActiveTo] date  NULL,
    [ItemDescription] nvarchar(100)  NULL,
    [ItemDescriptionAr] nvarchar(100)  NULL,
    [ItemRequestReason] nvarchar(100)  NULL,
    [codeUsageRequestId] nvarchar(30)  NULL,
    [ItemUnitType] nvarchar(10)  NULL,
    [ItemPrice] float  NULL,
    [ItemActive] bit  NULL,
    [ItemStatus] nvarchar(50)  NULL,
    [ItemStatusReason] nvarchar(MAX)  NULL,
    [CompanyID] int  NULL,
    [CreatedDate] date  NULL,
    [ModifiedDate] date  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='InvoiceHeaders' AND xtype='U')
BEGIN
CREATE TABLE [InvoiceHeaders] (
    [InvoiceID] int IDENTITY(1,1) NOT NULL,
    [ClientID] int  NULL,
    [CandidateID] int  NULL,
    [InvoiceDate] datetime  NULL,
    [SubTotal] float  NULL,
    [DiscountType] nvarchar(10)  NULL,
    [DiscountValue] float  NULL,
    [TaxPercent] float  NULL,
    [TotalAmount] float  NULL,
    [Status] nvarchar(50)  NULL,
    [CreatedBy] int  NULL,
    [CreatedAt] datetime  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Campaigns' AND xtype='U')
BEGIN
CREATE TABLE [Campaigns] (
    [CampaignID] int IDENTITY(1,1) NOT NULL,
    [Name] nvarchar(100)  NOT NULL,
    [Type] nvarchar(50)  NULL,
    [RequestID] int  NULL,
    [MediaChannel] nvarchar(50)  NULL,
    [AdText] nvarchar(MAX)  NULL,
    [Budget] decimal  NULL,
    [StartDate] date  NULL,
    [EndDate] date  NULL,
    [Status] nvarchar(50)  NULL,
    [CreatedAt] datetime  NULL,
    [Platform] nvarchar(50)  NULL,
    [TargetCount] int  NULL,
    [LanguageLevel] nvarchar(50)  NULL,
    [Nationality] nvarchar(100)  NULL,
    [AgeFrom] int  NULL,
    [AgeTo] int  NULL,
    [PreferredLocation] nvarchar(200)  NULL,
    [SpecialRequirements] nvarchar(MAX)  NULL,
    [CreatedBy] int  NULL,
    [MediaType] nvarchar(50)  NULL,
    [IsGraduated] bit  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL039' AND xtype='U')
BEGIN
CREATE TABLE [TBL039] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [GroupGuide] uniqueidentifier  NOT NULL,
    [CardGuide] nvarchar(256)  NOT NULL,
    [CardValue] float  NOT NULL,
    [Browsing] bit  NOT NULL,
    [Inserting] bit  NOT NULL,
    [Updating] bit  NOT NULL,
    [Deleting] bit  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL148' AND xtype='U')
BEGIN
CREATE TABLE [TBL148] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [RowID] int  NULL,
    [RowKey] uniqueidentifier  NULL,
    [Col01] nvarchar(MAX)  NULL,
    [Col02] nvarchar(MAX)  NULL,
    [Col03] nvarchar(MAX)  NULL,
    [Col04] nvarchar(MAX)  NULL,
    [Col05] nvarchar(MAX)  NULL,
    [Col06] nvarchar(MAX)  NULL,
    [Col07] nvarchar(MAX)  NULL,
    [Col08] nvarchar(MAX)  NULL,
    [Col09] nvarchar(MAX)  NULL,
    [Col10] nvarchar(MAX)  NULL,
    [Col11] nvarchar(MAX)  NULL,
    [Col12] nvarchar(MAX)  NULL,
    [Col13] nvarchar(MAX)  NULL,
    [Col14] nvarchar(MAX)  NULL,
    [Col15] nvarchar(MAX)  NULL,
    [Col16] nvarchar(MAX)  NULL,
    [Col17] nvarchar(MAX)  NULL,
    [Col18] nvarchar(MAX)  NULL,
    [Col19] nvarchar(MAX)  NULL,
    [Col20] nvarchar(MAX)  NULL,
    [Col21] nvarchar(MAX)  NULL,
    [Col22] nvarchar(MAX)  NULL,
    [Col23] nvarchar(MAX)  NULL,
    [Col24] nvarchar(MAX)  NULL,
    [Col25] nvarchar(MAX)  NULL,
    [Col26] nvarchar(MAX)  NULL,
    [Col27] nvarchar(MAX)  NULL,
    [Col28] nvarchar(MAX)  NULL,
    [Col29] nvarchar(MAX)  NULL,
    [Col30] nvarchar(MAX)  NULL,
    [Col31] nvarchar(MAX)  NULL,
    [Col32] nvarchar(MAX)  NULL,
    [Col33] nvarchar(MAX)  NULL,
    [Col34] nvarchar(MAX)  NULL,
    [Col35] nvarchar(MAX)  NULL,
    [Col36] nvarchar(MAX)  NULL,
    [Col37] nvarchar(MAX)  NULL,
    [Col38] nvarchar(MAX)  NULL,
    [Col39] nvarchar(MAX)  NULL,
    [Col40] nvarchar(MAX)  NULL,
    [Col41] nvarchar(MAX)  NULL,
    [ErrorMessage] nvarchar(MAX)  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL002' AND xtype='U')
BEGIN
CREATE TABLE [TBL002] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [CardCode] nvarchar(255)  NOT NULL,
    [ClosingAccountName] nvarchar(255)  NOT NULL,
    [ClosingAccountLatinName] nvarchar(255)  NULL,
    [Security] tinyint  NOT NULL,
    [MasterCloseAccount] uniqueidentifier  NULL,
    [BeginningInventoryAccount] uniqueidentifier  NULL,
    [ClosingInventoryAccount] uniqueidentifier  NULL,
    [BalanceAccount] uniqueidentifier  NULL,
    [CloseAccounts] tinyint  NOT NULL,
    [DebitBalanceCaption] nvarchar(255)  NULL,
    [CreditBalanceCaption] nvarchar(255)  NULL,
    [Notes] ntext  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL149' AND xtype='U')
BEGIN
CREATE TABLE [TBL149] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [FieldTypeID] int  NOT NULL,
    [FieldName] nvarchar(MAX)  NOT NULL,
    [ArgNum01] int  NULL,
    [ArgNum02] int  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Candidates' AND xtype='U')
BEGIN
CREATE TABLE [Candidates] (
    [CandidateID] int IDENTITY(1,1) NOT NULL,
    [FullName] nvarchar(100)  NOT NULL,
    [Email] nvarchar(100)  NULL,
    [Phone] nvarchar(50)  NULL,
    [Status] nvarchar(50)  NULL,
    [CampaignID] int  NULL,
    [InterestLevel] nvarchar(50)  NULL,
    [NextFollowUpDate] date  NULL,
    [Feedback] nvarchar(MAX)  NULL,
    [CVPath] nvarchar(200)  NULL,
    [SoftSkills] nvarchar(MAX)  NULL,
    [EnglishLevel] nvarchar(50)  NULL,
    [IsReadyForMatching] bit  NULL,
    [CreatedAt] datetime  NULL,
    [CurrentCEFR] nvarchar(10)  NULL,
    [TargetCEFR] nvarchar(10)  NULL,
    [LegacyData] nvarchar(MAX)  NULL,
    [GraduationBatch] nvarchar(100)  NULL,
    [GraduationDate] date  NULL,
    [SalesAgentID] int  NULL,
    [SourceChannel] nvarchar(100)  NULL,
    [SecondaryPhone] nvarchar(50)  NULL,
    [RecruiterID] int  NULL,
    [GraduationStatus] nvarchar(50)  NULL,
    [Rejoiner] bit  NULL,
    [Nationality] nvarchar(50)  NULL,
    [Location] nvarchar(100)  NULL,
    [PrimaryIntent] nvarchar(50)  NULL,
    [EngagementStatus] nvarchar(50)  NULL,
    [AvailabilityConstraints] nvarchar(MAX)  NULL,
    [WorkStatus] nvarchar(100)  NULL,
    [Venue] nvarchar(50)  NULL,
    [PlacementReason] nvarchar(100)  NULL,
    [RecordingLink] nvarchar(MAX)  NULL,
    [MarketingAssessment] nvarchar(MAX)  NULL,
    [PreviousApplicationDate] datetime  NULL,
    [AvailabilityStatus] nvarchar(50)  NULL,
    [AllocatorID] int  NULL,
    [HRCode] nvarchar(50)  NULL,
    [NationalID] nvarchar(50)  NULL,
    [TargetLanguage] nvarchar(50)  NULL,
    [ProjectName] nvarchar(100)  NULL,
    [EmploymentStatus] nvarchar(50)  NULL,
    [IsReferredToTraining] bit  NULL,
    [RecruitmentStage] nvarchar(50)  NULL,
    [RecruiterFeedback] nvarchar(MAX)  NULL,
    [IsGraduated] bit  NULL,
    [Address] nvarchar(255)  NULL,
    [Age] int  NULL,
    [WorkedHereBefore] bit  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Customers' AND xtype='U')
BEGIN
CREATE TABLE [Customers] (
    [CustID] int IDENTITY(1,1) NOT NULL,
    [CustType] nvarchar(5)  NULL,
    [CustTypeID] nvarchar(20)  NULL,
    [CustName] nvarchar(120)  NULL,
    [CustCountry] nvarchar(5)  NULL,
    [CustGovernate] nvarchar(30)  NULL,
    [CustRegionCity] nvarchar(50)  NULL,
    [CustStreet] nvarchar(120)  NULL,
    [CustBuildingNumber] nvarchar(10)  NULL,
    [CustPostalCode] nvarchar(10)  NULL,
    [CustFloor] nvarchar(10)  NULL,
    [CustRoom] nvarchar(10)  NULL,
    [CustLandmark] nvarchar(100)  NULL,
    [CustAdditionalInformation] nvarchar(100)  NULL,
    [CompanyID] int  NULL,
    [CustActive] bit  NULL,
    [Created] datetime  NULL,
    [Updated] datetime  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='InvoiceItems' AND xtype='U')
BEGIN
CREATE TABLE [InvoiceItems] (
    [ItemID] int IDENTITY(1,1) NOT NULL,
    [InvoiceID] int  NULL,
    [Description] nvarchar(200)  NULL,
    [Quantity] int  NULL,
    [UnitPrice] float  NULL,
    [LineTotal] float  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL108' AND xtype='U')
BEGIN
CREATE TABLE [TBL108] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [ArchiveType] uniqueidentifier  NOT NULL,
    [FieldName] nvarchar(255)  NOT NULL,
    [TemplateType] int  NOT NULL,
    [CardImage] image  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL159' AND xtype='U')
BEGIN
CREATE TABLE [TBL159] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [ConnectionID] smallint  NOT NULL,
    [RowGuide] uniqueidentifier  NOT NULL,
    [AgentGuide] uniqueidentifier  NULL,
    [CostGuide] uniqueidentifier  NULL,
    [ProductGuide] uniqueidentifier  NOT NULL,
    [Quantity] float  NOT NULL,
    [Unit] int  NOT NULL,
    [Price] float  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL094' AND xtype='U')
BEGIN
CREATE TABLE [TBL094] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [FormName] nvarchar(MAX)  NOT NULL,
    [FormKey] nvarchar(MAX)  NULL,
    [ControlName] nvarchar(MAX)  NOT NULL,
    [FieldName] nvarchar(MAX)  NULL,
    [MainID] int  NULL,
    [EventID] tinyint  NOT NULL,
    [BuildEvent] nvarchar(MAX)  NULL,
    [MessageQuery] nvarchar(MAX)  NULL,
    [DataValidation] nvarchar(MAX)  NULL,
    [MessageType] tinyint  NOT NULL,
    [IsActive] bit  NOT NULL,
    [ResultFormat] nvarchar(50)  NULL,
    [ExcuteType] int  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL082' AND xtype='U')
BEGIN
CREATE TABLE [TBL082] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [Category] uniqueidentifier  NOT NULL,
    [CategoryType] uniqueidentifier  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL134' AND xtype='U')
BEGIN
CREATE TABLE [TBL134] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [CardName] nvarchar(255)  NOT NULL,
    [LatinName] nvarchar(255)  NULL,
    [AffectItemsTax] bit  NOT NULL,
    [AffectBillTax] bit  NOT NULL,
    [BillTaxRatio] float  NOT NULL,
    [CheckConditions] bit  NOT NULL,
    [LocalTypeID] int  NOT NULL,
    [IntValue01] int  NOT NULL,
    [TaxAccount] uniqueidentifier  NULL,
    [ItemsTaxAccount] uniqueidentifier  NULL,
    [DeductTaxWhenExempt] bit  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL028' AND xtype='U')
BEGIN
CREATE TABLE [TBL028] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [RowGuide] uniqueidentifier  NOT NULL,
    [IsInPut] bit  NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [ItemGuide] uniqueidentifier  NOT NULL,
    [Quantity] float  NOT NULL,
    [Unit] tinyint  NOT NULL,
    [TotalValue] float  NOT NULL,
    [Discount0] float  NOT NULL,
    [Discount1] float  NOT NULL,
    [Discount2] float  NOT NULL,
    [Discount3] float  NOT NULL,
    [TotalCost] float  NOT NULL,
    [CostCenter] uniqueidentifier  NULL,
    [StoreID] uniqueidentifier  NULL,
    [StatementName] nvarchar(255)  NULL,
    [Notes] ntext  NULL,
    [Category01] uniqueidentifier  NULL,
    [Category02] uniqueidentifier  NULL,
    [Category03] uniqueidentifier  NULL,
    [Category04] uniqueidentifier  NULL,
    [Category05] uniqueidentifier  NULL,
    [RelatedAgent] uniqueidentifier  NULL,
    [RelatedUnit] uniqueidentifier  NULL,
    [UnitQuantity] float  NOT NULL,
    [QuantityRatio] float  NOT NULL,
    [ExpiryDate] datetime  NULL,
    [EstablishDate] datetime  NULL,
    [DiscountValue] float  NOT NULL,
    [ExtraValue] float  NOT NULL,
    [TaxValue] float  NOT NULL,
    [BillTax] float  NOT NULL,
    [BillCustom1] nvarchar(255)  NULL,
    [BillCustom2] nvarchar(255)  NULL,
    [BillCustom3] nvarchar(255)  NULL,
    [BillCustom4] nvarchar(255)  NULL,
    [BillCustom5] nvarchar(255)  NULL,
    [PatchCode] nvarchar(255)  NULL,
    [SplitBill] tinyint  NOT NULL,
    [ExtraQuantity] float  NOT NULL,
    [Length] float  NOT NULL,
    [Width] float  NOT NULL,
    [Hieght] float  NOT NULL,
    [Weight] float  NOT NULL,
    [Value] float  NOT NULL,
    [SalesPrice] float  NOT NULL,
    [Description] ntext  NULL,
    [ProductsAccount] uniqueidentifier  NULL,
    [SourceBill] uniqueidentifier  NULL,
    [SourceOperationBill] uniqueidentifier  NULL,
    [ManufacturerModel] uniqueidentifier  NULL,
    [Nonmergeable] bit  NOT NULL,
    [Printed] bit  NOT NULL,
    [CurrentStage] uniqueidentifier  NULL,
    [ReserveDate] datetime  NULL,
    [ActivateDate] datetime  NULL,
    [ExternalSourceBill] uniqueidentifier  NULL,
    [RecordImage] image  NULL,
    [ExcludeQtyFromRelations] bit  NULL,
    [UnitExtraQuantity] float  NOT NULL,
    [Saved_TaxRatio] float  NOT NULL,
    [Saved_Calc01] float  NOT NULL,
    [Saved_Calc02] float  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL075' AND xtype='U')
BEGIN
CREATE TABLE [TBL075] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [CardCode] nvarchar(255)  NOT NULL,
    [Security] tinyint  NOT NULL,
    [CardType] tinyint  NOT NULL,
    [CardName] nvarchar(255)  NOT NULL,
    [LatinName] nvarchar(255)  NULL,
    [Notes] ntext  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL040' AND xtype='U')
BEGIN
CREATE TABLE [TBL040] (
    [ID] int  NOT NULL,
    [TypeTerm] nvarchar(255)  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Matches' AND xtype='U')
BEGIN
CREATE TABLE [Matches] (
    [MatchID] int IDENTITY(1,1) NOT NULL,
    [CandidateID] int  NULL,
    [RequestID] int  NULL,
    [MatchDate] datetime  NULL,
    [Status] nvarchar(50)  NULL,
    [InterviewDate] datetime  NULL,
    [InterviewNotes] nvarchar(MAX)  NULL,
    [ClientFeedback] nvarchar(MAX)  NULL,
    [AllocatorID] int  NULL,
    [ReviewNotes] nvarchar(MAX)  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL122' AND xtype='U')
BEGIN
CREATE TABLE [TBL122] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [CardNumber] int  NOT NULL,
    [Security] tinyint  NOT NULL,
    [CardName] nvarchar(255)  NOT NULL,
    [LatinName] nvarchar(255)  NULL,
    [CardType] int  NOT NULL,
    [CardMode] int  NOT NULL,
    [IntValue01] int  NOT NULL,
    [IntValue02] int  NOT NULL,
    [IntValue03] int  NOT NULL,
    [IntValue04] int  NOT NULL,
    [NumberValue02] float  NOT NULL,
    [TextValue01] nvarchar(MAX)  NULL,
    [TextValue02] nvarchar(MAX)  NULL,
    [BitValue01] bit  NOT NULL,
    [BitValue02] bit  NOT NULL,
    [BitValue03] bit  NOT NULL,
    [DateValue01] datetime  NULL,
    [DateValue02] datetime  NULL,
    [LongText01] ntext  NULL,
    [Notes] ntext  NULL,
    [MainGuide] uniqueidentifier  NULL,
    [BitValue04] bit  NOT NULL,
    [BitValue05] bit  NOT NULL,
    [IntValue05] int  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL003' AND xtype='U')
BEGIN
CREATE TABLE [TBL003] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] nvarchar(256)  NOT NULL,
    [CardTerm] nvarchar(255)  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL109' AND xtype='U')
BEGIN
CREATE TABLE [TBL109] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [MainCardGuide] uniqueidentifier  NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [ControlName] nvarchar(255)  NOT NULL,
    [OperationID] int  NULL,
    [TypeID] int  NULL,
    [CardImage] image  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL041' AND xtype='U')
BEGIN
CREATE TABLE [TBL041] (
    [ID] int  NOT NULL,
    [TypeTerm] nvarchar(255)  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL026' AND xtype='U')
BEGIN
CREATE TABLE [TBL026] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [CardNumber] int  NOT NULL,
    [GenerateEntry1] smallint  NOT NULL,
    [GenerateEntry2] smallint  NOT NULL,
    [DoNotGenerateBill1] bit  NOT NULL,
    [DoNotGenerateBill2] bit  NOT NULL,
    [PriceType] tinyint  NOT NULL,
    [PriceType2] tinyint  NOT NULL,
    [PriceType3] tinyint  NOT NULL,
    [BillType] smallint  NOT NULL,
    [BillName] nvarchar(255)  NOT NULL,
    [BillLatinName] nvarchar(255)  NULL,
    [TextValue01] nvarchar(255)  NULL,
    [TextValue02] nvarchar(255)  NULL,
    [TextValue03] nvarchar(255)  NULL,
    [TextValue04] nvarchar(255)  NULL,
    [TextValue05] nvarchar(255)  NULL,
    [DefaultStore1] uniqueidentifier  NULL,
    [DefaultStore2] uniqueidentifier  NULL,
    [DefaultCostCenter1] uniqueidentifier  NULL,
    [DefaultCostCenter2] uniqueidentifier  NULL,
    [DefaultProject1] uniqueidentifier  NULL,
    [DefaultProject2] uniqueidentifier  NULL,
    [DefaultBranch1] uniqueidentifier  NULL,
    [DefaultBranch2] uniqueidentifier  NULL,
    [DefaultCurrency1] uniqueidentifier  NULL,
    [DefaultCurrency2] uniqueidentifier  NULL,
    [BuildBillTypeGuide1] uniqueidentifier  NULL,
    [BuildBillTypeGuide2] uniqueidentifier  NULL,
    [AccountOFOption1] uniqueidentifier  NULL,
    [AccountOFOption2] uniqueidentifier  NULL,
    [AccountOFOption3] uniqueidentifier  NULL,
    [AccountOFOption4] uniqueidentifier  NULL,
    [AccountOFOption5] uniqueidentifier  NULL,
    [AccountOFOption6] uniqueidentifier  NULL,
    [AccountOFOption7] uniqueidentifier  NULL,
    [AccountOFOption8] uniqueidentifier  NULL,
    [AccountOFOption9] uniqueidentifier  NULL,
    [AccountOFOption10] uniqueidentifier  NULL,
    [WithoutItemTax] bit  NOT NULL,
    [IntValue01] int  NOT NULL,
    [IntValue02] int  NOT NULL,
    [BooleanOption1] bit  NOT NULL,
    [BooleanOption2] bit  NOT NULL,
    [BooleanOption3] bit  NOT NULL,
    [BooleanOption4] bit  NOT NULL,
    [BooleanOption5] bit  NOT NULL,
    [BooleanOption6] bit  NOT NULL,
    [BooleanOption7] bit  NOT NULL,
    [BooleanOption8] bit  NOT NULL,
    [BooleanOption9] bit  NOT NULL,
    [BooleanOption10] bit  NOT NULL,
    [BooleanOption11] bit  NOT NULL,
    [BooleanOption12] bit  NOT NULL,
    [BooleanOption13] bit  NOT NULL,
    [BooleanOption14] bit  NOT NULL,
    [BooleanOption15] bit  NOT NULL,
    [BooleanOption16] bit  NOT NULL,
    [BooleanOption17] bit  NOT NULL,
    [BooleanOption18] bit  NOT NULL,
    [BooleanOption19] bit  NOT NULL,
    [BooleanOption20] bit  NOT NULL,
    [BooleanOption21] bit  NOT NULL,
    [BooleanOption22] bit  NOT NULL,
    [BooleanOption23] bit  NOT NULL,
    [BooleanOption24] bit  NOT NULL,
    [BooleanOption25] bit  NOT NULL,
    [BooleanOption26] bit  NOT NULL,
    [BooleanOption27] bit  NOT NULL,
    [BooleanOption28] bit  NOT NULL,
    [BooleanOption29] bit  NOT NULL,
    [BooleanOption30] bit  NOT NULL,
    [BooleanOption31] bit  NOT NULL,
    [BooleanOption32] bit  NOT NULL,
    [BooleanOption33] bit  NOT NULL,
    [BooleanOption34] bit  NOT NULL,
    [BooleanOption35] bit  NOT NULL,
    [BooleanOption36] bit  NOT NULL,
    [BooleanOption37] bit  NOT NULL,
    [BooleanOption38] bit  NOT NULL,
    [BooleanOption39] bit  NOT NULL,
    [BooleanOption40] bit  NOT NULL,
    [BooleanOption41] bit  NOT NULL,
    [BooleanOption42] bit  NOT NULL,
    [BarcodeType] uniqueidentifier  NULL,
    [ExpiryDateRequired] bit  NOT NULL,
    [SearchInPatchCode] bit  NOT NULL,
    [DoNotPostToStores] bit  NOT NULL,
    [DefaultAgent] uniqueidentifier  NULL,
    [DefaultAgent2] uniqueidentifier  NULL,
    [DefaultManufacturerModel] uniqueidentifier  NULL,
    [BondTypeGuide1] uniqueidentifier  NULL,
    [Category01] uniqueidentifier  NULL,
    [Category02] uniqueidentifier  NULL,
    [Category03] uniqueidentifier  NULL,
    [Category04] uniqueidentifier  NULL,
    [Category05] uniqueidentifier  NULL,
    [Notes] ntext  NULL,
    [SavePrintType] uniqueidentifier  NULL,
    [Fields] nvarchar(512)  NULL,
    [Color1] int  NOT NULL,
    [Color2] int  NOT NULL,
    [Number01] float  NOT NULL,
    [Number02] float  NOT NULL,
    [BooleanOption43] bit  NOT NULL,
    [TaxMethod] uniqueidentifier  NULL,
    [RelatedOperationGuide1] uniqueidentifier  NULL,
    [RelatedOperationGuide2] uniqueidentifier  NULL,
    [BooleanOption44] bit  NOT NULL,
    [BooleanOption45] bit  NOT NULL,
    [BooleanOption46] bit  NOT NULL,
    [BooleanOption47] bit  NOT NULL,
    [AccountOFOption09] uniqueidentifier  NULL,
    [AccountOFOption11] uniqueidentifier  NULL,
    [AccountOFOption12] uniqueidentifier  NULL,
    [AccountOFOption13] uniqueidentifier  NULL,
    [AccountOFOption14] uniqueidentifier  NULL,
    [AccountOFOption15] uniqueidentifier  NULL,
    [AccountOFOption16] uniqueidentifier  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL095' AND xtype='U')
BEGIN
CREATE TABLE [TBL095] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [AccountGuide] uniqueidentifier  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL168' AND xtype='U')
BEGIN
CREATE TABLE [TBL168] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [TypeID] smallint  NOT NULL,
    [Text01] nvarchar(MAX)  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL150' AND xtype='U')
BEGIN
CREATE TABLE [TBL150] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [TypeID] int  NOT NULL,
    [FormName] nvarchar(MAX)  NOT NULL,
    [FormID] nvarchar(MAX)  NULL,
    [Caption] nvarchar(MAX)  NOT NULL,
    [RelatedFile] image  NOT NULL,
    [PrintCount] int  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL083' AND xtype='U')
BEGIN
CREATE TABLE [TBL083] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [PeriodGuide] uniqueidentifier  NULL,
    [Category01] uniqueidentifier  NULL,
    [Category02] uniqueidentifier  NULL,
    [Category03] uniqueidentifier  NULL,
    [Category04] uniqueidentifier  NULL,
    [Category05] uniqueidentifier  NULL,
    [IntValue] int  NOT NULL,
    [FloatValue] float  NOT NULL,
    [TextValue1] nvarchar(255)  NULL,
    [Notes] ntext  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL162' AND xtype='U')
BEGIN
CREATE TABLE [TBL162] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [RecordDate] datetime  NOT NULL,
    [CardName] nvarchar(255)  NOT NULL,
    [ValueText] ntext  NOT NULL,
    [ErrorMessage] ntext  NULL,
    [Executed] bit  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL042' AND xtype='U')
BEGIN
CREATE TABLE [TBL042] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [MainGuide] uniqueidentifier  NULL,
    [IsUser] bit  NOT NULL,
    [CardName] nvarchar(255)  NOT NULL,
    [CardLatinName] nvarchar(255)  NULL,
    [Security] tinyint  NOT NULL,
    [JustForPOS] bit  NOT NULL,
    [SeparateGroup] bit  NOT NULL,
    [Notes] ntext  NULL,
    [CheckAccounts] bit  NOT NULL,
    [CheckCostCenters] bit  NOT NULL,
    [CheckProjects] bit  NOT NULL,
    [CheckBranches] bit  NOT NULL,
    [CheckStores] bit  NOT NULL,
    [CheckGroups] bit  NOT NULL,
    [CheckAgentsGroups] bit  NOT NULL,
    [CostCenterID] uniqueidentifier  NULL,
    [ProjectID] uniqueidentifier  NULL,
    [BranchID] uniqueidentifier  NULL,
    [StoreID] uniqueidentifier  NULL,
    [CashAccountID] uniqueidentifier  NULL,
    [UseCostCenters] bit  NOT NULL,
    [UseProjects] bit  NOT NULL,
    [UseBranches] bit  NOT NULL,
    [UseStores] bit  NOT NULL,
    [UseCashAccount] bit  NOT NULL,
    [CardImage] image  NULL,
    [FirstTransactionsNo] int  NOT NULL,
    [SeparateFinancialReports] bit  NOT NULL,
    [HideSeparatesColumn] bit  NOT NULL,
    [CheckUsedAccounts] bit  NOT NULL,
    [CheckUsedCostCenters] bit  NOT NULL,
    [CheckUsedProjects] bit  NOT NULL,
    [CheckUsedBranches] bit  NOT NULL,
    [CheckUsedStores] bit  NOT NULL,
    [CheckUsedGroups] bit  NOT NULL,
    [CheckUsedAgentsGroups] bit  NOT NULL,
    [CheckCustomTax] bit  NOT NULL,
    [CurrencyID] uniqueidentifier  NULL,
    [UseCurrency] bit  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL076' AND xtype='U')
BEGIN
CREATE TABLE [TBL076] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [AccountGuide] uniqueidentifier  NULL,
    [ItemsGuide] uniqueidentifier  NULL,
    [AccountRatio] float  NOT NULL,
    [Notes] nvarchar(255)  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL013' AND xtype='U')
BEGIN
CREATE TABLE [TBL013] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [UsGuide] uniqueidentifier  NOT NULL,
    [CardCode] nvarchar(255)  NULL,
    [NotActive] bit  NOT NULL,
    [UserName] nvarchar(255)  NOT NULL,
    [Password] nvarchar(50)  NULL,
    [Informations] ntext  NULL,
    [Security] tinyint  NOT NULL,
    [UserLanguage] smallint  NOT NULL,
    [POSGuide] uniqueidentifier  NULL,
    [BuiltIn] datetime  NOT NULL,
    [ShowInDropDown] bit  NOT NULL,
    [Notes] ntext  NULL,
    [UserColor] int  NULL,
    [RelatedAgent] uniqueidentifier  NULL,
    [OptionGuide] uniqueidentifier  NULL,
    [CostCenterGuide] uniqueidentifier  NULL,
    [ProjectGuide] uniqueidentifier  NULL,
    [BranchGuide] uniqueidentifier  NULL,
    [CardImage] image  NULL,
    [StoreGuide] uniqueidentifier  NULL,
    [CashAccountGuide] uniqueidentifier  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='RegionCity' AND xtype='U')
BEGIN
CREATE TABLE [RegionCity] (
    [CityID] int  NULL,
    [CityName] nvarchar(50)  NULL,
    [GovID] int  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL018' AND xtype='U')
BEGIN
CREATE TABLE [TBL018] (
    [ID] smallint  NOT NULL,
    [MoveTerm] nvarchar(50)  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL014' AND xtype='U')
BEGIN
CREATE TABLE [TBL014] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [Security] tinyint  NOT NULL,
    [CardDate] datetime  NULL,
    [CardName] nvarchar(255)  NOT NULL,
    [LatinName] nvarchar(255)  NULL,
    [CardType] int  NOT NULL,
    [WindowType] int  NOT NULL,
    [IntValue01] int  NOT NULL,
    [IntValue02] int  NOT NULL,
    [IntValue03] int  NOT NULL,
    [IntValue04] int  NOT NULL,
    [NumberValue01] float  NOT NULL,
    [NumberValue02] float  NOT NULL,
    [NumberValue03] float  NOT NULL,
    [NumberValue04] float  NOT NULL,
    [NumberValue05] float  NOT NULL,
    [NumberValue06] float  NOT NULL,
    [AccountGuide] uniqueidentifier  NULL,
    [AccountGuide02] uniqueidentifier  NULL,
    [CurrencyGuide] uniqueidentifier  NULL,
    [CurrencyGuide02] uniqueidentifier  NULL,
    [AttendanceGuide] uniqueidentifier  NULL,
    [RelatedCard] uniqueidentifier  NULL,
    [RelatedCard2] uniqueidentifier  NULL,
    [RelatedCard3] uniqueidentifier  NULL,
    [Category01] uniqueidentifier  NULL,
    [Category02] uniqueidentifier  NULL,
    [Category03] uniqueidentifier  NULL,
    [Category04] uniqueidentifier  NULL,
    [Category05] uniqueidentifier  NULL,
    [PeriodType] uniqueidentifier  NULL,
    [TextValue01] nvarchar(255)  NULL,
    [TextValue02] nvarchar(255)  NULL,
    [TextValue03] nvarchar(255)  NULL,
    [TextValue04] nvarchar(255)  NULL,
    [TextValue05] nvarchar(255)  NULL,
    [IsSelected] bit  NOT NULL,
    [BitValue1] bit  NOT NULL,
    [BitValue2] bit  NOT NULL,
    [BitValue3] bit  NOT NULL,
    [BitValue4] bit  NOT NULL,
    [BitValue5] bit  NOT NULL,
    [BitValue6] bit  NOT NULL,
    [BitValue7] bit  NOT NULL,
    [BitValue8] bit  NOT NULL,
    [BitValue9] bit  NOT NULL,
    [BitValue10] bit  NOT NULL,
    [LongText01] nvarchar(MAX)  NULL,
    [LongText02] nvarchar(MAX)  NULL,
    [LongText03] nvarchar(MAX)  NULL,
    [Date01] datetime  NULL,
    [Date02] datetime  NULL,
    [Date03] datetime  NULL,
    [Date04] datetime  NULL,
    [CalcDate01] datetime  NULL,
    [CalcDate02] datetime  NULL,
    [CostCenter] uniqueidentifier  NULL,
    [Project] uniqueidentifier  NULL,
    [Branch] uniqueidentifier  NULL,
    [AgentGuide] uniqueidentifier  NULL,
    [AgentGuide2] uniqueidentifier  NULL,
    [AgentGroupGuide] uniqueidentifier  NULL,
    [BillType] uniqueidentifier  NULL,
    [BondType] uniqueidentifier  NULL,
    [OperationBill] uniqueidentifier  NULL,
    [CardImage] image  NULL,
    [Notes] nvarchar(255)  NULL,
    [ByUser] uniqueidentifier  NULL,
    [ByGroup] uniqueidentifier  NULL,
    [BitValue11] bit  NOT NULL,
    [BitValue12] bit  NOT NULL,
    [BitValue13] bit  NOT NULL,
    [ActivateDate] datetime  NULL,
    [OperationBill2] uniqueidentifier  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL096' AND xtype='U')
BEGIN
CREATE TABLE [TBL096] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [CardName] nvarchar(255)  NOT NULL,
    [CardLatinName] nvarchar(255)  NULL,
    [Security] tinyint  NOT NULL,
    [DefaultShift] uniqueidentifier  NULL,
    [Category01] uniqueidentifier  NULL,
    [Category02] uniqueidentifier  NULL,
    [Category03] uniqueidentifier  NULL,
    [Category04] uniqueidentifier  NULL,
    [Category05] uniqueidentifier  NULL,
    [Category06] uniqueidentifier  NULL,
    [Category07] uniqueidentifier  NULL,
    [MainAttendance] uniqueidentifier  NULL,
    [Fields] ntext  NOT NULL,
    [BitValue1] bit  NOT NULL,
    [BitValue2] bit  NOT NULL,
    [BitValue3] bit  NOT NULL,
    [BitValue4] bit  NOT NULL,
    [BitValue5] bit  NOT NULL,
    [BitValue6] bit  NOT NULL,
    [LoginFromPeriod] float  NOT NULL,
    [LoginToPeriod] float  NOT NULL,
    [LogoutFromPeriod] float  NOT NULL,
    [LogoutToPeriod] float  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL169' AND xtype='U')
BEGIN
CREATE TABLE [TBL169] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [TypeID] smallint  NOT NULL,
    [Text01] nvarchar(MAX)  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL135' AND xtype='U')
BEGIN
CREATE TABLE [TBL135] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [CardType] int  NOT NULL,
    [Security] tinyint  NOT NULL,
    [CardName] nvarchar(255)  NOT NULL,
    [LatinName] nvarchar(255)  NULL,
    [Fields] ntext  NULL,
    [NormalAbcenteeVacation] uniqueidentifier  NULL,
    [UnjustifiedAbcenteeVacation] uniqueidentifier  NULL,
    [LateEntranceHourlyVacation] uniqueidentifier  NULL,
    [EarlyLeaveHourlyVacation] uniqueidentifier  NULL,
    [AbsenteeTimeHourlyVacation] uniqueidentifier  NULL,
    [NormalVacationExecutions] uniqueidentifier  NULL,
    [NormalAbcenteeExecutions] uniqueidentifier  NULL,
    [LateEntranceExecutions] uniqueidentifier  NULL,
    [EarlyLeaveExecutions] uniqueidentifier  NULL,
    [EarlyEntranceExecutions] uniqueidentifier  NULL,
    [LateLeaveExecutions] uniqueidentifier  NULL,
    [AbsenteeTimeExecutions] uniqueidentifier  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Trainers' AND xtype='U')
BEGIN
CREATE TABLE [Trainers] (
    [TrainerID] int IDENTITY(1,1) NOT NULL,
    [FullName] nvarchar(100)  NOT NULL,
    [Specialization] nvarchar(100)  NULL,
    [Phone] nvarchar(50)  NULL,
    [Email] nvarchar(100)  NULL,
    [HourlyRate] decimal  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL110' AND xtype='U')
BEGIN
CREATE TABLE [TBL110] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [CardName] nvarchar(255)  NOT NULL,
    [CardType] int  NOT NULL,
    [Security] tinyint  NOT NULL,
    [Notes] nvarchar(255)  NULL,
    [DateFormat] nvarchar(255)  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL019' AND xtype='U')
BEGIN
CREATE TABLE [TBL019] (
    [ID] smallint  NOT NULL,
    [PayTerm] nvarchar(255)  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL163' AND xtype='U')
BEGIN
CREATE TABLE [TBL163] (
    [SP_ID] int  NULL,
    [AccountSecurity] tinyint  NULL,
    [AffectCostomerPrice] bit  NULL,
    [AffectLastPurchasePrice] bit  NULL,
    [AgentGuide] uniqueidentifier  NULL,
    [AgentLatinName] nvarchar(255)  NULL,
    [AgentName] nvarchar(255)  NULL,
    [AgentSecurity] tinyint  NULL,
    [AllBillNetDiscount] float  NULL,
    [AllBillNetDiscountRate] float  NULL,
    [AllTaxBill] float  NULL,
    [AllTaxBillRate] float  NULL,
    [BillCustom1] nvarchar(255)  NULL,
    [BillCustom2] nvarchar(255)  NULL,
    [BillCustom3] nvarchar(255)  NULL,
    [BillCustom4] nvarchar(255)  NULL,
    [BillCustom5] nvarchar(255)  NULL,
    [BillDate] datetime  NULL,
    [BillDiscountsAndExtras] float  NULL,
    [BillDiscountsAndExtrasRatio] float  NULL,
    [BillItemNetTotalAfterTax] float  NULL,
    [BillItemNetTotalAfterTaxRate] float  NULL,
    [BillItemNetTotalBeforeTax] float  NULL,
    [BillItemNetTotalBeforeTaxRate] float  NULL,
    [BillKindID] smallint  NULL,
    [BillMethod] tinyint  NULL,
    [BillNotes] nvarchar(255)  NULL,
    [BillNotes2] nvarchar(255)  NULL,
    [BillNotes3] nvarchar(255)  NULL,
    [BillNotes4] nvarchar(255)  NULL,
    [BillNotes5] nvarchar(255)  NULL,
    [BillNumber] int  NULL,
    [BillNumber2] int  NULL,
    [BillQty] float  NULL,
    [BillQuantity] float  NULL,
    [BillSecurity] tinyint  NULL,
    [BillTotalDiscounts] float  NULL,
    [BillTotalExtras] float  NULL,
    [BillTotalValue] float  NULL,
    [BillType] smallint  NULL,
    [BillTypeGuide] uniqueidentifier  NULL,
    [BillTypeID] smallint  NULL,
    [Branch] uniqueidentifier  NULL,
    [BranchCode] nvarchar(255)  NULL,
    [BranchName] nvarchar(255)  NULL,
    [ByGroup] uniqueidentifier  NULL,
    [CalcKeyField] uniqueidentifier  NULL,
    [CalculatingField] uniqueidentifier  NULL,
    [Category01] uniqueidentifier  NULL,
    [Category02] uniqueidentifier  NULL,
    [Category03] uniqueidentifier  NULL,
    [Category04] uniqueidentifier  NULL,
    [Category05] uniqueidentifier  NULL,
    [CategoryName01] nvarchar(255)  NULL,
    [CategoryName02] nvarchar(255)  NULL,
    [CategoryName03] nvarchar(255)  NULL,
    [CategoryName04] nvarchar(255)  NULL,
    [CategoryName05] nvarchar(255)  NULL,
    [CommissionAccount] nvarchar(511)  NULL,
    [CommissionAccountCode] nvarchar(255)  NULL,
    [CommissionAccountGuide] uniqueidentifier  NULL,
    [CommissionAccountLatinName] nvarchar(255)  NULL,
    [CommissionAccountName] nvarchar(255)  NULL,
    [CommissionAccSecurity] tinyint  NULL,
    [CommissionSecurity] tinyint  NULL,
    [CostCenter] uniqueidentifier  NULL,
    [CostCenterCode] nvarchar(255)  NULL,
    [CostCenterName] nvarchar(255)  NULL,
    [CreditCardCommissionRatio] float  NULL,
    [CreditCardGuide] uniqueidentifier  NULL,
    [CreditCardName] nvarchar(255)  NULL,
    [CurrencyGuide] uniqueidentifier  NULL,
    [CurrencyLatinName] nvarchar(255)  NULL,
    [CurrencyName] nvarchar(255)  NULL,
    [CurrencyShortcut] nvarchar(255)  NULL,
    [CustomerName] nvarchar(255)  NULL,
    [DateValue] float  NULL,
    [Description] ntext  NULL,
    [Description2] nvarchar(255)  NULL,
    [DetailsStore] uniqueidentifier  NULL,
    [DiscountsAccountSecurity] tinyint  NULL,
    [DiscountsAndEctrasDistributed] bit  NULL,
    [DoneIn] datetime  NULL,
    [DoNotAffectCosts] bit  NULL,
    [DownPayment] float  NULL,
    [EstablishDate] datetime  NULL,
    [ExpiryDate] datetime  NULL,
    [ExtraQty] float  NULL,
    [ExtraQuantity] float  NULL,
    [Factor] float  NULL,
    [Factor2] float  NULL,
    [Factor3] float  NULL,
    [GroupCode] nvarchar(255)  NULL,
    [GroupGuid] uniqueidentifier  NULL,
    [GroupLatinName] nvarchar(255)  NULL,
    [GroupName] nvarchar(255)  NULL,
    [HeadStore] uniqueidentifier  NULL,
    [Hieght] float  NULL,
    [InPut] float  NULL,
    [InPutNetTotal] float  NULL,
    [InsertedIn] datetime  NULL,
    [InvoiceGuide] uniqueidentifier  NULL,
    [InvoiceID] int  NULL,
    [InvoiceLatinName] nvarchar(255)  NULL,
    [InvoiceMovementSide] smallint  NULL,
    [InvoiceName] nvarchar(255)  NULL,
    [IsAssets] bit  NULL,
    [Item] nvarchar(511)  NULL,
    [ItemBillDiscount] float  NULL,
    [ItemBillDiscountRate] float  NULL,
    [ItemBillTax] float  NULL,
    [ItemCategory01Guide] uniqueidentifier  NULL,
    [ItemCategory02Guide] uniqueidentifier  NULL,
    [ItemDiscount0] float  NULL,
    [ItemDiscount1] float  NULL,
    [ItemDiscount2] float  NULL,
    [ItemDiscount3] float  NULL,
    [ItemDiscountValue] float  NULL,
    [ItemDiscountValueRate] float  NULL,
    [ItemExtraValue] float  NULL,
    [ItemExtraValueRate] float  NULL,
    [ItemFirstNetTotal] float  NULL,
    [ItemFirstNetTotalRate] float  NULL,
    [ItemGroup] nvarchar(511)  NULL,
    [ItemLatinName] nvarchar(255)  NULL,
    [ItemName] nvarchar(255)  NULL,
    [ItemNetPrice] float  NULL,
    [ItemNetPriceAfterTax] float  NULL,
    [ItemNetPriceAfterTaxRate] float  NULL,
    [ItemNetPriceBeforeTax] float  NULL,
    [ItemNetPriceBeforeTaxRate] float  NULL,
    [ItemNetPriceRate] float  NULL,
    [ItemNetTotal] float  NULL,
    [ItemNetTotalAfterTax] float  NULL,
    [ItemNetTotalAfterTaxRate] float  NULL,
    [ItemNetTotalBeforeTax] float  NULL,
    [ItemNetTotalBeforeTaxRate] float  NULL,
    [ItemNetTotalRate] float  NULL,
    [ItemOverBillDiscountsAndExtras] float  NULL,
    [ItemPreparedNetTotal] float  NULL,
    [ItemPriceRatio] float  NULL,
    [ItemQuantity] float  NULL,
    [ItemSecurity] tinyint  NULL,
    [ItemSortID] int  NULL,
    [ItemSource] nvarchar(255)  NULL,
    [ItemTaxValue] float  NULL,
    [ItemTaxValueRate] float  NULL,
    [ItemTotalValue] float  NULL,
    [ItemTotalValueRate] float  NULL,
    [Length] float  NULL,
    [MainGroupGuide] uniqueidentifier  NULL,
    [MainQuantity] float  NULL,
    [MBillQty] float  NULL,
    [MBillQuantity] float  NULL,
    [MExtraQty] float  NULL,
    [MQuantity] float  NULL,
    [NetAfterTax] float  NULL,
    [NetBeforeTax] float  NULL,
    [NetBillQuantity] float  NULL,
    [NotAffectCostActivity] bit  NULL,
    [OrderNumber] int  NULL,
    [OutPut] float  NULL,
    [OutPutNetTotal] float  NULL,
    [OverBillDiscounts] float  NULL,
    [OverBillDiscountsAndExtras] float  NULL,
    [OverBillDiscountsAndExtrasRatio] float  NULL,
    [OverBillExtras] float  NULL,
    [Paid] float  NULL,
    [PatchCode] nvarchar(255)  NULL,
    [PayMethod] smallint  NULL,
    [PayTerm] nvarchar(255)  NULL,
    [POSDiscount] float  NULL,
    [POSGuide] uniqueidentifier  NULL,
    [POSTaxValue] float  NULL,
    [POSTaxValueRate] float  NULL,
    [Posted] tinyint  NULL,
    [PostToAccount] nvarchar(511)  NULL,
    [PostToAccountCode] nvarchar(255)  NULL,
    [PostToAccountGuide] uniqueidentifier  NULL,
    [PostToAccountLatinName] nvarchar(255)  NULL,
    [PostToAccountName] nvarchar(255)  NULL,
    [PriceBillNetDiscount] float  NULL,
    [PriceBillNetDiscountRate] float  NULL,
    [ProductCode] nvarchar(255)  NULL,
    [ProductGuide] uniqueidentifier  NULL,
    [ProductsAccount] uniqueidentifier  NULL,
    [ProductType] tinyint  NULL,
    [Project] uniqueidentifier  NULL,
    [ProjectCode] nvarchar(255)  NULL,
    [ProjectName] nvarchar(255)  NULL,
    [Qty] float  NULL,
    [Quantity] float  NULL,
    [Rate] float  NULL,
    [RecordDate] datetime  NULL,
    [RecordSecurity] tinyint  NULL,
    [RelatedAgent] uniqueidentifier  NULL,
    [RelatedObjects] nvarchar(255)  NULL,
    [ReserveDate] datetime  NULL,
    [RowDiscountRatio] float  NULL,
    [RowExtraRatio] float  NULL,
    [RowGuide] uniqueidentifier  NULL,
    [RowInsertedIn] datetime  NULL,
    [RowTaxRatio] float  NULL,
    [SalesPrice] float  NULL,
    [SavedCostPrice] float  NULL,
    [SavedTotalCost] float  NULL,
    [StatementName] nvarchar(255)  NULL,
    [StockProduct] smallint  NULL,
    [Store] nvarchar(511)  NULL,
    [StoreCode] nvarchar(255)  NULL,
    [StoreGuide] uniqueidentifier  NULL,
    [StoreID] uniqueidentifier  NULL,
    [StoreName] nvarchar(255)  NULL,
    [StoreSecurity] tinyint  NULL,
    [TaxAffectNetPrice] bit  NULL,
    [TaxAffectPrice] bit  NULL,
    [TaxBillNetDiscount] float  NULL,
    [TaxBillNetDiscountRate] float  NULL,
    [TaxMethod] uniqueidentifier  NULL,
    [TaxValue] float  NULL,
    [TaxValueRate] float  NULL,
    [TotalIncludeTax] bit  NULL,
    [Unit] tinyint  NULL,
    [UnitName] nvarchar(255)  NULL,
    [UnitPrice] float  NULL,
    [Value] float  NULL,
    [VariableUnit] uniqueidentifier  NULL,
    [VariableUnitName] nvarchar(255)  NULL,
    [VariableUnitPrice] float  NULL,
    [VariableUnitQuantity] float  NULL,
    [Weight] float  NULL,
    [Width] float  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL151' AND xtype='U')
BEGIN
CREATE TABLE [TBL151] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [GroupGuide] uniqueidentifier  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL167' AND xtype='U')
BEGIN
CREATE TABLE [TBL167] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [MaxDebit] float  NOT NULL,
    [MaxCredit] float  NOT NULL,
    [MinDebit] float  NOT NULL,
    [MinCredit] float  NOT NULL,
    [BudgetValue] float  NOT NULL,
    [BudgetType] smallint  NOT NULL,
    [AccountGuide] uniqueidentifier  NULL,
    [CostCenterGuide] uniqueidentifier  NULL,
    [ProjectGuide] uniqueidentifier  NULL,
    [BranchGuide] uniqueidentifier  NULL,
    [CategoryGuide01] uniqueidentifier  NULL,
    [CategoryGuide02] uniqueidentifier  NULL,
    [CategoryGuide03] uniqueidentifier  NULL,
    [CategoryGuide04] uniqueidentifier  NULL,
    [CategoryGuide05] uniqueidentifier  NULL,
    [AgentGuide] uniqueidentifier  NULL,
    [CurrencyGuide] uniqueidentifier  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL068' AND xtype='U')
BEGIN
CREATE TABLE [TBL068] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [InDate] datetime  NOT NULL,
    [DoneIn] datetime  NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [AccountGuide] uniqueidentifier  NOT NULL,
    [ContraAccountGuide] uniqueidentifier  NULL,
    [CurrencyGuide] uniqueidentifier  NOT NULL,
    [Debit] float  NOT NULL,
    [Credit] float  NOT NULL,
    [DebitRate] float  NOT NULL,
    [CreditRate] float  NOT NULL,
    [Notes] nvarchar(255)  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL170' AND xtype='U')
BEGIN
CREATE TABLE [TBL170] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [TypeID] smallint  NOT NULL,
    [Text01] nvarchar(MAX)  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='JobVacancies' AND xtype='U')
BEGIN
CREATE TABLE [JobVacancies] (
    [VacancyID] int IDENTITY(1,1) NOT NULL,
    [ClientID] int  NULL,
    [RoleTitle] nvarchar(100)  NULL,
    [Shifts] nvarchar(200)  NULL,
    [Location] nvarchar(100)  NULL,
    [SalaryPackage] nvarchar(100)  NULL,
    [Transportation] nvarchar(50)  NULL,
    [Insurance] nvarchar(50)  NULL,
    [GenderPreference] nvarchar(50)  NULL,
    [MaxAge] int  NULL,
    [Status] nvarchar(50)  NULL,
    [CreatedAt] datetime  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Classrooms' AND xtype='U')
BEGIN
CREATE TABLE [Classrooms] (
    [RoomID] int IDENTITY(1,1) NOT NULL,
    [RoomName] nvarchar(50)  NOT NULL,
    [Capacity] int  NULL,
    [IsActive] bit  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL077' AND xtype='U')
BEGIN
CREATE TABLE [TBL077] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [GrouptID] uniqueidentifier  NOT NULL,
    [InvoiceID] uniqueidentifier  NOT NULL,
    [ItemsAccount] uniqueidentifier  NULL,
    [DiscountAccount] uniqueidentifier  NULL,
    [ExtraAccount] uniqueidentifier  NULL,
    [StoreAccount] uniqueidentifier  NULL,
    [CostAccount] uniqueidentifier  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL051' AND xtype='U')
BEGIN
CREATE TABLE [TBL051] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [FrmName] nvarchar(255)  NOT NULL,
    [DefaultCurrency] uniqueidentifier  NULL,
    [DefaultAccount] uniqueidentifier  NULL,
    [Notes] ntext  NULL,
    [Fields] ntext  NULL,
    [Bonds] ntext  NULL,
    [Bills] ntext  NULL,
    [Options1] ntext  NULL,
    [CardImage] image  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL020' AND xtype='U')
BEGIN
CREATE TABLE [TBL020] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [CardNumber] int  NOT NULL,
    [InvoiceName] nvarchar(255)  NOT NULL,
    [LatinName] nvarchar(255)  NULL,
    [Shortcut] nvarchar(255)  NULL,
    [CustomFormatForTotal] nvarchar(255)  NULL,
    [LatinShortcut] nvarchar(255)  NULL,
    [DiscountCaption] nvarchar(255)  NULL,
    [QtyCalculation] smallint  NOT NULL,
    [BillType] smallint  NOT NULL,
    [BillKind] smallint  NOT NULL,
    [PriceType] tinyint  NOT NULL,
    [PriceType2] tinyint  NOT NULL,
    [POSType] tinyint  NOT NULL,
    [TaxMethod] uniqueidentifier  NULL,
    [DefaultPayType] smallint  NOT NULL,
    [DefaultItemUnit] smallint  NOT NULL,
    [DefaultCommission] float  NOT NULL,
    [InstalmentBondGuide] uniqueidentifier  NULL,
    [RelatedBondType] uniqueidentifier  NULL,
    [PaymentsBondType] uniqueidentifier  NULL,
    [LocalAdministrativeTaxAccount] uniqueidentifier  NULL,
    [LocalAdministrativeTaxRatio] float  NOT NULL,
    [TaxRatio] float  NOT NULL,
    [WithoutItemTax] bit  NOT NULL,
    [InvoiceMovementSide] smallint  NOT NULL,
    [AgentAccountSide] smallint  NOT NULL,
    [Fields] ntext  NOT NULL,
    [Security] tinyint  NOT NULL,
    [ShowTotals] bit  NOT NULL,
    [SearchAgentOnNewBill] bit  NOT NULL,
    [OfficialInvoice] bit  NOT NULL,
    [BooleanOption1] bit  NOT NULL,
    [BooleanOption2] bit  NOT NULL,
    [BooleanOption3] bit  NOT NULL,
    [BooleanOption4] bit  NOT NULL,
    [BooleanOption5] bit  NOT NULL,
    [BooleanOption6] bit  NOT NULL,
    [BooleanOption7] bit  NOT NULL,
    [BooleanOption8] bit  NOT NULL,
    [BooleanOption9] bit  NOT NULL,
    [BooleanOption10] bit  NOT NULL,
    [BooleanOption11] bit  NOT NULL,
    [BooleanOption12] bit  NOT NULL,
    [BooleanOption13] bit  NOT NULL,
    [BooleanOption14] bit  NOT NULL,
    [BooleanOption15] bit  NOT NULL,
    [BooleanOption16] bit  NOT NULL,
    [BooleanOption17] bit  NOT NULL,
    [BooleanOption18] bit  NOT NULL,
    [BooleanOption19] bit  NOT NULL,
    [BooleanOption20] bit  NOT NULL,
    [BooleanOption21] bit  NOT NULL,
    [BooleanOption22] bit  NOT NULL,
    [BooleanOption23] bit  NOT NULL,
    [BooleanOption24] bit  NOT NULL,
    [BooleanOption25] bit  NOT NULL,
    [BooleanOption26] bit  NOT NULL,
    [BooleanOption27] bit  NOT NULL,
    [BooleanOption28] bit  NOT NULL,
    [BooleanOption29] bit  NOT NULL,
    [BooleanOption30] bit  NOT NULL,
    [BooleanOption31] bit  NOT NULL,
    [BooleanOption32] bit  NOT NULL,
    [BooleanOption33] bit  NOT NULL,
    [BooleanOption34] bit  NOT NULL,
    [BooleanOption35] bit  NOT NULL,
    [BooleanOption36] bit  NOT NULL,
    [BooleanOption37] bit  NOT NULL,
    [BooleanOption38] bit  NOT NULL,
    [BooleanOption39] bit  NOT NULL,
    [NotAffectCostActivity] bit  NOT NULL,
    [UsePointsSystem] bit  NOT NULL,
    [TotalIncludeTax] bit  NOT NULL,
    [NumberOption1] float  NOT NULL,
    [NumberOption2] float  NOT NULL,
    [NumberOption3] float  NOT NULL,
    [ExpiryDateRequired] bit  NOT NULL,
    [IntOption1] int  NOT NULL,
    [EntryType] tinyint  NOT NULL,
    [GenerateEntry] smallint  NOT NULL,
    [GenerateBill] uniqueidentifier  NULL,
    [SearchInCodes] bit  NOT NULL,
    [SingleSaveButton] bit  NOT NULL,
    [DoNotPostToStores] bit  NOT NULL,
    [ManualPostToStores] bit  NOT NULL,
    [AutoPrintWhenAdd] bit  NOT NULL,
    [AutoPrintWhenEdit] bit  NOT NULL,
    [ShowPreviewWhenAdd] bit  NOT NULL,
    [ShowPreviewWhenEdit] bit  NOT NULL,
    [AffectCostomerPrice] bit  NOT NULL,
    [PayTermIsButtons] bit  NOT NULL,
    [ShowPaidAndRest] bit  NOT NULL,
    [AffectLastPurchasePrice] bit  NOT NULL,
    [AlwaysDetailing] bit  NOT NULL,
    [ShowPrintingButtons] bit  NOT NULL,
    [AddCommissionToTotal] bit  NOT NULL,
    [SearchInEmptyProductsCards] bit  NOT NULL,
    [WithButtons] tinyint  NOT NULL,
    [StartMaxmized] bit  NOT NULL,
    [BillMethod] tinyint  NOT NULL,
    [TotalCanChangeQty] bit  NOT NULL,
    [ClearCostCenterOnNew] bit  NOT NULL,
    [NetTotalColor] int  NOT NULL,
    [CashBalanceColor] int  NOT NULL,
    [ColorValue1] int  NOT NULL,
    [Color1] int  NOT NULL,
    [Color2] int  NOT NULL,
    [CashAccount] uniqueidentifier  NULL,
    [BankAccount] uniqueidentifier  NULL,
    [MainBill] uniqueidentifier  NULL,
    [MainBill2] uniqueidentifier  NULL,
    [PostToBill] uniqueidentifier  NULL,
    [PostToBill2] uniqueidentifier  NULL,
    [BankProcuringCommissionAccount] uniqueidentifier  NULL,
    [PostPrintType] uniqueidentifier  NULL,
    [SavePrintType] uniqueidentifier  NULL,
    [DefaultPostPrintType] uniqueidentifier  NULL,
    [ProductsAccount] uniqueidentifier  NULL,
    [DiscountsAccount] uniqueidentifier  NULL,
    [SubjectToTaxAccount] uniqueidentifier  NULL,
    [ExtrasAccount] uniqueidentifier  NULL,
    [BonusAccount] uniqueidentifier  NULL,
    [AgentProfitAccount] uniqueidentifier  NULL,
    [DefaultStore] uniqueidentifier  NULL,
    [DefaultCostCenter] uniqueidentifier  NULL,
    [DefaultProject] uniqueidentifier  NULL,
    [DefaultBranch] uniqueidentifier  NULL,
    [DefaultCurrency] uniqueidentifier  NULL,
    [DefaultGroup] uniqueidentifier  NULL,
    [RecipientBill] uniqueidentifier  NULL,
    [AutoGenerateContraAccount] bit  NOT NULL,
    [ContinuousInventoryAdoption] bit  NOT NULL,
    [ContinuousInventoryPriceType] tinyint  NOT NULL,
    [ContinuousInventoryCostAccount] uniqueidentifier  NULL,
    [ContinuousInventoryStoreAccount] uniqueidentifier  NULL,
    [ContinuousInventoryGiftsAccount] uniqueidentifier  NULL,
    [Category01] uniqueidentifier  NULL,
    [Category02] uniqueidentifier  NULL,
    [Category03] uniqueidentifier  NULL,
    [Category04] uniqueidentifier  NULL,
    [Category05] uniqueidentifier  NULL,
    [OperationBill] uniqueidentifier  NULL,
    [CostCenterType] tinyint  NOT NULL,
    [CostCenterType2] tinyint  NOT NULL,
    [CostCenterType3] tinyint  NOT NULL,
    [CostCenterType4] tinyint  NOT NULL,
    [ProjectType] tinyint  NOT NULL,
    [ProjectType2] tinyint  NOT NULL,
    [ProjectType4] tinyint  NOT NULL,
    [BranchType] tinyint  NOT NULL,
    [BranchType2] tinyint  NOT NULL,
    [BranchType4] tinyint  NOT NULL,
    [CategoriesType] tinyint  NOT NULL,
    [CategoriesType2] tinyint  NOT NULL,
    [AgentType] tinyint  NOT NULL,
    [AgentType2] tinyint  NOT NULL,
    [AttachmentType] tinyint  NOT NULL,
    [TabOrder] ntext  NULL,
    [AgentsGroup] uniqueidentifier  NULL,
    [AgentsGroup2] uniqueidentifier  NULL,
    [AgentsGroup3] uniqueidentifier  NULL,
    [AgentsGroup4] uniqueidentifier  NULL,
    [AgentsGroup5] uniqueidentifier  NULL,
    [RoundAccount] uniqueidentifier  NULL,
    [FinancialTransactionsBond] uniqueidentifier  NULL,
    [BarcodeType] uniqueidentifier  NULL,
    [RoundValue] float  NOT NULL,
    [SearchInPatchCode] bit  NOT NULL,
    [TextValue01] nvarchar(255)  NULL,
    [TaxInvoiceNo] nvarchar(255)  NULL,
    [OutPrintType] uniqueidentifier  NULL,
    [BooleanOption40] bit  NOT NULL,
    [BooleanOption41] bit  NOT NULL,
    [BooleanOption42] bit  NOT NULL,
    [BooleanOption43] bit  NOT NULL,
    [RecipientPayType] smallint  NOT NULL,
    [BooleanOption44] bit  NOT NULL,
    [ItemTaxAccount] uniqueidentifier  NULL,
    [OrderBillKind] smallint  NOT NULL,
    [BooleanOption45] bit  NOT NULL,
    [BooleanOption46] bit  NOT NULL,
    [BooleanOption47] bit  NOT NULL,
    [ReserveWarehouse] uniqueidentifier  NULL,
    [ExportType] uniqueidentifier  NULL,
    [StartNumber] int  NOT NULL,
    [MainNumberBill] uniqueidentifier  NULL,
    [BooleanOption48] bit  NOT NULL,
    [RelatedFields] ntext  NULL,
    [BooleanOption49] bit  NOT NULL,
    [ProjectType3] tinyint  NOT NULL,
    [BranchType3] tinyint  NOT NULL,
    [DefaultVariableUnit] smallint  NOT NULL,
    [EnFields] nvarchar(MAX)  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL152' AND xtype='U')
BEGIN
CREATE TABLE [TBL152] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [MainGuide] uniqueidentifier  NULL,
    [TypeID] smallint  NOT NULL,
    [Text01] nvarchar(MAX)  NULL,
    [CardImage] image  NULL,
    [Att01] image  NULL,
    [Att02] image  NULL,
    [Category01] uniqueidentifier  NULL,
    [Category02] uniqueidentifier  NULL,
    [Category03] uniqueidentifier  NULL,
    [Category04] uniqueidentifier  NULL,
    [Category05] uniqueidentifier  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL084' AND xtype='U')
BEGIN
CREATE TABLE [TBL084] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [MainGuide] uniqueidentifier  NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [Security] tinyint  NOT NULL,
    [CardName] nvarchar(255)  NOT NULL,
    [LatinName] nvarchar(255)  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Courses' AND xtype='U')
BEGIN
CREATE TABLE [Courses] (
    [CourseID] int IDENTITY(1,1) NOT NULL,
    [CourseName] nvarchar(100)  NOT NULL,
    [LevelOrder] int  NULL,
    [DefaultPrice] decimal  NULL,
    [Description] nvarchar(MAX)  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL004' AND xtype='U')
BEGIN
CREATE TABLE [TBL004] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [NotActive] bit  NOT NULL,
    [ClosingAccount] uniqueidentifier  NOT NULL,
    [CardCode] nvarchar(255)  NOT NULL,
    [AccountName] nvarchar(255)  NOT NULL,
    [MainAccount] uniqueidentifier  NULL,
    [DefaultCurrency] uniqueidentifier  NULL,
    [DefaultCostCenter] uniqueidentifier  NULL,
    [DefaultBranch] uniqueidentifier  NULL,
    [DefaultProject] uniqueidentifier  NULL,
    [Item_ID] uniqueidentifier  NULL,
    [LatinName] nvarchar(255)  NULL,
    [TaxCode] nvarchar(255)  NULL,
    [Security] tinyint  NOT NULL,
    [MaxDebit] float  NOT NULL,
    [MaxCredit] float  NOT NULL,
    [NotepaperMaxDebit] float  NOT NULL,
    [NotepaperMaxCredit] float  NOT NULL,
    [Caution] smallint  NOT NULL,
    [BuiltIn] datetime  NOT NULL,
    [Notes] ntext  NULL,
    [CardImage] image  NULL,
    [CalculatingField] uniqueidentifier  NULL,
    [ByUser] uniqueidentifier  NULL,
    [ByGroup] uniqueidentifier  NULL,
    [budget1] float  NOT NULL,
    [budget2] float  NOT NULL,
    [DetailByCostCenter] bit  NOT NULL,
    [DetailByProject] bit  NOT NULL,
    [DetailByBranch] bit  NOT NULL,
    [DetailByCurrency] bit  NOT NULL,
    [DetailByAgent] bit  NOT NULL,
    [DetailByCategory1] bit  NOT NULL,
    [DetailByCategory2] bit  NOT NULL,
    [DetailByCategory3] bit  NOT NULL,
    [DetailByCategory4] bit  NOT NULL,
    [DetailByCategory5] bit  NOT NULL,
    [DetailByContraAccount] bit  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL111' AND xtype='U')
BEGIN
CREATE TABLE [TBL111] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [ItemField] nvarchar(255)  NOT NULL,
    [FieldName] nvarchar(255)  NULL,
    [StartIndex] int  NOT NULL,
    [CodeLength] int  NOT NULL,
    [TypeGuide] uniqueidentifier  NULL,
    [Notes] nvarchar(255)  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL052' AND xtype='U')
BEGIN
CREATE TABLE [TBL052] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [FormKey] nvarchar(255)  NOT NULL,
    [ControlKey] nvarchar(255)  NOT NULL,
    [Property] nvarchar(255)  NOT NULL,
    [ForUser] uniqueidentifier  NULL,
    [Value1] ntext  NULL,
    [Value2] ntext  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL153' AND xtype='U')
BEGIN
CREATE TABLE [TBL153] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [MainGuide] uniqueidentifier  NULL,
    [TypeID] smallint  NOT NULL,
    [Text01] nvarchar(MAX)  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='PipelineStages' AND xtype='U')
BEGIN
CREATE TABLE [PipelineStages] (
    [StageID] int IDENTITY(1,1) NOT NULL,
    [CandidateID] int  NULL,
    [VacancyID] int  NULL,
    [ScreeningStatus] nvarchar(50)  NULL,
    [ScreeningNotes] nvarchar(MAX)  NULL,
    [TAStatus] nvarchar(50)  NULL,
    [TAScore_CEFR] nvarchar(10)  NULL,
    [TA_Recommendation] nvarchar(MAX)  NULL,
    [SubmissionStatus] nvarchar(50)  NULL,
    [SubmissionDate] datetime  NULL,
    [ValidationStartDate] date  NULL,
    [ValidationEndDate] date  NULL,
    [ValidationOutcome] nvarchar(50)  NULL,
    [UpdatedAt] datetime  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='company_data' AND xtype='U')
BEGIN
CREATE TABLE [company_data] (
    [ReceveInvID] int IDENTITY(1,1) NOT NULL,
    [Company_ID] int  NOT NULL,
    [taxpayerActivityCode] nvarchar(10)  NULL,
    [Issuer_ID] nvarchar(20)  NULL,
    [Issuer_Type] nvarchar(3)  NULL,
    [Issuer_Name] nvarchar(100)  NULL,
    [Issuer_Address_branchID] nvarchar(20)  NULL,
    [Issuer_Address_country] nvarchar(5)  NULL,
    [Issuer_Address_governate] nvarchar(20)  NULL,
    [Issuer_Address_regionCity] nvarchar(30)  NULL,
    [Issuer_Address_street] nvarchar(255)  NULL,
    [Issuer_Address_buildingNumber] nvarchar(10)  NULL,
    [Issuer_Address_postalCode] nvarchar(10)  NULL,
    [Issuer_Address_floor] nvarchar(20)  NULL,
    [Issuer_Address_room] nvarchar(20)  NULL,
    [Issuer_ClintID] nvarchar(255)  NULL,
    [Issuer_ClintSecret_1] nvarchar(255)  NULL,
    [Issuer_ClintSecret_2] nvarchar(255)  NULL,
    [Issuer_Pre_ClintID] nvarchar(255)  NULL,
    [Issuer_Pre_ClintSecret_1] nvarchar(255)  NULL,
    [Issuer_Pre_ClintSecret_2] nvarchar(255)  NULL,
    [Issuer_PinCode] nvarchar(20)  NULL,
    [Issuer_TokenType] nvarchar(100)  NULL,
    [DocumentTypeVersion] nvarchar(5)  NULL,
    [EnvironmentProd] bit  NULL,
    [ERP_Type] nvarchar(50)  NULL,
    [ERPConnection] nvarchar(MAX)  NULL,
    [ERPSqlString] nvarchar(MAX)  NULL,
    [InvoiceTemplate] nvarchar(50)  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='CourseBatches' AND xtype='U')
BEGIN
CREATE TABLE [CourseBatches] (
    [BatchID] int IDENTITY(1,1) NOT NULL,
    [CourseID] int  NULL,
    [TrainerID] int  NULL,
    [RoomID] int  NULL,
    [BatchName] nvarchar(100)  NULL,
    [StartDate] date  NULL,
    [EndDate] date  NULL,
    [ScheduleDescription] nvarchar(200)  NULL,
    [Status] nvarchar(50)  NULL,
    [CreatedAt] datetime  NULL,
    [HeadTrainerID] int  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL085' AND xtype='U')
BEGIN
CREATE TABLE [TBL085] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [TypeGuide] uniqueidentifier  NOT NULL,
    [CardDate] datetime  NULL,
    [CardDate2] datetime  NULL,
    [DateValue01] datetime  NULL,
    [RelatedArchive] uniqueidentifier  NULL,
    [RelatedArchive2] uniqueidentifier  NULL,
    [RelatedCostCenter] uniqueidentifier  NULL,
    [Security] tinyint  NOT NULL,
    [CardNumber] int  NOT NULL,
    [NumberValue01] float  NOT NULL,
    [IntValue01] int  NOT NULL,
    [IntValue02] int  NOT NULL,
    [IntValue03] int  NOT NULL,
    [TextValue01] nvarchar(MAX)  NULL,
    [TextValue02] nvarchar(MAX)  NULL,
    [TextValue03] nvarchar(MAX)  NULL,
    [Project] uniqueidentifier  NULL,
    [Branch] uniqueidentifier  NULL,
    [CostCenter] uniqueidentifier  NULL,
    [Store] uniqueidentifier  NULL,
    [UserGuide] uniqueidentifier  NULL,
    [BooleanValue01] bit  NOT NULL,
    [BooleanValue02] bit  NOT NULL,
    [BooleanValue03] bit  NOT NULL,
    [BooleanValue04] bit  NOT NULL,
    [BooleanValue05] bit  NOT NULL,
    [BooleanValue06] bit  NOT NULL,
    [BooleanValue07] bit  NOT NULL,
    [BooleanValue08] bit  NOT NULL,
    [CardName] nvarchar(MAX)  NULL,
    [Notes] nvarchar(MAX)  NULL,
    [CardImage] image  NULL,
    [ByUser] uniqueidentifier  NULL,
    [ByGroup] uniqueidentifier  NULL,
    [ReceveInvID] nvarchar(MAX)  NULL,
    [Company_ID] nvarchar(MAX)  NULL,
    [taxpayerActivityCode] nvarchar(MAX)  NULL,
    [Issuer_ID] nvarchar(MAX)  NULL,
    [Issuer_Type] nvarchar(MAX)  NULL,
    [Issuer_Name] nvarchar(MAX)  NULL,
    [Issuer_Address_branchID] nvarchar(MAX)  NULL,
    [Issuer_Address_country] nvarchar(MAX)  NULL,
    [Issuer_Address_governate] nvarchar(MAX)  NULL,
    [Issuer_Address_regionCity] nvarchar(MAX)  NULL,
    [Issuer_Address_street] nvarchar(MAX)  NULL,
    [Issuer_Address_buildingNumber] nvarchar(MAX)  NULL,
    [Issuer_Address_postalCode] nvarchar(MAX)  NULL,
    [Issuer_Address_floor] nvarchar(MAX)  NULL,
    [Issuer_Address_room] nvarchar(MAX)  NULL,
    [Issuer_ClintID] nvarchar(MAX)  NULL,
    [Issuer_ClintSecret_1] nvarchar(MAX)  NULL,
    [Issuer_ClintSecret_2] nvarchar(MAX)  NULL,
    [Issuer_Pre_ClintID] nvarchar(MAX)  NULL,
    [Issuer_Pre_ClintSecret_1] nvarchar(MAX)  NULL,
    [Issuer_Pre_ClintSecret_2] nvarchar(MAX)  NULL,
    [Issuer_PinCode] nvarchar(MAX)  NULL,
    [Issuer_TokenType] nvarchar(MAX)  NULL,
    [DocumentTypeVersion] nvarchar(MAX)  NULL,
    [EnvironmentProd] nvarchar(MAX)  NULL,
    [ERP_Type] nvarchar(MAX)  NULL,
    [ERPConnection] nvarchar(MAX)  NULL,
    [ERPSqlString] nvarchar(MAX)  NULL,
    [InvoiceTemplate] nvarchar(MAX)  NULL,
    [Invoice_style] uniqueidentifier  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL008' AND xtype='U')
BEGIN
CREATE TABLE [TBL008] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [CardCode] nvarchar(255)  NOT NULL,
    [Security] tinyint  NOT NULL,
    [WarehouseName] nvarchar(255)  NOT NULL,
    [LatinName] nvarchar(255)  NULL,
    [MainWarehouse] uniqueidentifier  NULL,
    [TradingClosing] uniqueidentifier  NULL,
    [BalanceSheetClosing] uniqueidentifier  NULL,
    [Notes] ntext  NULL,
    [CardImage] image  NULL,
    [ByUser] uniqueidentifier  NULL,
    [ByGroup] uniqueidentifier  NULL,
    [NotActive] bit  NOT NULL,
    [AccountGuide] uniqueidentifier  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL123' AND xtype='U')
BEGIN
CREATE TABLE [TBL123] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [RowGuide] uniqueidentifier  NOT NULL,
    [MainID] int  NULL,
    [AccountID] uniqueidentifier  NULL,
    [StoreID] uniqueidentifier  NULL,
    [CostCenterID] uniqueidentifier  NULL,
    [ProjectID] uniqueidentifier  NULL,
    [BranchID] uniqueidentifier  NULL,
    [KeyValue01] uniqueidentifier  NULL,
    [KeyValue02] uniqueidentifier  NULL,
    [RecordType] int  NOT NULL,
    [TypeID] int  NOT NULL,
    [IntValue01] int  NOT NULL,
    [IntValue02] int  NOT NULL,
    [NumberValue01] float  NOT NULL,
    [NumberValue02] float  NOT NULL,
    [TextValue01] nvarchar(MAX)  NULL,
    [TextValue02] nvarchar(MAX)  NULL,
    [TextValue03] nvarchar(MAX)  NULL,
    [TextValue04] nvarchar(MAX)  NULL,
    [TextValue05] nvarchar(MAX)  NULL,
    [BitValue01] bit  NOT NULL,
    [BitValue02] bit  NOT NULL,
    [BitValue03] bit  NOT NULL,
    [BitValue04] bit  NOT NULL,
    [DateValue01] datetime  NULL,
    [DateValue02] datetime  NULL,
    [LongText01] ntext  NULL,
    [LongText02] ntext  NULL,
    [LongText03] ntext  NULL,
    [LongText04] ntext  NULL,
    [ContraAccountID] uniqueidentifier  NULL,
    [BitValue05] bit  NOT NULL,
    [BitValue06] bit  NOT NULL,
    [BitValue07] bit  NOT NULL,
    [Image01] image  NULL,
    [BitValue08] bit  NOT NULL,
    [Notes] nvarchar(255)  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL078' AND xtype='U')
BEGIN
CREATE TABLE [TBL078] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [CardCode] nvarchar(255)  NULL,
    [CardNumber] int  NOT NULL,
    [CardDate] datetime  NULL,
    [CurrencyGuide] uniqueidentifier  NOT NULL,
    [MainGuide] uniqueidentifier  NULL,
    [Rate] float  NOT NULL,
    [Security] tinyint  NOT NULL,
    [CardStatus] tinyint  NOT NULL,
    [ClassificationCard] bit  NOT NULL,
    [CardName] nvarchar(255)  NOT NULL,
    [LatinName] nvarchar(255)  NULL,
    [Notes] ntext  NULL,
    [CardImage] image  NULL,
    [CostCenter] uniqueidentifier  NULL,
    [Project] uniqueidentifier  NULL,
    [Branch] uniqueidentifier  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL053' AND xtype='U')
BEGIN
CREATE TABLE [TBL053] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [OptionName] nvarchar(255)  NOT NULL,
    [ValueKey] uniqueidentifier  NULL,
    [ValueKey2] uniqueidentifier  NULL,
    [ForUser] uniqueidentifier  NULL,
    [ValueString] nvarchar(512)  NULL,
    [ValueString2] nvarchar(512)  NULL,
    [Value] float  NOT NULL,
    [Value2] float  NOT NULL,
    [ValueBoolean] bit  NOT NULL,
    [ValueBoolean2] bit  NOT NULL,
    [ValueBoolean3] bit  NOT NULL,
    [ByteValue] smallint  NOT NULL,
    [DateValue] datetime  NULL,
    [DateValue2] datetime  NULL,
    [ValueText] ntext  NULL,
    [ValueText2] ntext  NULL,
    [Value3] float  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL154' AND xtype='U')
BEGIN
CREATE TABLE [TBL154] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [MainGuide] uniqueidentifier  NULL,
    [TypeID] smallint  NOT NULL,
    [RangeValue] float  NOT NULL,
    [CommissionRatio] float  NOT NULL,
    [CommissionValue] float  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL112' AND xtype='U')
BEGIN
CREATE TABLE [TBL112] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [CardName] nvarchar(255)  NOT NULL,
    [FormName] nvarchar(255)  NOT NULL,
    [Category] nvarchar(255)  NULL,
    [Notes] nvarchar(255)  NULL,
    [MainGuide] uniqueidentifier  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL069' AND xtype='U')
BEGIN
CREATE TABLE [TBL069] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [SortID] int  NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [Accessory] nvarchar(255)  NOT NULL,
    [Price] float  NOT NULL,
    [Notes] nvarchar(255)  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL113' AND xtype='U')
BEGIN
CREATE TABLE [TBL113] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [MainGuide] uniqueidentifier  NULL,
    [MainID] int  NULL,
    [ControlName] nvarchar(255)  NOT NULL,
    [TextValue] nvarchar(255)  NOT NULL,
    [TextValue02] nvarchar(255)  NULL,
    [NumberValue] float  NULL,
    [NumberValue02] float  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL136' AND xtype='U')
BEGIN
CREATE TABLE [TBL136] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [CardDate] datetime  NOT NULL,
    [CardNumber] int  NOT NULL,
    [Security] tinyint  NOT NULL,
    [Notes] nvarchar(255)  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Enrollments' AND xtype='U')
BEGIN
CREATE TABLE [Enrollments] (
    [EnrollmentID] int IDENTITY(1,1) NOT NULL,
    [BatchID] int  NULL,
    [CandidateID] int  NULL,
    [EnrollmentDate] datetime  NULL,
    [Status] nvarchar(50)  NULL,
    [FinalGrade] decimal  NULL,
    [Notes] nvarchar(MAX)  NULL,
    [AgreedPrice] decimal  NULL,
    [OfferID] int  NULL,
    [ExitInterviewStatus] nvarchar(50)  NULL,
    [ExitInterviewOutcome] nvarchar(MAX)  NULL,
    [CompletionDate] datetime  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL097' AND xtype='U')
BEGIN
CREATE TABLE [TBL097] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [GroupGuide] uniqueidentifier  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL171' AND xtype='U')
BEGIN
CREATE TABLE [TBL171] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [TypeID] smallint  NOT NULL,
    [ItemGuide] uniqueidentifier  NULL,
    [Quantity] float  NOT NULL,
    [Unit] smallint  NOT NULL,
    [RelatedUnit] uniqueidentifier  NULL,
    [UnitQuantity] float  NOT NULL,
    [Number01] float  NOT NULL,
    [Number02] float  NOT NULL,
    [Number03] float  NOT NULL,
    [ManufacturerModel] uniqueidentifier  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL155' AND xtype='U')
BEGIN
CREATE TABLE [TBL155] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [ControlName] nvarchar(MAX)  NOT NULL,
    [FormName] nvarchar(MAX)  NOT NULL,
    [TypeID] smallint  NOT NULL,
    [TabIndex] int  NOT NULL,
    [ShortcutKey] int  NOT NULL,
    [TabStop] bit  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL009' AND xtype='U')
BEGIN
CREATE TABLE [TBL009] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [CardNumber] int  NOT NULL,
    [EntryName] nvarchar(255)  NOT NULL,
    [EntryLatinName] nvarchar(255)  NULL,
    [UseTerms] tinyint  NOT NULL,
    [EntryType] tinyint  NOT NULL,
    [EntryType2] tinyint  NOT NULL,
    [CostCenterType] tinyint  NOT NULL,
    [CostCenterType2] tinyint  NOT NULL,
    [CostCenterType3] tinyint  NOT NULL,
    [ProjectType] tinyint  NOT NULL,
    [ProjectType2] tinyint  NOT NULL,
    [ProjectType3] tinyint  NOT NULL,
    [BranchType] tinyint  NOT NULL,
    [BranchType2] tinyint  NOT NULL,
    [BranchType3] tinyint  NOT NULL,
    [CategoriesType] tinyint  NOT NULL,
    [CategoriesType2] tinyint  NOT NULL,
    [CategoriesType3] tinyint  NOT NULL,
    [AgentType] tinyint  NOT NULL,
    [AgentType2] tinyint  NOT NULL,
    [AgentType3] tinyint  NOT NULL,
    [DetailSearchBy] ntext  NULL,
    [DoNotGenerateEntry] bit  NOT NULL,
    [IsPayment] tinyint  NOT NULL,
    [CurrencyUnChangeable] bit  NOT NULL,
    [BooleanOption1] tinyint  NOT NULL,
    [BooleanOption2] tinyint  NOT NULL,
    [BooleanOption3] tinyint  NOT NULL,
    [BooleanOption4] tinyint  NOT NULL,
    [BooleanOption5] tinyint  NOT NULL,
    [BooleanOption6] tinyint  NOT NULL,
    [BooleanOption7] tinyint  NOT NULL,
    [BooleanOption8] tinyint  NOT NULL,
    [BooleanOption9] tinyint  NOT NULL,
    [BooleanOption10] tinyint  NOT NULL,
    [BooleanOption11] tinyint  NOT NULL,
    [BooleanOption12] tinyint  NOT NULL,
    [DoNotPostToAccounts] bit  NOT NULL,
    [DoNotGenerateEntryOnCollect] bit  NOT NULL,
    [UseSameAccountForCollect] bit  NOT NULL,
    [SingleAccounts] bit  NOT NULL,
    [BuiltTowEntries] bit  NOT NULL,
    [AffectContraAccountInEntry] bit  NOT NULL,
    [ReverseCollectEntry] bit  NOT NULL,
    [Fields] ntext  NULL,
    [BondType] int  NOT NULL,
    [EntryMode] int  NOT NULL,
    [DefaultValue] float  NOT NULL,
    [CardMode] tinyint  NOT NULL,
    [DefaultCurrency] uniqueidentifier  NULL,
    [CollectAccount] uniqueidentifier  NULL,
    [RelatedBondType] uniqueidentifier  NULL,
    [DefaultCostCenter] uniqueidentifier  NULL,
    [DefaultProject] uniqueidentifier  NULL,
    [DefaultBranch] uniqueidentifier  NULL,
    [IntermediateAccount] uniqueidentifier  NULL,
    [TruncateAccount] uniqueidentifier  NULL,
    [ReturnAccount] uniqueidentifier  NULL,
    [DebitName] nvarchar(255)  NULL,
    [CreditName] nvarchar(255)  NULL,
    [ShortcutName] nvarchar(255)  NULL,
    [LatinShortcutName] nvarchar(255)  NULL,
    [Text01] nvarchar(255)  NULL,
    [Text02] nvarchar(255)  NULL,
    [Notes] ntext  NULL,
    [TwoCurrencies] bit  NOT NULL,
    [SaveImageAsLocation] bit  NOT NULL,
    [DefaultAccount] uniqueidentifier  NULL,
    [FinancialTransactionsBond] uniqueidentifier  NULL,
    [AutoGenerateContraAccount] bit  NOT NULL,
    [Category01] uniqueidentifier  NULL,
    [Category02] uniqueidentifier  NULL,
    [Category03] uniqueidentifier  NULL,
    [Category04] uniqueidentifier  NULL,
    [Category05] uniqueidentifier  NULL,
    [DefaultPrintType] uniqueidentifier  NULL,
    [BankProcuringCommissionAccount] uniqueidentifier  NULL,
    [AttachmentType] tinyint  NOT NULL,
    [BooleanOption13] tinyint  NOT NULL,
    [BooleanOption14] tinyint  NOT NULL,
    [BooleanOption15] tinyint  NOT NULL,
    [BooleanOption16] tinyint  NOT NULL,
    [BooleanOption17] tinyint  NOT NULL,
    [ContraAccountType2] tinyint  NOT NULL,
    [ContraAccountType3] tinyint  NOT NULL,
    [TaxAccount] uniqueidentifier  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL070' AND xtype='U')
BEGIN
CREATE TABLE [TBL070] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [GroupGuide] uniqueidentifier  NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [HideRecord] bit  NOT NULL,
    [CardValue] float  NOT NULL,
    [BrowsingPosted] tinyint  NOT NULL,
    [InsertingPosted] tinyint  NOT NULL,
    [UpdatingPosted] tinyint  NOT NULL,
    [DeletingPosted] tinyint  NOT NULL,
    [PrintingPosted] tinyint  NOT NULL,
    [BuildEntryPosted] tinyint  NOT NULL,
    [ChangePricesPosted] tinyint  NOT NULL,
    [PostedExtraRatio] float  NOT NULL,
    [PostedDiscountRatio] float  NOT NULL,
    [PostedBillExtraRatio] float  NOT NULL,
    [PostedBillDiscountRatio] float  NOT NULL,
    [Posting] tinyint  NOT NULL,
    [BrowsePrices] tinyint  NOT NULL,
    [BrowsingUnPosted] tinyint  NOT NULL,
    [InsertingUnPosted] tinyint  NOT NULL,
    [UpdatingUnPosted] tinyint  NOT NULL,
    [DeletingUnPosted] tinyint  NOT NULL,
    [PrintingUnPosted] tinyint  NOT NULL,
    [PrintingUnSaved] tinyint  NOT NULL,
    [BuildEntryUnPosted] tinyint  NOT NULL,
    [UnPostedExtraRatio] float  NOT NULL,
    [UnPostedDiscountRatio] float  NOT NULL,
    [UnPostedBillExtraRatio] float  NOT NULL,
    [UnPostedBillDiscountRatio] float  NOT NULL,
    [ChangePricesUnPosted] tinyint  NOT NULL,
    [ChangeStockItemsPrice] tinyint  NOT NULL,
    [ChangeServiceItemsPrice] tinyint  NOT NULL,
    [CloseCashBox] bit  NOT NULL,
    [PayExpense] bit  NOT NULL,
    [SubtractOutput] bit  NOT NULL,
    [EditPostedItems] tinyint  NOT NULL,
    [EditUnPostedItems] tinyint  NOT NULL,
    [BrowsingPosted2] tinyint  NOT NULL,
    [InsertingPosted2] tinyint  NOT NULL,
    [UpdatingPosted2] tinyint  NOT NULL,
    [DeletingPosted2] tinyint  NOT NULL,
    [PrintingPosted2] tinyint  NOT NULL,
    [BuildEntryPosted2] tinyint  NOT NULL,
    [ChangePricesPosted2] tinyint  NOT NULL,
    [PostedExtraRatio2] float  NOT NULL,
    [PostedDiscountRatio2] float  NOT NULL,
    [BrowsingUnPosted2] tinyint  NOT NULL,
    [InsertingUnPosted2] tinyint  NOT NULL,
    [UpdatingUnPosted2] tinyint  NOT NULL,
    [DeletingUnPosted2] tinyint  NOT NULL,
    [PrintingUnPosted2] tinyint  NOT NULL,
    [PrintingUnSaved2] tinyint  NOT NULL,
    [BuildEntryUnPosted2] tinyint  NOT NULL,
    [UnPostedExtraRatio2] float  NOT NULL,
    [UnPostedDiscountRatio2] float  NOT NULL,
    [ChangePricesUnPosted2] tinyint  NOT NULL,
    [ChangeStockItemsPrice2] tinyint  NOT NULL,
    [ChangeServiceItemsPrice2] tinyint  NOT NULL,
    [ModifyForOthers] tinyint  NOT NULL,
    [ModelPrint] tinyint  NOT NULL,
    [ModelDelete] tinyint  NOT NULL,
    [ModelAdd] tinyint  NOT NULL,
    [ModelUpdate] tinyint  NOT NULL,
    [UnlimitedExtrasPosted] bit  NOT NULL,
    [UnlimitedExtrasUnPosted] bit  NOT NULL,
    [ProductsAccount] uniqueidentifier  NULL,
    [StoreGuide] uniqueidentifier  NULL,
    [CashAccount] uniqueidentifier  NULL,
    [DefaultCostCenter] uniqueidentifier  NULL,
    [DefaultProject] uniqueidentifier  NULL,
    [DefaultBranch] uniqueidentifier  NULL,
    [ChangeCardNumber] bit  NOT NULL,
    [MinimumPrice] tinyint  NOT NULL,
    [MaximumPrice] tinyint  NOT NULL,
    [PayMethod1] bit  NOT NULL,
    [PayMethod2] bit  NOT NULL,
    [PayMethod3] bit  NOT NULL,
    [PayMethod4] bit  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL114' AND xtype='U')
BEGIN
CREATE TABLE [TBL114] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [MainGuide] uniqueidentifier  NULL,
    [RelatedAgent] uniqueidentifier  NULL,
    [MainGuide2] uniqueidentifier  NULL,
    [RelatedCard] uniqueidentifier  NULL,
    [MainID] int  NULL,
    [Notes] nvarchar(255)  NULL,
    [TextValue01] nvarchar(255)  NULL,
    [TextValue02] nvarchar(255)  NULL,
    [TextValue03] nvarchar(255)  NULL,
    [TextValue04] nvarchar(255)  NULL,
    [TextValue05] nvarchar(255)  NULL,
    [CostCenter] uniqueidentifier  NULL,
    [TypeID] int  NOT NULL,
    [IntValue01] int  NOT NULL,
    [IntValue02] int  NOT NULL,
    [IntValue03] int  NOT NULL,
    [NumberValue01] float  NULL,
    [NumberValue02] float  NULL,
    [NumberValue03] float  NULL,
    [NumberValue04] float  NULL,
    [NumberValue05] float  NULL,
    [Category01] uniqueidentifier  NULL,
    [Category02] uniqueidentifier  NULL,
    [Category03] uniqueidentifier  NULL,
    [Category04] uniqueidentifier  NULL,
    [Category05] uniqueidentifier  NULL,
    [AccountGuide] uniqueidentifier  NULL,
    [CurrencyGuide] uniqueidentifier  NULL,
    [BitValue01] bit  NOT NULL,
    [BitValue02] bit  NOT NULL,
    [DateValue01] datetime  NULL,
    [DateValue02] datetime  NULL,
    [DateValue03] datetime  NULL,
    [DateValue04] datetime  NULL,
    [LongText01] ntext  NULL,
    [LongText02] ntext  NULL,
    [LongText03] ntext  NULL,
    [CardImage] image  NULL,
    [Attachment] image  NULL,
    [Project] uniqueidentifier  NULL,
    [Branch] uniqueidentifier  NULL,
    [LongText04] ntext  NULL,
    [BitValue03] int  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL054' AND xtype='U')
BEGIN
CREATE TABLE [TBL054] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [CurrencyGuide] uniqueidentifier  NULL,
    [AccountGuide] uniqueidentifier  NULL,
    [CreditCardGuide] uniqueidentifier  NULL,
    [InDate] datetime  NULL,
    [Value] float  NOT NULL,
    [ValueRate] float  NOT NULL,
    [Notes] nvarchar(255)  NULL,
    [AgentGuide] uniqueidentifier  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL043' AND xtype='U')
BEGIN
CREATE TABLE [TBL043] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] nvarchar(255)  NOT NULL,
    [CardTerm] nvarchar(255)  NOT NULL,
    [ObjectID] tinyint  NOT NULL,
    [TypeID] tinyint  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='PlacementTests' AND xtype='U')
BEGIN
CREATE TABLE [PlacementTests] (
    [TestID] int IDENTITY(1,1) NOT NULL,
    [CandidateID] int  NULL,
    [TestDate] datetime  NULL,
    [TestType] nvarchar(50)  NULL,
    [AssignedAssessorID] int  NULL,
    [Status] nvarchar(50)  NULL,
    [ResultLevel] nvarchar(50)  NULL,
    [Feedback] nvarchar(MAX)  NULL,
    [CreatedAt] datetime  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL098' AND xtype='U')
BEGIN
CREATE TABLE [TBL098] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [CardDate] datetime  NOT NULL,
    [CardNumber] int  NOT NULL,
    [Security] tinyint  NOT NULL,
    [AttendanceGuide] uniqueidentifier  NULL,
    [ShiftGuide] uniqueidentifier  NULL,
    [Category01] uniqueidentifier  NULL,
    [Category02] uniqueidentifier  NULL,
    [Category03] uniqueidentifier  NULL,
    [Category04] uniqueidentifier  NULL,
    [Category05] uniqueidentifier  NULL,
    [Notes] nvarchar(255)  NULL,
    [TextValue01] nvarchar(255)  NULL,
    [TextValue02] nvarchar(255)  NULL,
    [CostCenter] uniqueidentifier  NULL,
    [Project] uniqueidentifier  NULL,
    [Branch] uniqueidentifier  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL079' AND xtype='U')
BEGIN
CREATE TABLE [TBL079] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [IsInPut] bit  NOT NULL,
    [ProductGuide] uniqueidentifier  NOT NULL,
    [Quantity] float  NOT NULL,
    [TotalValue] float  NOT NULL,
    [Unit] tinyint  NOT NULL,
    [CostCenter] uniqueidentifier  NULL,
    [RelatedMethod] uniqueidentifier  NULL,
    [Length] float  NOT NULL,
    [Width] float  NOT NULL,
    [Hieght] float  NOT NULL,
    [RelatedUnit] uniqueidentifier  NULL,
    [UnitQuantity] float  NOT NULL,
    [Weight] float  NOT NULL,
    [Value] float  NOT NULL,
    [Description] ntext  NULL,
    [Notes] nvarchar(255)  NULL,
    [BillCustom1] nvarchar(255)  NULL,
    [BillCustom2] nvarchar(255)  NULL,
    [BillCustom3] nvarchar(255)  NULL,
    [BillCustom4] nvarchar(255)  NULL,
    [BillCustom5] nvarchar(255)  NULL,
    [Category01] uniqueidentifier  NULL,
    [Category02] uniqueidentifier  NULL,
    [Category03] uniqueidentifier  NULL,
    [Category04] uniqueidentifier  NULL,
    [Category05] uniqueidentifier  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='InvoiceStatus' AND xtype='U')
BEGIN
CREATE TABLE [InvoiceStatus] (
    [id] int  NOT NULL,
    [InvInternalID] nvarchar(255)  NULL,
    [InvStatusCode] nvarchar(50)  NULL,
    [InvStatus] nvarchar(50)  NULL,
    [InvDate] datetime  NULL,
    [TransDate] datetime  NULL,
    [SubmissionID] nvarchar(255)  NULL,
    [InvUuid] nvarchar(255)  NULL,
    [longId] nvarchar(255)  NULL,
    [Environment] nvarchar(50)  NULL,
    [HashKey] nvarchar(255)  NULL,
    [ErrorCode] nvarchar(255)  NULL,
    [ErroeMessage] nvarchar(255)  NULL,
    [ErrorTarget] nvarchar(255)  NULL,
    [ErrorDetailsMessage] nvarchar(MAX)  NULL,
    [ErrorDetailsTarget] nvarchar(255)  NULL,
    [ProperityPath] nvarchar(255)  NULL,
    [CreatedDate] datetime  NULL,
    [ModifiedDate] datetime  NULL,
    [CompanyID] int  NULL,
    [IsReturn] bit  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='StudentPayments' AND xtype='U')
BEGIN
CREATE TABLE [StudentPayments] (
    [PaymentID] int IDENTITY(1,1) NOT NULL,
    [EnrollmentID] int  NULL,
    [Amount] decimal  NOT NULL,
    [PaymentDate] datetime  NULL,
    [ReceivedBy] int  NULL,
    [Notes] nvarchar(200)  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL005' AND xtype='U')
BEGIN
CREATE TABLE [TBL005] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [NotActive] bit  NOT NULL,
    [CardCode] nvarchar(255)  NOT NULL,
    [Security] tinyint  NOT NULL,
    [CostCenter] nvarchar(255)  NOT NULL,
    [LatinName] nvarchar(255)  NULL,
    [CardType] tinyint  NOT NULL,
    [DefaultAccount] uniqueidentifier  NULL,
    [DefaultAccount2] uniqueidentifier  NULL,
    [DefaultAccount3] uniqueidentifier  NULL,
    [MainCostCenter] uniqueidentifier  NULL,
    [DefaultValue] float  NULL,
    [IntValue] int  NOT NULL,
    [Notes] ntext  NULL,
    [CardImage] image  NULL,
    [CostCenterNotes2] nvarchar(255)  NULL,
    [CostCenterNotes3] nvarchar(255)  NULL,
    [CostCenterNotes4] nvarchar(255)  NULL,
    [CostCenterNotes5] nvarchar(255)  NULL,
    [CostCenterNotes6] nvarchar(255)  NULL,
    [CostCenterNotes7] nvarchar(255)  NULL,
    [CostCenterNotes8] nvarchar(255)  NULL,
    [CostCenterNotes9] nvarchar(255)  NULL,
    [UsedInHR] bit  NOT NULL,
    [ByUser] uniqueidentifier  NULL,
    [ByGroup] uniqueidentifier  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL156' AND xtype='U')
BEGIN
CREATE TABLE [TBL156] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [CardNumber] int  NOT NULL,
    [CardName] nvarchar(255)  NOT NULL,
    [LatinName] nvarchar(255)  NULL,
    [Security] tinyint  NOT NULL,
    [TypeID] smallint  NOT NULL,
    [CardType] smallint  NOT NULL,
    [Notes] ntext  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL137' AND xtype='U')
BEGIN
CREATE TABLE [TBL137] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [RecordGuide] uniqueidentifier  NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [AgentGuide] uniqueidentifier  NOT NULL,
    [PLogIn] datetime  NULL,
    [PLogOut] datetime  NULL,
    [CLogIn] datetime  NULL,
    [CLogOut] datetime  NULL,
    [TimeoutInWork01] datetime  NULL,
    [TimeinInWork01] datetime  NULL,
    [TimeoutInWork02] datetime  NULL,
    [TimeinInWork02] datetime  NULL,
    [TimeoutInWork03] datetime  NULL,
    [TimeinInWork03] datetime  NULL,
    [TimeoutInWork04] datetime  NULL,
    [TimeinInWork04] datetime  NULL,
    [TimeoutInWork05] datetime  NULL,
    [TimeinInWork05] datetime  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL164' AND xtype='U')
BEGIN
CREATE TABLE [TBL164] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [CardName] nvarchar(255)  NOT NULL,
    [LatinName] nvarchar(255)  NULL,
    [MainGuide] uniqueidentifier  NULL,
    [Notes] ntext  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL021' AND xtype='U')
BEGIN
CREATE TABLE [TBL021] (
    [ID] int  NOT NULL,
    [TimeTerm] nvarchar(255)  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL044' AND xtype='U')
BEGIN
CREATE TABLE [TBL044] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [GroupGuide] uniqueidentifier  NOT NULL,
    [CardGuide] nvarchar(255)  NOT NULL,
    [CardValue] float  NOT NULL,
    [Browsing] tinyint  NOT NULL,
    [Inserting] tinyint  NOT NULL,
    [Updating] tinyint  NOT NULL,
    [Deleting] tinyint  NOT NULL,
    [Printing] tinyint  NOT NULL,
    [CardUsing] tinyint  NOT NULL,
    [ModelPrint] tinyint  NOT NULL,
    [ModelDelete] tinyint  NOT NULL,
    [ModelAdd] tinyint  NOT NULL,
    [ModelUpdate] tinyint  NOT NULL,
    [ShowBalance] tinyint  NOT NULL,
    [TypeID] tinyint  NOT NULL,
    [UnSavedPrinting] tinyint  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TrainingOffers' AND xtype='U')
BEGIN
CREATE TABLE [TrainingOffers] (
    [OfferID] int IDENTITY(1,1) NOT NULL,
    [CandidateID] int  NULL,
    [TrainingLevel] nvarchar(50)  NULL,
    [DeliveryMode] nvarchar(50)  NULL,
    [ClassTiming] nvarchar(100)  NULL,
    [TrainingFee] decimal  NULL,
    [Status] nvarchar(50)  NULL,
    [CreatedAt] datetime  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL029' AND xtype='U')
BEGIN
CREATE TABLE [TBL029] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [IsInPut] bit  NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [AccountID] uniqueidentifier  NOT NULL,
    [CurrencyGuide] uniqueidentifier  NOT NULL,
    [ContraAccount] uniqueidentifier  NULL,
    [Discount] float  NOT NULL,
    [Extra] float  NOT NULL,
    [DiscountToSave] float  NOT NULL,
    [ExtraToSave] float  NOT NULL,
    [CostCenter] uniqueidentifier  NULL,
    [OperationBond] uniqueidentifier  NULL,
    [Description] ntext  NULL,
    [NotEffectPrice] bit  NOT NULL,
    [NotEffectTax] bit  NOT NULL,
    [Security] tinyint  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Attendance' AND xtype='U')
BEGIN
CREATE TABLE [Attendance] (
    [AttendanceID] int IDENTITY(1,1) NOT NULL,
    [EnrollmentID] int  NULL,
    [Date] date  NOT NULL,
    [Status] nvarchar(50)  NULL,
    [RecordedBy] int  NULL,
    [RecordedAt] datetime  NULL,
    [CheckInTime] time  NULL,
    [CheckOutTime] time  NULL,
    [TotalHours] decimal  NULL,
    [AssignmentDone] bit  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL138' AND xtype='U')
BEGIN
CREATE TABLE [TBL138] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardNumber] int  NOT NULL,
    [CardName] nvarchar(255)  NOT NULL,
    [LatinName] nvarchar(255)  NULL,
    [Notes] nvarchar(MAX)  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL166' AND xtype='U')
BEGIN
CREATE TABLE [TBL166] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [TypeID] int  NOT NULL,
    [CharID] nvarchar(255)  NOT NULL,
    [CharText] nvarchar(255)  NULL,
    [AscID] int  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL055' AND xtype='U')
BEGIN
CREATE TABLE [TBL055] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [GroupGuide] uniqueidentifier  NOT NULL,
    [MainGroup] uniqueidentifier  NULL,
    [BillGuide] uniqueidentifier  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='InvRecever' AND xtype='U')
BEGIN
CREATE TABLE [InvRecever] (
    [ReceverID] int IDENTITY(1,1) NOT NULL,
    [publicUrl] text  NULL,
    [Invtype] nvarchar(50)  NULL,
    [Invid] nvarchar(200)  NULL,
    [Invscore] nvarchar(50)  NULL,
    [Recever_uuid] nvarchar(150)  NULL,
    [Recever_submissionUuid] nvarchar(150)  NULL,
    [Recever_longId] nvarchar(150)  NULL,
    [Recever_internalId] nvarchar(100)  NULL,
    [Recever_documentType] nvarchar(100)  NULL,
    [Recever_documentTypeNameEn] nvarchar(100)  NULL,
    [Recever_documentTypeNameAr] nvarchar(100)  NULL,
    [Recever_documentTypeVersion] nvarchar(50)  NULL,
    [Recever_submissionDate] nvarchar(100)  NULL,
    [Recever_issueDate] nvarchar(100)  NULL,
    [Recever_lastModifiedDateTimeUtc] nvarchar(100)  NULL,
    [Recever_submitterId] nvarchar(MAX)  NULL,
    [Recever_submitterName] nvarchar(MAX)  NULL,
    [Recever_issuerTaxPayerId] nvarchar(100)  NULL,
    [Recever_recipientType] nvarchar(50)  NULL,
    [Recever_recipientTypeNameEN] nvarchar(100)  NULL,
    [Recever_recipientTypeNameAR] nvarchar(100)  NULL,
    [Recever_recipientTaxPayerId] nvarchar(100)  NULL,
    [Recever_recipientId] nvarchar(150)  NULL,
    [Recever_recipientName] nvarchar(150)  NULL,
    [Recever_intermediaryRIN] nvarchar(50)  NULL,
    [Recever_intermediaryName] nvarchar(100)  NULL,
    [Recever_documentStatusEN] nvarchar(100)  NULL,
    [Recever_documentStatusAR] nvarchar(100)  NULL,
    [Recever_cancelRequestDate] nvarchar(50)  NULL,
    [Recever_rejectRequestDate] nvarchar(50)  NULL,
    [Recever_cancelRequestDelayedDate] nvarchar(50)  NULL,
    [Recever_rejectRequestDelayedDate] nvarchar(50)  NULL,
    [Recever_declineCancelRequestDate] nvarchar(50)  NULL,
    [Recever_declineRejectRequestDate] nvarchar(50)  NULL,
    [Recever_totalSales] float  NULL,
    [Recever_totalDiscount] float  NULL,
    [Recever_netAmount] float  NULL,
    [Recever_totalInvoiceAmount] float  NULL,
    [Recever_totalTax] float  NULL,
    [Recever_maxPercision] nvarchar(50)  NULL,
    [Recever_documentStatusReason] nvarchar(50)  NULL,
    [Recever_submissionChannel] nvarchar(50)  NULL,
    [Recever_InvLine] text  NULL,
    [CompanyID] int  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL124' AND xtype='U')
BEGIN
CREATE TABLE [TBL124] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [TableID] int  NOT NULL,
    [FieldName] varchar(200)  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL157' AND xtype='U')
BEGIN
CREATE TABLE [TBL157] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [CardNumber] int  NOT NULL,
    [ValueType] tinyint  NOT NULL,
    [MonthStart] tinyint  NOT NULL,
    [MonthEnd] tinyint  NOT NULL,
    [DayStart] tinyint  NOT NULL,
    [DayEnd] tinyint  NOT NULL,
    [CardName] nvarchar(255)  NOT NULL,
    [LatinName] nvarchar(255)  NULL,
    [AccountID] uniqueidentifier  NULL,
    [Security] tinyint  NOT NULL,
    [Notes] ntext  NULL,
    [Script01] ntext  NULL,
    [Script02] ntext  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='WeeklyExams' AND xtype='U')
BEGIN
CREATE TABLE [WeeklyExams] (
    [ExamResultID] int IDENTITY(1,1) NOT NULL,
    [EnrollmentID] int  NULL,
    [WeekNumber] int  NOT NULL,
    [Score] decimal  NULL,
    [MaxScore] decimal  NULL,
    [ExamDate] date  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL125' AND xtype='U')
BEGIN
CREATE TABLE [TBL125] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [TypeID] smallint  NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [JobGuide] uniqueidentifier  NULL,
    [TextValue01] nvarchar(255)  NULL,
    [TextValue02] nvarchar(255)  NULL,
    [TextValue03] nvarchar(255)  NULL,
    [TextValue04] nvarchar(255)  NULL,
    [TextValue05] nvarchar(255)  NULL,
    [IntValue01] int  NOT NULL,
    [IntValue02] int  NOT NULL,
    [Category01] uniqueidentifier  NULL,
    [Category02] uniqueidentifier  NULL,
    [Category03] uniqueidentifier  NULL,
    [Category04] uniqueidentifier  NULL,
    [Category05] uniqueidentifier  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL056' AND xtype='U')
BEGIN
CREATE TABLE [TBL056] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [ItemGuide] uniqueidentifier  NOT NULL,
    [BillGuide] uniqueidentifier  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='CareerReadiness' AND xtype='U')
BEGIN
CREATE TABLE [CareerReadiness] (
    [ReadinessID] int IDENTITY(1,1) NOT NULL,
    [CandidateID] int  NULL,
    [EnrollmentID] int  NULL,
    [Status] nvarchar(50)  NULL,
    [EvaluationDate] datetime  NULL,
    [Notes] nvarchar(MAX)  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL099' AND xtype='U')
BEGIN
CREATE TABLE [TBL099] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [RecordGuide] uniqueidentifier  NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [PLogIn] datetime  NULL,
    [PLogOut] datetime  NULL,
    [CLogIn] datetime  NULL,
    [CLogOut] datetime  NULL,
    [ShiftGuide] uniqueidentifier  NULL,
    [AgentGuide] uniqueidentifier  NOT NULL,
    [CostCenter] uniqueidentifier  NULL,
    [Category01] uniqueidentifier  NULL,
    [Category02] uniqueidentifier  NULL,
    [Category03] uniqueidentifier  NULL,
    [Category04] uniqueidentifier  NULL,
    [Category05] uniqueidentifier  NULL,
    [Category06] uniqueidentifier  NULL,
    [Category07] uniqueidentifier  NULL,
    [Notes] nvarchar(255)  NULL,
    [TextValue01] nvarchar(255)  NULL,
    [TextValue02] nvarchar(255)  NULL,
    [TextValue03] nvarchar(255)  NULL,
    [TextValue04] nvarchar(255)  NULL,
    [TextValue05] nvarchar(255)  NULL,
    [DvcIn] nvarchar(255)  NULL,
    [DvcOut] nvarchar(255)  NULL,
    [NumberValue01] float  NOT NULL,
    [IgnoreDifferenceForLogin] bit  NOT NULL,
    [IgnoreDifferenceForLogout] bit  NOT NULL,
    [ManuallyEdit] bit  NOT NULL,
    [CType] int  NOT NULL,
    [CLateEntrance] datetime  NULL,
    [CEarlyEntrance] datetime  NULL,
    [CLateLeave] datetime  NULL,
    [CEarlyLeave] datetime  NULL,
    [DetailsGuide] uniqueidentifier  NULL,
    [CTotalPeriod] datetime  NULL,
    [CTimeAbsentee] datetime  NULL,
    [CLateEntrance2] datetime  NULL,
    [CEarlyEntrance2] datetime  NULL,
    [CLateLeave2] datetime  NULL,
    [CEarlyLeave2] datetime  NULL,
    [CTotalPeriod2] datetime  NULL,
    [CTimeAbsentee2] datetime  NULL,
    [CLateEntrance3] datetime  NULL,
    [CEarlyEntrance3] datetime  NULL,
    [CLateLeave3] datetime  NULL,
    [CEarlyLeave3] datetime  NULL,
    [CTotalPeriod3] datetime  NULL,
    [CTimeAbsentee3] datetime  NULL,
    [CLateEntrance4] datetime  NULL,
    [CEarlyEntrance4] datetime  NULL,
    [CLateLeave4] datetime  NULL,
    [CEarlyLeave4] datetime  NULL,
    [CTotalPeriod4] datetime  NULL,
    [CTimeAbsentee4] datetime  NULL,
    [CLateEntrance5] datetime  NULL,
    [CEarlyEntrance5] datetime  NULL,
    [CLateLeave5] datetime  NULL,
    [CEarlyLeave5] datetime  NULL,
    [CTotalPeriod5] datetime  NULL,
    [CTimeAbsentee5] datetime  NULL,
    [ContractGuide] uniqueidentifier  NULL,
    [Project] uniqueidentifier  NULL,
    [Branch] uniqueidentifier  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL015' AND xtype='U')
BEGIN
CREATE TABLE [TBL015] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [MainGuide] uniqueidentifier  NULL,
    [RelatedAgent] uniqueidentifier  NULL,
    [MainAccountGuide] uniqueidentifier  NULL,
    [MainTaxAccountGuide] uniqueidentifier  NULL,
    [DefaultPayType] smallint  NOT NULL,
    [GroupName] nvarchar(255)  NOT NULL,
    [Security] tinyint  NOT NULL,
    [LatinName] nvarchar(255)  NULL,
    [Notes] ntext  NULL,
    [CardImage] image  NULL,
    [ByUser] uniqueidentifier  NULL,
    [ByGroup] uniqueidentifier  NULL,
    [UnifiedAccountGuide] uniqueidentifier  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='GeneralSales' AND xtype='U')
BEGIN
CREATE TABLE [GeneralSales] (
    [SaleID] int IDENTITY(1,1) NOT NULL,
    [ServiceName] nvarchar(200)  NOT NULL,
    [Amount] decimal  NOT NULL,
    [PaymentMethod] nvarchar(50)  NULL,
    [ClientName] nvarchar(100)  NULL,
    [Notes] nvarchar(MAX)  NULL,
    [CreatedBy] int  NULL,
    [SaleDate] datetime  NULL,
    [CandidateID] int  NULL,
    [ServiceID] int  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Receip_Data' AND xtype='U')
BEGIN
CREATE TABLE [Receip_Data] (
    [ReceiptID] int IDENTITY(1,1) NOT NULL,
    [DateTimeIssued] datetime  NULL,
    [ReceiptNumber] nvarchar(50)  NULL,
    [Uuid] nvarchar(150)  NULL,
    [PreviousUUID] nvarchar(150)  NULL,
    [referenceUUID] nvarchar(150)  NULL,
    [ReferenceOldUUID] nvarchar(150)  NULL,
    [Currency] nvarchar(5)  NULL,
    [exchangeRate] float  NULL,
    [sOrderNameCode] nvarchar(50)  NULL,
    [OrderdeliveryMode] nvarchar(50)  NULL,
    [GrossWeight] float  NULL,
    [NetWeight] float  NULL,
    [ReceiptType] nvarchar(5)  NULL,
    [TypeVersion] nvarchar(10)  NULL,
    [Rin] nvarchar(15)  NULL,
    [CompanyTradeName] nvarchar(100)  NULL,
    [BranchCode] nvarchar(5)  NOT NULL,
    [Country] nvarchar(5)  NULL,
    [Governate] nvarchar(20)  NULL,
    [RegionCity] nvarchar(30)  NULL,
    [Street] nvarchar(150)  NULL,
    [BuildingNumber] nvarchar(20)  NULL,
    [PostalCode] nvarchar(50)  NULL,
    [Floor] nvarchar(5)  NULL,
    [Room] nvarchar(5)  NULL,
    [Landmark] nvarchar(150)  NULL,
    [AdditionalInformation] nvarchar(150)  NULL,
    [DeviceSerialNumber] nvarchar(40)  NULL,
    [SyndicateLicenseNumber] nvarchar(40)  NULL,
    [ActivityCode] nvarchar(30)  NULL,
    [BuyerType] nvarchar(5)  NULL,
    [BuyerID] nvarchar(40)  NULL,
    [BuyerName] nvarchar(150)  NULL,
    [BuyerMobileNumber] nvarchar(20)  NULL,
    [BuyerPaymentNumber] nvarchar(20)  NULL,
    [InternalCode] nvarchar(40)  NULL,
    [Description] nvarchar(150)  NULL,
    [ItemType] nvarchar(5)  NULL,
    [ItemCode] nvarchar(40)  NULL,
    [UnitType] nvarchar(5)  NULL,
    [Quantity] float  NULL,
    [UnitPrice] float  NULL,
    [NetSale] float  NULL,
    [TotalSale] float  NULL,
    [Total] float  NULL,
    [CommercialDiscount] float  NULL,
    [ItemDiscount] float  NULL,
    [ValueDifference] float  NULL,
    [TaxType] nvarchar(5)  NULL,
    [SubType] nvarchar(10)  NULL,
    [TaxAmount] float  NULL,
    [TaxRate] float  NULL,
    [ExtraReceiptDiscount] float  NULL,
    [NetAmount] float  NULL,
    [FeesAmount] float  NULL,
    [TotalAmount] float  NULL,
    [PaymentMethod] nvarchar(50)  NULL,
    [Adjustment] float  NULL,
    [ContractorName] nvarchar(100)  NULL,
    [ContractorAmount] float  NULL,
    [ContractorRate] float  NULL,
    [BeneficiaryAmount] float  NULL,
    [BeneficiaryRate] float  NULL,
    [IsSend] bit  NULL,
    [CompanyID] int  NULL,
    [CreatedDate] datetime  NULL,
    [ModifiedDate] datetime  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL080' AND xtype='U')
BEGIN
CREATE TABLE [TBL080] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [IsInPut] bit  NOT NULL,
    [AccountID] uniqueidentifier  NOT NULL,
    [CurrencyGuide] uniqueidentifier  NOT NULL,
    [CostCenter] uniqueidentifier  NULL,
    [Discount] float  NOT NULL,
    [Extra] float  NOT NULL,
    [ContraAccount] uniqueidentifier  NULL,
    [DiscountToSave] float  NOT NULL,
    [ExtraToSave] float  NOT NULL,
    [Description] ntext  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL006' AND xtype='U')
BEGIN
CREATE TABLE [TBL006] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [MainGuide] uniqueidentifier  NULL,
    [CardCode] nvarchar(255)  NOT NULL,
    [TaxRatio] float  NOT NULL,
    [GroupName] nvarchar(255)  NOT NULL,
    [Security] tinyint  NOT NULL,
    [LatinName] nvarchar(255)  NULL,
    [MainAccount] uniqueidentifier  NULL,
    [TradingClosing] uniqueidentifier  NULL,
    [BarcodeType] uniqueidentifier  NULL,
    [ForceCodesInInput] bit  NOT NULL,
    [ForceCodesInOutput] bit  NOT NULL,
    [ExpiryDateRequired] bit  NOT NULL,
    [CostCenterRequired] bit  NOT NULL,
    [Category01Required] bit  NOT NULL,
    [Category02Required] bit  NOT NULL,
    [Category03Required] bit  NOT NULL,
    [Category04Required] bit  NOT NULL,
    [Category05Required] bit  NOT NULL,
    [PatchCodeRequired] bit  NOT NULL,
    [ExpiryDateCheckInventory] bit  NOT NULL,
    [CostCenterCheckInventory] bit  NOT NULL,
    [Category01CheckInventory] bit  NOT NULL,
    [Category02CheckInventory] bit  NOT NULL,
    [Category03CheckInventory] bit  NOT NULL,
    [Category04CheckInventory] bit  NOT NULL,
    [Category05CheckInventory] bit  NOT NULL,
    [PatchCodeCheckInventory] bit  NOT NULL,
    [CannotDuplicateSerial] bit  NOT NULL,
    [BalanceSheetClosing] uniqueidentifier  NULL,
    [TextValue01] nvarchar(255)  NULL,
    [TextValue02] nvarchar(255)  NULL,
    [IsAssets] bit  NOT NULL,
    [Notes] ntext  NULL,
    [ButtonColor] int  NOT NULL,
    [Balance_Selected] bit  NOT NULL,
    [CardImage] image  NULL,
    [ByUser] uniqueidentifier  NULL,
    [ByGroup] uniqueidentifier  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL115' AND xtype='U')
BEGIN
CREATE TABLE [TBL115] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [FingerID] int  NOT NULL,
    [SignDate] datetime  NOT NULL,
    [FingerType] int  NOT NULL,
    [SignType] tinyint  NOT NULL,
    [DeviceName] nvarchar(255)  NULL,
    [Notes] nvarchar(255)  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='CorporateInvoices' AND xtype='U')
BEGIN
CREATE TABLE [CorporateInvoices] (
    [InvoiceID] int IDENTITY(1,1) NOT NULL,
    [ClientID] int  NULL,
    [ServiceType] nvarchar(100)  NULL,
    [Description] nvarchar(MAX)  NULL,
    [Amount] decimal  NOT NULL,
    [IssueDate] datetime  NULL,
    [DueDate] date  NULL,
    [Status] nvarchar(50)  NULL,
    [CreatedBy] int  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL172' AND xtype='U')
BEGIN
CREATE TABLE [TBL172] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [GroupGuide] uniqueidentifier  NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [CardValue] float  NOT NULL,
    [Browsing] tinyint  NOT NULL,
    [Inserting] tinyint  NOT NULL,
    [Updating] tinyint  NOT NULL,
    [Deleting] tinyint  NOT NULL,
    [Printing] tinyint  NOT NULL,
    [CardUsing] tinyint  NOT NULL,
    [ModelPrint] tinyint  NOT NULL,
    [ModelDelete] tinyint  NOT NULL,
    [ModelAdd] tinyint  NOT NULL,
    [ModelUpdate] tinyint  NOT NULL,
    [ShowBalance] tinyint  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL086' AND xtype='U')
BEGIN
CREATE TABLE [TBL086] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [Notes] nvarchar(255)  NULL,
    [AccountID] uniqueidentifier  NULL,
    [AccountID2] uniqueidentifier  NULL,
    [AccountCondition] ntext  NULL,
    [AgentGroupID] uniqueidentifier  NULL,
    [AgentGroupID2] uniqueidentifier  NULL,
    [AgentCondition] ntext  NULL,
    [Option1] tinyint  NOT NULL,
    [Option2] tinyint  NOT NULL,
    [ContraAccountNotAffected] bit  NOT NULL,
    [ValueToGenerate] ntext  NOT NULL,
    [AccountToGenerate] ntext  NULL,
    [ContraAccountToGenerate] ntext  NULL,
    [ContraAccountID] uniqueidentifier  NULL,
    [CostCenter] uniqueidentifier  NULL,
    [NoteToGenerate] ntext  NULL,
    [NoteToGenerate2] ntext  NULL,
    [ValueToGenerate2] ntext  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL140' AND xtype='U')
BEGIN
CREATE TABLE [TBL140] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [ItemID] uniqueidentifier  NOT NULL,
    [StoreID] uniqueidentifier  NOT NULL,
    [MinLimit] float  NOT NULL,
    [MaxLimit] float  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL045' AND xtype='U')
BEGIN
CREATE TABLE [TBL045] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [GroupGuide] uniqueidentifier  NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [HideRecord] bit  NOT NULL,
    [CardValue] float  NOT NULL,
    [BrowsingPosted] tinyint  NOT NULL,
    [InsertingPosted] tinyint  NOT NULL,
    [UpdatingPosted] tinyint  NOT NULL,
    [DeletingPosted] tinyint  NOT NULL,
    [PrintingPosted] tinyint  NOT NULL,
    [Posting] tinyint  NOT NULL,
    [BrowsingUnPosted] tinyint  NOT NULL,
    [InsertingUnPosted] tinyint  NOT NULL,
    [UpdatingUnPosted] tinyint  NOT NULL,
    [DeletingUnPosted] tinyint  NOT NULL,
    [PrintingUnSaved] tinyint  NOT NULL,
    [ModelPrint] tinyint  NOT NULL,
    [ModelDelete] tinyint  NOT NULL,
    [ModelAdd] tinyint  NOT NULL,
    [ModelUpdate] tinyint  NOT NULL,
    [DefaultAccount] uniqueidentifier  NULL,
    [DefaultCostCenter] uniqueidentifier  NULL,
    [DefaultProject] uniqueidentifier  NULL,
    [DefaultBranch] uniqueidentifier  NULL,
    [ChangeCardNumber] bit  NOT NULL,
    [PrintingUnPosted] tinyint  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='DBInformations' AND xtype='U')
BEGIN
CREATE TABLE [DBInformations] (
    [DBVer_26015] int  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='RecruitmentFailures' AND xtype='U')
BEGIN
CREATE TABLE [RecruitmentFailures] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CandidateID] int  NULL,
    [Stage] nvarchar(50)  NULL,
    [Reason] nvarchar(MAX)  NULL,
    [LoggedBy] int  NULL,
    [CreatedAt] datetime  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL030' AND xtype='U')
BEGIN
CREATE TABLE [TBL030] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [MainGuide] uniqueidentifier  NULL,
    [CardNumber] int  NOT NULL,
    [CardCode] nvarchar(255)  NULL,
    [CardName] nvarchar(255)  NOT NULL,
    [Security] tinyint  NOT NULL,
    [LatinName] nvarchar(255)  NULL,
    [Notes] ntext  NULL,
    [CardImage] image  NULL,
    [ByUser] uniqueidentifier  NULL,
    [ByGroup] uniqueidentifier  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL116' AND xtype='U')
BEGIN
CREATE TABLE [TBL116] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [SignOut] datetime  NULL,
    [SignIn] datetime  NULL,
    [Notes] nvarchar(255)  NULL,
    [DetailsGuide] uniqueidentifier  NULL,
    [TypeID] tinyint  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL058' AND xtype='U')
BEGIN
CREATE TABLE [TBL058] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [TypeIDENTITY] nvarchar(255)  NOT NULL,
    [CardName] nvarchar(255)  NOT NULL,
    [DoneIn] datetime  NOT NULL,
    [CardType] int  NOT NULL,
    [Notes] ntext  NULL,
    [CardImage] image  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL158' AND xtype='U')
BEGIN
CREATE TABLE [TBL158] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [Damage] ntext  NOT NULL,
    [WarrantyIncluded] bit  NOT NULL,
    [MaintenanceMan] nvarchar(255)  NULL,
    [DamageDescription] ntext  NULL,
    [Description] ntext  NULL,
    [Cost] float  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='invoice_data' AND xtype='U')
BEGIN
CREATE TABLE [invoice_data] (
    [inv_ID] int IDENTITY(1,1) NOT NULL,
    [Issuer_ID] nvarchar(20)  NULL,
    [Issuer_Type] nvarchar(3)  NULL,
    [Issuer_Name] nvarchar(100)  NULL,
    [Issuer_Address_branchID] nvarchar(20)  NULL,
    [Issuer_Address_country] nvarchar(5)  NULL,
    [Issuer_Address_governate] nvarchar(20)  NULL,
    [Issuer_Address_regionCity] nvarchar(30)  NULL,
    [Issuer_Address_street] nvarchar(255)  NULL,
    [Issuer_Address_buildingNumber] nvarchar(10)  NULL,
    [Issuer_Address_postalCode] nvarchar(10)  NULL,
    [Issuer_Address_floor] nvarchar(20)  NULL,
    [Issuer_Address_room] nvarchar(20)  NULL,
    [Issuer_Address_landmark] nvarchar(MAX)  NULL,
    [Issuer_Address_additionalInformation] nvarchar(MAX)  NULL,
    [Receiver_ID] nvarchar(20)  NULL,
    [Receiver_Type] nvarchar(3)  NULL,
    [Receiver_Name] nvarchar(100)  NULL,
    [Receiver_Address_country] nvarchar(30)  NULL,
    [Receiver_Address_governate] nvarchar(250)  NULL,
    [Receiver_Address_regionCity] nvarchar(250)  NULL,
    [Receiver_Address_street] nvarchar(500)  NULL,
    [Receiver_Address_buildingNumber] nvarchar(20)  NULL,
    [Receiver_Address_postalCode] nvarchar(10)  NULL,
    [Receiver_Address_floor] nvarchar(20)  NULL,
    [Receiver_Address_room] nvarchar(20)  NULL,
    [Receiver_Address_landmark] nvarchar(MAX)  NULL,
    [Receiver_Address_additionalInformation] nvarchar(MAX)  NULL,
    [DocumentType] nvarchar(5)  NULL,
    [documentTypeVersion] nvarchar(5)  NULL,
    [dateTimeIssued] datetime  NULL,
    [taxpayerActivityCode] nvarchar(10)  NULL,
    [internalID] nvarchar(50)  NULL,
    [purchaseOrderReference] nvarchar(30)  NULL,
    [purchaseOrderDescription] nvarchar(MAX)  NULL,
    [salesOrderReference] nvarchar(MAX)  NULL,
    [salesOrderDescription] nvarchar(MAX)  NULL,
    [proformaInvoiceNumber] nvarchar(30)  NULL,
    [payment_bankName] nvarchar(30)  NULL,
    [payment_bankAddress] nvarchar(255)  NULL,
    [payment_bankAccountNo] nvarchar(50)  NULL,
    [payment_bankAccountIBAN] nvarchar(50)  NULL,
    [payment_swiftCode] nvarchar(50)  NULL,
    [payment_terms] nvarchar(255)  NULL,
    [delivery_approach] nvarchar(50)  NULL,
    [delivery_packaging] nvarchar(50)  NULL,
    [delivery_dateValidity] nvarchar(50)  NULL,
    [delivery_exportPort] nvarchar(50)  NULL,
    [delivery_countryOfOrigin] nvarchar(50)  NULL,
    [delivery_grossWeight] float  NULL,
    [delivery_netWeight] float  NULL,
    [delivery_terms] nvarchar(255)  NULL,
    [invoiceLines_description] nvarchar(255)  NULL,
    [invoiceLines_itemType] nvarchar(5)  NULL,
    [invoiceLines_itemCode] nvarchar(50)  NULL,
    [invoiceLines_internalCode] nvarchar(50)  NULL,
    [invoiceLines_unitType] nvarchar(5)  NULL,
    [invoiceLines_quantity] float  NULL,
    [invoiceLines_unitValue_currencySold] nvarchar(5)  NULL,
    [invoiceLines_unitValue_amountSold] decimal  NULL,
    [invoiceLines_unitValue_currencyExchangeRate] float  NULL,
    [invoiceLines_unitValue_amountEGP] float  NULL,
    [invoiceLines_salesTotal] float  NULL,
    [invoiceLines_valueDifference] float  NULL,
    [invoiceLines_totalTaxableFees] float  NULL,
    [invoiceLines_discount_rate] float  NULL,
    [invoiceLines_discount_amount] float  NULL,
    [invoiceLines_netTotal] float  NULL,
    [invoiceLines_taxableItems_taxType1] nvarchar(5)  NULL,
    [invoiceLines_taxableItems_subType1] nvarchar(10)  NULL,
    [invoiceLines_taxableItems_rate1] float  NULL,
    [invoiceLines_taxableItems_amount1] float  NULL,
    [invoiceLines_taxableItems_taxType] nvarchar(5)  NULL,
    [invoiceLines_taxableItems_subType] nvarchar(10)  NULL,
    [invoiceLines_taxableItems_rate] float  NULL,
    [invoiceLines_taxableItems_amount] float  NULL,
    [invoiceLines_total] float  NULL,
    [totalSalesAmount] float  NULL,
    [totalDiscountAmount] float  NULL,
    [netAmount] float  NULL,
    [taxTotals_taxType] nvarchar(5)  NULL,
    [taxTotals_amount] float  NULL,
    [extraDiscountAmount] float  NULL,
    [totalItemsDiscountAmount] float  NULL,
    [totalAmount] float  NULL,
    [invIsSend] bit  NULL,
    [CompanyID] int  NULL,
    [CreatedDate] datetime  NULL,
    [ModifiedDate] datetime  NULL,
    [PreviousUUID] nvarchar(255)  NULL,
    [referenceUUID] nvarchar(255)  NULL,
    [DeviceSerialNumber] nvarchar(50)  NULL,
    [SyndicateLicenseNumber] nvarchar(50)  NULL,
    [BuyerMobileNumber] nvarchar(50)  NULL,
    [BuyerPaymentNumber] nvarchar(50)  NULL,
    [PaymentMethod] nvarchar(10)  NULL,
    [Adjustment] float  NULL,
    [ContractorName] nvarchar(100)  NULL,
    [ContractorAmount] float  NULL,
    [ContractorRate] float  NULL,
    [BeneficiaryAmount] float  NULL,
    [BeneficiaryRate] float  NULL,
    [InvoiceGuideUniqe] uniqueidentifier  NULL,
    [BillNumber] int  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='CorporatePayments' AND xtype='U')
BEGIN
CREATE TABLE [CorporatePayments] (
    [PaymentID] int IDENTITY(1,1) NOT NULL,
    [InvoiceID] int  NULL,
    [Amount] decimal  NOT NULL,
    [PaymentDate] datetime  NULL,
    [PaymentMethod] nvarchar(50)  NULL,
    [ReferenceNumber] nvarchar(100)  NULL,
    [ReceivedBy] int  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL126' AND xtype='U')
BEGIN
CREATE TABLE [TBL126] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [UserGuide] uniqueidentifier  NULL,
    [MainGuide] uniqueidentifier  NULL,
    [CardNumber] int  NOT NULL,
    [CardDate] datetime  NOT NULL,
    [Security] tinyint  NOT NULL,
    [NoteState] tinyint  NOT NULL,
    [NoteTitle] nvarchar(250)  NULL,
    [NoteBody] nvarchar(MAX)  NOT NULL,
    [Category01] uniqueidentifier  NULL,
    [Category02] uniqueidentifier  NULL,
    [Category03] uniqueidentifier  NULL,
    [Category04] uniqueidentifier  NULL,
    [Category05] uniqueidentifier  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL016' AND xtype='U')
BEGIN
CREATE TABLE [TBL016] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [AgentName] nvarchar(255)  NOT NULL,
    [Prefix] nvarchar(255)  NULL,
    [LatinName] nvarchar(255)  NULL,
    [BirthPlace] nvarchar(255)  NULL,
    [Suffix] nvarchar(255)  NULL,
    [IDNumber] nvarchar(255)  NULL,
    [Passport] nvarchar(255)  NULL,
    [FirstName] nvarchar(255)  NULL,
    [FatherName] nvarchar(255)  NULL,
    [LastName] nvarchar(255)  NULL,
    [TaxCode] nvarchar(255)  NULL,
    [MotherName] nvarchar(255)  NULL,
    [CardNumber] int  NOT NULL,
    [Gender] int  NOT NULL,
    [Security] tinyint  NOT NULL,
    [SalaryType] tinyint  NOT NULL,
    [FixedSalary] float  NOT NULL,
    [DaySalary] float  NOT NULL,
    [CostPercentage] float  NOT NULL,
    [NotActive] bit  NOT NULL,
    [Birthdate] datetime  NULL,
    [DateStart] datetime  NULL,
    [DateBegin] datetime  NULL,
    [DateEnd] datetime  NULL,
    [MaxDebit] float  NOT NULL,
    [MaxCredit] float  NOT NULL,
    [NotepaperMaxDebit] float  NOT NULL,
    [NotepaperMaxCredit] float  NOT NULL,
    [Religion] nvarchar(255)  NULL,
    [Maritalstatus] nvarchar(255)  NULL,
    [DateValue1] datetime  NULL,
    [DateValue2] datetime  NULL,
    [DateValue3] datetime  NULL,
    [DateValue4] datetime  NULL,
    [DateValue5] datetime  NULL,
    [DateValue6] datetime  NULL,
    [DateValue7] datetime  NULL,
    [DateValue8] datetime  NULL,
    [DateValue9] datetime  NULL,
    [DateValue0] datetime  NULL,
    [DetailingItems] bit  NOT NULL,
    [BitValue1] bit  NOT NULL,
    [BitValue2] bit  NOT NULL,
    [BitValue3] bit  NOT NULL,
    [BitValue4] bit  NOT NULL,
    [BitValue5] bit  NOT NULL,
    [BitValue6] bit  NOT NULL,
    [BitValue7] bit  NOT NULL,
    [BitValue8] bit  NOT NULL,
    [BitValue9] bit  NOT NULL,
    [BitValue10] bit  NOT NULL,
    [BitValue11] bit  NOT NULL,
    [CreditNotAllowed] bit  NOT NULL,
    [DueAge] int  NOT NULL,
    [DueAgeAmount] int  NOT NULL,
    [DueAgeType] uniqueidentifier  NULL,
    [FloatValue1] float  NOT NULL,
    [FloatValue2] float  NOT NULL,
    [FloatValue3] float  NOT NULL,
    [FloatValue4] float  NOT NULL,
    [FloatValue5] float  NOT NULL,
    [FloatValue6] float  NOT NULL,
    [Barcode] nvarchar(255)  NULL,
    [PriceType] tinyint  NOT NULL,
    [Phone] nvarchar(255)  NULL,
    [Phone2] nvarchar(255)  NULL,
    [Mobile] nvarchar(255)  NULL,
    [SubjectToTax] bit  NOT NULL,
    [Fax] nvarchar(255)  NULL,
    [MaxDiscountRatio] float  NOT NULL,
    [DefaultPriceType] int  NOT NULL,
    [Nationality] nvarchar(255)  NULL,
    [Sponsor] nvarchar(255)  NULL,
    [TextValue1] nvarchar(255)  NULL,
    [TextValue2] nvarchar(255)  NULL,
    [TextValue3] nvarchar(255)  NULL,
    [TextValue4] nvarchar(255)  NULL,
    [TextValue5] nvarchar(255)  NULL,
    [TextValue6] nvarchar(255)  NULL,
    [TextValue7] nvarchar(255)  NULL,
    [TextValue8] nvarchar(255)  NULL,
    [TextValue9] nvarchar(255)  NULL,
    [TextValue0] nvarchar(255)  NULL,
    [TextValue10] nvarchar(255)  NULL,
    [TextValue11] nvarchar(255)  NULL,
    [TextValue12] nvarchar(255)  NULL,
    [TextValue13] nvarchar(255)  NULL,
    [TextValue14] nvarchar(255)  NULL,
    [TextValue15] nvarchar(255)  NULL,
    [TextValue16] nvarchar(255)  NULL,
    [TextValue17] nvarchar(255)  NULL,
    [TextValue18] nvarchar(255)  NULL,
    [TextValue19] nvarchar(255)  NULL,
    [TextValue20] nvarchar(255)  NULL,
    [TextValue21] nvarchar(255)  NULL,
    [TextValue22] nvarchar(255)  NULL,
    [TextValue23] nvarchar(255)  NULL,
    [TextValue24] nvarchar(255)  NULL,
    [TextValue25] nvarchar(255)  NULL,
    [TextValue26] nvarchar(255)  NULL,
    [RadioValue1] tinyint  NOT NULL,
    [NumberValue1] int  NOT NULL,
    [NumberValue2] int  NOT NULL,
    [NumberValue3] int  NOT NULL,
    [NumberValue4] int  NOT NULL,
    [NumberValue5] int  NOT NULL,
    [ItemsDiscountRatio] float  NOT NULL,
    [EMail] nvarchar(255)  NULL,
    [Website] nvarchar(255)  NULL,
    [CashAccountID] uniqueidentifier  NULL,
    [TaxAccountID] uniqueidentifier  NULL,
    [AccountID] uniqueidentifier  NOT NULL,
    [Project] uniqueidentifier  NULL,
    [Branch] uniqueidentifier  NULL,
    [MainAgent] uniqueidentifier  NULL,
    [MainAgent2] uniqueidentifier  NULL,
    [MainGroupGuide] uniqueidentifier  NULL,
    [CostCenter] uniqueidentifier  NULL,
    [CostCenter2] uniqueidentifier  NULL,
    [Warehouse] uniqueidentifier  NULL,
    [Suspended] bit  NOT NULL,
    [RelatedAdministration] uniqueidentifier  NULL,
    [RelatedAdministration2] uniqueidentifier  NULL,
    [DefaultCurrency] uniqueidentifier  NULL,
    [Category01] uniqueidentifier  NULL,
    [Category02] uniqueidentifier  NULL,
    [Category03] uniqueidentifier  NULL,
    [Category04] uniqueidentifier  NULL,
    [Category05] uniqueidentifier  NULL,
    [Category06] uniqueidentifier  NULL,
    [Category07] uniqueidentifier  NULL,
    [Category08] uniqueidentifier  NULL,
    [Category09] uniqueidentifier  NULL,
    [Category10] uniqueidentifier  NULL,
    [Category11] uniqueidentifier  NULL,
    [Category12] uniqueidentifier  NULL,
    [Category13] uniqueidentifier  NULL,
    [Category14] uniqueidentifier  NULL,
    [Category15] uniqueidentifier  NULL,
    [LongText01] ntext  NULL,
    [LongText02] ntext  NULL,
    [LongText03] ntext  NULL,
    [LongTextValue] nvarchar(MAX)  NULL,
    [CardImage] image  NULL,
    [CardImage2] image  NULL,
    [Notes] ntext  NULL,
    [FullAdress] nvarchar(510)  NULL,
    [Country] nvarchar(255)  NULL,
    [City] nvarchar(255)  NULL,
    [IsEmployee] bit  NOT NULL,
    [MapLink] ntext  NULL,
    [ByUser] uniqueidentifier  NULL,
    [ByGroup] uniqueidentifier  NULL,
    [AddressID] uniqueidentifier  NULL,
    [RegionID] uniqueidentifier  NULL,
    [CommercialRegister] nvarchar(255)  NULL,
    [IBAN] nvarchar(255)  NULL,
    [BankCode] nvarchar(255)  NULL,
    [CitySubdivision] nvarchar(255)  NULL,
    [PlotIdentification] nvarchar(255)  NULL,
    [RelatedAdministration3] uniqueidentifier  NULL,
    [TaxType] tinyint  NULL,
    [StreetName] nvarchar(255)  NULL,
    [BuildingNumber] nvarchar(255)  NULL,
    [PostalZoneNumber] nvarchar(255)  NULL,
    [Governorate] nvarchar(255)  NULL,
    [Tax_UniqueNumber] nvarchar(255)  NULL,
    [Tax_UnifiedNumber] nvarchar(255)  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Notifications' AND xtype='U')
BEGIN
CREATE TABLE [Notifications] (
    [NotificationID] int IDENTITY(1,1) NOT NULL,
    [UserID] int  NULL,
    [Message] nvarchar(MAX)  NULL,
    [Type] nvarchar(50)  NULL,
    [RelatedID] int  NULL,
    [IsRead] bit  NULL,
    [CreatedAt] datetime  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL141' AND xtype='U')
BEGIN
CREATE TABLE [TBL141] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [RowGuide] uniqueidentifier  NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [LCNumber] nvarchar(255)  NULL,
    [ManualLCNumber] nvarchar(255)  NULL,
    [LCDate] datetime  NULL,
    [LCEndDate] datetime  NULL,
    [SupplierBank] nvarchar(255)  NULL,
    [LCAccount] uniqueidentifier  NULL,
    [LCClosed] bit  NOT NULL,
    [PurchaseOrderNo] nvarchar(255)  NULL,
    [FreightType] uniqueidentifier  NULL,
    [DeliveryDate] datetime  NULL,
    [DeadlineDeliveryDate] datetime  NULL,
    [LCAmount] float  NOT NULL,
    [LCCurrency] uniqueidentifier  NULL,
    [LCAmountRate] float  NOT NULL,
    [LCIssuingBank] nvarchar(255)  NULL,
    [LCAdvisingBank] nvarchar(255)  NULL,
    [LCConfirmingBank] nvarchar(255)  NULL,
    [LCTransferringBank] nvarchar(255)  NULL,
    [CoverRatio] float  NOT NULL,
    [CoverAmount] float  NOT NULL,
    [HSCode] nvarchar(255)  NULL,
    [PaymentType] uniqueidentifier  NULL,
    [LCType] uniqueidentifier  NULL,
    [TermsOfPayment] uniqueidentifier  NULL,
    [GoodsType] uniqueidentifier  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL117' AND xtype='U')
BEGIN
CREATE TABLE [TBL117] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [CostCenter] uniqueidentifier  NULL,
    [IntValue01] int  NOT NULL,
    [IntValue02] int  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL059' AND xtype='U')
BEGIN
CREATE TABLE [TBL059] (
    [ID] tinyint  NOT NULL,
    [TypeTerm] nvarchar(255)  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Users_1' AND xtype='U')
BEGIN
CREATE TABLE [Users_1] (
    [UserID] int IDENTITY(1,1) NOT NULL,
    [Username] nvarchar(50)  NOT NULL,
    [Password] nvarchar(255)  NOT NULL,
    [Role] nvarchar(50)  NOT NULL,
    [FullName] nvarchar(100)  NULL,
    [Email] nvarchar(100)  NULL,
    [CreatedAt] datetime  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL060' AND xtype='U')
BEGIN
CREATE TABLE [TBL060] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [BillGuide] uniqueidentifier  NOT NULL,
    [Value] float  NOT NULL,
    [CollectDate] datetime  NOT NULL,
    [Notes] nvarchar(255)  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL031' AND xtype='U')
BEGIN
CREATE TABLE [TBL031] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [Attachment] nvarchar(255)  NULL,
    [SerialNumber] nvarchar(255)  NULL,
    [Type] nvarchar(255)  NULL,
    [Description] ntext  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL081' AND xtype='U')
BEGIN
CREATE TABLE [TBL081] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [CardOrder] int  NOT NULL,
    [NotActive] bit  NOT NULL,
    [CardNumber] int  NOT NULL,
    [Security] tinyint  NOT NULL,
    [CardName] nvarchar(255)  NOT NULL,
    [LatinName] nvarchar(255)  NULL,
    [MainCard] uniqueidentifier  NULL,
    [CategoryType] uniqueidentifier  NOT NULL,
    [Notes] nvarchar(255)  NULL,
    [BranchNo] nvarchar(MAX)  NULL,
    [VendorName] nvarchar(MAX)  NULL,
    [ModelName] nvarchar(MAX)  NULL,
    [OperatingSystem] nvarchar(MAX)  NULL,
    [DeviceName] nvarchar(MAX)  NULL,
    [Status] nvarchar(MAX)  NULL,
    [Description] nvarchar(MAX)  NULL,
    [TaxpayerBranch] nvarchar(MAX)  NULL,
    [SerialNumber] nvarchar(MAX)  NULL,
    [ActiveFrom] nvarchar(MAX)  NULL,
    [ActiveTo] nvarchar(MAX)  NULL,
    [clientID] nvarchar(MAX)  NULL,
    [clientSecret1] nvarchar(MAX)  NULL,
    [clientSecret2] nvarchar(MAX)  NULL,
    [ClintID_Pre] nvarchar(MAX)  NULL,
    [ClintSecret1_Pre] nvarchar(MAX)  NULL,
    [ClintSecret2_Pre] nvarchar(MAX)  NULL,
    [CompanyID] nvarchar(MAX)  NULL,
    [Account01] uniqueidentifier  NULL,
    [ActiveFromDate] datetime  NULL,
    [ActiveToDate] datetime  NULL,
    [ByGroup] uniqueidentifier  NULL,
    [ByUser] uniqueidentifier  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL087' AND xtype='U')
BEGIN
CREATE TABLE [TBL087] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [Caption] nvarchar(255)  NOT NULL,
    [AccountID] uniqueidentifier  NOT NULL,
    [CurrencyID] uniqueidentifier  NOT NULL,
    [DoneIn] datetime  NOT NULL,
    [Value] float  NOT NULL,
    [CurrencyBalance] float  NOT NULL,
    [Notes] ntext  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Services' AND xtype='U')
BEGIN
CREATE TABLE [Services] (
    [ServiceID] int IDENTITY(1,1) NOT NULL,
    [ServiceName] nvarchar(100)  NOT NULL,
    [DefaultPrice] decimal  NULL,
    [Price] decimal  NULL,
    [Category] nvarchar(50)  NULL,
    [ServiceType] nvarchar(50)  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL127' AND xtype='U')
BEGIN
CREATE TABLE [TBL127] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [ReceiverGuide] uniqueidentifier  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL118' AND xtype='U')
BEGIN
CREATE TABLE [TBL118] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [AccountGuide] uniqueidentifier  NOT NULL,
    [DebitValue] float  NOT NULL,
    [CreditValue] float  NOT NULL,
    [SideType] int  NOT NULL,
    [Ratio] float  NOT NULL,
    [RoundUpValue] float  NOT NULL,
    [Notes] ntext  NULL,
    [NotEffectPrice] bit  NOT NULL,
    [NotEffectTax] bit  NOT NULL,
    [RatioCalculationAsDivision] bit  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL032' AND xtype='U')
BEGIN
CREATE TABLE [TBL032] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [Damage] ntext  NOT NULL,
    [WarrantyIncluded] bit  NOT NULL,
    [MaintenanceMan] uniqueidentifier  NULL,
    [DamageDescription] ntext  NULL,
    [Description] ntext  NULL,
    [Cost] float  NOT NULL,
    [Security] tinyint  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL061' AND xtype='U')
BEGIN
CREATE TABLE [TBL061] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [GroupGuide] uniqueidentifier  NOT NULL,
    [OperationName] nvarchar(255)  NULL,
    [Allow] bit  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL160' AND xtype='U')
BEGIN
CREATE TABLE [TBL160] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [BillGuide] uniqueidentifier  NOT NULL,
    [IsHidden] bit  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL128' AND xtype='U')
BEGIN
CREATE TABLE [TBL128] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [CardNumber] int  NOT NULL,
    [Security] tinyint  NOT NULL,
    [UnitName] nvarchar(255)  NOT NULL,
    [LatinName] nvarchar(255)  NULL,
    [MainUnit] tinyint  NOT NULL,
    [IsFixed] bit  NOT NULL,
    [Quantity] float  NOT NULL,
    [Price] float  NOT NULL,
    [AgentPrice] float  NOT NULL,
    [WholePrice] float  NOT NULL,
    [EndUserPrice] float  NOT NULL,
    [Price5Item] float  NOT NULL,
    [Price6Item] float  NOT NULL,
    [Price7Item] float  NOT NULL,
    [StanderCost] float  NOT NULL,
    [Barcode] nvarchar(255)  NULL,
    [Notes] nvarchar(255)  NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [Weight] float  NOT NULL,
    [Value] float  NOT NULL,
    [Length] float  NOT NULL,
    [Width] float  NOT NULL,
    [Hieght] float  NOT NULL,
    [Points] float  NOT NULL,
    [IsDefault] bit  NOT NULL,
    [AgentPriceCurrency] uniqueidentifier  NULL,
    [WholePriceCurrency] uniqueidentifier  NULL,
    [EndUserPriceCurrency] uniqueidentifier  NULL,
    [Price5ItemCurrency] uniqueidentifier  NULL,
    [Price6ItemCurrency] uniqueidentifier  NULL,
    [Price7ItemCurrency] uniqueidentifier  NULL,
    [StanderCostCurrency] uniqueidentifier  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL100' AND xtype='U')
BEGIN
CREATE TABLE [TBL100] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [TypeID] int  NOT NULL,
    [CardName] nvarchar(255)  NULL,
    [ItemGroupGuide] uniqueidentifier  NULL,
    [MainGroup] uniqueidentifier  NULL,
    [ItemGuide] uniqueidentifier  NULL,
    [CardImage] image  NULL,
    [Notes] nvarchar(255)  NULL,
    [StoreGuide] uniqueidentifier  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TASchedules' AND xtype='U')
BEGIN
CREATE TABLE [TASchedules] (
    [SlotID] int IDENTITY(1,1) NOT NULL,
    [SlotDate] date  NOT NULL,
    [SlotTime] nvarchar(10)  NOT NULL,
    [Status] nvarchar(50)  NULL,
    [Type] nvarchar(50)  NULL,
    [CandidateID] int  NULL,
    [BookedBy] int  NULL,
    [EvaluatorID] int  NULL,
    [Notes] nvarchar(MAX)  NULL,
    [CreatedAt] datetime  NULL,
    [InterviewType] nvarchar(50)  NULL,
    [IsConfirmedByRecruiter] bit  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL033' AND xtype='U')
BEGIN
CREATE TABLE [TBL033] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [Option01] int  NOT NULL,
    [CardType] nvarchar(MAX)  NOT NULL,
    [ShowButton] bit  NOT NULL,
    [PrintCount] int  NOT NULL,
    [CardName] nvarchar(MAX)  NOT NULL,
    [LatinName] nvarchar(MAX)  NULL,
    [ClassID] nvarchar(MAX)  NULL,
    [CardTypeID] int  NOT NULL,
    [CardFile] image  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL062' AND xtype='U')
BEGIN
CREATE TABLE [TBL062] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [GroupGuide] uniqueidentifier  NOT NULL,
    [TabName] nvarchar(255)  NULL,
    [Allow] bit  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL088' AND xtype='U')
BEGIN
CREATE TABLE [TBL088] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CurrencyID] uniqueidentifier  NOT NULL,
    [ContraCurrencyID] uniqueidentifier  NULL,
    [DoneIn] datetime  NOT NULL,
    [Rate] float  NOT NULL,
    [Notes] ntext  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL161' AND xtype='U')
BEGIN
CREATE TABLE [TBL161] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [UserGuide] uniqueidentifier  NULL,
    [GroupGuide] uniqueidentifier  NULL,
    [PCName] nvarchar(255)  NULL,
    [PrinterName] nvarchar(255)  NULL,
    [PrintCount] int  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL142' AND xtype='U')
BEGIN
CREATE TABLE [TBL142] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [CardNumber] int  NOT NULL,
    [CardDate] datetime  NOT NULL,
    [Security] tinyint  NOT NULL,
    [BillGuide] uniqueidentifier  NULL,
    [AgentGuide] uniqueidentifier  NOT NULL,
    [Additions] float  NOT NULL,
    [Discounts] float  NOT NULL,
    [CardImage] image  NULL,
    [Notes] nvarchar(255)  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL089' AND xtype='U')
BEGIN
CREATE TABLE [TBL089] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [AgentGuide] uniqueidentifier  NULL,
    [UserGuide] uniqueidentifier  NOT NULL,
    [InsertedIn] datetime  NOT NULL,
    [TypeID] tinyint  NOT NULL,
    [Boolean01] bit  NOT NULL,
    [DoneIn] datetime  NOT NULL,
    [CostCenter01] uniqueidentifier  NULL,
    [Category01] uniqueidentifier  NULL,
    [Category02] uniqueidentifier  NULL,
    [Category03] uniqueidentifier  NULL,
    [Category04] uniqueidentifier  NULL,
    [Description1] nvarchar(255)  NULL,
    [Description2] nvarchar(255)  NULL,
    [Description3] nvarchar(255)  NULL,
    [Notes1] ntext  NULL,
    [Notes2] ntext  NULL,
    [Notes3] ntext  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Evaluations' AND xtype='U')
BEGIN
CREATE TABLE [Evaluations] (
    [EvaluationID] int IDENTITY(1,1) NOT NULL,
    [CandidateID] int  NULL,
    [SlotID] int  NULL,
    [Score_Comprehension] int  NULL,
    [Score_Fluency] int  NULL,
    [Score_Pronunciation] int  NULL,
    [Score_Structure] int  NULL,
    [Score_Vocabulary] int  NULL,
    [CEFR_Level] nvarchar(10)  NULL,
    [Decision] nvarchar(50)  NULL,
    [RecommendedLevel] nvarchar(50)  NULL,
    [Comments] nvarchar(MAX)  NULL,
    [EvaluatorID] int  NULL,
    [EvaluationDate] datetime  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL063' AND xtype='U')
BEGIN
CREATE TABLE [TBL063] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [ItemGuide] uniqueidentifier  NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [Unit] tinyint  NOT NULL,
    [Quantity] float  NOT NULL,
    [PriceRatio] float  NOT NULL,
    [Category01] uniqueidentifier  NULL,
    [Category02] uniqueidentifier  NULL,
    [Category03] uniqueidentifier  NULL,
    [Category04] uniqueidentifier  NULL,
    [Category05] uniqueidentifier  NULL,
    [RelatedUnit] uniqueidentifier  NULL,
    [UnitQuantity] float  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL101' AND xtype='U')
BEGIN
CREATE TABLE [TBL101] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [CardName] nvarchar(255)  NOT NULL,
    [TextValue] nvarchar(255)  NULL,
    [MainGuide] uniqueidentifier  NULL,
    [UserGuide] uniqueidentifier  NULL,
    [TypeID] tinyint  NOT NULL,
    [MainType] tinyint  NOT NULL,
    [Notes] nvarchar(255)  NULL,
    [OptionGuide] uniqueidentifier  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL119' AND xtype='U')
BEGIN
CREATE TABLE [TBL119] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [CardNumber] int  NOT NULL,
    [CardName] nvarchar(255)  NOT NULL,
    [CardLatinName] nvarchar(255)  NULL,
    [BondGuide] uniqueidentifier  NULL,
    [BillGuide] uniqueidentifier  NULL,
    [OperationBillGuide] uniqueidentifier  NULL,
    [DefaultCurrency] uniqueidentifier  NULL,
    [DefaultAccount] uniqueidentifier  NULL,
    [Security] tinyint  NOT NULL,
    [BondType] int  NOT NULL,
    [CardType] int  NOT NULL,
    [AutoBuildBond] bit  NOT NULL,
    [Boolean01] bit  NOT NULL,
    [Option01] int  NOT NULL,
    [Option02] int  NOT NULL,
    [Notes] nvarchar(255)  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL046' AND xtype='U')
BEGIN
CREATE TABLE [TBL046] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] nvarchar(255)  NOT NULL,
    [CardTerm] nvarchar(255)  NOT NULL,
    [CardImage] image  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL023' AND xtype='U')
BEGIN
CREATE TABLE [TBL023] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [InsertedIn] datetime  NOT NULL,
    [RowGuide] uniqueidentifier  NOT NULL,
    [ProductGuide] uniqueidentifier  NOT NULL,
    [Quantity] float  NOT NULL,
    [ExtraQuantity] float  NOT NULL,
    [Unit] tinyint  NOT NULL,
    [TotalValue] float  NOT NULL,
    [TotalValue2] float  NOT NULL,
    [TotalCost] float  NOT NULL,
    [DiscountValue] float  NOT NULL,
    [Discount0] float  NOT NULL,
    [Discount1] float  NOT NULL,
    [Discount2] float  NOT NULL,
    [Discount3] float  NOT NULL,
    [ExtraValue] float  NOT NULL,
    [TaxValue] float  NOT NULL,
    [BillTax] float  NOT NULL,
    [StoreID] uniqueidentifier  NULL,
    [StatementName] nvarchar(255)  NULL,
    [ExpiryDate] datetime  NULL,
    [EstablishDate] datetime  NULL,
    [Color] ntext  NULL,
    [Weight] float  NOT NULL,
    [Value] float  NOT NULL,
    [Length] float  NOT NULL,
    [Width] float  NOT NULL,
    [Hieght] float  NOT NULL,
    [Description] nvarchar(MAX)  NULL,
    [CostCenter] uniqueidentifier  NULL,
    [BillCustom1] nvarchar(255)  NULL,
    [BillCustom2] nvarchar(255)  NULL,
    [BillCustom3] nvarchar(255)  NULL,
    [BillCustom4] nvarchar(255)  NULL,
    [BillCustom5] nvarchar(255)  NULL,
    [PatchCode] nvarchar(255)  NULL,
    [Category01] uniqueidentifier  NULL,
    [Category02] uniqueidentifier  NULL,
    [Category03] uniqueidentifier  NULL,
    [Category04] uniqueidentifier  NULL,
    [Category05] uniqueidentifier  NULL,
    [SourceBill] uniqueidentifier  NULL,
    [ProductsAccount] uniqueidentifier  NULL,
    [RelatedAgent] uniqueidentifier  NULL,
    [CurrentStage] uniqueidentifier  NULL,
    [RelatedUnit] uniqueidentifier  NULL,
    [UnitQuantity] float  NOT NULL,
    [SalesPrice] float  NOT NULL,
    [Quantity2] float  NOT NULL,
    [Description2] nvarchar(255)  NULL,
    [RelatedObjects] nvarchar(255)  NULL,
    [Printed] bit  NOT NULL,
    [Nonmergeable] bit  NOT NULL,
    [RecordDate] datetime  NULL,
    [ReserveDate] datetime  NULL,
    [ActivateDate] datetime  NULL,
    [RecordSecurity] tinyint  NOT NULL,
    [CalcKeyField] uniqueidentifier  NULL,
    [ExternalRelation] ntext  NULL,
    [ExternalSourceBill] uniqueidentifier  NULL,
    [OfferGuide] uniqueidentifier  NULL,
    [UnitQuantity2] float  NOT NULL,
    [ExcludeQtyFromRelations] bit  NULL,
    [UnitExtraQuantity] float  NOT NULL,
    [Project] uniqueidentifier  NULL,
    [Branch] uniqueidentifier  NULL,
    [Saved_TaxRatio] float  NOT NULL,
    [Saved_Calc01] float  NOT NULL,
    [Saved_Calc02] float  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='WeeklyProgress' AND xtype='U')
BEGIN
CREATE TABLE [WeeklyProgress] (
    [ProgressID] int IDENTITY(1,1) NOT NULL,
    [EnrollmentID] int  NULL,
    [WeekNumber] int  NOT NULL,
    [Strengths] nvarchar(MAX)  NULL,
    [Weaknesses] nvarchar(MAX)  NULL,
    [RFI] nvarchar(MAX)  NULL,
    [ActionPlan] nvarchar(MAX)  NULL,
    [Severity] nvarchar(20)  NULL,
    [TrainerID] int  NULL,
    [CreatedAt] datetime  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL047' AND xtype='U')
BEGIN
CREATE TABLE [TBL047] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [GroupGuide] uniqueidentifier  NOT NULL,
    [CardGuide] nvarchar(255)  NOT NULL,
    [CardValue] float  NOT NULL,
    [Browsing] bit  NOT NULL,
    [Saving] bit  NOT NULL,
    [Exporting] bit  NOT NULL,
    [Deleting] bit  NOT NULL,
    [AdvancedPrint] bit  NOT NULL,
    [ExcelTemplates] bit  NOT NULL,
    [PrintPreview] tinyint  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Schedules' AND xtype='U')
BEGIN
CREATE TABLE [Schedules] (
    [ScheduleID] int IDENTITY(1,1) NOT NULL,
    [Context] nvarchar(50)  NOT NULL,
    [OwnerUserID] int  NULL,
    [OwnerClientID] int  NULL,
    [SlotDate] date  NOT NULL,
    [SlotTime] nvarchar(10)  NOT NULL,
    [Status] nvarchar(50)  NULL,
    [BookedCandidateID] int  NULL,
    [BookingMode] nvarchar(50)  NULL,
    [MeetingLink] nvarchar(MAX)  NULL,
    [Notes] nvarchar(MAX)  NULL,
    [CreatedAt] datetime  NULL,
    [IsConfirmedByRecruiter] bit  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL143' AND xtype='U')
BEGIN
CREATE TABLE [TBL143] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [SerialCode] nvarchar(255)  NOT NULL,
    [ExpiryDate] datetime  NULL,
    [EstablishDate] datetime  NULL,
    [Notes] nvarchar(255)  NULL,
    [CardImage] image  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL007' AND xtype='U')
BEGIN
CREATE TABLE [TBL007] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [CardCode] nvarchar(255)  NOT NULL,
    [ProductName] nvarchar(255)  NOT NULL,
    [LatinName] nvarchar(255)  NULL,
    [StatementName] nvarchar(255)  NULL,
    [Source] nvarchar(255)  NULL,
    [StockProduct] smallint  NULL,
    [ListAlternatives] bit  NULL,
    [GroupGuid] uniqueidentifier  NOT NULL,
    [DefaultCurrency] uniqueidentifier  NULL,
    [AccountID] uniqueidentifier  NULL,
    [RelatedAgent] uniqueidentifier  NULL,
    [Security] tinyint  NOT NULL,
    [Specification] nvarchar(MAX)  NULL,
    [ProductType] tinyint  NOT NULL,
    [ItemColor] int  NULL,
    [DefaultUnit] smallint  NULL,
    [NotActive] bit  NOT NULL,
    [NotTaxable] bit  NOT NULL,
    [ManuallyActivate] bit  NOT NULL,
    [NotDiscountable] bit  NOT NULL,
    [ExpiryDateRequired] bit  NOT NULL,
    [Custom] nvarchar(255)  NULL,
    [Custom2] nvarchar(255)  NULL,
    [Custom3] nvarchar(255)  NULL,
    [Custom4] nvarchar(255)  NULL,
    [Custom5] nvarchar(255)  NULL,
    [Unit] nvarchar(255)  NULL,
    [Unit2] nvarchar(255)  NULL,
    [Unit3] nvarchar(255)  NULL,
    [Barcode] nvarchar(255)  NULL,
    [Barcode2] nvarchar(255)  NULL,
    [Barcode3] nvarchar(255)  NULL,
    [Weight] float  NOT NULL,
    [Value] float  NOT NULL,
    [Length] float  NOT NULL,
    [Width] float  NOT NULL,
    [Hieght] float  NOT NULL,
    [Weight2] float  NOT NULL,
    [Value2] float  NOT NULL,
    [Length2] float  NOT NULL,
    [Width2] float  NOT NULL,
    [Hieght2] float  NOT NULL,
    [Weight3] float  NOT NULL,
    [Value3] float  NOT NULL,
    [Length3] float  NOT NULL,
    [Width3] float  NOT NULL,
    [Hieght3] float  NOT NULL,
    [IsAssets] bit  NOT NULL,
    [DefaultExpiryDate] datetime  NULL,
    [Factor2] float  NULL,
    [Factor3] float  NULL,
    [TaxRatio] float  NULL,
    [MaxLimit] float  NULL,
    [MinLimit] float  NULL,
    [AgentPrice] float  NOT NULL,
    [AgentPrice2] float  NOT NULL,
    [AgentPrice3] float  NOT NULL,
    [AgentPriceTax] float  NOT NULL,
    [AgentPriceCurrency] uniqueidentifier  NULL,
    [WholePrice] float  NOT NULL,
    [WholePrice2] float  NOT NULL,
    [WholePrice3] float  NOT NULL,
    [WholePriceTax] float  NOT NULL,
    [WholePriceCurrency] uniqueidentifier  NULL,
    [EndUserPrice] float  NOT NULL,
    [EndUserPrice2] float  NOT NULL,
    [EndUserPrice3] float  NOT NULL,
    [EndUserPriceTax] float  NOT NULL,
    [EndUserPriceCurrency] uniqueidentifier  NULL,
    [Price5Item] float  NOT NULL,
    [Price5Item2] float  NOT NULL,
    [Price5Item3] float  NOT NULL,
    [Price5ItemTax] float  NOT NULL,
    [Price5ItemCurrency] uniqueidentifier  NULL,
    [Price6Item] float  NOT NULL,
    [Price6Item2] float  NOT NULL,
    [Price6Item3] float  NOT NULL,
    [Price6ItemTax] float  NOT NULL,
    [Price6ItemCurrency] uniqueidentifier  NULL,
    [Price7Item] float  NOT NULL,
    [Price7Item2] float  NOT NULL,
    [Price7Item3] float  NOT NULL,
    [Price7ItemTax] float  NOT NULL,
    [Price7ItemCurrency] uniqueidentifier  NULL,
    [StanderCost] float  NOT NULL,
    [StanderCost2] float  NOT NULL,
    [StanderCost3] float  NOT NULL,
    [StanderCostTax] float  NOT NULL,
    [StanderCostCurrency] uniqueidentifier  NULL,
    [CardOrder] int  NOT NULL,
    [Points] float  NOT NULL,
    [Points2] float  NOT NULL,
    [Points3] float  NOT NULL,
    [Category01] uniqueidentifier  NULL,
    [Category02] uniqueidentifier  NULL,
    [Category03] uniqueidentifier  NULL,
    [Category04] uniqueidentifier  NULL,
    [Category05] uniqueidentifier  NULL,
    [CardImage] image  NULL,
    [ByUser] uniqueidentifier  NULL,
    [DefaultVariableUnit] uniqueidentifier  NULL,
    [ByGroup] uniqueidentifier  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL102' AND xtype='U')
BEGIN
CREATE TABLE [TBL102] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [DeviceType] tinyint  NOT NULL,
    [DeviceName] nvarchar(255)  NULL,
    [ConnectionType] tinyint  NOT NULL,
    [Details] nvarchar(255)  NULL,
    [Info01] nvarchar(255)  NULL,
    [Info02] nvarchar(255)  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL064' AND xtype='U')
BEGIN
CREATE TABLE [TBL064] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [GroupGuide] uniqueidentifier  NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [CardValue] float  NOT NULL,
    [BrowsingPosted] tinyint  NOT NULL,
    [InsertingPosted] tinyint  NOT NULL,
    [UpdatingPosted] tinyint  NOT NULL,
    [DeletingPosted] tinyint  NOT NULL,
    [PrintingPosted] tinyint  NOT NULL,
    [BrowsePrices] tinyint  NOT NULL,
    [Posting] tinyint  NOT NULL,
    [BuildEntryPosted] tinyint  NOT NULL,
    [ChangePricesPosted] tinyint  NOT NULL,
    [PostedDiscountRatio] float  NOT NULL,
    [PostedExtraRatio] float  NOT NULL,
    [SubtractOutput] bit  NOT NULL,
    [BrowsingUnPosted] tinyint  NOT NULL,
    [InsertingUnPosted] tinyint  NOT NULL,
    [UpdatingUnPosted] tinyint  NOT NULL,
    [DeletingUnPosted] tinyint  NOT NULL,
    [PrintingUnPosted] tinyint  NOT NULL,
    [PrintingUnSaved] tinyint  NOT NULL,
    [BuildEntryUnPosted] tinyint  NOT NULL,
    [ChangePricesUnPosted] tinyint  NOT NULL,
    [UnPostedExtraRatio] float  NOT NULL,
    [UnPostedDiscountRatio] float  NOT NULL,
    [ChangeStockItemsPrice] bit  NOT NULL,
    [ModelPrint] tinyint  NOT NULL,
    [ModelDelete] tinyint  NOT NULL,
    [ModelAdd] tinyint  NOT NULL,
    [ModelUpdate] tinyint  NOT NULL,
    [MinimumPrice] tinyint  NOT NULL,
    [MaximumPrice] tinyint  NOT NULL,
    [ChangeServiceItemsPrice] bit  NOT NULL,
    [ChangeQuantity] bit  NOT NULL,
    [ChangeQuantity2] bit  NOT NULL,
    [PostedBillDiscountRatio] float  NOT NULL,
    [PostedBillExtraRatio] float  NOT NULL,
    [UnPostedBillExtraRatio] float  NOT NULL,
    [UnPostedBillDiscountRatio] float  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL090' AND xtype='U')
BEGIN
CREATE TABLE [TBL090] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [DoneIn] datetime  NOT NULL,
    [RememberIn] datetime  NULL,
    [InsertedIn] datetime  NOT NULL,
    [UserGuide] uniqueidentifier  NOT NULL,
    [HideIt] tinyint  NOT NULL,
    [Description1] nvarchar(255)  NULL,
    [Description2] nvarchar(255)  NULL,
    [Description3] nvarchar(255)  NULL,
    [Notes1] ntext  NULL,
    [Notes2] ntext  NULL,
    [Notes3] ntext  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL034' AND xtype='U')
BEGIN
CREATE TABLE [TBL034] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [ControlName] nvarchar(MAX)  NOT NULL,
    [ControlType] int  NOT NULL,
    [IntValue01] int  NULL,
    [CardImage] image  NULL,
    [PrintType] tinyint  NOT NULL,
    [MainCr] nvarchar(MAX)  NULL,
    [TextValue] ntext  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL144' AND xtype='U')
BEGIN
CREATE TABLE [TBL144] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [CardNumber] int  NOT NULL,
    [CardDate] datetime  NOT NULL,
    [CardName] nvarchar(250)  NULL,
    [Security] tinyint  NOT NULL,
    [NotActive] bit  NOT NULL,
    [UseExtraQuantity] bit  NOT NULL,
    [Quantity] float  NOT NULL,
    [BillsCount] float  NOT NULL,
    [AgentGroupGuide] uniqueidentifier  NULL,
    [AgentGuide] uniqueidentifier  NULL,
    [CostCenterGuide] uniqueidentifier  NULL,
    [ProjectGuide] uniqueidentifier  NULL,
    [BranchGuide] uniqueidentifier  NULL,
    [PayMethod] tinyint  NOT NULL,
    [OfferType] int  NOT NULL,
    [OfferValue] float  NOT NULL,
    [OfferDiscount] float  NOT NULL,
    [DateStart] datetime  NULL,
    [DateEnd] datetime  NULL,
    [TimeStart] datetime  NULL,
    [TimeEnd] datetime  NULL,
    [ItemUseType] int  NOT NULL,
    [Notes] ntext  NULL,
    [AgentCostCenter] uniqueidentifier  NULL,
    [AgentProject] uniqueidentifier  NULL,
    [AgentBranch] uniqueidentifier  NULL,
    [AgentAddress] uniqueidentifier  NULL,
    [AgentCategory01] uniqueidentifier  NULL,
    [AgentCategory02] uniqueidentifier  NULL,
    [IntValue01] int  NOT NULL,
    [BitValue01] bit  NOT NULL,
    [BitValue02] bit  NOT NULL,
    [BitValue03] bit  NOT NULL,
    [Number01] float  NOT NULL,
    [Number02] float  NOT NULL,
    [CustomNumber01] float  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='UnitTypes' AND xtype='U')
BEGIN
CREATE TABLE [UnitTypes] (
    [UnitID] int IDENTITY(1,1) NOT NULL,
    [UnitCode] nvarchar(10)  NULL,
    [UnitName] nvarchar(50)  NULL,
    [UnitNameAR] nvarchar(50)  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL103' AND xtype='U')
BEGIN
CREATE TABLE [TBL103] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [ItemGuide] uniqueidentifier  NULL,
    [GroupGuide] uniqueidentifier  NULL,
    [MinQuantity] float  NOT NULL,
    [BillType] uniqueidentifier  NULL,
    [RelatedUnit] uniqueidentifier  NULL,
    [CostCenter] uniqueidentifier  NULL,
    [Branch] uniqueidentifier  NULL,
    [Project] uniqueidentifier  NULL,
    [Category01] uniqueidentifier  NULL,
    [Category02] uniqueidentifier  NULL,
    [Category03] uniqueidentifier  NULL,
    [Category04] uniqueidentifier  NULL,
    [Category05] uniqueidentifier  NULL,
    [AgentGuide] uniqueidentifier  NULL,
    [AgentGroup] uniqueidentifier  NULL,
    [AgentCostCenter] uniqueidentifier  NULL,
    [AgentBranch] uniqueidentifier  NULL,
    [AgentProject] uniqueidentifier  NULL,
    [AgentCategory01] uniqueidentifier  NULL,
    [AgentCategory02] uniqueidentifier  NULL,
    [AgentCategory03] uniqueidentifier  NULL,
    [AgentCategory04] uniqueidentifier  NULL,
    [AgentCategory05] uniqueidentifier  NULL,
    [Price] float  NOT NULL,
    [DiscountRatio] float  NOT NULL,
    [ExtraRatio] float  NOT NULL,
    [CurrencyGuide] uniqueidentifier  NULL,
    [PriceType] int  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL035' AND xtype='U')
BEGIN
CREATE TABLE [TBL035] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [MainID] int  NOT NULL,
    [PropertyName] nvarchar(MAX)  NOT NULL,
    [PropertyValue] nvarchar(MAX)  NULL,
    [PropertyValue2] nvarchar(MAX)  NULL,
    [PropertyValue3] nvarchar(MAX)  NULL,
    [PropertyNumberValue] float  NOT NULL,
    [ControlImage] image  NULL,
    [PropertyValue4] nvarchar(MAX)  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TrainingPlans' AND xtype='U')
BEGIN
CREATE TABLE [TrainingPlans] (
    [PlanID] int IDENTITY(1,1) NOT NULL,
    [EnrollmentID] int  NULL,
    [WeekNumber] int  NOT NULL,
    [FocusArea] nvarchar(200)  NULL,
    [TargetGoals] nvarchar(MAX)  NULL,
    [CreatedBy] int  NULL,
    [CreatedAt] datetime  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL091' AND xtype='U')
BEGIN
CREATE TABLE [TBL091] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [InsertedIn] datetime  NOT NULL,
    [EventID] smallint  NOT NULL,
    [ObjectID] int  NOT NULL,
    [UserGuide] uniqueidentifier  NULL,
    [CardGuide] uniqueidentifier  NULL,
    [PCID] nvarchar(255)  NOT NULL,
    [CardName] nvarchar(500)  NULL,
    [FormName] varchar(50)  NULL,
    [FormKey] uniqueidentifier  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL129' AND xtype='U')
BEGIN
CREATE TABLE [TBL129] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [BillGuide] uniqueidentifier  NOT NULL,
    [BillSide] smallint  NULL,
    [IsHidden] bit  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL048' AND xtype='U')
BEGIN
CREATE TABLE [TBL048] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [GroupGuide] uniqueidentifier  NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [CardValue] ntext  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='POS_Data' AND xtype='U')
BEGIN
CREATE TABLE [POS_Data] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [BranchNo] nvarchar(255)  NULL,
    [VendorName] nvarchar(255)  NULL,
    [ModelName] nvarchar(255)  NULL,
    [OperatingSystem] nvarchar(255)  NULL,
    [DeviceName] nvarchar(255)  NULL,
    [Status] nvarchar(255)  NULL,
    [Description] nvarchar(255)  NULL,
    [TaxpayerBranch] nvarchar(255)  NULL,
    [SerialNumber] nvarchar(255)  NULL,
    [ActiveFrom] datetime  NULL,
    [ActiveTo] datetime  NULL,
    [clientID] nvarchar(255)  NULL,
    [clientSecret1] nvarchar(255)  NULL,
    [clientSecret2] nvarchar(255)  NULL,
    [ClintID_Pre] nvarchar(100)  NULL,
    [ClintSecret1_Pre] nvarchar(100)  NULL,
    [ClintSecret2_Pre] nvarchar(100)  NULL,
    [CompanyID] int  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL120' AND xtype='U')
BEGIN
CREATE TABLE [TBL120] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [CardNumber] int  NOT NULL,
    [CurrencyGuide] uniqueidentifier  NULL,
    [Rate] float  NOT NULL,
    [MainAdmin] uniqueidentifier  NULL,
    [MainBill] uniqueidentifier  NULL,
    [AgentGuide] uniqueidentifier  NULL,
    [AccountGuide] uniqueidentifier  NULL,
    [CostCenter] uniqueidentifier  NULL,
    [Project] uniqueidentifier  NULL,
    [Branch] uniqueidentifier  NULL,
    [CardDate] datetime  NOT NULL,
    [CardDate2] datetime  NULL,
    [DoneIn] datetime  NOT NULL,
    [NumberValue01] float  NOT NULL,
    [IntValue01] int  NOT NULL,
    [Security] tinyint  NOT NULL,
    [CardImage] image  NULL,
    [Notes] nvarchar(255)  NULL,
    [CardDate3] datetime  NULL,
    [BondType1] uniqueidentifier  NULL,
    [BondType2] uniqueidentifier  NULL,
    [ByGroup] uniqueidentifier  NULL,
    [ByUser] uniqueidentifier  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL092' AND xtype='U')
BEGIN
CREATE TABLE [TBL092] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [AgentGuide] uniqueidentifier  NOT NULL,
    [JobGuide] uniqueidentifier  NULL,
    [TypeID] smallint  NOT NULL,
    [SalaryType] smallint  NOT NULL,
    [TextValue01] nvarchar(255)  NULL,
    [TextValue02] nvarchar(255)  NULL,
    [TextValue03] nvarchar(255)  NULL,
    [TextValue04] nvarchar(255)  NULL,
    [TextValue05] nvarchar(255)  NULL,
    [DateValue01] datetime  NULL,
    [DateValue02] datetime  NULL,
    [NumberValue01] float  NOT NULL,
    [NumberValue02] float  NOT NULL,
    [NumberValue03] float  NOT NULL,
    [AccountGuide] uniqueidentifier  NULL,
    [IntValue01] float  NOT NULL,
    [IntValue02] int  NOT NULL,
    [CurrencyGuide] uniqueidentifier  NULL,
    [Category01] uniqueidentifier  NULL,
    [Category02] uniqueidentifier  NULL,
    [Category03] uniqueidentifier  NULL,
    [Category04] uniqueidentifier  NULL,
    [Category05] uniqueidentifier  NULL,
    [RelatedAdministration] uniqueidentifier  NULL,
    [CardImage] image  NULL,
    [Attachment] image  NULL,
    [LongText01] nvarchar(MAX)  NULL,
    [LongText02] nvarchar(MAX)  NULL,
    [Notes] nvarchar(255)  NULL,
    [TextValue06] nvarchar(255)  NULL,
    [TextValue07] nvarchar(255)  NULL,
    [LongTextValue] nvarchar(MAX)  NULL,
    [RelatedAdministration2] uniqueidentifier  NULL,
    [BitValue01] bit  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL036' AND xtype='U')
BEGIN
CREATE TABLE [TBL036] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [TermKey] nvarchar(255)  NOT NULL,
    [Lang00] nvarchar(255)  NULL,
    [Lang01] nvarchar(255)  NULL,
    [Lang02] nvarchar(255)  NULL,
    [Lang03] nvarchar(255)  NULL,
    [Lang04] nvarchar(255)  NULL,
    [Lang05] nvarchar(255)  NULL,
    [Lang06] nvarchar(255)  NULL,
    [Lang07] nvarchar(255)  NULL,
    [Lang08] nvarchar(255)  NULL,
    [Lang09] nvarchar(255)  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='ClientInterviews' AND xtype='U')
BEGIN
CREATE TABLE [ClientInterviews] (
    [InterviewID] int IDENTITY(1,1) NOT NULL,
    [MatchID] int  NULL,
    [InterviewDate] datetime  NULL,
    [Status] nvarchar(50)  NULL,
    [Feedback] nvarchar(MAX)  NULL,
    [RejectionReason] nvarchar(100)  NULL,
    [ActionRequired] nvarchar(200)  NULL,
    [RecordedBy] int  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL010' AND xtype='U')
BEGIN
CREATE TABLE [TBL010] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [BondNumber] int  NOT NULL,
    [PayType] uniqueidentifier  NULL,
    [TimeLength] int  NOT NULL,
    [BondNumber2] int  NOT NULL,
    [DocumentNumber] nvarchar(255)  NULL,
    [Posted] tinyint  NOT NULL,
    [Collected] bit  NOT NULL,
    [Boolean01] bit  NOT NULL,
    [Boolean02] bit  NOT NULL,
    [Security] tinyint  NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [MainGuide2] uniqueidentifier  NULL,
    [BondDate] datetime  NOT NULL,
    [BondDate2] datetime  NULL,
    [OperationDate] datetime  NULL,
    [DueDate] datetime  NULL,
    [DoneIn] datetime  NOT NULL,
    [CurrencyGuide] uniqueidentifier  NOT NULL,
    [AccountGuide] uniqueidentifier  NULL,
    [AccountGuide2] uniqueidentifier  NULL,
    [AccountGuide3] uniqueidentifier  NULL,
    [AgentGuide] uniqueidentifier  NULL,
    [AgentGuide2] uniqueidentifier  NULL,
    [Project] uniqueidentifier  NULL,
    [Branch] uniqueidentifier  NULL,
    [CostCenter] uniqueidentifier  NULL,
    [DynamicBond] uniqueidentifier  NULL,
    [RelatedAdministration] uniqueidentifier  NULL,
    [Rate] float  NOT NULL,
    [Value] float  NOT NULL,
    [Value2] float  NOT NULL,
    [Value3] float  NOT NULL,
    [Notes] nvarchar(255)  NULL,
    [BondNotes2] nvarchar(255)  NULL,
    [BondNotes3] nvarchar(255)  NULL,
    [BondNotes4] nvarchar(255)  NULL,
    [BondNotes5] nvarchar(255)  NULL,
    [BondNotes6] nvarchar(255)  NULL,
    [BondNotes7] nvarchar(255)  NULL,
    [BondNotes8] nvarchar(255)  NULL,
    [BondNotes9] nvarchar(255)  NULL,
    [BondNotes10] nvarchar(255)  NULL,
    [BillGuide] uniqueidentifier  NULL,
    [BillGuide2] uniqueidentifier  NULL,
    [RelatedBillType] uniqueidentifier  NULL,
    [MainBondType] uniqueidentifier  NULL,
    [RelatedArchive] uniqueidentifier  NULL,
    [RelatedArchive2] uniqueidentifier  NULL,
    [InsertedIn] datetime  NOT NULL,
    [Category01] uniqueidentifier  NULL,
    [Category02] uniqueidentifier  NULL,
    [Category03] uniqueidentifier  NULL,
    [Category04] uniqueidentifier  NULL,
    [Category05] uniqueidentifier  NULL,
    [ByUser] uniqueidentifier  NULL,
    [ByGroup] uniqueidentifier  NULL,
    [CardType] tinyint  NOT NULL,
    [CardImage] image  NULL,
    [BankGuide] uniqueidentifier  NULL,
    [CheckID01] int  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL049' AND xtype='U')
BEGIN
CREATE TABLE [TBL049] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [NotActive] bit  NOT NULL,
    [CardCode] nvarchar(255)  NOT NULL,
    [Security] tinyint  NOT NULL,
    [IntValue] int  NOT NULL,
    [DefaultAccount] uniqueidentifier  NULL,
    [DefaultAccount2] uniqueidentifier  NULL,
    [ProjectName] nvarchar(255)  NOT NULL,
    [LatinName] nvarchar(255)  NULL,
    [MainProject] uniqueidentifier  NULL,
    [Notes] nvarchar(255)  NULL,
    [ProjectNotes2] nvarchar(255)  NULL,
    [ProjectNotes3] nvarchar(255)  NULL,
    [ProjectNotes4] nvarchar(255)  NULL,
    [ProjectNotes5] nvarchar(255)  NULL,
    [ProjectNotes6] nvarchar(255)  NULL,
    [CardImage] image  NULL,
    [ByUser] uniqueidentifier  NULL,
    [ByGroup] uniqueidentifier  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL037' AND xtype='U')
BEGIN
CREATE TABLE [TBL037] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [TypeName] nvarchar(255)  NOT NULL,
    [TypeLatinName] nvarchar(255)  NULL,
    [MCount] int  NOT NULL,
    [MainID] int  NOT NULL,
    [Notes] ntext  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL027' AND xtype='U')
BEGIN
CREATE TABLE [TBL027] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [CardGuide] uniqueidentifier  NOT NULL,
    [CardNumber] int  NOT NULL,
    [DoneIn] datetime  NOT NULL,
    [InsertedIn] datetime  NOT NULL,
    [CurrencyGuide1] uniqueidentifier  NULL,
    [CurrencyGuide2] uniqueidentifier  NULL,
    [RelatedBill1] uniqueidentifier  NULL,
    [RelatedBill2] uniqueidentifier  NULL,
    [MainBillGuide] uniqueidentifier  NULL,
    [Rate1] float  NOT NULL,
    [Rate2] float  NOT NULL,
    [CreditCard] uniqueidentifier  NULL,
    [ManufacturerModel] uniqueidentifier  NULL,
    [MainTransaction] uniqueidentifier  NULL,
    [PayMethod1] smallint  NOT NULL,
    [StoreGuide1] uniqueidentifier  NOT NULL,
    [StoreGuide2] uniqueidentifier  NULL,
    [AgentGuide1] uniqueidentifier  NULL,
    [AgentGuide2] uniqueidentifier  NULL,
    [AccountA1] uniqueidentifier  NULL,
    [AccountA2] uniqueidentifier  NULL,
    [AccountB1] uniqueidentifier  NULL,
    [AccountB2] uniqueidentifier  NULL,
    [CostCenter1] uniqueidentifier  NULL,
    [CostCenter2] uniqueidentifier  NULL,
    [Project1] uniqueidentifier  NULL,
    [Project2] uniqueidentifier  NULL,
    [Branch1] uniqueidentifier  NULL,
    [Branch2] uniqueidentifier  NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [InDate] datetime  NULL,
    [InDate2] datetime  NULL,
    [Customer] nvarchar(255)  NULL,
    [CustomerName] nvarchar(255)  NULL,
    [Security] tinyint  NOT NULL,
    [TaxValue] float  NOT NULL,
    [BuildBillNotes1] nvarchar(255)  NULL,
    [BuildBillNotes2] nvarchar(255)  NULL,
    [BuildBillNotes3] nvarchar(255)  NULL,
    [BuildBillNotes4] nvarchar(255)  NULL,
    [BuildBillNotes5] nvarchar(255)  NULL,
    [BuildBillNotes6] nvarchar(255)  NULL,
    [Ready] bit  NOT NULL,
    [TimeLong] float  NOT NULL,
    [CostLimit] float  NOT NULL,
    [SentTo] nvarchar(255)  NULL,
    [Cost] float  NOT NULL,
    [Price] float  NOT NULL,
    [Returned] bit  NOT NULL,
    [Posted] bit  NOT NULL,
    [Posted1] bit  NOT NULL,
    [Posted2] bit  NOT NULL,
    [IntValue01] int  NOT NULL,
    [IntValue02] int  NOT NULL,
    [CardImage] image  NULL,
    [DownPayment1] float  NOT NULL,
    [ChangeValue] float  NOT NULL,
    [Receiver] nvarchar(255)  NULL,
    [Delivered] bit  NOT NULL,
    [WithAttachment] bit  NOT NULL,
    [CurrentStage] uniqueidentifier  NULL,
    [Barcode] nvarchar(255)  NULL,
    [Description] ntext  NULL,
    [ByUser] uniqueidentifier  NULL,
    [ByGroup] uniqueidentifier  NULL,
    [Number01] float  NOT NULL,
    [Number02] float  NOT NULL,
    [InDate3] datetime  NULL,
    [InDate4] datetime  NULL,
    [TypeID] int  NOT NULL,
    [Category01] uniqueidentifier  NULL,
    [Category02] uniqueidentifier  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL130' AND xtype='U')
BEGIN
CREATE TABLE [TBL130] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [TypeID] tinyint  NOT NULL,
    [ResultType] tinyint  NOT NULL,
    [PeriodID] tinyint  NOT NULL,
    [LongText01] nvarchar(MAX)  NULL,
    [LongText02] nvarchar(MAX)  NULL,
    [Number01] float  NOT NULL,
    [Number02] float  NOT NULL,
    [Number03] float  NOT NULL,
    [Number04] float  NOT NULL,
    [Category01] uniqueidentifier  NULL,
    [Category02] uniqueidentifier  NULL,
    [Category03] uniqueidentifier  NULL,
    [Category04] uniqueidentifier  NULL,
    [Category05] uniqueidentifier  NULL,
    [CurrencyGuide] uniqueidentifier  NULL,
    [AccountGuide] uniqueidentifier  NULL,
    [ContraAccount] uniqueidentifier  NULL,
    [CostCenter] uniqueidentifier  NULL,
    [Branch] uniqueidentifier  NULL,
    [Project] uniqueidentifier  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Governate' AND xtype='U')
BEGIN
CREATE TABLE [Governate] (
    [GovID] smallint  NULL,
    [GovName] nvarchar(20)  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Users' AND xtype='U')
BEGIN
CREATE TABLE [Users] (
    [UserID] int IDENTITY(1,1) NOT NULL,
    [UserName] nvarchar(50)  NULL,
    [UserPassword] nvarchar(50)  NULL,
    [UserType] nvarchar(50)  NULL,
    [CompanyID] int  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='FieldIDBills' AND xtype='U')
BEGIN
CREATE TABLE [FieldIDBills] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [FieldTypeID] int  NOT NULL,
    [FieldName] nvarchar(MAX)  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL038' AND xtype='U')
BEGIN
CREATE TABLE [TBL038] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [RowGuide] uniqueidentifier  NOT NULL,
    [AccountGuide] uniqueidentifier  NOT NULL,
    [CurrencyGuide] uniqueidentifier  NOT NULL,
    [TruncatedValue] float  NOT NULL,
    [TruncatedValueRate] float  NOT NULL,
    [TruncatedValueAccount] uniqueidentifier  NULL,
    [AffectCost] bit  NOT NULL,
    [TruncatedNotes] nvarchar(255)  NULL,
    [Debit] float  NOT NULL,
    [Credit] float  NOT NULL,
    [DebitRate] float  NOT NULL,
    [CreditRate] float  NOT NULL,
    [ContraAccount] uniqueidentifier  NULL,
    [CollectDate] datetime  NULL,
    [RowDate] datetime  NULL,
    [DueDate] datetime  NULL,
    [Collected] bit  NOT NULL,
    [CollectEntry] uniqueidentifier  NULL,
    [Notes] nvarchar(255)  NULL,
    [ChequeNumber] nvarchar(255)  NULL,
    [BondDetailsNotes2] nvarchar(255)  NULL,
    [BondDetailsNotes3] nvarchar(255)  NULL,
    [BondDetailsNotes4] nvarchar(255)  NULL,
    [BondDetailsNotes5] nvarchar(255)  NULL,
    [BondDetailsNotes6] nvarchar(255)  NULL,
    [BondDetailsNotes7] nvarchar(255)  NULL,
    [BondDetailsNotes8] nvarchar(255)  NULL,
    [BondDetailsNotes9] nvarchar(255)  NULL,
    [Beneficiary] nvarchar(255)  NULL,
    [EndorseToAccountGuide] uniqueidentifier  NULL,
    [EndorsementDate] datetime  NULL,
    [ReturnDate] datetime  NULL,
    [RelatedBond] uniqueidentifier  NULL,
    [Checked] tinyint  NULL,
    [Project] uniqueidentifier  NULL,
    [Branch] uniqueidentifier  NULL,
    [CostCenter] uniqueidentifier  NULL,
    [ReturnedAccount] uniqueidentifier  NULL,
    [IntermediateAccount] uniqueidentifier  NULL,
    [Category01] uniqueidentifier  NULL,
    [Category02] uniqueidentifier  NULL,
    [Category03] uniqueidentifier  NULL,
    [Category04] uniqueidentifier  NULL,
    [Category05] uniqueidentifier  NULL,
    [TransferToAccount] uniqueidentifier  NULL,
    [SetoffDate] datetime  NULL,
    [SourceBill] uniqueidentifier  NULL,
    [AgentGuide] uniqueidentifier  NULL,
    [CreditCard] uniqueidentifier  NULL,
    [ContraNotAffected] bit  NOT NULL,
    [NotEndorsable] bit  NOT NULL,
    [CollectOnlyOnItsDate] bit  NOT NULL,
    [CanNotWithdrawAsCash] bit  NOT NULL,
    [ExternalRelation] ntext  NULL,
    [ExternalSourceBill] uniqueidentifier  NULL,
    [BankGuide] uniqueidentifier  NULL,
    [ItemGuide] uniqueidentifier  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TaxTypes' AND xtype='U')
BEGIN
CREATE TABLE [TaxTypes] (
    [TaxID] int IDENTITY(1,1) NOT NULL,
    [TaxCode] nvarchar(255)  NULL,
    [TaxName] nvarchar(255)  NULL,
    [TaxNameAR] nvarchar(255)  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL071' AND xtype='U')
BEGIN
CREATE TABLE [TBL071] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [AccountGuide] uniqueidentifier  NOT NULL,
    [DebitValue] float  NOT NULL,
    [CreditValue] float  NOT NULL,
    [SideType] int  NOT NULL,
    [Ratio] float  NOT NULL,
    [Notes] ntext  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL173' AND xtype='U')
BEGIN
CREATE TABLE [TBL173] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [ItemGuide] uniqueidentifier  NULL,
    [GroupGuide] uniqueidentifier  NULL,
    [TaxRatio] float  NOT NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TBL145' AND xtype='U')
BEGIN
CREATE TABLE [TBL145] (
    [ID] int IDENTITY(1,1) NOT NULL,
    [MainGuide] uniqueidentifier  NOT NULL,
    [GroupID] uniqueidentifier  NULL,
    [TypeID] int  NOT NULL,
    [ItemID] uniqueidentifier  NULL,
    [Quantity] float  NOT NULL,
    [Gifts] float  NOT NULL,
    [ExtraQuantityRule] int  NOT NULL,
    [Unit] int  NOT NULL,
    [PriceValue] float  NOT NULL,
    [ValueFrom] float  NOT NULL,
    [ValueTo] float  NOT NULL,
    [DiscountValue] float  NOT NULL,
    [DiscountRatio] float  NOT NULL,
    [Notes] ntext  NULL,
    [RelatedUnit] uniqueidentifier  NULL
);
END
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='ItemsData' AND xtype='U')
BEGIN
CREATE TABLE [ItemsData] (
    [ItemID] int IDENTITY(1,1) NOT NULL,
    [ItemInternalID] nvarchar(50)  NULL,
    [ItemName] nvarchar(100)  NULL,
    [ItemNameAr] nvarchar(100)  NULL,
    [ItemDesc] nvarchar(100)  NULL,
    [ItemDescAr] nvarchar(100)  NULL,
    [ItemType] nvarchar(5)  NULL,
    [ItemCode] nvarchar(50)  NULL,
    [ItemUnitType] nvarchar(10)  NULL,
    [ItemPrice] float  NULL,
    [ItemActive] bit  NULL,
    [Created] datetime  NULL,
    [Updated] datetime  NULL
);
END
GO

