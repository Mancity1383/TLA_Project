def build_ll1_table(grammar, first, follow):
    # LL(1) parse table:
    # key   = (Nonterminal, Terminal)
    # value = RHS of the production A → α (as a list of symbols)
    table = {}

    for A, productions in grammar.productions.items():
        for production in productions:

            if production == ['eps']:
                for b in follow[A]:
                    table[(A, b)] = production

            else:
                first_alpha = set()
                for symbol in production:
                    first_alpha |= (first[symbol] - {'eps'})
                    if 'eps' not in first[symbol]:   #if eps it continues the loop.
                        break
                else:
                    first_alpha.add('eps')

                for a in first_alpha - {'eps'}:
                    table[(A, a)] = production

                if 'eps' in first_alpha:
                    for b in follow[A]:
                        table[(A, b)] = production

    return table
