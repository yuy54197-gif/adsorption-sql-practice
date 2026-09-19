"""Day 1：把数据读进来，先搞清楚它长什么样。

运行方式（在任意目录都可以）：
    python day1.py
"""
import os

import pandas as pd

# ---------------------------------------------------------------
# 路径处理：以「脚本所在目录」为基准，而不是「当前工作目录」。
# 这样无论你在哪个目录敲 python day1.py，都能找到数据文件。
# ---------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "adsorption_data.csv")

print("=" * 60)
print("脚本所在目录 :", BASE_DIR)
print("当前工作目录 :", os.getcwd())
print("数据文件路径 :", CSV_PATH)
print("=" * 60)

# ---------------------------------------------------------------
# 1. 读数据
#    encoding="utf-8-sig" 是为了正确处理带 BOM 的中文表头
# ---------------------------------------------------------------
df = pd.read_csv(CSV_PATH, encoding="utf-8-sig")

# ---------------------------------------------------------------
# 2. 看数据长什么样
# ---------------------------------------------------------------
print("\n--- head()：前 5 行 ---")
print(df.head())

print("\n--- shape：(行数, 列数) ---")
print(df.shape)

print("\n--- columns：列名 ---")
print(df.columns)

print("\n--- dtypes：每列的数据类型 ---")
print(df.dtypes)

print("\n--- isna().sum()：每列缺几个值 ---")
print(df.isna().sum())

print("\n--- describe()：数值列的基本统计 ---")
print(df.describe())
