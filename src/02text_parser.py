import os
import re
import json
from bs4 import BeautifulSoup

def clean_html_to_text(html_content):
    """清除 HTML 标签，并将所有类型的空白字符标准化"""
    soup = BeautifulSoup(html_content, "html.parser")
    for table in soup.find_all("table"):
        table.decompose() 
    
    text = soup.get_text(separator=" ", strip=True)
    # 将多个空格、换行、\xa0 等特殊字符，全部压缩成一个普通空格
    text = re.sub(r'\s+', ' ', text)
    return text

def extract_section_regex(text, start_regex, end_regex):
    """
    升级版提取器：使用正则表达式进行灵活匹配
    """
    # (?is) 修饰符：i=忽略大小写, s=允许 . 匹配包括换行符在内的所有字符
    pattern = re.compile(rf"(?is){start_regex}.*?(?={end_regex})")
    
    # 使用 finditer 找出所有匹配项
    matches = list(pattern.finditer(text))
    
    if not matches:
        return None
        
    # 【规避目录陷阱】: 真正的正文往往非常长，而目录只有几行字。找到长度最长的那块。
    best_match = max(matches, key=lambda m: len(m.group()))
    return best_match.group().strip()

def process_10k_directory(base_data_dir="data/sec-edgar-filings", output_dir="data/processed_texts"):
    os.makedirs(output_dir, exist_ok=True)
    extracted_data = []

    for ticker in os.listdir(base_data_dir):
        ticker_path = os.path.join(base_data_dir, ticker, "10-K")
        if not os.path.exists(ticker_path):
            continue
            
        print(f"[*] 正在处理公司: {ticker}")
        
        for accession in os.listdir(ticker_path):
            doc_path = os.path.join(ticker_path, accession, "primary-document.html")
            if not os.path.exists(doc_path):
                doc_path = os.path.join(ticker_path, accession, "full-submission.txt")
            if not os.path.exists(doc_path):
                continue
                
            with open(doc_path, 'r', encoding='utf-8', errors='ignore') as f:
                raw_content = f.read()
                
            # 1. 强力清洗 HTML
            clean_text = clean_html_to_text(raw_content)
            
            # 极度包容的正则表达式
            # 开始: 匹配 "Item 1A" (允许中间有多个空格，允许后面有点号)
            start_1a = r"Item\s+1A\.?"
            # 结束: 匹配 "Item 1B" 或 "Item 1C" 或 "Item 2" 
            end_1a = r"Item\s+(?:1B|1C|2)\.?"
            item_1a = extract_section_regex(clean_text, start_1a, end_1a)
                 
            # 同理增强 Item 7 (可能由于没有 7A 直接跳到 8)
            start_7 = r"Item\s+7\.?"
            end_7 = r"Item\s+(?:7A|8)\.?"
            item_7 = extract_section_regex(clean_text, start_7, end_7)
                 
            print(f"  [+] {accession}: Item 1A 长度={len(item_1a) if item_1a else 0} 字符")
            
            extracted_data.append({
                "ticker": ticker,
                "accession": accession,
                "item_1a_risk_factors": item_1a,
                "item_7_mda": item_7
            })
            
    output_file = os.path.join(output_dir, "extracted_10k_sections.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(extracted_data, f, ensure_ascii=False, indent=2)
        
    print(f"\n[√] 全部处理完成！已保存至: {output_file}")

if __name__ == "__main__":
    process_10k_directory()