#生成Excel多sheet报告

import pandas as pd


def generate_excel_report(ae_analysis, enroll_analysis, output_path):
    """生成Excel报告"""
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # AE汇总
        ae_stats = pd.DataFrame({
            '指标': ['总事件数', 'AE数', 'SAE数', '未解决数', '紧急SAE数'],
            '数值': [
                ae_analysis['total'],
                ae_analysis['ae_only'],
                ae_analysis['sae_count'],
                len(ae_analysis['unresolved']),
                len(ae_analysis['critical_sae'])
            ]
        })
        ae_stats.to_excel(writer, sheet_name='AE_汇总', index=False)

        ae_analysis['severity'].reset_index().to_excel(
            writer, sheet_name='AE_严重程度', index=False, header=['严重程度', '数量']
        )
        ae_analysis['outcome'].reset_index().to_excel(
            writer, sheet_name='AE_转归', index=False, header=['转归', '数量']
        )

        # 入组明细
        enroll_analysis['df'].to_excel(writer, sheet_name='入组明细', index=False)

        # 入组汇总
        enroll_summary = pd.DataFrame({
            '指标': ['有效中心数', '总计划入组', '总累计入组', '整体完成率'],
            '数值': [
                enroll_analysis['site_count'],
                enroll_analysis['total_planned'],
                enroll_analysis['total_enrolled'],
                f"{enroll_analysis['completion_rate']:.1%}"
            ]
        })
        enroll_summary.to_excel(writer, sheet_name='入组汇总', index=False)

    print(f"📁 Excel report saved to: {output_path}")