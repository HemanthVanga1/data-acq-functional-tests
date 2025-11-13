#!/usr/bin/env python3
"""
Unit tests for SSML parsing utilities.
"""

import unittest
import xmlrunner
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from ssml import SSMLTag, SSMLText, parseSSML, ssmlNodeToText  # Adjust import path

class TestParseSSML(unittest.TestCase):
    def test_parse_tag_names(self):
        self.assertEqual(parseSSML("<speak></speak>"), SSMLTag(name="speak"))
        self.assertEqual(
            parseSSML("<speak><p></p></speak>"),
            SSMLTag(name="speak", children=[SSMLTag(name="p")]),
        )
        self.assertEqual(
            parseSSML("< speak   >< p ></  p ></speak >"),
            SSMLTag(name="speak", children=[SSMLTag(name="p")]),
        )

    def test_throw_on_missing_speak_tag(self):
        self.assertRaises(Exception, lambda: parseSSML("Hello world"))
        self.assertRaises(Exception, lambda: parseSSML("<p>Hello world</p>"))
        self.assertRaises(
            Exception, lambda: parseSSML("<p><speak>Hello world</speak></p>")
        )
        self.assertRaises(Exception, lambda: parseSSML("Hello <speak>world</speak>"))

    def test_throw_on_multiple_top_level_tags_or_text(self):
        self.assertRaises(
            Exception, lambda: parseSSML("<speak>Hello world</speak><foo></foo>")
        )
        self.assertRaises(Exception, lambda: parseSSML("<speak>Hello world</speak>foo"))
        self.assertRaises(
            Exception, lambda: parseSSML("<foo></foo><speak>Hello world</speak>")
        )
        self.assertRaises(Exception, lambda: parseSSML("foo<speak>Hello world</speak>"))

    def test_throw_on_missing_or_invalid_ssml_opening_and_closing_tags(self):
        self.assertRaises(Exception, lambda: parseSSML("<speak>Hello world"))
        self.assertRaises(Exception, lambda: parseSSML("Hello world</speak>"))
        self.assertRaises(Exception, lambda: parseSSML("<speak><p>Hello world</speak>"))
        self.assertRaises(
            Exception, lambda: parseSSML("<speak>Hello world</p></speak>")
        )
        self.assertRaises(
            Exception, lambda: parseSSML("<speak><p>Hello <s>world</s></speak>")
        )
        self.assertRaises(
            Exception, lambda: parseSSML("<speak><p>Hello <s>world</p></speak>")
        )
        self.assertRaises(
            Exception, lambda: parseSSML("<speak><p>Hello <s>world</p></p></speak>")
        )
        self.assertRaises(
            Exception, lambda: parseSSML("<speak><p>Hello world</s></speak>")
        )
        self.assertRaises(
            Exception, lambda: parseSSML("<speak><p>Hello world</p></p></speak>")
        )

    def test_parse_tag_attributes(self):
        self.assertEqual(
            parseSSML('<speak foo=""></speak>'),
            SSMLTag(name="speak", attributes={"foo": ""}),
        )
        self.assertEqual(
            parseSSML('<speak foo="bar"></speak>'),
            SSMLTag(name="speak", attributes={"foo": "bar"}),
        )
        self.assertEqual(
            parseSSML('<speak baz:foo="bar"></speak>'),
            SSMLTag(name="speak", attributes={"baz:foo": "bar"}),
        )
        self.assertEqual(
            parseSSML('<speak foo  = "bar"></speak>'),
            SSMLTag(name="speak", attributes={"foo": "bar"}),
        )
        self.assertEqual(
            parseSSML('<speak foo  = "bar" hello="world"></speak>'),
            SSMLTag(name="speak", attributes={"foo": "bar", "hello": "world"}),
        )
        self.assertEqual(
            parseSSML('<speak><p foo="bar">Hello</p></speak>'),
            SSMLTag(
                name="speak",
                children=[
                    SSMLTag(
                        name="p",
                        attributes={"foo": "bar"},
                        children=[SSMLText("Hello")],
                    )
                ],
            ),
        )

    def test_throw_on_invalid_tag_attributes(self):
        self.assertRaises(Exception, lambda: parseSSML("<speak foo='bar'></speak>"))
        self.assertRaises(Exception, lambda: parseSSML("<speak foo></speak>"))
        self.assertRaises(Exception, lambda: parseSSML('<speak foo="bar></speak>'))
        self.assertRaises(Exception, lambda: parseSSML("<speak foo=bar></speak>"))
        self.assertRaises(Exception, lambda: parseSSML('<speak foo=bar"></speak>'))
        self.assertRaises(Exception, lambda: parseSSML('<speak ="bar"></speak>'))

    def test_parse_text(self):
        self.assertEqual(
            parseSSML("<speak>Hello world</speak>"),
            SSMLTag(name="speak", children=[SSMLText("Hello world")]),
        )
        self.assertEqual(
            parseSSML("<speak>Hello<p> world</p> foo</speak>"),
            SSMLTag(
                name="speak",
                children=[
                    SSMLText("Hello"),
                    SSMLTag(
                        name="p",
                        children=[
                            SSMLText(" world"),
                        ],
                    ),
                    SSMLText(" foo"),
                ],
            ),
        )

    def test_node_to_text(self):
        self.assertEqual(
            ssmlNodeToText(SSMLTag(name="speak", children=[SSMLText("Hello world")])),
            "<speak>Hello world</speak>",
        )
        self.assertEqual(
            ssmlNodeToText(
                SSMLTag(
                    name="speak",
                    children=[
                        SSMLText("Hello"),
                        SSMLTag(
                            name="p",
                            attributes={"attr": "value"},
                            children=[
                                SSMLText(" world"),
                            ],
                        ),
                        SSMLText(" foo"),
                    ],
                )
            ),
            '<speak>Hello<p attr="value"> world</p> foo</speak>',
        )

    def test_unescape_xml_characters_in_text(self):
        self.assertEqual(
            parseSSML("<speak>TS &gt; JS</speak>"),
            SSMLTag(
                name="speak",
                children=[
                    SSMLText("TS > JS"),
                ],
            ),
        )
        self.assertEqual(
            parseSSML("<speak>TS &amp;&gt; JS</speak>"),
            SSMLTag(
                name="speak",
                children=[
                    SSMLText("TS &> JS"),
                ],
            ),
        )

if __name__ == "__main__":
    if os.getenv('CI'): 
        os.makedirs('test-reports', exist_ok=True)
        xml_output = 'test-reports/ssml.xml'
        with open(xml_output, 'wb') as output:
            unittest.main(
                testRunner=xmlrunner.XMLTestRunner(output=output, verbosity=2) ,exit=False, failfast=False, buffer=False, catchbreak=False
            )
        sys.exit(0)
    else:
        unittest.main()
        sys.exit(0)