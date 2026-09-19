"""Day 3：第一次写 SQL —— 把你用 pandas 做过的分组统计，用 SQL 重做一遍。

运行：python day3.py
"""
import os
import sqlite3

import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "adsorption.db")

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 20)
pd.set_option("display.unicode.east_asian_width", True)

conn = sqlite3.connect(DB_PATH)


def show(title: str, sql: str) -> None:
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)
    print(pd.read_sql(sql, conn).to_string(index=False))


# 1. 看库里有哪些表
show("1) 数据库里现在有几张表", """
    SELECT name AS 表名 FROM sqlite_master WHERE type = 'table'
""")

# 2. 对应 pandas: df.groupby("材料类型")["吸附容量_mgg"].mean()
show("2) 每种材料的平均吸附容量（= pandas 的 groupby + mean）", """
    SELECT 材料类型,
           COUNT(*)                    AS 记录数,
           ROUND(AVG(吸附容量_mgg), 2)  AS 平均吸附容量,
           ROUND(MAX(吸附容量_mgg), 2)  AS 最高值
    FROM   adsorption_model
    GROUP  BY 材料类型
    ORDER  BY 平均吸附容量 DESC
""")

# 3. 对应 pandas: df[df["吸附容量_mgg"] > 80]
show("3) 筛选：吸附容量大于 80 的记录（= pandas 的布尔索引）", """
    SELECT 记录编号, 材料类型, 目标污染物, Fe负载量_pct, 吸附容量_mgg
    FROM   adsorption_model
    WHERE  吸附容量_mgg > 80
    ORDER  BY 吸附容量_mgg DESC
""")

# 4. 对应 pandas: df.groupby(["材料类型","目标污染物"]).agg(["count","mean"])
show("4) 材料 × 污染物 双分组（= pandas 的 groupby 两个字段）", """
    SELECT 目标污染物,
           材料类型,
           COUNT(*)                    AS 记录数,
           ROUND(AVG(吸附容量_mgg), 2)  AS 平均吸附容量
    FROM   adsorption_model
    GROUP  BY 目标污染物, 材料类型
    ORDER  BY 目标污染物, 平均吸附容量 DESC
""")

# 5. 两表对比：原始表 vs 建模表
show("5) 三张表的行数对比（用 UNION ALL 拼起来）", """
    SELECT 'adsorption_raw'   AS 表名, COUNT(*) AS 条数 FROM adsorption_raw
    UNION ALL
    SELECT 'adsorption_clean', COUNT(*) FROM adsorption_clean
    UNION ALL
    SELECT 'adsorption_model', COUNT(*) FROM adsorption_model
""")

conn.close()
print("\n完成。这些 SQL 和你之前写的 pandas 代码，是同一件事的两种写法。")
