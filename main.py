
from flask import Flask, request, render_template_string,jsonify
from pyvis.network import Network
import json
from first_follow import first_follow
from grammar.grammar_reader import GrammarReader,Grammar
from table import ll1_table
import dpda.dpda_and_tree as DPDA
import matplotlib.pyplot as plt
import networkx as nx

"""
    for using some option like clicking and selecting and for showing problems we decided to use Flask library that give us this features ,
    we have home page that shows Graph if there was no problem and shows error if there was problem,
    and for showing graph with networkX library we needed html file and we add pyvis library to extend the feautres too,
    we could use other library like Graphviz but the output was picture and pdf but we wanted to select the nodes and being able to move them,
    it is more beautiful in this way too :)
    we used this Colab Link : https://colab.research.google.com/drive/1upm3eO935KQQIA-2Kffg2hGu8387UnXp#scrollTo=49SXPOHWBNqN
    to create network and visualize out graph in html

"""
G = nx.DiGraph()
grammer = Grammar()

#Find the main parent of the selected_node to start checking to down from that
def check_parent(sent_node):
    global G
    my_node = dict()
    for nodes,data in G.nodes(data=True):
       if nodes == sent_node :
          my_node = data
    children_list = []

    for node, data in G.nodes(data=True):
        if "parent" in data and data["parent"] == sent_node:
            children_list.append(node)

    for item in children_list:
        if G.nodes[item]['label'] in ['LEFT_PAR','LEFT_BRACE']:
            return sent_node

    if 'parent' not in my_node:
        return None

    return check_parent(my_node['parent'])
     
#Rename the label by finding node that has same label in same scope
def change_the_label(sent_node,main_node,selected_label,choosen_label):
    global G
    if G.out_degree(sent_node) == 0 :
        return
    children_list = []
    
    for node, data in G.nodes(data=True):
        if "parent" in data and data["parent"] == sent_node:
            # if data['label'] == 'LEFT_PAR' and sent_node != main_node:
            #     return
            children_list.append(node)
    for item in children_list:
        change_the_label(item,main_node,selected_label,choosen_label)
        if G.nodes[item]['label'] == selected_label:
            print(G.nodes[item]['label'])
            G.nodes[item]['label'] = choosen_label
    

