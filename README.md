# 📈 US Corporate 10-K NLP Sentiment Analysis Pipeline

## Project Overview
This project is an end-to-end financial Natural Language Processing (NLP) data pipeline. It aims to automatically acquire 10-K annual reports of US-listed companies (e.g., AAPL, MSFT, TSLA), clean and extract highly informative core sections (Item 1A. Risk Factors & Item 7. MD&A), and perform quantitative sentiment scoring using the deep learning-based `FinBERT` model. Ultimately, it generates structured panel data suitable for empirical financial research (such as asset pricing and factor analysis).

## Architecture & Workflow
The project adopts a highly modular design, with the main scheduler `main.py` orchestrating four core modules:

1. **`01data_fetcher.py`**: Utilizes `sec-edgar-downloader` to connect directly to the SEC database, fetching raw HTML/TXT format 10-K filings in a compliant and batch manner.
2. **`02text_parser.py`**: Addressing the complex and unstructured HTML format of 10-K filings, this module uses `BeautifulSoup` combined with highly robust heuristic regular expressions to accurately remove table noise and locate/extract specific sections. This completely resolves the "table of contents trap" and heterogeneous layout issues.
3. **`03finbert_analyzer.py`**: Breaks through the 512-token limit of traditional Transformer models by adopting a **Sliding Window Chunking** strategy to fully traverse ultra-long financial texts. It utilizes `ProsusAI/finbert` to calculate and output comprehensive sentiment polarity scores.
4. **`04data_exporter.py`**: Automatically extracts the filing year feature from the Accession Number, flattens the nested JSON data, and outputs well-structured CSV/Excel panel data, achieving a perfect closed loop from unstructured to structured data.

## Repository Structure
```text
FIN-NLP-PROJECT/
├── data/
│   ├── processed_texts/       # Cleaned JSON and final exported CSV/Excel files
│   └── sec-edgar-filings/     # Raw SEC 10-K filings (categorized by Ticker)
├── src/
│   ├── 01data_fetcher.py      # Data acquisition module
│   ├── 02text_parser.py       # Text preprocessing and extraction module
│   ├── 03finbert_analyzer.py  # FinBERT sentiment analysis module
│   └── 04data_exporter.py     # Structured data export module
├── main.py                    # Global Pipeline orchestration script
├── requirements.txt           # Core dependencies list
└── README.md                  # Project documentation
```
