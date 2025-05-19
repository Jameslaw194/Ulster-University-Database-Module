from datetime import datetime

input_file = "serviceemp.txt"
output_file = "serviceemp.sql"

table_name = "Service"
columns = [
    "service_id",
    "employee_id",
    "time_spent"
]

def format_date(date_str):
    try:
        return datetime.strptime(date_str, "%d-%m-%Y").strftime("%Y-%m-%d")
    except ValueError:
        return date_str

def format_value(value, column_name):
    """Format the value for SQL insertion."""
    if value.upper() == "NULL":
        return "NULL"  # No quotes for NULL
    if column_name == "milage" and value.isnumeric():
        return value  # No quotes for numeric milage
    if column_name in {"dropoff_date", "next_service", "date_of_manufacture"}:
        return f"'{format_date(value)}'"  # Format and wrap dates in quotes
    return f"'{value}'"  # Wrap all other values in quotes

# Read and process the data
with open(input_file, "r") as file:
    raw_data = file.read().strip()  # Read the entire file and strip trailing newlines/whitespace

# Split the data into columns
column_data = raw_data.split("#####")
column_data = [col.strip().split("\n") for col in column_data]  # Split each column into rows

# Transpose the data to create rows
rows = list(zip(*column_data))  # Combine corresponding entries from each column into rows

# Generate the SQL INSERT statement
values = ",\n".join([
    f"({', '.join([format_value(value, columns[i]) for i, value in enumerate(row)])})"
    for row in rows
])
sql_statement = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES\n{values};"

# Write the SQL statement to the output file
with open(output_file, "w") as file:
    file.write(sql_statement)

print(f"SQL INSERT statement has been saved to {output_file}.")
