import pyodbc
import json
import os

# Configuration
CONFIG_FILE = 'db_config.json'
OUTPUT_FILE = 'schema_export.sql'

def get_connection():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f: config = json.load(f)
    else:
        config = {"server": ".", "port": "1433", "database": "Place2026DB", "use_trusted": True}

    server = config.get("server", ".")
    port = config.get("port", "1433")
    database = config.get("database", "Place2026DB")
    
    if config.get("use_trusted"):
        conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server},{port};DATABASE={database};Trusted_Connection=yes;'
    else:
        conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server},{port};DATABASE={database};UID={config.get("username")};PWD={config.get("password")}'
    
    return pyodbc.connect(conn_str)

def generate_schema_script():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Get list of user tables
        cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
        tables = [row[0] for row in cursor.fetchall()]
        
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write("-- Database Schema Export\n")
            f.write("-- Run this to create missing tables\n\n")
            
            for table in tables:
                print(f"Exporting schema for: {table}")
                f.write(f"IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='{table}' AND xtype='U')\n")
                f.write("BEGIN\n")
                f.write(f"CREATE TABLE [{table}] (\n")
                
                # Get columns
                cursor.execute(f"SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, IS_NULLABLE, COLUMN_DEFAULT FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table}' ORDER BY ORDINAL_POSITION")
                columns = cursor.fetchall()
                
                col_defs = []
                for col in columns:
                    c_name, c_type, c_len, c_null, c_def = col
                    
                    # Format Type
                    if c_type in ['nvarchar', 'varchar', 'char', 'nchar']:
                        type_str = f"{c_type}({c_len if c_len != -1 else 'MAX'})"
                    else:
                        type_str = c_type
                        
                    # Format Nullable
                    null_str = "NULL" if c_null == 'YES' else "NOT NULL"
                    
                    # Format Identity (Simplified check - usually ID columns are identity in this schema)
                    ident_str = ""
                    if c_name.endswith("ID") and c_type == 'int':
                         # Check actual identity property
                         cursor.execute(f"SELECT COLUMNPROPERTY(OBJECT_ID('{table}'),'{c_name}','IsIdentity')")
                         is_ident = cursor.fetchone()[0]
                         if is_ident: ident_str = "IDENTITY(1,1)"

                    line = f"    [{c_name}] {type_str} {ident_str} {null_str}"
                    col_defs.append(line)
                
                f.write(",\n".join(col_defs))
                
                # Add Primary Key Constraint (Simplistic)
                # We assume PK is the first identity column or TableNameID
                # For robust export we should query sys.indexes but this is a quick helper
                
                f.write("\n);\n")
                f.write("END\n")
                f.write("GO\n\n")
                
        print(f"Schema export completed: {OUTPUT_FILE}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generate_schema_script()
