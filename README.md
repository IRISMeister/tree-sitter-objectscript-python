
# 目的
開発者コミュニティの[ポスト](https://community.intersystems.com/node/585345)が少々そっけなかったので、pythonから使う方法を調べました。

>Introducing tree‑sitter‑objectscript: High‑Performance Syntax Parsing for ObjectScript in Your Favorite Editors

# ビルド方法
tree-sitter-objectscriptをpythonから使える用にビルドします。setup.pyがあるので下記を実行するだけです。

```
$ git clone https://github.com/intersystems/tree-sitter-objectscript-python
$ cd tree-sitter-objectscript-python
$ python3 -m venv venv
$ source venv/bin/activate
$ git clone https://github.com/intersystems/tree-sitter-objectscript
$ cd tree-sitter-objectscript
$ pip install .
Processing /home/irismeister/work/tree-sitter-objectscript
  Installing build dependencies ... done
  Getting requirements to build wheel ... done
  Preparing metadata (pyproject.toml) ... done
Building wheels for collected packages: tree-sitter-objectscript
  Building wheel for tree-sitter-objectscript (pyproject.toml) ... done
  Created wheel for tree-sitter-objectscript: filename=tree_sitter_objectscript-1.3.2-cp38-abi3-linux_x86_64.whl size=2645396 sha256=cdfc624ecc1c2829d97c2744d1bb5ba22f8c0bc84c9f0b4716961c8f462fb4a9
  Stored in directory: /home/irismeister/.cache/pip/wheels/d0/43/e7/b2fe575efc4f43caafef0537bb79db4ab778eae18503d8a64f
Successfully built tree-sitter-objectscript
Installing collected packages: tree-sitter-objectscript
Successfully installed tree-sitter-objectscript-1.3.2
$ cd ..
$ pip install tree-sitter
$ pip list
Package                  Version
------------------------ -------
pip                      24.0
tree-sitter              0.25.2
tree-sitter-objectscript 1.3.2
```

# サンプル
下記のいずれも行っていることに大差はないです。

クエリ周り(Query, QueryCursorなど)のバージョン間の改変が多いようで、ちゃんと動作するシンタックスに行き着くのに苦労しました。現在、tree-sitter 0.25.2です。

## 基本動作確認のための単純な処理
[parse_class.py](./parse_class.py)

どのシンタックスがどのようなCSTに変換されるかを確認することを主目的です。

> Tree-sitterのCST（Concrete Syntax Tree：具象構文木）は、ソースコードを解析して生成される、コメントや空白を含むすべてのトークン情報を保持した詳細な木構造です。抽象構文木（AST）とは異なり、コードの完全な表現（構文の具体化）を維持するため、高精度なシンタックスハイライトや高速なインクリメンタル解析に利用されています。 

```
$ python parse_class.py
source_file [Point(row=0, column=0)-Point(row=25, column=0)]
  class_definition [Point(row=1, column=0)-Point(row=24, column=1)]
    keyword_class [Point(row=1, column=0)-Point(row=1, column=5)]
    identifier [Point(row=1, column=6)-Point(row=1, column=17)]
    class_body [Point(row=2, column=0)-Point(row=24, column=1)]                ・
                ・
                ・
                        string_literal [Point(row=22, column=10)-Point(row=22, column=15)]
            } [Point(row=23, column=0)-Point(row=23, column=1)]
      } [Point(row=24, column=0)-Point(row=24, column=1)]
----
{'kw': [<Node type=system_defined_variable, start_point=(5, 8), end_point=(5, 11)>, <Node type=keyword_write, start_point=(15, 4), end_point=(15, 9)>, <Node type=keyword_write, start_point=(22, 4), end_point=(22, 9)>]}
6: $ZTRAP / $ETRAP の使用は禁止されています（TRY/CATCH を使用してください）。kw system_defined_variable
16: WRITE の使用は禁止されています。kw keyword_write
23: WRITE の使用は禁止されています。kw keyword_write      
```

最後の{'kw':...を見ると、writeコマンドが15行目の4～9列と、22行目の4～9列目にあることが分かります。


[parse_routine.py](./parse_routine.py)

ルーチン(クラス定義ではないもの)も処理可能です。


## ソースコードの引数化

ソースコードの入力をファイル渡しに変更し、Lintっぽくしたものです。

[parse_class_files.py](./parse_class_files.py)

[Sample.Test.cls](./Sample.Test.cls)

実行例
```
$ python parse_class_files.py Sample.Test.cls
Sample.Test.cls:14 WRITE の使用は禁止されています
Sample.Test.cls:21 WRITE の使用は禁止されています
Sample.Test.cls:15 GOTO の使用は禁止されています
Sample.Test.cls:5 $ZTRAP / $ETRAP の使用は禁止されています（TRY/CATCH を使用してください）
```

# クエリの書き方

クエリの書き方が独特です。下記はwriteコマンドに合致するクエリです。

```
(command_write (keyword_write) @kw)
```

クエリの記述方法はLLMに相談しながら進めました。下記のように元のソースコードと、CSTを全部プロンプトに張り付けて、マッチしたい場所をCSTにして欲しいと要求しました。

```
{CST出力}

{IRISのクラスコード}

Set $ZT="ERR"にマッチするCSTを教えて。
```

ただし、試しに全てのコマンド(node typeがcommand_で始まる)をマッチするCSTを要求した際の回答は下記だったが、これは誤り。
```
q="""
((_) @command (#match? @command "^command_"))
"""
```

理由は...とのこと。
```
match? はノードの種類ではなく「テキスト(ソースの文字列)」を調べる
キャプチャした _ ノードの中身は set という文字列で、^command_ にマッチしません。
command_set というのはノードの type であって、ノードのテキストではありません。
そのため、ワイルドカードで command_set 自体を捕まえたつもりでも、#match? が文字列 set を見てしまい、空の結果になっています。
 
(_ @var1) (#match? @var1 "^set$") ;; ノードのテキストに対してはこんな感じ
```

指定したコマンド(node typeがcommand_xxx)を抽出するクエリの例
```
q="""
[
  (command_set)
  (command_write)
  (command_if)
  (command_do)
] @command
"""
```

# 発展
がんばればLintが作れます。

