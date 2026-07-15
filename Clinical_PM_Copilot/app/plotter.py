import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


def plot_comprehensive_dashboard(ae_analysis, enroll_analysis, output_path):
    """
    生成综合看板（6合1），所有文字均为英文
    """
    df_ae = ae_analysis['df']
    df_en = enroll_analysis['df']

    # ---- 数据映射（中文 -> 英文） ----
    severity_map = {'轻度': 'Mild', '中度': 'Moderate', '重度': 'Severe'}
    outcome_map = {'痊愈': 'Recovered', '好转中': 'Improving', '未好转': 'Not Recovered', '死亡': 'Death'}
    status_map = {'已解决': 'Resolved', '进行中': 'Ongoing', '待处理': 'Pending'}
    ae_name_map = {
        '头痛': 'Headache', '恶心': 'Nausea', '皮疹': 'Rash', '乏力': 'Fatigue',
        '腹泻': 'Diarrhea', '发热': 'Fever', '失眠': 'Insomnia', '转氨酶升高': 'Elevated ALT',
        '咳嗽': 'Cough', '关节痛': 'Arthralgia', '便秘': 'Constipation', '脱发': 'Alopecia',
        '食欲减退': 'Anorexia', '呕吐': 'Vomiting', '口腔溃疡': 'Oral Ulcer', '下肢水肿': 'Leg Edema',
        '头晕': 'Dizziness', '心悸': 'Palpitations', '皮肤瘙痒': 'Pruritus', '肌肉酸痛': 'Myalgia',
        '严重肺炎': 'Severe Pneumonia', '急性肾损伤': 'Acute Kidney Injury', '肝衰竭': 'Liver Failure',
        '严重过敏反应': 'Anaphylaxis', '心肌梗死': 'Myocardial Infarction', '严重感染性休克': 'Septic Shock'
    }
    risk_map = {'低': 'Low', '中': 'Medium', '高': 'High', '极高': 'Extreme'}

    # 创建英文副本
    df_ae_en = df_ae.copy()
    df_ae_en['严重程度'] = df_ae_en['严重程度'].map(severity_map)
    df_ae_en['转归'] = df_ae_en['转归'].map(outcome_map)
    df_ae_en['状态'] = df_ae_en['状态'].map(status_map)
    df_ae_en['AE名称'] = df_ae_en['AE名称'].map(ae_name_map)

    df_en_en = df_en.copy()
    df_en_en['风险等级'] = df_en_en['风险等级'].map(risk_map)

    # ---- 绘图设置 ----
    sns.set_theme(style="whitegrid")
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rcParams['axes.unicode_minus'] = False

    fig = plt.figure(figsize=(20, 14))
    gs = fig.add_gridspec(2, 3, hspace=0.4, wspace=0.3)

    # 子图1：AE严重程度
    ax1 = fig.add_subplot(gs[0, 0])
    severity_order = ['Mild', 'Moderate', 'Severe']
    sns.countplot(data=df_ae_en, y='严重程度', hue='严重程度', order=severity_order,
                  ax=ax1, palette='Reds_r', legend=False)
    ax1.set_title('AE Severity Distribution', fontsize=16, fontweight='bold')
    ax1.set_xlabel('Number of Events', fontsize=12)
    ax1.set_ylabel('Severity', fontsize=12)
    for p in ax1.patches:
        ax1.annotate(f'{int(p.get_width())}', (p.get_width() + 0.5, p.get_y() + 0.5),
                     va='center', fontsize=11)

    # 子图2：AE转归（饼图）
    ax2 = fig.add_subplot(gs[0, 1])
    outcome_counts = df_ae_en['转归'].value_counts()
    order_outcome = ['Recovered', 'Improving', 'Not Recovered', 'Death']
    outcome_counts = outcome_counts.reindex([o for o in order_outcome if o in outcome_counts], fill_value=0)
    explode = [0.05 if x in ['Not Recovered', 'Death'] else 0 for x in outcome_counts.index]
    ax2.pie(outcome_counts, labels=outcome_counts.index, autopct='%1.1f%%',
            startangle=90, explode=explode, shadow=True)
    ax2.set_title('AE Outcome Composition', fontsize=16, fontweight='bold')

    # 子图3：AE状态
    ax3 = fig.add_subplot(gs[0, 2])
    status_order = ['Resolved', 'Ongoing', 'Pending']
    sns.countplot(data=df_ae_en, y='状态', hue='状态', order=status_order,
                  ax=ax3, palette=['#2ca02c', '#ff7f0e', '#d62728'], legend=False)
    ax3.set_title('AE Status Overview', fontsize=16, fontweight='bold')
    ax3.set_xlabel('Number of Events', fontsize=12)
    ax3.set_ylabel('Status', fontsize=12)
    for p in ax3.patches:
        ax3.annotate(f'{int(p.get_width())}', (p.get_width() + 0.5, p.get_y() + 0.5),
                     va='center', fontsize=11)

    # 子图4：Top 5 AE
    ax4 = fig.add_subplot(gs[1, 0])
    top_ae = df_ae_en['AE名称'].value_counts().head(5)
    sns.barplot(x=top_ae.values, y=top_ae.index, hue=top_ae.index,
                ax=ax4, palette='Blues_r', legend=False)
    ax4.set_title('Top 5 Most Frequent AEs', fontsize=16, fontweight='bold')
    ax4.set_xlabel('Frequency', fontsize=12)
    ax4.set_ylabel('AE Name', fontsize=12)
    for p in ax4.patches:
        ax4.annotate(f'{int(p.get_width())}', (p.get_width() + 0.3, p.get_y() + 0.5),
                     va='center', fontsize=11)

    # 子图5：各中心完成率
    ax5 = fig.add_subplot(gs[1, 1])
    plot_df = df_en_en.sort_values('完成率_实际', ascending=False)
    bars = sns.barplot(data=plot_df, x='完成率_实际', y='中心编号', hue='中心编号',
                       ax=ax5, palette='coolwarm', legend=False)
    ax5.set_title('Enrollment Completion Rate by Site', fontsize=16, fontweight='bold')
    ax5.set_xlabel('Completion Rate (Enrolled/Planned)', fontsize=12)
    ax5.set_ylabel('Site ID', fontsize=12)
    ax5.axvline(x=1.0, color='red', linestyle='--', linewidth=2, label='Target (100%)')
    ax5.legend()
    for p in bars.patches:
        width = p.get_width()
        ax5.annotate(f'{width * 100:.0f}%', (width + 0.02, p.get_y() + 0.5),
                     va='center', fontsize=9)

    # 子图6：风险等级分布
    ax6 = fig.add_subplot(gs[1, 2])
    risk_order = ['Extreme', 'High', 'Medium', 'Low']
    risk_counts = df_en_en['风险等级'].value_counts().reindex(risk_order, fill_value=0)
    colors_risk = ['#d62728', '#d62728', '#ff7f0e', '#2ca02c']
    sns.barplot(x=risk_counts.values, y=risk_counts.index, hue=risk_counts.index,
                ax=ax6, palette=colors_risk, legend=False)
    ax6.set_title('Enrollment Risk Level Distribution', fontsize=16, fontweight='bold')
    ax6.set_xlabel('Number of Sites', fontsize=12)
    ax6.set_ylabel('Risk Level', fontsize=12)
    for p in ax6.patches:
        ax6.annotate(f'{int(p.get_width())}', (p.get_width() + 0.3, p.get_y() + 0.5),
                     va='center', fontsize=11)

    fig.suptitle('Clinical Trial Dashboard', fontsize=24, fontweight='bold', y=0.98)
    fig.subplots_adjust(top=0.93, hspace=0.35, wspace=0.3)
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"📊 Comprehensive dashboard saved to: {output_path}")


