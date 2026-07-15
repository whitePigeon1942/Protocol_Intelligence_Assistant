# Clinical Trial PM Copilot

自动化临床试验项目管理工具，专为项目经理设计，每周自动生成入组进度和不良事件报告。

## 📁 项目结构
见 [文件夹组织](#文件夹组织)

## 🚀 快速开始
1. 安装依赖：`pip install -r requirements.txt`
2. 将 `AE.xlsx` 和 `enrollment.xlsx` 放入 `data/raw/`
3. 运行：`python app/main.py`

## 📊 输出
- `outputs/YYYY-MM-DD/summary_report.xlsx`：结构化数据
- `outputs/YYYY-MM-DD/clinical_trial_charts.png`：综合看板（6合1）
- `outputs/YYYY-MM-DD/enrollment_dashboard.png`：入组专项看板

## 🔧 自定义配置
编辑 `config/settings.yaml` 修改路径、阈值等。

## 📅 自动运行（每周一）
- macOS/Linux: `crontab -e` 添加 `0 8 * * 1 cd /path/to/project && python app/main.py`
- Windows: 使用任务计划程序