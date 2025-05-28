from first_follow import first_follow
from grammar.grammar_reader import GrammarReader
from table import ll1_table
import dpda_and_tree as DPDA
import matplotlib.pyplot as plt
import networkx as nx

grammer = GrammarReader.load("x.txt")
first = first_follow.compute_first(grammer)
follow = first_follow.compute_follow(grammer, first)
LL1_table = ll1_table.build_ll1_table(grammer, first, follow)

dpda = DPDA.DPDA(grammer,LL1_table)
transitions = dpda.create_transitions()
token_check,token_list = DPDA.create_token('y.txt', grammer)
graph = DPDA.create_dpda(token_list, grammer, transitions)