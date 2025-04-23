import pandas as pd
from sqlalchemy import create_engine

DATABASE_FILE = "instance/users.db"
engine = create_engine(f"sqlite:///{DATABASE_FILE}")

query = "SELECT * FROM User"
df = pd.read_sql(query, engine)

df.to_excel("users_export.xlsx", index=False)

print("Database exported successfully to users_export.xlsx!")
