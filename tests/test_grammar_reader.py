from grammar.grammar_reader import GrammarReader

def test_load_grammar():
    grammar = GrammarReader.load("examples/grammar.ll1")
    assert grammar.start_symbol == "E"
    assert "E_prime" in grammar.nonterminals
    assert "PLUS" in grammar.terminals
    assert "E" in grammar.productions
    assert "IDENTIFIER" in grammar.token_patterns

    