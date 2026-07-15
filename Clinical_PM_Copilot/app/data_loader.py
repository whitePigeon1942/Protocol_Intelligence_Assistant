#负责读取Excel并进行基础清洗

import pandas as pd
import os
from datetime import datetime


def load_ae_data(filepath):
    """读取AE数据，清洗日期列"""
    df = pd.read_excel(filepath, sheet_name=0)
    df.columns = df.columns.str.strip()

    # 日期转换
    df['发生日期'] = pd.to_datetime(df['发生日期'], errors='coerce')
    df['解决日期'] = pd.to_datetime(df['解决日期'], errors='coerce')

    # 计算持续天数
    df['持续天数'] = df.apply(
        lambda r: (r['解决日期'] - r['发生日期']).days
        if pd.notna(r['发生日期']) and pd.notna(r['解决日期']) else None,
        axis=1
    )
    return df


def load_enrollment_data(filepath):
    """读取入组数据，过滤汇总行，计算完成率"""
    df = pd.read_excel(filepath, sheet_name=0)

    # 过滤汇总行
    df = df[~df['中心编号'].astype(str).str.contains('汇总|合计', na=False)].copy()

    # 数值列转换
    numeric_cols = ['计划入组', '累计筛选', '累计入组', '本周新增']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # 计算完成率
    df['完成率_实际'] = df['累计入组'] / df['计划入组']

    # 日期转换
    if '首例入组日期' in df.columns:
        df['首例入组日期'] = pd.to_datetime(df['首例入组日期'], errors='coerce')

    return df


def backup_raw_data(data_dir, file_name):
    """每周运行前自动备份原始文件到 archive/"""
    src = os.path.join(data_dir, file_name)
    if not os.path.exists(src):
        return

    archive_dir = os.path.join(data_dir, "archive")
    os.makedirs(archive_dir, exist_ok=True)

    date_str = datetime.now().strftime("%Y-%m-%d")
    dst = os.path.join(archive_dir, f"{date_str}_{file_name}")

    # 如果当天已经备份过，跳过
    if not os.path.exists(dst):
        import shutil
        shutil.copy2(src, dst)
        print(f"📂 Backed up: {dst}")