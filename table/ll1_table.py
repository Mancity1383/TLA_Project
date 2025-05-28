def build_ll1_table(grammar, first, follow) -> dict:
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
                    if 'eps' not in first[symbol]:
                        break
                else:
                    first_alpha.add('eps')

                for a in first_alpha - {'eps'}:
                    table[(A, a)] = production

                if 'eps' in first_alpha:
                    for b in follow[A]:
                        table[(A, b)] = production

    return table
