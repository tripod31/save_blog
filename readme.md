save_blog
=====
blogspotのブログの記事をCSV/テキストで保存します

Windows用実行ファイル
-----
save_blog.exe  
python、必要ライブラリが中に含まれています。  

開発環境
-----
python3.5  

必要ライブラリ
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
