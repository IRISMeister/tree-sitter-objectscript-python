# 特定のノードの子要素に特定のノードが存在するか(しないか)を確認する例
# try-catchは、そもそもcatch無しだとシンタックスエラーになるので、例としてはあまりよろしくない、事が後で判明した。

from typing import Iterable, List

from tree_sitter import Language, Parser, Node, Query, QueryCursor

import tree_sitter_objectscript

LANG = Language(tree_sitter_objectscript.language_objectscript())
PARSER = Parser()
PARSER.language = LANG

def parse_file(path: str) -> bytes:
    with open(path, encoding='utf8') as f:
        return f.read().encode('utf8')


def walk(node: Node) -> Iterable[Node]:
    """Pre‑order traversal of the subtree."""
    yield node
    for child in node.children:
        yield from walk(child)


def find_nodes(root: Node, type_name: str) -> List[Node]:
    """Return all nodes of the given type in `root`."""
    return [n for n in walk(root) if n.type == type_name]


def catch_has_throw(catch_node):
    cursor = catch_node.walk()
    reached_root = False

    while not reached_root:
        node = cursor.node

        if node.type == "command_throw":
            return True

        if cursor.goto_first_child():
            continue

        if cursor.goto_next_sibling():
            continue

        while True:
            if not cursor.goto_parent():
                reached_root = True
                break
            if cursor.goto_next_sibling():
                break

    return False


def dump(node: Node, indent: int = 0) -> None:
    print('  ' * indent + f'{node.type} [{node.start_point}-{node.end_point}]')
    for c in node.children:
        dump(c, indent + 1)


def main(filename: str) -> None:
    code = parse_file(filename)
    tree = PARSER.parse(code)
    root = tree.root_node
    dump(root)
    print('----')

    # 特定ノード(node type=command_trycatch)をrootから検索
    q = Query(LANG, '(command_trycatch) @try')
    cursor = QueryCursor(q)
    captures = cursor.captures(root)

    for cap, nodes in captures.items():
        # capはクエリ内のキャプチャ名（この例では"@try"）が入る。nodesは見つかったノードのリスト。
        if cap == 'try':
            #try_node = nodes[0]
            for try_node in nodes:
                print('Found TRY at', try_node.start_point)
                # tryノードの子要素にcatch_blockノードが存在するか確認
                node_catches = find_nodes(try_node, 'catch_block')
                if not node_catches:
                    print('⚠️ try without catch at', try_node.start_point)
                for node_catch in node_catches:
                    # catch内にthrowコマンドが存在するか確認
                    if not catch_has_throw(node_catch):
                        print("Lint Error: THROW missing in CATCH at", node_catch.start_point)

                    #dump(node_catch)
                    for n in walk(node_catch):
                        text = code[n.start_byte:n.end_byte].decode('utf8')
                        print(f'node info: {n.type}: {text!r}')


if __name__ == '__main__':
    import sys
    main(sys.argv[1] if len(sys.argv) > 1 else 'Sample.Test.cls')
