from grammar.grammar_reader import GrammarReader
def compute_first(grammar):
    first = {}
    for symbol in grammar.nonterminals:
        first[symbol] = set()
    for symbol in grammar.terminals:
        first[symbol] = {symbol}

    for terminal in grammar.terminals:
        first[terminal].add(terminal)

    changed = True
    while changed:
        changed = False

        for head in grammar.productions:
            for production in grammar.productions[head]:
                if production == ['eps']:
                    if 'eps' not in first[head]:
                        first[head].add('eps')
                        changed = True
                    continue

                for symbol in production:
                    before = len(first[head])
                    first[head].update(first[symbol] - {'eps'})       
                    after = len(first[head])

                    if after > before:
                        changed = True

                    if 'eps' not in first[symbol]:     
                        break
                else:
                    if 'eps' not in first[head]:
                        first[head].add('eps')
                        changed = True

    return first

# grammar = GrammarReader.load("examples/grammar.ll1")
# print(compute_first(grammar))




def compute_follow(grammar, first):

    follow = {}
    for nonterminal in grammar.nonterminals:
        follow[nonterminal] = set()

    follow[grammar.start_symbol].add('$')

    changed = True
    while changed:
        changed = False

        for head, productions in grammar.productions.items():
            for production in productions:
                trailer = follow[head].copy()

                for symbol in reversed(production):
                    if symbol in grammar.nonterminals:
                        before = len(follow[symbol])
                        follow[symbol].update(trailer)
                        after = len(follow[symbol])
                        if after > before:
                            changed = True

                        if 'eps' in first[symbol]:
                            trailer.update(first[symbol] - {'eps'})
                        else:
                            trailer = first[symbol].copy()

                    else:
                        trailer = {symbol}

    return follow




# to run this file we should do like this:
#                                           python -m first_follow.first_follow