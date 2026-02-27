from __future__ import annotations
from typing import Iterable, List, Tuple
from tree_sitter import Parser, Language, Node, Query, QueryCursor
import tree_sitter_objectscript

# language and parser are shared constants
LANG = Language(tree_sitter_objectscript.language_objectscript())

def make_parser() -> Parser:
    """Return a freshly initialised ``Parser`` for ObjectScript."""

    parser = Parser()
    parser.language=LANG
    return parser

def parse_source(source: bytes) -> Node:
    """Parse the given source bytes and return the root node."""

    tree = make_parser().parse(source)
    return tree.root_node

def dump(node: Node, indent: int = 0) -> None:
    """Pretty‑print ``node`` and its children with indentation."""

    print("  " * indent + f"{node.type} [{node.start_point}-{node.end_point}]")
    for c in node.children:
        dump(c, indent + 1)


def find_violations(root: Node) -> List[Tuple[str, Node]]:
    """Return a list of (capture_name, node) for forbidden constructs.

    Currently detects WRITE, GOTO and various error‑trap variables.
    """

    q = r"""
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

    (glvn (lvn) @cap_set_lvn (#match? @cap_set_lvn "[^a-z0-9]") )
    
    """

    query = Query(LANG, q)
    cursor = QueryCursor(query)
    captures = cursor.captures(root)

    return captures


def report_violations(violations: Iterable[Tuple[str, Node]], source) -> None:
    """Print human‑readable warnings for each capture returned by
    ``find_violations``.
    """

    for cap_name, nodes in violations.items():
        for node in nodes:
            start_row=node.start_point[0]+1
            start_col=node.start_point[1]
            end_row=node.end_point[0]+1
            end_col=node.end_point[1]
            location=f"{start_row}:{start_col} - {end_row}:{end_col}"
            #print(location)
            text = source[node.start_byte:node.end_byte].decode('utf8')

            line = node.start_point[0] + 1
            if cap_name == "cap_command_write":
                print(f"{line}行目: WRITE の使用は禁止されています。{cap_name} {node.type}")
            elif cap_name == "cap_error_trap":
                print(
                    f"{line}行目: $ZTRAP / $ETRAP の使用は禁止されています（TRY/CATCH を使用してください）。"
                    f"{cap_name} {node.type}"
                )
            elif cap_name == "cap_command_goto":
                print(f"{line}行目: GOTOの使用は禁止されています。{cap_name} {node.type}")
            elif cap_name == "cap_set_lvn":
                print(f"{line}行目: ローカル変数[{text}]が命名規約違反です。{cap_name} {node.type} at {location}")
            else:
                print(f"{line}行目: {cap_name} {node.type} ")


# sample program used when the module is executed directly
SAMPLE = b"""
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

# ToDo: Ruleと違反時の表示メッセージをひとつの構造にまとめたほうが良い. parse_class_file.pyを参照。

def main(source: bytes = SAMPLE) -> None:
    root = parse_source(source)
    #dump(root)
    #print("----")
    violations = find_violations(root)
    report_violations(violations,source)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding="utf8") as f:
            src = f.read().encode("utf8")
    else:
        src = SAMPLE
    main(src)
