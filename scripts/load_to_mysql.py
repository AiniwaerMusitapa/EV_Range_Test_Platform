import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine

# --------------------------------------------------
# 1. Set project paths
# --------------------------------------------------
base_dir = Path(__file__).resolve().parents[1]
clean_file = base_dir / "data" / "clean" / "range_test_clean.csv"

# --------------------------------------------------
# 2. MySQL connection settings
# --------------------------------------------------
MYSQL_USER = "root"
MYSQL_PASSWORD = "YOUR_PASSWORD"
MYSQL_HOST = "localhost"
MYSQL_PORT = "3306"
MYSQL_DATABASE = "ev_range_test_db"

# --------------------------------------------------
# 3. Create database connection
# --------------------------------------------------
connection_string = (
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
    f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
)

engine = create_engine(connection_string)

# --------------------------------------------------
# 4. Load cleaned CSV
# --------------------------------------------------
df = pd.read_csv(clean_file)

print("Clean data loaded.")
print("Data shape:", df.shape)

# Convert date field to date format
df["test_date"] = pd.to_datetime(df["test_date"]).dt.date

# --------------------------------------------------
# 5. Insert data into MySQL
# --------------------------------------------------
df.to_sql(
    name="range_tests",
    con=engine,
    if_exists="append",
    index=False
)

print("Data inserted into MySQL table: range_tests")