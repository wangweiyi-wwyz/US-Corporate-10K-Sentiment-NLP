import subprocess
import sys
import os
import time

def run_step(script_name, description):
    """运行单个步骤并捕获输出状态"""
    script_path = os.path.join("src", script_name)
    
    print(f"\n{'='*50}")
    print(f"开始执行: {description}")
    print(f"运行脚本: {script_path}")
    print(f"{'='*50}\n")
    
    if not os.path.exists(script_path):
        print(f"[-] 致命错误: 找不到脚本 {script_path}")
        sys.exit(1)
        
    start_time = time.time()
    
    try:
        # 使用 subprocess 运行脚本，实时将输出流向控制台
        result = subprocess.run([sys.executable, script_path], check=True)
        elapsed_time = time.time() - start_time
        print(f"\n[√] {script_name} 执行成功！(耗时: {elapsed_time:.2f} 秒)")
        
    except subprocess.CalledProcessError as e:
        print(f"\n[x] {script_name} 执行失败！返回码: {e.returncode}")
        print("[!] 请检查上述错误日志，修复后重试。流水线已终止。")
        sys.exit(1)

def main():
    print("""
    ====================================================
        US Corporate 10-K NLP & Sentiment Pipeline
    ====================================================
    """)
    
    # 定义流水线步骤顺序
    pipeline_steps = [
        ("01data_fetcher.py", "阶段 1: 从 SEC EDGAR 下载 10-K 原始文件"),
        ("02text_parser.py", "阶段 1/2: 解析 HTML 并提取 Item 1A / Item 7 核心文本"),
        ("03finbert_analyzer.py", "阶段 3: 使用 FinBERT 进行长文本分块情感极性计算"),
        ("04data_exporter.py", "阶段 4: 数据展平与面板数据 (CSV/Excel) 导出"),
        ("05_market_data.py", "阶段 5: 提取发布日期并计算 CAR (yfinance)"),
        ("06_regression_analysis.py", "阶段 6: 运行面板 OLS 回归与可视化分析")
    ]
    
    total_start = time.time()
    
    for script, desc in pipeline_steps:
        run_step(script, desc)
        
    total_time = time.time() - total_start
    print(f"\n{'*'*50}")
    print(f"全部流水线执行完毕！总耗时: {total_time:.2f} 秒")
    print(f"最终数据已生成在 data/processed_texts/ 目录下。")
    print(f"{'*'*50}\n")

if __name__ == "__main__":
    # 确保运行环境在项目根目录
    if not os.path.exists("src"):
        print("[-] 请在项目根目录下 (FIN-NLP-PROJECT) 执行此脚本！")
        sys.exit(1)
        
    main()