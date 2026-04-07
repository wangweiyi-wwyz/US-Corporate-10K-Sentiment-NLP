# 📈 US Corporate 10-K NLP Sentiment Analysis Pipeline

## 项目简介 (Project Overview)
本项目是一个端到端（End-to-End）的金融自然语言处理数据管道。项目旨在自动化获取美股上市公司（如 AAPL, MSFT, TSLA 等）的 10-K 年度报告，清洗并提取极具信息价值的核心章节（Item 1A. Risk Factors & Item 7. MD&A），并使用基于深度学习的 `FinBERT` 模型对其进行量化情感打分，最终生成适用于金融实证研究（如资产定价、因子分析）的结构化面板数据。

## 架构与工作流 (Architecture & Workflow)
项目采用高度模块化的设计，主调度器 `main.py` 统筹四大核心模块：

1. **`01data_fetcher.py`**: 利用 `sec-edgar-downloader` 直连 SEC 数据库，合规、批量获取原始 HTML/TXT 格式的 10-K 文件。
2. **`02text_parser.py`**: 针对 10-K 复杂的非结构化 HTML 格式，使用 `BeautifulSoup` 结合鲁棒性极强的启发式正则表达式，精准剔除表格噪音并定位提取特定章节，彻底解决“目录陷阱”与排版异构问题。
3. **`03finbert_analyzer.py`**: 突破传统 Transformer 模型的 512 Token 限制，采用**滑动窗口切分策略 (Sliding Window Chunking)** 完整遍历超长财报文本，利用 `ProsusAI/finbert` 输出综合情感极性得分。
4. **`04data_exporter.py`**: 自动提取 Accession Number 中的年份特征，扁平化嵌套 JSON 数据，输出规整的 CSV/Excel 面板数据，实现数据从非结构化到结构化的完美闭环。

## 项目结构 (Repository Structure)
```text
FIN-NLP-PROJECT/
├── data/
│   ├── processed_texts/       # 清洗后的 JSON 与最终导出的 CSV/Excel
│   └── sec-edgar-filings/     # 存放 SEC 原始 10-K 文件 (按 Ticker 分类)
├── src/
│   ├── 01data_fetcher.py      # 数据获取模块
│   ├── 02text_parser.py       # 文本预处理与提取模块
│   ├── 03finbert_analyzer.py  # FinBERT 情感分析模块
│   └── 04data_exporter.py     # 结构化数据导出模块
├── main.py                    # 全局 Pipeline 调度总控脚本
├── requirements.txt           # 核心依赖清单
└── README.md                  # 项目文档