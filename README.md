# mazegaki-dic
Google日本語入力で使える漢直向けの交ぜ書き辞書を、GoldenDictで使えるHunspell辞書に変換します。<br/>
mecab-ipadic-2.7.0-20070801 の \*.csv から作成しています。

python3 ../hunspell_ja_JP/apply_iconv_to_dic.py ../hunspell_ja_JP/ja_JP.aff ja_JP.part.txt --plain --apply && python3 convert_with_conjugation.py && python3 sort_lines.py mazegaki_st.txt mazegaki_st_sorted.txt && python3 dedup_sorted.py mazegaki_st_sorted.txt mazegaki_st_sorted_dedup.txt && python3 merge_with_count.py ja_JP.part.txt mazegaki_st_sorted_dedup.txt ja_JP.dic && python3 ../hunspell_ja_JP/apply_iconv_to_dic.py ../hunspell_ja_JP/ja_JP.aff ja_JP.dic --apply && python3 add_homonym_flag.py ja_JP.dic --apply

## ファイルの説明

### ipadic.maze.csv
ほぼフルサイズの交ぜ書き辞書です。

エントリの一例:
```
着包み	着包み	名詞	きぐるみ	--	BASE
着ぐるみ	着包み	名詞	きぐるみ
き包み	着包み	名詞	きぐるみ
きぐるみ	着包み	名詞	きぐるみ
着包み族	着包み族	名詞	きぐるみぞく	--	BASE
着包みぞく	着包み族	名詞	きぐるみぞく
着ぐるみ族	着包み族	名詞	きぐるみぞく
着ぐるみぞく	着包み族	名詞	きぐるみぞく
き包み族	着包み族	名詞	きぐるみぞく
き包みぞく	着包み族	名詞	きぐるみぞく
きぐるみ族	着包み族	名詞	きぐるみぞく
きぐるみぞく	着包み族	名詞	きぐるみぞく
着包みん	着包みん	名詞	きぐるみん	--	BASE
着ぐるみん	着包みん	名詞	きぐるみん
き包みん	着包みん	名詞	きぐるみん
きぐるみん	着包みん	名詞	きぐるみん

思い出す	思い出す	動詞サ行五段	おもいだす	--	BASE
思いだす	思い出す	動詞サ行五段	おもいだす
おもい出す	思い出す	動詞サ行五段	おもいだす

```

「よみ」と「単語」が一致しているエントリには「コメント」に ` -- BASE` と付加してあります。そこから次の `BASE` までが交ぜ書き展開されたエントリとなります。

新しい単語を追加した後、LibreOffice CalcでC列を1番目のキー、D列を2番目のキー、B列を3番目のキー、A列を4番目のキーとして並べ替えてください。

### convert_with_conjugation.py
ipadic.maze.csvをもとにmazegaki_st.txtを生成します。

### mazegaki_st.txt
GoldenDictで使えるHunspell辞書（の一部）。

エントリの一例:
```
着ぐるみ st:着包み
き包み st:着包み
着包みぞく st:着包み族
着ぐるみ族 st:着包み族
着ぐるみぞく st:着包み族
き包み族 st:着包み族
き包みぞく st:着包み族
きぐるみ族 st:着包み族
着ぐるみん st:着包みん
き包みん st:着包みん

思いだし st:思い出す
思いださ st:思い出す
思いだす st:思い出す
思いだそ st:思い出す
思いだせ st:思い出す
おもい出せ st:思い出す
おもい出し st:思い出す
おもい出す st:思い出す
おもい出さ st:思い出す
おもい出そ st:思い出す

```

### sort_lines.py
mazegaki_st.txtを並べ替えます。

### dedup_sorted.py 
重複した行を取り除きます。

### merge_with_count.py
python3 merge_with_count.py A B C<br/>

ファイルAとファイルBとをくっつけてファイルCを作ります。またファイルCの冒頭でファイルの行数を記入します。

### apply_iconv_to_dic.py（hunspell_ja_JP 側）

`ja_JP.aff` の `ICONV`（旧字体・繁体→新字体）に合わせて、`.dic` と
`ja_JP.part.txt` の見出しを折り畳みます。ICONV は**入力**側で効くため、旧字体の
ままの行は引けなくなります（`spell()` では気付けません）。

```bash
python3 ../hunspell_ja_JP/apply_iconv_to_dic.py ../hunspell_ja_JP/ja_JP.aff ja_JP.part.txt --plain --apply
python3 ../hunspell_ja_JP/apply_iconv_to_dic.py ../hunspell_ja_JP/ja_JP.aff ja_JP.dic --apply
```

冪等なので、`ICONV` を変えたときだけでなく毎回実行して構いません。生成後の
`ja_JP.dic` に掛けたあと `add_homonym_flag.py` を実行してください（折り畳みで
同じ head が増えることがあるため）。

### add_homonym_flag.py
python3 add_homonym_flag.py ja_JP.dic --apply<br/>

同じ head が複数行ある場合、その**すべての行**に未定義フラグ `Zz` を付けます。
hunspell 1.7.3–1.7.6 の `HashMgr::add_word()` は「同 head・affix flag なし」の行を
`HENTRY_DATA`（`st:` など）を比較せず重複として捨てるため、たとえば

```
青み st:青味
青み st:青身
```

の片方が静かに消えます（`spell()` は true のままなので気付けません）。
flag が付いていれば `next_homonym` 側に回り、両方残ります。

`Zz` は **ja_JP.aff で定義しないこと**（定義すると語形派生が始まる）。`FLAG long` なので
2 文字が必要です。`Xx`/`xx` は形容詞規則として既に使われているため借用できません。
既定は dry-run、`--apply` で書き込み（`.bak` を自動作成、冪等）。

**hunspell 1.7.3–1.7.6 が現役でなくなったら（各ディストリ LTS を含む）、
この工程ごとパイプラインから削除してよいです。**

