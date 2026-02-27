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
    Set var=1
    Set ^glo=1

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
ClassMethod TryCatch()
{
    Try {
        Set a=3/0
    }
    Catch {
        Write "Error trapped"
    }
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
print("----")

q=r"""
(command_write
  (keyword_write) @cap_command_write
)

(command_goto (keyword_goto) @cap_command_goto)

(
    command_set
    (set_argument
        (system_defined_variable) @cap_error_trap
        (#match? @cap_error_trap "^\\$(ZT|ZTRAP|ETRAP)$")
    )
)
"""

query = Query(lang, q)

# このあたりの書き方がバージョン間での変化が激しい模様
query_cursor = QueryCursor(query)
captures = query_cursor.captures(root)
print(captures)

for capture_name, nodes in captures.items():
    for node in nodes:
        line = node.start_point[0] + 1
        if capture_name == "cap_command_write":
            print(f"{line}: WRITE の使用は禁止されています。{capture_name} {node.type}")
        if capture_name == "cap_error_trap":
            print(f"{line}: $ZTRAP / $ETRAP の使用は禁止されています（TRY/CATCH を使用してください）。{capture_name} {node.type}")
        if capture_name == "cap_command_goto":
            print(f"{line}: GOTOの使用は禁止されています。{capture_name} {node.type}")
