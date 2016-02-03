#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 blogspotブログの記事をCSV/テキストで保存
"""
import argparse
from lxml import html
import urllib.request
#import codecs
from datetime import datetime
import csv
import os
import sys
#from yoshi.util import get_common_list
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
#OUT_ENCODING='utf-8'

FILEDNAMES=("title","date","label","html","text")

#HtmlElementを指定してそのタグの下の内容をHTMLとテキストで返す
def get_content(dom):
    content_text =get_text_one(dom)
    content_html = dom.text
    for e in dom.getchildren():
        content_text+=get_text_one(e)
        if e.tag == "div" and e.attrib.has_key("style") and e.attrib["style"] == "clear: both;":
            pass
        else:
            content_html+= html.tostring(e,encoding='utf-8').decode('utf-8')
    content_html = content_html.replace('\xa0'," ")
    return (content_html,content_text)

def get_text_one(e):
    content_text=""
    if e.tag=="br":
        content_text+="\n"
    if e.text !=None:
        content_text+= e.text.replace('\n','')            
    if e.tail !=None:
        content_text+= e.tail.replace('\n','')
    content_text=content_text.replace('\xa0'," ")    #CP932への変換時エラーが出るため置換

    return content_text

#クロージャ
def func_read_page():
    count=1

    def read_page(rows,url,p_label):
        nonlocal count   #これをしないとエラー
        
        sys.stdout.flush()
        response = urllib.request.urlopen(url)
        html_str = response.read()
        dom = html.fromstring(html_str)
        
        #posts=dom.cssselect('div.post-outer')
        posts = dom.xpath('//div[@class="post-outer"]')
    
        for post in posts:
            row={}
            """
            #cssselectパッケージ要
            title   =post.cssselect('h3.entry-title a')
            date    =post.cssselect('a.timestamp-link abbr')
            labels  =post.cssselect('span.post-labels a')
            content =post.cssselect('div.entry-content')
            """
            title   =post.xpath('descendant::h3[contains(@class,"entry-title")]/a')
            date    =post.xpath('descendant::a[@class="timestamp-link"]/abbr')
            labels  =post.xpath('descendant::span[@class="post-labels"]/a')
            content =post.xpath('descendant::div[contains(@class,"entry-content")]')
            
            row['title']=title[0].text
            try:
                row['date']=datetime.strptime(date[0].text,"%m/%d/%Y").strftime("%Y/%m/%d")
            except:
                row['date']=""
            
            lbls = list(map(lambda l:l.text, labels))
            row['label']=" ".join(lbls)
            row['html'],row['text']=get_content(content[0])
            
            if p_label is None or len(get_common_list(p_label.split(","), lbls))>0:
                print("読み込み中　%02d件目:%s "% (count,row['title']),end="\n")
                count+=1
                rows.append(row)
        
        #前の投稿があれば再帰呼び出し
        prev_page_link = dom.xpath('//a[@class="blog-pager-older-link"]')
        if len(prev_page_link) >0:
            url_prev = prev_page_link[0].attrib['href']
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
        count=1
        for row in rows:
            line='■%s\n%s\n(%d/%d:%s:%s)\n\n' % \
                (row['title'],row['text'],count,len(rows),row['date'],row['label'],)
            f.write(line)
            count+=1
            
    msg = "\n%s:%d件出力" % (args.out_file_csv,len(rows))
    print(msg)

