from tree_sitter import Parser, Language, Query,QueryCursor
import tree_sitter_objectscript
import sys

def dump(node, indent=0):
    print("  " * indent + f"{node.type} [{node.start_point}-{node.end_point}]")
    for c in node.children:
        dump(c, indent + 1)

def lint_file(path):
    lang = Language(tree_sitter_objectscript.language_objectscript())

    parser = Parser()
    parser.language = lang

    with open(path, encoding="utf8") as f:
        code=f.read()
        tree = parser.parse(code.encode("utf8"))
        root = tree.root_node
        dump(root)

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
                    (#match? @kw "^\\$(ZT|ZTRAP|ETRAP)$")
                    )
                )
                """,
                "message": "$ZTRAP / $ETRAP の使用は禁止されています（TRY/CATCH を使用してください）"
            }
        }

        errors = []

        for rule_name, rule in RULES.items():
            #print(rule_name)
            #print(rule["query"])
            query = Query(lang, rule["query"])
            cursor = QueryCursor(query)

            captures = cursor.captures(root)

            for nodes in captures.values():
                for node in nodes:
                    line = node.start_point[0] + 1
                    errors.append({
                        "file": path,
                        "line": line,
                        "message": rule['message'],
                        "rule_name": {rule_name}
                    })


        return errors


def main():
    has_error = False

    for path in sys.argv[1:]:
        for v in lint_file(path):
            has_error = True
            print(f"{v['file']}:{v['line']} {v['message']}")

    sys.exit(1 if has_error else 0)

if __name__ == "__main__":
    main()