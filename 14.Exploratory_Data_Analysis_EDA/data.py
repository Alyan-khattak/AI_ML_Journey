
import pandas as pd
import numpy as np
from faker import Faker
import random

fake = Faker()
np.random.seed(42)
random.seed(42)

n = 5000

# Cities and related info
cities = ["Karachi", "Lahore", "Islamabad", "Peshawar", "Quetta", "Multan"]
education_levels = ["Primary", "Secondary", "Bachelors", "Masters", "PhD"]
job_titles = ["Software Engineer", "Data Analyst", "Teacher", "Doctor", "Manager", "Sales Executive", "Accountant", "Designer", None]
departments = ["IT", "HR", "Finance", "Marketing", "Operations", "Sales"]
genders = ["Male", "Female"]
marital_status = ["Single", "Married", "Divorced"]

# Salary based on education (with noise)
edu_salary_map = {
    "Primary": 25000,
    "Secondary": 35000,
    "Bachelors": 60000,
    "Masters": 90000,
    "PhD": 130000
}

educations = np.random.choice(education_levels, n, p=[0.08, 0.15, 0.40, 0.30, 0.07])
base_salaries = [edu_salary_map[e] for e in educations]

data = {
    "employee_id":   [f"EMP{str(i).zfill(4)}" for i in range(1, n+1)],
    "name":          [fake.name() for _ in range(n)],
    "age":           np.random.randint(22, 60, n).tolist(),
    "gender":        np.random.choice(genders, n, p=[0.60, 0.40]).tolist(),
    "city":          np.random.choice(cities, n).tolist(),
    "education":     educations.tolist(),
    "department":    np.random.choice(departments, n).tolist(),
    "job_title":     [random.choice(job_titles) for _ in range(n)],
    "experience_years": np.random.randint(0, 35, n).tolist(),
    "salary":        [int(b + np.random.normal(0, b * 0.15)) for b in base_salaries],
    "bonus_percent": np.random.choice([0, 5, 10, 15, 20, 25], n, p=[0.20, 0.25, 0.25, 0.15, 0.10, 0.05]).tolist(),
    "working_hours_per_week": np.random.randint(20, 65, n).tolist(),
    "performance_rating": np.random.choice(["Poor", "Average", "Good", "Excellent"], n, p=[0.10, 0.30, 0.40, 0.20]).tolist(),
    "remote_work":   np.random.choice(["Yes", "No"], n, p=[0.35, 0.65]).tolist(),
    "joining_year":  np.random.randint(2005, 2024, n).tolist(),
    "last_promotion_year": np.random.randint(2010, 2024, n).tolist(),
    "projects_completed": np.random.randint(0, 50, n).tolist(),
    "training_hours": np.random.randint(0, 200, n).tolist(),
    "satisfaction_score": np.round(np.random.uniform(1.0, 10.0, n), 1).tolist(),
    "left_company":  np.random.choice([0, 1], n, p=[0.75, 0.25]).tolist(),   # TARGET
}

df = pd.DataFrame(data)

# ---- Inject Messiness ----

# 1. Random NaNs across multiple cols
for col in ["job_title", "bonus_percent", "training_hours", "satisfaction_score", "last_promotion_year"]:
    idx = df.sample(frac=0.08).index
    df.loc[idx, col] = np.nan

# 2. Salary outliers
df.loc[np.random.choice(df.index, 30), "salary"] = np.random.choice([-999, 0, 9999999], 30)

# 3. Age outliers
df.loc[np.random.choice(df.index, 20), "age"] = np.random.choice([0, -5, 150], 20)

# 4. Inconsistent gender strings
df.loc[np.random.choice(df[df["gender"]=="Male"].index, 60), "gender"] = np.random.choice(["male", "M", "MALE", "m"], 60)
df.loc[np.random.choice(df[df["gender"]=="Female"].index, 60), "gender"] = np.random.choice(["female", "F", "FEMALE", "f"], 60)

# 5. Duplicate rows (40 duplicates)
dup_rows = df.sample(40)
df = pd.concat([df, dup_rows], ignore_index=True)

# 6. Inconsistent city strings
df.loc[np.random.choice(df.index, 50), "city"] = np.random.choice(["karachi", "LAHORE", "islamabad ", " Multan"], 50)

# 7. Salary as string with 'PKR' prefix in some rows
df["salary"] = df["salary"].astype(str)
idx = np.random.choice(df.index, 80)
df.loc[idx, "salary"] = df.loc[idx, "salary"].apply(lambda x: "PKR" + str(x))

# 8. Joining year as string in some rows
df["joining_year"] = df["joining_year"].astype(str)
idx2 = np.random.choice(df.index, 60)
df.loc[idx2, "joining_year"] = df.loc[idx2, "joining_year"].apply(lambda x: "Year-" + x)

# shuffle
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

df.to_csv("/home/aizen/AI_ML/14.Exploratory_Data_Analysis_EDA/employee_messy.csv", index=False)
print("Shape:", df.shape)
print("Columns:", df.columns.tolist())
print("\nSample:")
print(df.head(3))
print("\nMissing values:")
print(df.isnull().sum())

