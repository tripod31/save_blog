save_blog
=====
blogspotのブログの記事をCSV/テキストで保存します

development environment
-----
python3.5  

required libraries
-----
beautifulsoup4  

使い方
-----

    python save_blog.py  
        --url [ブログのURL]  
        --out_dir [出力先ディレクトリ。デフォルトは"./out"]  
        --out_file_csv [出力CSVファイル名。デフォルトは"blog.csv"]　 
        --out_file_text [出力ファイル名。デフォルトは"blog.txt"]  
        --out_encoding [出力文字エンコード。デフォルトは"cp932"(sjis)]  
        --label [指定すれば出力をラベル名で絞る。","区切り。]
