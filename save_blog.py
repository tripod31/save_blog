#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 blogspotブログの記事をCSV/テキストで保存します
"""
import argparse
from bs4 import BeautifulSoup,element
import urllib.request
from datetime import datetime
import csv
import os
import sys
#from yoshi.util import get_common_list
import re
import io

'''
配列の共通する要素の配列を求める
'''
def get_common_list(list1,list2):
    set1 = set(list1)
    set2 = set(list2)
    return list(set1 & set2)
    
#引数のデフォルト
URL_BLOG="http://cleanstand.blogspot.jp/"
OUT_DIR="out"
OUT_FILE_CSV="blog.csv"
OUT_FILE_TXT="blog.txt"
OUT_ENCODING='cp932'

FILEDNAMES=("title","date","label","html","text")

#nodeを指定してそのタグ以下の内容をテキストで返す
#buf    StringIO:テキストを戻すためのバッファ
def get_text(node,buf):
    if isinstance(node,element.Tag):
        if node.name == "br":
            buf.write("\n")
        for e in node.contents:
            get_text(e,buf)
    if isinstance(node,element.NavigableString):
        t = re.sub(r'[\n\xa0 ]','',node.string)
        buf.write(t)

#子要素がないタグ（BR以外）を削除
def remove_empty_node(node):
    empty_nodes = node.findAll(lambda tag:
                               isinstance(node,element.Tag) and
                               len(tag.contents) == 0 and
                               tag.name != "br" 
                                )
    for e in empty_nodes:
        e.extract()
    
def get_html(node):
    remove_empty_node(node)
    html = ""
    #先頭のDIVを除くため子ノードを見る
    for e in node.contents:
        t = re.sub(r'[\xa0]','',str(e))
        html += t
    return html
    
#クロージャ
def func_read_page():
    count=1 #件数

    def read_page(rows,url,p_label):
        nonlocal count   #これをしないとエラー
        
        sys.stdout.flush()
        response = urllib.request.urlopen(url)
        html_str = response.read()
        dom = BeautifulSoup(html_str,"html.parser")
        
        posts=dom.select('div.post-outer')

        for post in posts:
            row={}
            title   =post.select('h3.entry-title a')
            date    =post.select('a.timestamp-link abbr')
            labels  =post.select('span.post-labels a')
            content =post.select('div.entry-content')

            row['title']=title[0].text
            try:
                row['date']=datetime.strptime(date[0].text,"%m/%d/%Y").strftime("%Y/%m/%d")
            except:
                row['date']=""
            
            lbls = list(map(lambda l:l.text, labels))
            row['label']=" ".join(lbls)
            row['html']=get_html(content[0])
            buf = io.StringIO()
            get_text(content[0],buf)  
            row['text']=buf.getvalue()

            if p_label is None or len(get_common_list(p_label.split(","), lbls))>0:
                print("読み込み中　%02d件目:%s "% (count,row['title']),end="\n")
                count+=1
                rows.append(row)
        
        #前の投稿があれば再帰呼び出し
        prev_page_link = dom.select("a.blog-pager-older-link")
        if len(prev_page_link) >0:
            url_prev = prev_page_link[0]['href']
            read_page(rows,url_prev,p_label)
    
    return read_page
    
if __name__ == '__main__':
    #引数
    parser = argparse.ArgumentParser()
    parser.add_argument('--url',            default=URL_BLOG)    #必須でない引数
    parser.add_argument('--out_dir',        default=OUT_DIR)    #必須でない引数
    parser.add_argument('--out_file_csv',   default=OUT_FILE_CSV)    #必須でない引数
    parser.add_argument('--out_file_txt',   default=OUT_FILE_TXT)    #必須でない引数
    parser.add_argument('--out_encoding',   default=OUT_ENCODING)    #必須でない引数
    parser.add_argument('--label')    #ラベルでフィルタする。","で区切る
    
    args=parser.parse_args()
    rows=list()
    f = func_read_page()
 
    f(rows,args.url,args.label)
    
    if not os.path.exists(args.out_dir):
        os.makedirs(args.out_dir)
    
    #CSV出力
    with open(os.path.join(args.out_dir,args.out_file_csv),mode="w") as f:
        #writer = util.MyDictWriter(f, FILEDNAMES,lineterminator="\n",out_encoding=args.out_encoding)    #python2
        writer = csv.DictWriter(f, FILEDNAMES,lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    
    #テキスト出力
    with open(os.path.join(args.out_dir,args.out_file_txt),mode="w") as f:
        line = '%s:%s\n\n' % (datetime.now().strftime("%Y/%m/%d %H:%M:%S"),args.url)
        f.write(line)
        count=1
        for row in rows:
            line='■%s\n%s\n(%d/%d:%s:%s)\n\n' % \
                (row['title'],row['text'],count,len(rows),row['date'],row['label'],)
            f.write(line)
            count+=1
            
    msg = "\n%s:%d件出力" % (args.out_file_csv,len(rows))
    print(msg)