def plot_enrollment_dashboard(df, output_path, recent_df=None):
    """
    生成入组专项看板（2x3 布局），包含：
    - 总入组统计（文本）
    - 地区分布（饼图）
    - 最近4周新增入组（柱状图，若 recent_df 非空）
    - Site 排名（水平条形图）
    - 入组趋势（按首例入组日期排序）
    """
    # ---- 地区映射（同前） ----
    china_provinces = [
        '北京', '上海', '广东', '四川', '湖北', '浙江', '山东', '河南',
        '湖南', '安徽', '福建', '河北', '吉林', '江苏', '辽宁', '陕西',
        '云南', '重庆', '天津', '新疆', '江西', '山西', '贵州', '甘肃',
        '海南', '内蒙古', '宁夏', '青海', '广西', '西藏'
    ]
    country_map = {
        '韩国': 'South Korea', '日本': 'Japan', '台湾': 'Taiwan', '香港': 'Hong Kong',
        '新加坡': 'Singapore', '美国': 'USA', '英国': 'UK', '法国': 'France',
        '德国': 'Germany', '加拿大': 'Canada', '澳大利亚': 'Australia',
        '马来西亚': 'Malaysia', '泰国': 'Thailand', '越南': 'Vietnam',
        '印度': 'India', '荷兰': 'Netherlands'
    }
    df_plot = df.copy()
    df_plot['省份'] = df_plot['省份'].apply(lambda x: 'China' if x in china_provinces else x)
    df_plot['省份'] = df_plot['省份'].map(country_map).fillna(df_plot['省份'])

    # ---- 统计量 ----
    total_planned = df_plot['计划入组'].sum()
    total_enrolled = df_plot['累计入组'].sum()
    completion_rate = total_enrolled / total_planned if total_planned > 0 else 0
    df_sorted = df_plot.sort_values('累计入组', ascending=False)
    df_trend = df_plot.sort_values('首例入组日期', ascending=True)

    fig = plt.figure(figsize=(18, 12))  # 加宽以容纳三列
    gs = fig.add_gridspec(2, 3, hspace=0.35, wspace=0.3)

    # ---- 子图1：总入组统计（文本） ----
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.axis('off')
    textstr = (
        f"Total Enrollment Summary\n"
        f"-------------------------\n"
        f"Planned Total    : {total_planned:,.0f}\n"
        f"Enrolled Total   : {total_enrolled:,.0f}\n"
        f"Completion Rate  : {completion_rate:.1%}\n"
        f"\nValid Sites      : {len(df_plot)}"
    )
    ax1.text(0.1, 0.5, textstr, transform=ax1.transAxes, fontsize=16,
             verticalalignment='center', linespacing=1.8,
             bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))
    ax1.set_title('Overall Status', fontsize=14, fontweight='bold', pad=20)

    # ---- 子图2：地区分布（饼图） ----
    ax2 = fig.add_subplot(gs[0, 1])
    region_counts = df_plot.groupby('省份')['累计入组'].sum().sort_values(ascending=False)
    if len(region_counts) > 1:
        ax2.pie(region_counts, labels=region_counts.index, autopct='%1.1f%%',
                startangle=90, shadow=True)
        ax2.set_title('Enrollment by Region', fontsize=14, fontweight='bold')
    else:
        ax2.pie([1], labels=['Global'], autopct='%1.1f%%', startangle=90)
        ax2.set_title('All Sites in One Region', fontsize=14, fontweight='bold')
    ax2.axis('equal')

    # ---- 子图3：最近4周新增入组（柱状图） ----
    ax3 = fig.add_subplot(gs[0, 2])
    if recent_df is not None and not recent_df.empty:
        # recent_df 已按 week_start 升序排列
        x = range(len(recent_df))
        bars = ax3.bar(x, recent_df['total_new'], color='#ff7f0e')
        ax3.set_xticks(x)
        ax3.set_xticklabels(recent_df['week_start'].dt.strftime('%Y-%m-%d'),
                            rotation=45, ha='right', fontsize=9)
        ax3.set_xlabel('Week', fontsize=11)
        ax3.set_ylabel('New Enrollments', fontsize=11)
        ax3.set_title('New Enrollments (Last 4 Weeks)', fontsize=14, fontweight='bold')
        for bar in bars:
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width() / 2., height + 0.5,
                     f'{int(height)}', ha='center', va='bottom', fontsize=10)
    else:
        ax3.text(0.5, 0.5, 'No historical data\nfor recent weeks',
                 ha='center', va='center', transform=ax3.transAxes, fontsize=14)
        ax3.set_title('New Enrollments (Last 4 Weeks)', fontsize=14, fontweight='bold')

    # ---- 子图4：Site 排名（占第二行左侧一列） ----
    ax4 = fig.add_subplot(gs[1, 0])
    top_n = min(10, len(df_sorted))
    plot_df = df_sorted.head(top_n)
    site_labels = plot_df['中心编号'].tolist()
    bars = ax4.barh(site_labels, plot_df['累计入组'], color='skyblue')
    ax4.set_xlabel('Enrolled Count', fontsize=12)
    ax4.set_ylabel('Site ID', fontsize=12)
    ax4.set_title(f'Top {top_n} Sites by Enrollment', fontsize=14, fontweight='bold')
    for bar in bars:
        width = bar.get_width()
        ax4.text(width + 0.5, bar.get_y() + bar.get_height() / 2,
                 f'{int(width)}', va='center', ha='left', fontsize=10)
    ax4.invert_yaxis()

    # ---- 子图5：入组趋势（按首例入组日期排序，占第二行右侧两列） ----
    ax5 = fig.add_subplot(gs[1, 1:3])  # 合并右侧两列
    trend_df = df_trend.head(20) if len(df_trend) > 20 else df_trend
    x = range(len(trend_df))
    bars = ax5.bar(x, trend_df['累计入组'], color='lightgreen')
    ax5.set_xticks(x)
    ax5.set_xticklabels(trend_df['首例入组日期'].dt.strftime('%Y-%m-%d'),
                        rotation=45, ha='right', fontsize=8)
    ax5.set_xlabel('First Enrollment Date', fontsize=12)
    ax5.set_ylabel('Cumulative Enrolled', fontsize=12)
    ax5.set_title('Enrollment Trend by Site Launch Date', fontsize=14, fontweight='bold')

    # ---- 全局标题 ----
    fig.suptitle('Enrollment Dashboard', fontsize=24, fontweight='bold', y=0.98)
    fig.subplots_adjust(top=0.93, hspace=0.35, wspace=0.3)
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"📊 Enrollment dashboard saved to: {output_path}")


def plot_longterm_trend(db_path, output_path):
    """
    从数据库读取所有历史周数据，绘制累计入组趋势线图
    """
    import sqlite3
    conn = sqlite3.connect(db_path)
    query = """
        SELECT week_start, SUM(total_enrolled) as total_enrolled
        FROM enrollment_history
        GROUP BY week_start
        ORDER BY week_start
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    if df.empty:
        print("⚠️ No historical data found for trend plot.")
        return

    plt.figure(figsize=(12, 6))
    plt.plot(df['week_start'], df['total_enrolled'], marker='o', linestyle='-', color='#1f77b4', linewidth=2)
    plt.title('Cumulative Enrollment Over Time', fontsize=16, fontweight='bold')
    plt.xlabel('Week', fontsize=12)
    plt.ylabel('Total Enrolled', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"📈 Long-term enrollment trend saved to: {output_path}")