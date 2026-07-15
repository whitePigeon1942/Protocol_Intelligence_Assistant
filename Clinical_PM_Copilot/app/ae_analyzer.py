#封装所有AE统计逻辑

import pandas as pd


def analyze_ae(df):
    """返回AE分析结果字典"""
    total = len(df)
    sae_count = df[df['事件类型'] == 'SAE'].shape[0]
    ae_only = total - sae_count

    severity_dist = df['严重程度'].value_counts()
    outcome_dist = df['转归'].value_counts()
    status_dist = df['状态'].value_counts()
    top_ae = df['AE名称'].value_counts().head(5)

    unresolved = df[df['状态'].isin(['进行中', '待处理'])]
    critical_sae = df[
        (df['事件类型'] == 'SAE') &
        (df['转归'].isin(['未好转', '死亡'])) &
        (df['解决日期'].isna())
        ]

    return {
        'total': total,
        'ae_only': ae_only,
        'sae_count': sae_count,
        'severity': severity_dist,
        'outcome': outcome_dist,
        'status': status_dist,
        'top_ae': top_ae,
        'unresolved': unresolved,
        'critical_sae': critical_sae,
        'df': df  # 保留原始df供绘图使用
    }