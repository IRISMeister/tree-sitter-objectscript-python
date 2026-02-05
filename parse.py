from tree_sitter import Parser, Language, Query,QueryCursor
import tree_sitter_objectscript

lang = Language(tree_sitter_objectscript.language_objectscript())

parser = Parser()
parser.language = lang

code = b"""
Class Sample.Test
{
ClassMethod trap()
{
    Set $ZT="ERR"
    Quit
ERR
    Quit
}
ClassMethod Hello()
{
    Write "Hello"
    GOTO END
END
    Quit
}
ClassMethod Bye()
{
    Write "Bye"
}
}
"""

tree = parser.parse(code)
root = tree.root_node

def dump(node, indent=0):
    print("  " * indent + f"{node.type} [{node.start_point}-{node.end_point}]")
    for c in node.children:
        dump(c, indent + 1)
# 全ダンプ表示
dump(root)


query = Query(lang, 
"""
(command_write
  (keyword_write) @kw
)
""")

# このあたりの書き方がバージョン間での変化が激しい模様
query_cursor = QueryCursor(query)
captures = query_cursor.captures(root)
print(captures)

for capture_name, nodes in captures.items():
    for node in nodes:
        line = node.start_point[0] + 1
        print(f"{line}: WRITE の使用は禁止されています。{capture_name} {node.type}")
