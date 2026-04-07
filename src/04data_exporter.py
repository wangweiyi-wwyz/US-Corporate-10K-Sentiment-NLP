import json
import pandas as pd
import os

def json_to_tabular(input_json_path, output_csv_path, output_excel_path=None):
    """
    读取 FinBERT 分析后的 JSON 文件，展平嵌套字典，
    提取财报年份，并导出为 CSV (或 Excel) 文件。
    """
    print(f"[*] 正在读取 JSON 数据: {input_json_path}")
    
    # 1. 检查文件是否存在
    if not os.path.exists(input_json_path):
        print(f"[-] 错误: 找不到文件 {input_json_path}")
        return

    # 2. 加载 JSON 数据
    with open(input_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    print(f"[+] 成功读取 {len(data)} 条记录，正在进行数据展平...")

    # 3. 展平数据 (Flattening)
    flat_data = []
    for item in data:
        # 基础信息
        ticker = item.get("ticker", "UNKNOWN")
        accession = item.get("accession", "UNKNOWN")
        
        # 提取嵌套的 metrics 字典
        metrics = item.get("sentiment_metrics", {})
        
        # 构建扁平化的一行数据
        row = {
            "Ticker": ticker,
            "Accession_Number": accession,
            "Sentiment_Score": metrics.get("sentiment_score", None),
            "Positive_Ratio": metrics.get("positive", None),
            "Negative_Ratio": metrics.get("negative", None),
            "Neutral_Ratio": metrics.get("neutral", None),
            "Total_Chunks": metrics.get("total_chunks", None)
        }
        flat_data.append(row)

    # 4. 转换为 Pandas DataFrame
    df = pd.DataFrame(flat_data)

    # 5. 从 Accession 号中提取财报年份
    # Accession 号标准格式为: XXXXXXXXXX-YY-XXXXXX (例如: 0000320193-22-000108)
    # 中间的 'YY' 代表提交年份的后两位。
    def extract_year(acc_str):
        try:
            parts = acc_str.split('-')
            if len(parts) >= 2:
                year_suffix = int(parts[1])
                # SEC EDGAR 系统电子化主要在 1990 年代后期之后
                # 如果是 90 以上，算作 199X 年，否则算作 20XX 年
                if year_suffix >= 90:
                    return 1900 + year_suffix
                else:
                    return 2000 + year_suffix
            return None
        except:
            return None

    # 应用年份提取函数，并在 Ticker 后面插入新的一列 "Filing_Year"
    df.insert(1, 'Filing_Year', df['Accession_Number'].apply(extract_year))

    # 6. 按公司和年份排序，让数据看起来更规整
    df = df.sort_values(by=["Ticker", "Filing_Year"]).reset_index(drop=True)

    # 7. 导出为 CSV
    df.to_csv(output_csv_path, index=False, encoding='utf-8-sig') # utf-8-sig 保证 Excel 打开不会乱码
    print(f"[√] 成功导出 CSV 文件至: {os.path.abspath(output_csv_path)}")

    # 8. 导出为 Excel
    if output_excel_path:
        try:
            df.to_excel(output_excel_path, index=False)
            print(f"[√] 成功导出 Excel 文件至: {os.path.abspath(output_excel_path)}")
        except ImportError:
            print("[-] 提示: 若需导出 Excel 文件，请在终端运行 `pip install openpyxl`")

if __name__ == "__main__":
    # 定义输入输出路径
    INPUT_FILE = "data/processed_texts/10k_sentiment_results.json"
    OUTPUT_CSV = "data/processed_texts/10k_sentiment_analysis_final.csv"
    OUTPUT_EXCEL = "data/processed_texts/10k_sentiment_analysis_final.xlsx"
    
    json_to_tabular(
        input_json_path=INPUT_FILE, 
        output_csv_path=OUTPUT_CSV,
        output_excel_path=OUTPUT_EXCEL 
    )