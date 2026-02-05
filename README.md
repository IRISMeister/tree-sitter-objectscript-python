
# 目的
開発者コミュニティの[ポスト](https://community.intersystems.com/node/585345)が少々そっけなかったので、pythonから使う方法を調べました。

>Introducing tree‑sitter‑objectscript: High‑Performance Syntax Parsing for ObjectScript in Your Favorite Editors

# ビルド方法
tree-sitter-objectscriptをpythonから使える用にビルドします。setup.pyがあるので下記を実行するだけです。

```
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
$ pip install tree-sitter
$ pip list
Package                  Version
------------------------ -------
pip                      24.0
tree-sitter              0.25.2
tree-sitter-objectscript 1.3.2
```

# サンプル
下記のいずれも行っていることは大差ないです。

クエリ周り(Query, QueryCursorなど)のバージョン間の改変が多いようで、ちゃんと動作するシンタックスに行き着くのに苦労しました。現在、tree-sitter 0.25.2ですが、今後動かなくなるかもしれません。

## 基本動作確認のための単純な処理
[parse.py](./parse.py)

どのシンタックスがどのようなCSTに変換されるかを確認することを主目的です。

> Tree-sitterのCST（Concrete Syntax Tree：具象構文木）は、ソースコードを解析して生成される、コメントや空白を含むすべてのトークン情報を保持した詳細な木構造です。抽象構文木（AST）とは異なり、コードの完全な表現（構文の具体化）を維持するため、高精度なシンタックスハイライトや高速なインクリメンタル解析に利用されています。 

```
$ python parse.py
source_file [Point(row=0, column=0)-Point(row=22, column=0)]
  class_definition [Point(row=1, column=0)-Point(row=21, column=1)]
    keyword_class [Point(row=1, column=0)-Point(row=1, column=5)]
    identifier [Point(row=1, column=6)-Point(row=1, column=17)]
    class_body [Point(row=2, column=0)-Point(row=21, column=1)]
                ・
                ・
                ・
            } [Point(row=20, column=0)-Point(row=20, column=1)]
      } [Point(row=21, column=0)-Point(row=21, column=1)]
{'kw': [<Node type=keyword_write, start_point=(12, 4), end_point=(12, 9)>, <Node type=keyword_write, start_point=(19, 4), end_point=(19, 9)>]}
```

最後の{'kw':...を見ると、writeコマンドが12行目の4～9列と、19行目の4～9列目にあることが分かります。


## 複数ルール化

ルールを複数化しました。

[parse_rules.py](./parse_rules.py)

## ソースコードの引数化

ソースコードの入力をファイル渡しに変更し、Lintっぽくしたものです。

[parse_files.py](./parse_files.py)

[Sample.Test.cls](./Sample.Test.cls)

実行例
```
$ python parse_files.py Sample.Test.cls
Sample.Test.cls:12 WRITE の使用は禁止されています
Sample.Test.cls:19 WRITE の使用は禁止されています
Sample.Test.cls:13 GOTO の使用は禁止されています
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

# 発展
がんばればLintが作れます。

