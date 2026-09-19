import pandas as pd
import sqlite3

# 读数据
df = pd.read_csv("adsorption_data.csv", encoding="utf-8-sig")

# 看数据长什么样
#print(df.head())        # 前 5 行
#print(df.shape)         # (行数, 列数)
#print(df.columns)       # 列名
#print(df.info())        # 每列类型 + 有没有缺值
#print(df.isna().sum())  # 每列缺几个值

#print(df.dtypes)
#print(df[df["吸附容量_mgg"] > 80])
#print(df.groupby("材料类型")["吸附容量_mgg"].mean().sort_values(ascending=False))
#print(df[(df["Fe负载量_pct"] > 5) & (df["pH"].between(6, 8))])

#print(df.groupby(["材料类型", "目标污染物"])["吸附容量_mgg"].mean())
#print(df["材料类型"].value_counts())

#print(df.groupby(["目标污染物", "材料类型"])["吸附容量_mgg"].agg(["count", "mean"]))
#print(df.groupby(["目标污染物","材料类型" ])["吸附容量_mgg"].mean())

# 先看看缺在哪
#print(df[df["pH"].isna()])              # 缺值所在行
#print(df["pH"].isna().sum())            # 缺几个

# 三种处理方式，各有适用场景
df_drop = df.dropna()                              # 方式1：直接删（简单但损失数据）
#df_fill = df.fillna({"pH": df["pH"].median()})     # 方式2：用中位数填
#df_keep = df.copy()                                # 方式3：不处理，标记出来

# 检查结果
print(df.shape, "->", df_drop.shape)

#print(df[df["pH"].isna()][["记录编号","材料类型","目标污染物","Fe负载量_pct","吸附容量_mgg"]])
print(df[df["pH"].isna()])

conn = sqlite3.connect("adsorption.db")     # 建库（文件不存在会自动创建）
df.to_sql("adsorption", conn, if_exists="replace", index=False)
print("写入完成，共", len(df), "条")

# 立刻读回来验证
check = pd.read_sql("SELECT COUNT(*) AS 总数 FROM adsorption", conn)
print(check)
#conn.close()

# 2. 建立清洗规则：缺失 pH 标记出来，而不是删掉
df_clean = df.copy()
df_clean["pH是否缺失"] = df_clean["pH"].isna()        # 加一列标记

# 3. 真正要建模时才决定怎么处理
df_model = df_clean.dropna(subset=["吸附容量_mgg"])    # 只删目标变量缺失的
print("原始:", len(df), "| 可用于建模:", len(df_model))

pd.read_sql("""
    SELECT '原始' AS 表名, COUNT(*) AS 条数 FROM adsorption_raw
    UNION ALL
    SELECT '建模用', COUNT(*) FROM adsorption_model
""", conn)

conn.close()


