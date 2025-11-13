# src/ssml.py
from typing import List, Dict, Optional, Union
import xml.etree.ElementTree as ET
import html
import re

class SSMLText:
    def __init__(self, text: str):
        self.text = text

    def __repr__(self):
        return f"SSMLText({self.text!r})"

    def __eq__(self, other):
        return isinstance(other, SSMLText) and self.text == other.text


class SSMLTag:
    def __init__(
        self,
        name: str,
        attributes: Optional[Dict[str, str]] = None,
        children: Optional[List[Union["SSMLTag", SSMLText]]] = None,
    ):
        self.name = name
        self.attributes = attributes or {}
        self.children = children or []

    def __repr__(self):
        return f"SSMLTag(name={self.name!r}, attributes={self.attributes!r}, children={self.children!r})"

    def __eq__(self, other):
        if not isinstance(other, SSMLTag):
            return False
        return (self.name == other.name and
                self.attributes == other.attributes and
                self.children == other.children)


def _normalize_tag_whitespace(s: str) -> str:
    """
    Normalize whitespace inside tags so ElementTree can parse inputs like:
    "< speak   >< p ></  p ></speak >" -> "<speak><p></p></speak>"
    Only modifies what's inside '<...>' so text is preserved.
    """
    def fix_tag(match):
        tag = match.group(0)
        # remove spaces after '<' or '</'
        tag = re.sub(r'^<\s+', '<', tag)
        tag = re.sub(r'^</\s+', '</', tag)
        # remove spaces before '>'
        tag = re.sub(r'\s+>$', '>', tag)
        # collapse spaces between tag name and attributes to single space
        tag = re.sub(r'<(/?)(\S+)\s+', lambda m: f"<{m.group(1)}{m.group(2)} ", tag, count=1)
        return tag
    return re.sub(r'<[^>]+>', fix_tag, s)


def parseSSML(ssml: str) -> 'SSMLTag':
    """
    Parse SSML string into SSMLTag/SSMLText structure and enforce test rules:
      - attribute values must use double quotes (single quotes -> raise Exception)
      - tolerate extra whitespace in tags (like "< speak >")
      - accept attribute names containing ':' by temporarily replacing ':' in names
      - must contain exactly one top-level <speak> element (otherwise raise Exception)
      - must not contain stray top-level text (raise)
    """
    # Disallow single-quoted attribute values (tests expect this to raise)
    if "'" in ssml and re.search(r"=\s*'[^']*'", ssml):
        raise Exception("single-quoted attributes are not allowed")

    # Normalize whitespace to help the XML parser handle unusual spacing
    normalized = _normalize_tag_whitespace(ssml)

    # Protect attribute names that include ':' (otherwise ET treats them as XML namespaces)
    placeholder = "__COLON__"
    attr_colon_pattern = re.compile(r'([A-Za-z0-9_\-\.]+):([A-Za-z0-9_\-\.]+)\s*=')
    replaced = attr_colon_pattern.sub(r'\1' + placeholder + r'\2=', normalized)

    # Wrap in a single root to detect multiple top-level nodes and pass ET parsing
    wrapped = f"<root>{replaced}</root>"

    try:
        root_elem = ET.fromstring(wrapped)
    except ET.ParseError:
        # Propagate parse error for tests that expect invalid markup to raise
        raise

    # Check for stray text directly under root (top-level text is invalid)
    if root_elem.text and root_elem.text.strip() != "":
        raise Exception("Invalid top-level text")

    # Root must contain exactly one child node (the <speak> element)
    children = list(root_elem)
    if len(children) != 1:
        raise Exception("Multiple top-level tags or missing speak tag")

    # Also ensure there is no stray text after the speak child (child.tail)
    # or between top-level children (but we already enforced len(children)==1).
    first_child = children[0]
    if first_child.tail and first_child.tail.strip() != "":
        raise Exception("Invalid top-level text")

    # Build SSMLTag/SSMLText objects recursively and restore ':' in attribute names
    def build(elem: ET.Element) -> SSMLTag:
        attrs: Dict[str, str] = {}
        for k, v in elem.attrib.items():
            key = k.replace(placeholder, ":")
            attrs[key] = v
        tag = SSMLTag(name=elem.tag, attributes=attrs, children=[])
        if elem.text and elem.text.strip() != "":
            tag.children.append(SSMLText(html.unescape(elem.text)))
        for child in list(elem):
            tag.children.append(build(child))
            if child.tail and child.tail.strip() != "":
                tag.children.append(SSMLText(html.unescape(child.tail)))
        return tag

    parsed = build(first_child)
    # Tests expect the top-level tag to be <speak>
    if parsed.name != "speak":
        raise Exception("Top-level tag must be <speak>")
    return parsed


def ssmlNodeToText(node: Union['SSMLTag', SSMLText]) -> str:
    """
    Convert SSMLTag/SSMLText nodes back to textual SSML representation.
    """
    if isinstance(node, SSMLText):
        return node.text
    attrs = ""
    if node.attributes:
        parts = [f'{k}="{v}"' for k, v in node.attributes.items()]
        attrs = " " + " ".join(parts)
    inner = "".join(ssmlNodeToText(c) for c in node.children)
    return f"<{node.name}{attrs}>{inner}</{node.name}>"
