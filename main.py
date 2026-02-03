import requests
from bs4 import BeautifulSoup
import pandas as pd

# 获取arxiv检索论文函数
def fetch_arxiv_papers(keyword):
    url = f"https://arxiv.org/search?query={keyword}&searchtype=all"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'} # 模拟浏览器
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    print(soup)
    papers = []
    for paper in soup.find_all('li', class_='arxiv-result'): 
        title = paper.find('p', class_='title is-5 mathjax').text.strip()# 获取文章标题
        link_tag = paper.find('a',string='pdf')# 查找pdf的超链接
        if link_tag:
            link = link_tag.get('href')
        # 抓取文章作者
        authors_tag = paper.find('p', class_='authors')
        authors = ''
        if authors_tag:
            author_spans = authors_tag.find_all('a')
            authors = ', '.join([a.text.strip() for a in author_spans])
        papers.append({'文章标题': title, '链接': link, '作者': authors})
    return pd.DataFrame(papers)

# 执行并保存
keyword = input("请输入检索关键词：")  # 运行后让用户从键盘输入关键词
df = fetch_arxiv_papers(keyword)
import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()  # 隐藏主窗口

# 弹窗让用户选择保存位置和文件名
default_filename = f'arXiv_{keyword}_论文列表.xlsx'
excel_filename = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                              filetypes=[("Excel files", "*.xlsx")],
                                              initialfile=default_filename,
                                              title="保存文件到…")
if not excel_filename:
    print("未选择保存位置，已取消保存。")
    exit()
df.to_excel(excel_filename, index=True)
print(f"已保存到 {excel_filename}")