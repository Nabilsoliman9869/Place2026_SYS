import sys
import re
import os

def fix_file(filename):
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found.")
        return

    print(f"Processing {filename}...")
    try:
        with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            
        new_lines = []
        current_table = None
        
        for line in lines:
            # 1. Fix Python Booleans (False -> 0, True -> 1)
            # We look for False/True surrounded by delimiters common in SQL VALUES
            line = line.replace(' False,', ' 0,').replace(' True,', ' 1,')
            line = line.replace('(False,', '(0,').replace('(True,', '(1,')
            line = line.replace(', False)', ', 0)').replace(', True)', ', 1)')
            
            # 2. Handle Identity Insert
            # Check if this line is an INSERT statement
            # Regex to capture table name: INSERT INTO [Table] or INSERT INTO Table
            match = re.search(r'INSERT INTO \[?(\w+)\]?', line, re.IGNORECASE)
            if match:
                table = match.group(1)
                
                # If we switched tables, turn OFF the previous one and ON the new one
                if table != current_table:
                    if current_table:
                        new_lines.append(f"SET IDENTITY_INSERT [{current_table}] OFF;\n")
                        new_lines.append("GO\n")
                    
                    current_table = table
                    # Only turn ON if the table actually has an Identity column (we assume yes for dumps with IDs)
                    # To be safe, we wrap it in a try-catch in SQL or just output it.
                    # Since we can't know the schema, we output it. If it fails (no identity), it's just a warning usually.
                    new_lines.append(f"SET IDENTITY_INSERT [{current_table}] ON;\n")
                    new_lines.append("GO\n")
            
            new_lines.append(line)
            
        if current_table:
             new_lines.append(f"SET IDENTITY_INSERT [{current_table}] OFF;\n")
             new_lines.append("GO\n")
             
        output_file = "fixed_" + filename
        with open(output_file, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
            
        print(f"Done! Fixed file saved as: {output_file}")
        print("Please run the new file in SQL Server.")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        fix_file(sys.argv[1])
    else:
        print("Usage: python fix_sql_syntax.py <your_sql_file.sql>")
