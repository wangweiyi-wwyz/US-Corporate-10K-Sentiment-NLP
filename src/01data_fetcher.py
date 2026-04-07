import os
from sec_edgar_downloader import Downloader

def fetch_10k_filings(ticker: str, email_address: str, 
download_dir: str = "data", after_date: str = "2022-01-01"):
    """
    从 SEC EDGAR 系统下载指定公司的 10-K 报告。
    
    参数:
        ticker: 公司股票代码
        email_address: 你的邮箱地址 (SEC 强制要求，用于标识请求者)
        download_dir: 存放数据的本地文件夹路径
        after_date: 下载此日期之后的报告 (格式 YYYY-MM-DD)
    """
    print(f"[*] 正在初始化下载器，目标公司: {ticker}")
    print(f"[*] 数据将保存至: {os.path.abspath(download_dir)}")
    
    try:
        # 初始化 Downloader
        # SEC 要求提供公司名/项目名和邮箱，以防止恶意爬虫
        dl = Downloader("Fin_NLP_Research", email_address, download_dir)
        
        # 执行下载
        num_downloaded = dl.get("10-K", ticker, after=after_date)
        
        print(f"[+] 下载完成！共获取到 {num_downloaded} 份 10-K 文件。")
        
    except Exception as e:
        print(f"[-] 下载过程中出现错误: {e}")

if __name__ == "__main__":
    # 配置文件参数
    TARGET_COMPANY = "AMD"  
    YOUR_EMAIL = "2816903640@qq.com"  
    
    # 确保保存数据的目录存在
    os.makedirs("data", exist_ok=True)
    
    # 运行下载任务
    fetch_10k_filings(TARGET_COMPANY, YOUR_EMAIL)