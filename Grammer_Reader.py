

class Grammar:
    def __init__(self):
        self.start_symbol = None             
        self.nonterminals = set()            
        self.terminals = set()                
        self.productions = dict()            
        self.token_patterns = dict()         


class GrammarReader:
    @staticmethod
    def load(filepath: str) -> Grammar:
        grammar = Grammar()

        with open(filepath, 'r') as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                if line.startswith("START ="):
                    grammar.start_symbol = line.split('=')[1].strip()

                elif line.startswith("NON_TERMINALS ="):
                    grammar.nonterminals = {
                        x.strip() for x in line.split('=')[1].split(',')
                    }

                elif line.startswith("TERMINALS ="):
                    grammar.terminals = {
                        x.strip() for x in line.split('=')[1].split(',')
                    }

                elif '->' in line:
                    head, body = line.split('->')
                    head = head.strip()
                    body = body.strip()

                    if head in grammar.nonterminals:
                        alternatives = [
                            alt.strip().split() for alt in body.split('|')
                        ]
                        grammar.productions.setdefault(head, []).extend(alternatives)
                    else:
                        grammar.token_patterns[head] = body

        return grammar



