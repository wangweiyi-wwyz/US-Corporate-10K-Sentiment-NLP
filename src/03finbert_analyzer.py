import json
import os
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from tqdm import tqdm

def analyze_long_text_with_finbert(text, tokenizer, model, chunk_size=400, overlap=50):
    """
    使用滑动窗口策略对长文本进行切分，并使用 FinBERT 分析每个块的情感。
    """
    if not text:
         return {"positive": 0, "negative": 0, "neutral": 0, "sentiment_score": 0}

    # 1. 将文本转化为 Token IDs
    # 参数 add_special_tokens=False，因为我们后面切块后会手动或由模型自动处理特殊 Token
    tokens = tokenizer.encode(text, add_special_tokens=False)
    total_tokens = len(tokens)
    
    # 2. 如果文本很短，直接处理
    if total_tokens <= 510: # BERT 限制 512，减去 [CLS] 和 [SEP]
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            outputs = model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
        
        # FinBERT labels: [Positive, Negative, Neutral]
        return {
            "positive": probs[0][0].item(),
            "negative": probs[0][1].item(),
            "neutral": probs[0][2].item(),
            "sentiment_score": probs[0][0].item() - probs[0][1].item() # 综合得分：正向 - 负向
        }

    # 3. 滑动窗口切分长文本
    chunk_results = []
    # 使用步长 (chunk_size - overlap) 遍历 tokens
    step = chunk_size - overlap
    for i in tqdm(range(0, total_tokens, step), desc="  => 推理进度", leave=False, unit="块"):
        chunk_tokens = tokens[i : i + chunk_size]
    
        # 将 token ids 解码回文本，再喂给 tokenizer 以确保 [CLS] [SEP] 格式正确
        chunk_text = tokenizer.decode(chunk_tokens)
        inputs = tokenizer(chunk_text, return_tensors="pt", truncation=True, max_length=512)
        
        with torch.no_grad():
            outputs = model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
            chunk_results.append({
                "positive": probs[0][0].item(),
                "negative": probs[0][1].item(),
                "neutral": probs[0][2].item()
            })

    # 4. 聚合所有块的结果 (这里采用简单的平均值计算)
    num_chunks = len(chunk_results)
    avg_pos = sum(c["positive"] for c in chunk_results) / num_chunks
    avg_neg = sum(c["negative"] for c in chunk_results) / num_chunks
    avg_neu = sum(c["neutral"] for c in chunk_results) / num_chunks

    return {
        "positive": avg_pos,
        "negative": avg_neg,
        "neutral": avg_neu,
        "sentiment_score": avg_pos - avg_neg, # 情感极性得分：越低代表风险描述越悲观
        "total_chunks": num_chunks
    }

def run_sentiment_analysis(input_json="data/processed_texts/extracted_10k_sections.json", output_json="data/processed_texts/10k_sentiment_results.json"):
    """读取提取好的 10-K 数据，运行情感分析，并保存结果"""
    
    print("[*] 正在加载 FinBERT 模型 (首次运行会自动下载，约 400MB)...")
    # ProsusAI/finbert 是公认在金融领域表现优秀的开源情感分类模型
    tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
    model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
    print("[+] 模型加载完毕！")

    with open(input_json, 'r', encoding='utf-8') as f:
        data = json.load(f)

    results = []
    
    for i, record in enumerate(data):
        ticker = record.get("ticker")
        accession = record.get("accession")
        risk_factors_text = record.get("item_1a_risk_factors")
        
        print(f"[*] 正在分析 {ticker} ({accession}) 的 Risk Factors...")
        
        # 对 Item 1A 进行分块情感分析
        sentiment_metrics = analyze_long_text_with_finbert(risk_factors_text, tokenizer, model)
        
        print(f"  -> 分析完成。划分为 {sentiment_metrics.get('total_chunks', 1)} 个区块。综合情感得分: {sentiment_metrics['sentiment_score']:.4f}")
        
        # 组装结果
        record_result = {
            "ticker": ticker,
            "accession": accession,
            "sentiment_metrics": sentiment_metrics
        }
        results.append(record_result)

    # 保存分析结果
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
        
    print(f"\n[√] 所有情感分析计算完毕！结果已保存至: {output_json}")

if __name__ == "__main__":
    run_sentiment_analysis()