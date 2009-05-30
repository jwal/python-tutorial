"""miscelanneous utility functions

XXX: svn mv pythonutil.py gramtools.py / parsertools.py
"""

import sys
import os
import parser2

# from pypy.interpreter.pyparser.grammar import Parser
from pytoken2 import setup_tokens
from ebnfgrammar2 import GRAMMAR_GRAMMAR
from ebnflexer2 import GrammarSource
from ebnfparse2 import EBNFBuilder

from tuplebuilder2 import TupleBuilder

PYTHON_VERSION = ".".join([str(i) for i in sys.version_info[:2]])

def dirname(filename):
    """redefine dirname to avoid the need of os.path.split being rpython
    """
    i = filename.rfind(os.sep) + 1
    assert i >= 0
    return filename[:i]


def get_grammar_file(version):
    """NOT_RPYTHON
       Returns the python grammar corresponding to our CPython version."""
    # building parsers at run-time kind of works, but the logic to load
    # the grammar file from pypy/interpreter/pyparser/data/, moreover with
    # a hard-coded absolute path, makes little sense in a translated PyPy.
    # This is why this function is marked as NOT_RPYTHON.

    if version == "native":
        _ver = PYTHON_VERSION
    elif version == "stable":
        _ver = "_stablecompiler"
    elif version in ("2.3","2.4","2.5a","2.5"):
        _ver = version
    else:
        raise ValueError('no such grammar version: %s' % version)
    # two osp.join to avoid TyperError: can only iterate over tuples of length 1 for now
    # generated by call to osp.join(a, *args)
    return os.path.join( dirname(__file__), "Grammar" + _ver), _ver


def build_parser(gramfile, parser):
    """reads a (EBNF) grammar definition and builds a parser for it"""
    setup_tokens(parser)
    # XXX: clean up object dependencies
#     from pypy.rlib.streamio import open_file_as_stream
    stream = open(gramfile, "rb")
    try:
        grammardef = stream.read()
    finally:
        stream.close()
    assert isinstance(grammardef, str)
    source = GrammarSource(GRAMMAR_GRAMMAR, grammardef)
    builder = EBNFBuilder(GRAMMAR_GRAMMAR, dest_parser=parser)
    GRAMMAR_GRAMMAR.root_rules['grammar'].match(source, builder)
    builder.resolve_rules()
    parser.build_first_sets()
    parser.keywords = builder.keywords
    return parser


def build_parser_for_version(version, parser):
    gramfile, _ = get_grammar_file(version)
    return build_parser(gramfile, parser)


# ## XXX: the below code should probably go elsewhere

# ## convenience functions for computing AST objects using recparser
# def ast_from_input(input, mode, transformer, parser):
#     """converts a source input into an AST

#      - input : the source to be converted
#      - mode : 'exec', 'eval' or 'single'
#      - transformer : the transfomer instance to use to convert
#                      the nested tuples into the AST
#      XXX: transformer could be instantiated here but we don't want
#           here to explicitly import compiler or stablecompiler or
#           etc. This is to be fixed in a clean way
#     """
#     builder = TupleBuilder(parser, lineno=True)
#     parser.parse_source(input, mode, builder)
#     tuples = builder.stack[-1].as_tuple(True)
#     return transformer.compile_node(tuples)


# def pypy_parse(source, mode='exec', lineno=False):
#     from pypy.interpreter.pyparser.pythonparse import PythonParser, make_pyparser
#     # parser = build_parser_for_version("2.4", PythonParser())
#     parser = make_pyparser('stable')
#     builder = TupleBuilder(parser)
#     parser.parse_source(source, mode, builder)
#     return builder.stack[-1].as_tuple(lineno)


# def source2ast(source, mode='exec', version='2.4', space=None):
#     from pypy.interpreter.pyparser.pythonparse import PythonParser, make_pyparser
#     from pypy.interpreter.pyparser.astbuilder import AstBuilder
#     parser = make_pyparser(version)
#     builder = AstBuilder(parser, version, space=space)
#     parser.parse_source(source, mode, builder)
#     return builder.rule_stack[-1]


# ## convenience functions around CPython's parser functions
# def python_parsefile(filename, lineno=False):
#     """parse <filename> using CPython's parser module and return nested tuples
#     """
#     pyf = file(filename)
#     source = pyf.read()
#     pyf.close()
#     return python_parse(source, 'exec', lineno)

# def python_parse(source, mode='exec', lineno=False):
#     """parse python source using CPython's parser module and return
#     nested tuples
#     """
#     if mode == 'eval':
#         tp = parser.expr(source)
#     else:
#         tp = parser.suite(source)
#     return parser.ast2tuple(tp, line_info=lineno)

# def pypy_parsefile(filename, lineno=False):
#     """parse <filename> using PyPy's parser module and return
#     a tuple of three elements :
#      - The encoding declaration symbol or None if there were no encoding
#        statement
#      - The TupleBuilder's stack top element (instance of
#        tuplebuilder.StackElement which is a wrapper of some nested tuples
#        like those returned by the CPython's parser)
#      - The encoding string or None if there were no encoding statement
#     nested tuples
#     """
#     pyf = file(filename)
#     source = pyf.read()
#     pyf.close()
#     return pypy_parse(source, 'exec', lineno)