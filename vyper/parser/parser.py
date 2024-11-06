from lark import Lark, ParseTree, Transformer
from lark import Transformer, Tree, Token
from typing import List, Union, Optional, Any, Sequence
from lark.indenter import Indenter
from pathlib import Path

from vyper.config import Config


class PythonIndenter(Indenter):
    @property
    def NL_type(self):
        return "_NEWLINE"

    @property
    def OPEN_PAREN_types(self):
        return ["LPAR", "LSQB", "LBRACE"]

    @property
    def CLOSE_PAREN_types(self):
        return ["RPAR", "RSQB", "RBRACE"]

    @property
    def INDENT_type(self):
        return "_INDENT"

    @property
    def DEDENT_type(self):
        return "_DEDENT"

    @property
    def tab_len(self):
        return 8


class Parser:
    """Vyper Parser

    @note: wrapper for the Lark parser
    """

    def __init__(self, grammar: Path) -> None:
        self._parser = Lark(
            grammar.read_text(),
            parser="lalr",
            postlex=PythonIndenter(),
            start="file_input",
            maybe_placeholders=False,
            propagate_positions=True,
        )

    @classmethod
    def default(cls):
        return cls(grammar=Config().grammar_path)

    def parse(self, source: str) -> ParseTree:
        return self._parser.parse(source)


class YAMLAnnotationTransformer(Transformer):
    """Transform the parse tree into valid Python code."""

    def type_yaml_annotation(self, items: List[Union[Tree, Token]]) -> Tree:
        """Transforms yaml_annotation rule from grammar:
        yaml_annotation: name "@" NAME ["[" mod_list? "]"]
        """
        if len(items) == 5:  # With modifications: name "@" yaml_id "[" mods "]"
            type_name, _, yaml_id, _, modifications = items
            return Tree("yaml_annotation", [type_name, yaml_id, modifications])
        else:  # Without modifications: name "@" yaml_id
            type_name, _, yaml_id = items
            return Tree("yaml_annotation", [type_name, yaml_id, None])

    def modification_list(self, items: List[Union[Tree, Token]]) -> Tree:
        """Transforms mod_list rule from grammar:
        mod_list: modification+
        """
        return Tree("modification_list", items)

    def modification(self, items: List[Union[Tree, Token]]) -> Tree:
        """Transforms modification rule from grammar:
        modification: path "=" value _NEWLINE?
        """
        print(f"Modification items: {items}")  # Debug what we're getting
        for item in items:
            print(f"  Item: {item} (type: {type(item)})")  # Debug each item's structure

        # Validate we have at least path, =, value
        if len(items) >= 3:
            path, equals, value, *rest = items
            return Tree("modification", [path, equals, value])
        else:
            raise ValueError(f"Invalid modification structure: {items}")

    def path(self, items: List[Union[Tree, Token]]) -> Tree:
        """Transforms path rule from grammar:
        path: name ("." name | "[" NUMBER "]")*
        """
        path_parts = []
        for item in items:
            if isinstance(item, Tree):
                # Keep tree structure for nested paths
                path_parts.append(item)
            elif isinstance(item, Token):
                path_parts.append(item)
            else:
                path_parts.append(Token("PATH_PART", str(item)))
        return Tree("path", path_parts)

    def format_modifications(self, modifications: Optional[Tree]) -> Tree:
        """Helper method to format a list of modifications into a tree structure.
        Not directly tied to a grammar rule, but helps process modification lists.
        """
        if not modifications:
            return Tree("modifications", [])
        return Tree("modifications", [mod for mod in modifications.children if mod])


class PythonExtendedTranspiler:
    def __init__(self):
        self.parser = Parser.default()
        self.transformer = YAMLAnnotationTransformer()

    def transpile(self, source: str) -> str:
        # Parse the source code
        tree = self.parser.parse(source)

        # Transform the tree
        transformed = self.transformer.transform(tree)

        # Convert back to source code
        return str(transformed)


if __name__ == "__main__":
    source = Path("test/sample.vy").resolve().read_text()

    transpiler = PythonExtendedTranspiler()
    tree = transpiler.parser.parse(source)
    print(tree.pretty())

    post_source = transpiler.transpile(source)
    # result = transpiler.transpile(source)
    print("Transpiled code:")
    print(post_source)
