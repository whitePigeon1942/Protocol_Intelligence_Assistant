import os
import sys
import yaml
import logging
from datetime import datetime

# 添加项目根目录到 sys.path（以便导入 app 模块）
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.data_loader import load_ae_data, load_enrollment_data, backup_raw_data
from app.ae_analyzer import analyze_ae
from app.enrollment_analyzer import analyze_enrollment
from app.report_generator import generate_excel_report
from app.plotter import plot_comprehensive_dashboard, plot_enrollment_dashboard, plot_longterm_trend
from app.db_manager import DatabaseManager

# ==================== 加载配置 ====================
# 获取项目根目录（main.py 位于 app/ 子目录下）
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(PROJECT_ROOT, "config", "settings.yaml")

with open(CONFIG_PATH, 'r') as f:
    config = yaml.safe_load(f)

# 将配置文件中的相对路径转换为基于项目根目录的绝对路径
DATA_DIR = os.path.join(PROJECT_ROOT, config['paths']['data_dir'])
OUTPUT_DIR = os.path.join(PROJECT_ROOT, config['paths']['output_dir'])
DB_PATH = os.path.join(PROJECT_ROOT, config['paths']['db_path'])
LOG_DIR = os.path.join(PROJECT_ROOT, config['paths']['log_dir'])

AE_FILE = config['files']['ae']
ENROLL_FILE = config['files']['enrollment']

# ==================== 设置日志 ====================
os.makedirs(LOG_DIR, exist_ok=True)
log_filename = os.path.join(LOG_DIR, f"run_{datetime.now().strftime('%Y%m%d')}.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler()
    ]
)


# ==================== 主函数 ====================
def run_weekly_report():
    logging.info("=== Weekly Clinical Trial Report Started ===")
    today = datetime.now().strftime("%Y-%m-%d")

    # 1. 备份原始数据
    backup_raw_data(DATA_DIR, AE_FILE)
    backup_raw_data(DATA_DIR, ENROLL_FILE)

    # 2. 加载数据
    ae_path = os.path.join(DATA_DIR, AE_FILE)
    enroll_path = os.path.join(DATA_DIR, ENROLL_FILE)

    if not os.path.exists(ae_path) or not os.path.exists(enroll_path):
        logging.error("Data files not found! Please check data/raw/ directory.")
        logging.error(f"Expected AE: {ae_path}")
        logging.error(f"Expected Enrollment: {enroll_path}")
        return

    df_ae = load_ae_data(ae_path)
    df_enroll = load_enrollment_data(enroll_path)
    logging.info(f"Loaded AE: {len(df_ae)} rows, Enrollment: {len(df_enroll)} rows")

    # 3. 分析
    ae_analysis = analyze_ae(df_ae)
    enroll_analysis = analyze_enrollment(df_enroll)

    logging.info(f"Total AE: {ae_analysis['total']}, SAE: {ae_analysis['sae_count']}")
    logging.info(f"Enrollment Rate: {enroll_analysis['completion_rate']:.1%}")

    # 4. 保存到数据库
    db = DatabaseManager(DB_PATH)
    db.save_enrollment_snapshot(df_enroll, today)
    db.save_ae_snapshot(df_ae, today)

    # 5. 创建输出目录（按日期）
    output_subdir = os.path.join(OUTPUT_DIR, today)
    os.makedirs(output_subdir, exist_ok=True)

    # 6. 生成Excel报告
    excel_path = os.path.join(output_subdir, "summary_report.xlsx")
    generate_excel_report(ae_analysis, enroll_analysis, excel_path)

    # 7. 生成综合图表（6合1）
    chart_path = os.path.join(output_subdir, "clinical_trial_charts.png")
    plot_comprehensive_dashboard(ae_analysis, enroll_analysis, chart_path)

    # 8. 获取最近4周新增入组数据（用于dashboard）
    recent_df = db.get_weekly_new_enrollment(weeks=4)

    # 9. 生成入组专项看板（含最近4周新增）
    enroll_dash_path = os.path.join(output_subdir, "enrollment_dashboard.png")
    plot_enrollment_dashboard(enroll_analysis['df'], enroll_dash_path, recent_df=recent_df)

    # 10. 生成长期入组趋势图（基于历史数据库）
    trend_path = os.path.join(output_subdir, "enrollment_trend.png")
    plot_longterm_trend(DB_PATH, trend_path)

    logging.info(f"✅ All outputs saved to: {output_subdir}")
    logging.info("=== Weekly Report Completed Successfully ===")


if __name__ == "__main__":
    run_weekly_report()