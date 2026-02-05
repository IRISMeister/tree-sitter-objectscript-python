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

# 複数Rule
RULES = {
    "WRITE": {
        "query": "(command_write (keyword_write) @kw)",
        "message": "WRITE の使用は禁止されています"
    },
    "GOTO": {
        "query": "(command_goto (keyword_goto) @kw)",
        "message": "GOTO の使用は禁止されています"
    },
    "ZTRAP": {
        # $ZTRAP, $ETRAP 両方捕まえる
        "query": r"""
        (
          command_set
            (set_argument
              (system_defined_variable) @kw
              (#match? @kw "^\\$(ZT|ZTAP|ETRAP)$")
            )
        )
        """,
        "message": "$ZTRAP / $ETRAP の使用は禁止されています（TRY/CATCH を使用してください）"
    }
}

errors = []

for rule_name, rule in RULES.items():
    print(rule_name)
    print(rule["query"])
    query = Query(lang, rule["query"])
    cursor = QueryCursor(query)

    captures = cursor.captures(root)

    for nodes in captures.values():
        for node in nodes:
            line = node.start_point[0] + 1
            errors.append(
                f"{line}: {rule['message']} {rule_name}"
            )

print(errors)
