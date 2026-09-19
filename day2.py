"""数据体检 + 正确入库（三张表）

修复上一版的问题：
  1. 算了没存 —— df_model 只存在内存里，没写进数据库
  2. 查了没打印 —— pd.read_sql 的结果没有 print
  3. 非法值 —— Fe 负载量出现负值（物理上不成立）

运行：python day2.py
"""
import os
import sqlite3

import pandas as pd

# ---------- 路径：锚定脚本所在目录，与运行位置无关 ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "adsorption_data.csv")
DB_PATH = os.path.join(BASE_DIR, "adsorption.db")

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 20)

df = pd.read_csv(CSV_PATH, encoding="utf-8-sig")

# ===============================================================
# 第一步：数据体检（真实项目里这一步永远最先做）
# ===============================================================
print("=" * 70)
print("【数据体检】")
print("=" * 70)

print(f"\n1) 规模：{df.shape[0]} 行 × {df.shape[1]} 列")

print("\n2) 缺失值分布：")
miss = df.isna().sum()
print(miss[miss > 0].to_string() if (miss > 0).any() else "   无缺失")

print("\n3) 数值列的越界检查（物理上不可能的值）：")
ranges = {
    "Fe负载量_pct": (0, 100),
    "热解温度_C": (100, 1200),
    "初始质量浓度_mgL": (0, None),
    "pH": (0, 14),
    "投加量_gL": (0, None),
    "吸附时间_h": (0, None),
    "吸附容量_mgg": (0, None),
}
for col, (low, high) in ranges.items():
    s = df[col].dropna()
    bad_low = (s < low).sum() if low is not None else 0
    bad_high = (s > high).sum() if high is not None else 0
    flag = "⚠️ 有越界" if (bad_low or bad_high) else "✅"
    print(f"   {col:18} 范围 [{s.min():.2f}, {s.max():.2f}]  "
          f"下界越界 {bad_low} 条, 上界越界 {bad_high} 条  {flag}")

# ===============================================================
# 第二步：清洗（保留原始，另存清洗版）
# ===============================================================
print("\n" + "=" * 70)
print("【数据清洗】")
print("=" * 70)

df_clean = df.copy()

# 2.1 越界值截断到物理边界（不是删除！）
neg_fe = (df_clean["Fe负载量_pct"] < 0).sum()
df_clean.loc[df_clean["Fe负载量_pct"] < 0, "Fe负载量_pct"] = 0.0
print(f"\n1) Fe 负载量负值截断为 0：修正 {neg_fe} 条")

# 2.2 缺失值标记（不删、不填，先把事实记下来）
df_clean["pH是否缺失"] = df_clean["pH"].isna()
print(f"2) pH 缺失标记：{df_clean['pH是否缺失'].sum()} 条")

# 2.3 目标变量缺失的行单独分出（这些不能用于建模，但仍然保留）
df_model = df_clean.dropna(subset=["吸附容量_mgg"]).copy()
print(f"3) 拆分：全部 {len(df_clean)} 条 | 可用于建模 {len(df_model)} 条"
      f"（剔除 {len(df_clean) - len(df_model)} 条目标变量缺失）")

# ===============================================================
# 第三步：入库 —— 三张表，都写进去
# ===============================================================
print("\n" + "=" * 70)
print("【写入数据库】")
print("=" * 70)

conn = sqlite3.connect(DB_PATH)
df.to_sql("adsorption_raw", conn, if_exists="replace", index=False)
df_clean.to_sql("adsorption_clean", conn, if_exists="replace", index=False)
df_model.to_sql("adsorption_model", conn, if_exists="replace", index=False)

# 验证：不要相信 print 的数字，用 SQL 查回来
verify = pd.read_sql("""
    SELECT 'adsorption_raw'   AS 表名, COUNT(*) AS 条数 FROM adsorption_raw
    UNION ALL
    SELECT 'adsorption_clean', COUNT(*) FROM adsorption_clean
    UNION ALL
    SELECT 'adsorption_model', COUNT(*) FROM adsorption_model
""", conn)
print("\n写入结果（来自数据库查询，不是打印变量）：")
print(verify.to_string(index=False))

# 内存 vs 数据库 交叉核对
print(f"\n交叉核对：内存中 df={len(df)}, df_clean={len(df_clean)}, df_model={len(df_model)}")
conn.close()

# ===============================================================
# 第四步：结论 —— 缺失是随机的吗？
# ===============================================================
print("\n" + "=" * 70)
print("【判断：pH 缺失是随机的吗？（决定能不能删）】")
print("=" * 70)

sub = df[df["pH"].isna()]
print(f"\n缺失 pH 的记录共 {len(sub)} 条，分布在：")
print(sub.groupby(["材料类型", "目标污染物"]).size().to_string())
print("\n对照：全部记录的材料分布")
print(df.groupby("材料类型").size().to_string())