app = Flask(__name__)
@app.route("/")
def index():
    global G,grammer
    #Get the grammer from txt file
    grammer = GrammarReader.load("x.txt")
    #Create first for every nonterminal to use in creating LL1 Table
    first = first_follow.compute_first(grammer)
    #Create Follow for every nonterminal to use in creating LL1 Table
    follow = first_follow.compute_follow(grammer, first)
    #Create LL1 Table
    LL1_table = ll1_table.build_ll1_table(grammer, first, follow)
    #Create Token from input
    token_check,token_list = DPDA.create_token('y.txt', grammer)
    if token_list is None :
       return render_template_string("""
          <html>
            <head>
              <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
              <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css">
            </head>
            <body>
              <div class="d-flex justify-content-center align-items-center" style="margin-top: 500px;">
                <div class="alert alert-danger d-flex align-items-center" role="alert">
                  <i class="bi bi-exclamation-triangle-fill me-2"></i>
                  <div>""" + token_check + """</div>
                </div> 
              </div>

                 <div class="d-flex justify-content-center align-items-center">
                <div class="alert alert-info d-flex align-items-center" role="alert">
                  <i class="bi bi-question-circle-fill me-2"></i>
                  <div>Fix Your Mistake Stupid!!</div>
                </div>
              </div>
            </body>
          </html>

           """
          )
    else:
      #Check Accept or Reject and Create Graph
      dpda = DPDA.DPDA(grammer,LL1_table)
      transitions = dpda.create_transitions()
      token_check,token_list = DPDA.create_token('y.txt', grammer)
      Check,graph = DPDA.check_and_create_graph(token_list, grammer, transitions)

      if Check is None:
        G= graph
        #Choose size of nodes
        for _, props in G.nodes(data=True):
            props['size'] = 20

        """
        opts :
              in opts part we add some feautures to the graph that we created like :
                1.if user selected the node it gets border that user gets which nodes got selected
                2.size and type of font to show the labels of nodes
                3.put the the graph in tree form and make it UP to Down form
                4.set how nodes get sorted within levels that can have 	"hubsize" (by node degree) value too but its isn't useful here
                5. we can disable phyics too but here i prefer to be enable
        """
        opts = {
        "nodes": {
        "borderWidthSelected": 5,
        "font": {
          "size": 20,
          "face": "verdana"
          }
        },
        "layout": {
          "hierarchical": {
            "enabled": True,
            "direction": "UD",
            "sortMethod": "directed",
          }
        },
      }
        
        #Create Network from graph can set option on network
        net = Network(height="1080px", width="100%", directed=True)
        net.set_options(json.dumps(opts))


        """
          in this part we find the root that has in_degree 0 that means there is no parent for it,
          and we find the level of each nodes by using Shortest Path algorithm,
          then we add level data to data of each node to use it when we want add nodes to network
          !! we can do it by using function "from_nx" but makes it messy
        """

        root = [n for n, d in G.in_degree() if d == 0][0]
        levels = nx.single_source_shortest_path_length(G, root)

        for node, level in levels.items():
            G.nodes[node]["level"] = level

        for node,data in G.nodes(data=True):
          net.add_node(node,label=data.get("label", node), level=G.nodes[node]["level"])

        """
          in this part we had problem that the tree was reversed and we decided to add edges in the reverse to for example :
            if T node is in Right part and E_prime node is in the left part of parent node by doing this we 
            changes theirs sides
        """
        edges = list(G.edges())
        edges = edges[::-1]
        for source, target in edges:
            net.add_edge(source, target)
            G.nodes[target]["parent"] = source

        html = net.generate_html()

        #add click option to get data about the nodes that clicked by user and get new_label data with using JavaScipts
        click_script = """
        <script type="text/javascript">
        document.addEventListener("DOMContentLoaded", () => {
        const network = window.network;

        network.on("click", function(params) {
        if (!params.nodes.length) return;
        const node = network.body.data.nodes.get(params.nodes[0]);

        const promptText = `
        This is a new option just for you my little stupid
        change whatever you like, now you change the "${node.label}"
        then you try to change the world, now what name do you wana choose?
        `.trim();

        const newLabel = window.prompt(promptText, node.label);

        if (newLabel === null) return;

        fetch("/node_click", {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify({
        id:        node.id,
        label:     node.label,
        new_label: newLabel
        })
        })
        .then(res => res.json())
        .then(data => {
        network.body.data.nodes.update(data.changed || data);
        })
        .catch(console.error);
        });
        });
        </script>

        """
        #add click option to html part
        page = html.replace("</body>", click_script + "\n</body>")
        return render_template_string(page)
      else:
        
        """
          in this part we show the user what is the problem and where is the problem when the code was runing that helped me to debug better :)
          for showing the problem we use 'Check' varible that we used for accept or reject,
          then we suggest a way to fix it too :)))))))
        """

        return render_template_string("""
            <html>
              <head>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
                <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css">
              </head>
              <body>
                <div class="d-flex justify-content-center align-items-center" style="margin-top: 500px;">
                  <div class="alert alert-danger d-flex align-items-center" role="alert">
                    <i class="bi bi-exclamation-triangle-fill me-2"></i>
                    <div>""" + Check + """</div>
                  </div> 
                </div>

                  <div class="d-flex justify-content-center align-items-center">
                  <div class="alert alert-info d-flex align-items-center" role="alert">
                    <i class="bi bi-question-circle-fill me-2"></i>
                    <div>Fix Your Mistake Stupid!!</div>
                  </div>
                </div>
              </body>
            </html>

            """
            )

    

@app.route("/node_click", methods=["POST"])
def node_click():
    global grammer
    data = request.get_json()
    main_id = data["id"]
    clicked_label = data["label"]
    new_label= data["new_label"]
    if(clicked_label) not in grammer.terminals and (clicked_label) not in grammer.nonterminals:
      parent = check_parent(main_id)
      change_the_label(parent,parent, clicked_label,new_label)

      changed = []
      for node, attrs in G.nodes(data=True):
          changed.append({
              "id":    node,
              "label": attrs["label"]
          })

      return jsonify(changed=changed)

if __name__ == "__main__":
    app.run(debug=True)


