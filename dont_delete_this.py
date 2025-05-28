from collections import deque
from grammar.grammar_reader import Grammar,GrammarReader
import networkx as nx
import uuid
from table import ll1_table
import re

"""
    create_token :
        in this function we create token for each words in input by using regex that we got first from the user,
        this function will help us in 'create_dpda' function and help us,
        it return tuple that includes ( Problem(if exist else None),token_list(if input was correct else None) )

    create_dpda:
        this function check if user's input or code is correct and in the right format by looking at LL1 tables and make decision,
        we make this decision by creating transition by looking at input and top of stack and LL1 table,
        the way that it works is it check input token and pop from stack (stack contains nontermianls and terminals and a id that is useful for create graph) if
        poped item is terminal the we check (input,pop) transition by looking to LL1 table if this transition eexist and if poped item is terminal we check
        if input and poped item are equel or no if they were equal then we add input_header else we find that there is problem in the input and it gets reject,
        after we check it if every was ok we return Graph without any probelm but if there was problem we return string of problem and None.
"""

class DPDA :
    def __init__(self,grammer:Grammar,LL1:ll1_table.build_ll1_table):
        self.transition = dict()
        self.grammer = grammer
        self.LL1 =LL1

    def create_transitions(self) -> dict :
        self.grammer.nonterminals.add('$')
        for non_terms in self.grammer.nonterminals:
            for terms in self.grammer.terminals:
                if (non_terms,terms) in self.LL1:
                    my_tuple = (terms,non_terms)
                    self.transition[my_tuple] = self.LL1[(non_terms,terms)][::-1]
        return self.transition

def create_token(input_filepath,grammer:Grammar) -> tuple:
    token_list = []
    inputs_data = list()

    #reading input from txt file
    with open(input_filepath,'r') as input :
        inputs_data = input.read().split()

    #check type of every input by looking at regex
    for item in inputs_data:
        check = True
        for pattern in grammer.token_patterns.keys():
            my_pattern = grammer.token_patterns[pattern]
            first = my_pattern[0]
            last = my_pattern[-1]
            #delete / from first and end of pattern if exist
            if first == '/' and last == '/':
                my_pattern = my_pattern[1:-1]
            #check the word to find its pattern
            match = re.fullmatch(my_pattern,item)
            #add item and its type if matched
            if match is not None:
                check = False
                token_list.append((item,pattern))
                break
        if check :
            #if there is not match pattern so there is probelm and we show what is the problem
            return (f"Mistake in Grammer : '{item}' ",None)
    return (None,token_list)
        
def create_dpda(token:list,grammer:Grammar,LL1:ll1_table.build_ll1_table) -> tuple:
    # create stack by using deque we could use list too , there is no diffrent
    stack = deque()

    #create graph
    graph = nx.DiGraph()

    #add $ sign at the end of the input token
    token.append(("",'$'))

    #create id for nodes that is unique for each node
    id = str(uuid.uuid4())\
    
    #add Start non-terminal and create the root node
    stack.append((grammer.start_symbol,id))
    graph.add_node(id,label = 'Main')

    #input_token_header that is 0 first
    token_index = 0
    while(True):
        if(len(stack) == 0):
            break
        #get top item and extract its data cause it's tuple
        top_stack = stack.pop()
        top = top_stack[0]
        id = top_stack[1]
        word_in_input = str(token[token_index][0])
        word = token[token_index][1]

        #check if top is in nontermials
        if top in grammer.nonterminals:
            if (top,word) in LL1.keys():

                """
                    we use its inverse for adding to stack because we want add for example:
                    E -> TE'
                    if we do it without inverse it adds T then E' and top will be E' but we want T being top so we inverse
                """

                length = len(LL1[(top,word)])
                for items in range(length-1,-1,-1):
                    child_id = str(uuid.uuid4())
                    #add items to stack
                    stack.append((LL1[(top,word)][items],child_id))

                    #add node to graph and then add the directed edge
                    graph.add_node(child_id,label = LL1[(top,word)][items])
                    graph.add_edge(id,child_id)

            else :
                #return problem with None
                return (f"Problem :No Transaction , Input on : '{word}' but Stack on : '{top}'",None)
            
        #check if top is in terminals
        elif top in grammer.terminals:
            if top == word :
                child_id = str(uuid.uuid4())
                #add node to graph and then add the directed edge that this node will be at the end of tree and it will be leaf
                graph.add_node(child_id,label = word_in_input)
                graph.add_edge(id,child_id)

                #change the input_token_header
                token_index += 1
            else :
                #return problem with None
                return (f"Problem : Not Equal (terminals are not Equal) , Input on : '{word}' but Stack of : '{top}'",None)
            
    #return None and graph if there is no problem
    return (None,graph)

        