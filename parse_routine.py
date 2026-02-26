from tree_sitter import Parser, Language, Query,QueryCursor
import tree_sitter_objectscript_core

lang = Language(tree_sitter_objectscript_core.language_objectscript_core())

parser = Parser()
parser.language = lang

code = b"""
#define MYMACRO1 123
 set a=1
 write a
 Quit
"""

with open("test.mac", encoding="utf8") as f:
    # vscode形式の場合先頭にROUTINE xxx のような行が入るのでそれを読み飛ばす
    first = f.readline()
    code=f.read()
    if not first.startswith("ROUTINE "):
        code=first + code
    code=code.encode("utf8")

tree = parser.parse(code)
root = tree.root_node

def dump(node, indent=0):
    print("  " * indent + f"{node.type} [{node.start_point}-{node.end_point}]")
    for c in node.children:
        dump(c, indent + 1)
# 全ダンプ表示
dump(root)

q=r"""
(
    command_set
    (set_argument
        (system_defined_variable) @kw
        (#match? @kw "^\\$(ZT|ZTRAP|ETRAP)$")
    )
)
"""

query=Query(lang, q)
query_cursor = QueryCursor(query)
captures = query_cursor.captures(root)
print(captures)

for capture_name, nodes in captures.items():
    for node in nodes:
        line = node.start_point[0] + 1
        print(f"{line}: $ZTRAP / $ETRAP の使用は禁止されています（TRY/CATCH を使用してください）。 {capture_name} {node.type}")
