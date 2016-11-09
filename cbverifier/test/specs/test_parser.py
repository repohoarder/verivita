""" Test the traces package.

"""

import logging
import unittest



from ply.lex import LexToken
import ply.yacc as yacc


try:
    import unittest2 as unittest
except ImportError:
    import unittest

from cbverifier.specs.spec_lex import lexer
from cbverifier.specs.spec_parser import spec_parser

import cbverifier.specs.spec_parser




class TestSpecs(unittest.TestCase):

    @staticmethod
    def new_tok(lexpos, tok_type, lineno, value):
        # Create a token for return
        tok = LexToken()
        tok.value = value
        tok.lineno = lineno
        tok.lexpos = lexpos
        tok.type = tok_type

        return tok

    def _test_multiple_token(self, token_list, string):
        # clean the lexer state
        # for f in lexer: None
        lexer.input(string)

        i = 0
        tok = lexer.token()
        while (tok is not None):
            if i > len(token_list):
                raise Exception("Found more tokens than expeced")

            self.assertTrue(tok.value == token_list[i].value)
            self.assertTrue(tok.lineno == token_list[i].lineno)
            self.assertTrue(tok.lexpos == token_list[i].lexpos)
            self.assertTrue(tok.type == token_list[i].type)

            i = i + 1
            tok = lexer.token()

        # did not parse anything else
        with self.assertRaises(StopIteration):
            lexer.next()

    def _test_single_token(self, lexpos, tok_type, lineno, value, string):
        tok_ref = TestSpecs.new_tok(lexpos,tok_type,lineno,value)

        return self._test_multiple_token([tok_ref], string)


    def test_lexer(self):
        self._test_single_token(0,'TOK_ID',1,'ciao','ciao')
        self._test_single_token(0,'TOK_INT',1,2,'2')
        self._test_single_token(0,'TOK_FLOAT',1,0.0,'0.0')

        self._test_single_token(0, 'TOK_NOT', 1, '!', '!')
        self._test_single_token(0, 'TOK_AND', 1, '&', '&')
        self._test_single_token(0, 'TOK_OR', 1, '|', '|')
        self._test_single_token(0, 'TOK_SEQUENCE', 1, ';', ';')
        self._test_single_token(0, 'TOK_STAR', 1, '[*]', '[*]')
        self._test_single_token(0, 'TOK_ENABLE', 1, '|+', '|+')
        self._test_single_token(0, 'TOK_DISABLE', 1, '|-', '|-')
        self._test_single_token(0, 'TOK_DOT', 1, '.', '.')
        self._test_single_token(0, 'TOK_COMMA', 1, ',', ',')
        self._test_single_token(0, 'TOK_LPAREN', 1, '(', '(')
        self._test_single_token(0, 'TOK_RPAREN', 1, ')', ')')

        self._test_single_token(0, 'TOK_TRUE', 1, 'TRUE', 'TRUE')
        self._test_single_token(0, 'TOK_FALSE', 1, 'FALSE', 'FALSE')
        self._test_single_token(0, 'TOK_SPEC', 1, 'SPEC', 'SPEC')




            # TestSpecs.new_tok(lexpos,tok_type,lineno,value)
        res = [TestSpecs.new_tok(0,'TOK_ID',1,'l'),
               TestSpecs.new_tok(1,'TOK_DOT',1,'.'),
               TestSpecs.new_tok(2,'TOK_ID',1,'l'),
               TestSpecs.new_tok(3,'TOK_LPAREN',1,'('),
               TestSpecs.new_tok(4,'TOK_RPAREN',1,')')]
        self._test_multiple_token(res, "l.l()"),




    def test_parser(self):
        # a = parser.parse("SPEC l.o|nClick(l) |- l.onDestroy(b)")
        #a = parser.parse("SPEC l.l() |- l.l(b)")
        #a = parser.parse("SPEC l.l() |- l.l(b)")

        a = spec_parser.parse("SPEC l.l() |- l.l(b)")
        print a

        self.assertTrue(a is not None)
