import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import openpyxl
import tkinter as tk
from tkinter import simpledialog
from tkinter import filedialog
from datetime import datetime


# 获取arxiv检索论文函数
def fetch_arxiv_papers(keyword, max_papers):
    url = f"https://arxiv.org/search?query={keyword}&searchtype=all"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'} # 模拟浏览器
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    papers = []
    current_papers = 0
    while current_papers < max_papers:
        for paper in soup.find_all('li', class_='arxiv-result'): 
            if current_papers >= max_papers:
                break
            current_papers += 1
        # 获取文章标题、发表日期、摘要、链接、作者
            title = paper.find('p', class_='title is-5 mathjax').text.strip()# 获取文章标题
            date = paper.find('p', class_='is-size-7').text.strip()
            abstract = paper.find('span', class_='abstract-full has-text-grey-dark mathjax').text.strip()
            link_tag = paper.find('a',string='pdf')# 查找pdf的超链接
            if link_tag:
                link = link_tag.get('href')
            # 抓取文章作者
            authors_tag = paper.find('p', class_='authors')
            authors = ''
            if authors_tag:
                author_spans = authors_tag.find_all('a')
                authors = ', '.join([a.text.strip() for a in author_spans])
            # 把日期从文字整合成数字表达形式
            date_pattern = re.search(r'(\d{1,2}) (\w+), (\d{4})', date)
            if date_pattern:
                day = date_pattern.group(1)
                month_str = date_pattern.group(2)
                year = date_pattern.group(3)
                # 月份英文缩写转数字
                try:
                    month = datetime.strptime(month_str, '%b').month
                except ValueError:
                    try:
                        month = datetime.strptime(month_str, '%B').month
                    except ValueError:
                        month = 1
                date = f"{year}-{month:02d}-{int(day):02d}"
                papers.append({
                    'Title': title,
                    'Link': link,
                    'Authors': authors,
                    'Date': date,
                    'Abstract': abstract
                })
        # 获取下一页的url
        next_page_tag = soup.find('a', attrs={'title': 'Next'})
        if next_page_tag and 'href' in next_page_tag.attrs:
            next_page_url = "https://arxiv.org" + next_page_tag['href']
            response = requests.get(next_page_url, headers=headers)
        abstract = paper.find('span', class_='abstract-full has-text-grey-dark mathjax').text.strip()
        link_tag = paper.find('a',string='pdf')# 查找pdf的超链接
        if link_tag:
            link = link_tag.get('href')
        
        papers.append({
            'Title': title,
            'Link': link,
            'Authors': authors,
            'Date': date,
            'Abstract': abstract
        })
    return pd.DataFrame(papers)

# 执行并保存
# 弹窗输入关键词
root = tk.Tk()
root.withdraw()  # 隐藏主窗口

keyword = simpledialog.askstring("keyword", "please input the keyword:")
if not keyword:
    print("no keyword input, cancelled.")
    exit()
# 弹窗让用户输入文章数量
max_papers = simpledialog.askinteger("max_papers", "please input the number of papers you want to search:", minvalue=1, initialvalue=10)
if not max_papers:
    print("invalid number of papers, cancelled.")
    exit()
df = fetch_arxiv_papers(keyword, max_papers)

root = tk.Tk()
root.withdraw()  # 隐藏主窗口

# 弹窗让用户选择保存位置和文件名
default_filename = f'arXiv_{keyword}_paper_list.xlsx'
excel_filename = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                              filetypes=[("Excel files", "*.xlsx")],
                                              initialfile=default_filename,
                                              title="save file to...")
if not excel_filename:
    print("no save location selected, cancelled.")
    exit()
df.to_excel(excel_filename, index=True)
print(f"saved to {excel_filename}")