#封装所有入组分析逻辑

def analyze_enrollment(df):
    """返回入组分析结果字典"""
    total_planned = df['计划入组'].sum()
    total_enrolled = df['累计入组'].sum()
    completion_rate = total_enrolled / total_planned if total_planned > 0 else 0

    risk_counts = df['风险等级'].value_counts()
    high_risk = df[df['风险等级'].isin(['高', '极高'])]

    # Site排名
    site_ranking = df.sort_values('累计入组', ascending=False)[['中心编号', '中心名称', '累计入组', '完成率_实际']]

    return {
        'total_planned': total_planned,
        'total_enrolled': total_enrolled,
        'completion_rate': completion_rate,
        'site_count': len(df),
        'risk_counts': risk_counts,
        'high_risk': high_risk,
        'site_ranking': site_ranking,
        'df': df
    }