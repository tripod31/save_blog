#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ファイルの内容をcherrynoteのDBに書き込む
"""
import argparse
import sqlite3
import os,sys

if __name__ == '__main__':
    #引数
    parser = argparse.ArgumentParser()
    parser.add_argument('--in_file' ,required=True)
    parser.add_argument('--db_file' ,required=True)
    parser.add_argument('--node_name' ,required=True)
    
    args=parser.parse_args()

    #テキスト出力
    if not os.path.exists(args.in_file):
        print(args.in_file+"がありません")
        sys.exit()
    
    if not os.path.exists(args.db_file):
        print(args.db_file+"がありません")
        sys.exit()
    
    with open(args.in_file,mode="r") as f:
        txt = f.read()
    if len(txt) ==0:
        print(args.in_file+":ファイルが空です")
        sys.exit()
    
    txt = "<?xml version=\"1.0\" ?><node><rich_text>%s</rich_text></node>" % txt
    txt = txt.replace('\'','\'\'')
    conn=sqlite3.connect(args.db_file)
    csr= conn.cursor()
    sql = "UPDATE node SET txt='%s' WHERE name='%s'" % (txt,args.node_name)
    csr.execute(sql)
    n = csr.rowcount
    if n == 1:
        conn.commit()
        print("[%s]のノードを更新しました" % args.node_name)        
    elif n==0:
        conn.rollback()
        print("[%s]のノードがありません" % args.node_name)
    else:
        conn.commit()
        print("[%s]のノードが複数あるため更新しません" % args.node_name)
    
    csr.close()
    conn.close()
    