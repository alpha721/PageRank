"""@package docstring
Documentation for this module
  @author Neetu
"""

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from fractions import Fraction


###################### Visualization #################################

def draw_graph(matrix, ratings,labels=None, graph_layout='random',
               node_size=1600, node_color='blue', node_alpha=0.3,
               node_text_size=12,
               edge_color='blue', edge_alpha=0.3, edge_tickness=1,
               edge_text_pos=0.3,
               text_font='sans-serif'):
    """ function for visualization of the pagerank algorithm """
    
    # create networkx graph
    G=nx.Graph()

    nodes = set([i for i in range(0,100)])
    
    #add nodes
    for node in nodes:
      G.add_node(node)
      
    #add edges  
    for i in range(0,100):
      for j in range(0,100):
        if ( matrix.item((i,j)) == 1.0):
          G.add_edge(i,j) 
           
    # these are different layouts for the network you may try
    # random seems to work best

    if graph_layout == 'spring':
        graph_pos=nx.spring_layout(G)
    elif graph_layout == 'spectral':
        graph_pos=nx.spectral_layout(G)
    elif graph_layout == 'random':
        graph_pos=nx.random_layout(G)
    else:
        graph_pos=nx.shell_layout(G)   
    
    # draw graph
    nx.draw_networkx_nodes(G,graph_pos,node_size=node_size, 
                           alpha=node_alpha, node_color=node_color)
    nx.draw_networkx_edges(G,graph_pos,width=edge_tickness,
                           alpha=edge_alpha,edge_color=edge_color)
    nx.draw_networkx_labels(G, graph_pos,font_size=node_text_size,
                            font_family=text_font)

    if labels is None:
        labels = range(n)

    l = {}
    for i in range(0,100):
      l[i] = ratings[i]
    nx.draw_random(G,node_size = ratings*100, labels = l, with_labels= True)

    # show graph
    plt.show()

###################################################################################################

"""
the following code takes in a data file and computes pagerank for each node in the data
Two choices are available :
  1. General pagerank
  2. Topic-specific pagerank

"""

def main():
    """ main function """

    # given alpha value
    alpha = 0.85
    
    # read text from given data
    lines = read_data("adj_matrix")

    node = len(lines)
    
    # get adjacency matrix 
    adj_mat = get_adj_mat(lines)
    
    adj_mat = np.matrix(adj_mat)
    
    """ here choice is given to the user to either choose:
        i) general pagerank
        ii) If topic specific pagerank, choose from a list of topics provided
    """
    pages = choose_topic()
    if ( pages == -1):
        page_rank(adj_mat)
    else: 
        topic_page_rank(adj_mat,pages)
      
        

def read_data(file_name):
    """ function to read data from the file
        Input: file name
        Returns: a vector consisting of each line read from the file  
    """

    f = open(file_name, 'r') # open file_name
    lines = f.readlines()    # store data into lines               
    f.close()                # close file_name
    return lines             # return data
    
def get_adj_mat(lines):
    """ function to construct adjacency matrix for the data
        Input: vector of lines read from the data
        Output: adjacency matrix
    """
    
    num_of_node = len(lines)
    
    adj_matrix = np.zeros((num_of_node,num_of_node)) # get matrix of zeros

    for i in range(0,num_of_node):
        for j in range(0,num_of_node):
            adj_matrix[i][j] = float(lines[i][j*2]) # add 1 to places that have edge(s)

    M = np.matrix(adj_matrix) #convert to required matrix format
    return M

############################## PAGE RANK ######################################################
    
def page_rank(adj_matrix):
    """ function implementing general pagerank algorithm
        Uses power iteration method
        Input: adj_matrix for the data
        Output: Retrieves top 10 results based on the pagerank computed 
    """

    M = adj_matrix
    M = np.matrix(M) #convert to required matrix format
    
    """ construct the teleportation matrix """
    n = len(adj_matrix)
    prob_matrix = np.zeros((n,n))
    dp = Fraction(1,n)
    prob_matrix[:] = dp #teleportation matrix

    # default value of beta
    beta = 0.85
    
    adj_matrix *= 1.0
    
    """the following code handles : i) spider traps ii) dead ends """ 
    
    for i in range(0,n):
        if( sum(adj_matrix[:,i]) == 0):
            adj_matrix[:,i] = 1.0/n
        else: adj_matrix[:,i] *= 1.0/sum(adj_matrix[:,i])

    # calculate the probability matrix using the general pagerank formula
    A = adj_matrix * beta + (( 1 - beta) * prob_matrix)

    """ power iteration """
    
    r = np.matrix([dp]*n)
    r = np.transpose(r)

    previous_r = r

    for it in range(1,100):
        r = A*r
        if( previous_r == r).all():
            break
        previous_r = r

    
    ratings = r
    ratings = [i[0] for i in sorted(enumerate(ratings),key=lambda x:x[1])]# reverse = True)]
    
    #show the top 10 searches
    
    f = open("nodes",'r')
    lines = f.readlines()

    #number of nodes 
    n =  float(lines[0])

    a = {}
    i = 2
    while ( i < len(lines)):
        line = lines[i]

        no = float(line.split(None, 1)[0])
        l = lines[i+1]
        a[no] = l

        i += 5

    print "the top 10 results of the general search: "
    for i in range(0,10):
      print a[ratings[i]]
      print "\n"

########################################################################################################

######################## TOPIC SPECIFIC PAGERANK #######################################################    

def choose_topic():
    """ function for choosing a topic from a given set of topics for topic specific pagerank """

    print "choose a specific topic from the list given: "
    print "or input -1 for performing a general search"
    t = open("topic")
    lines = t.readlines()
    for i in range(0,len(lines)):
        print lines[i].split()[0] 

    x = raw_input("topic-id >> ")
    x = int(x)

    if ( x == -1):
        return -1
    
    for i in range(0,len(lines)):
        line = lines[i]
        words = line.split()
        word = words[0]
        topic = int(word.split(':')[0])

        if( topic == x):
            data = words[1:]
            print data
            break
    pages = []
    for i in range(len(data)):
        pages.append(int(data[i]))

    return pages

def topic_page_rank(adj_matrix,topic):
    """ function implementing topic specific pagerank"""

    """ the teleportation matrix
        Here the probability of teleporting to the topic specific pages 
        than the general pages 
    """
    n = len(adj_matrix)
    prob_matrix = np.matrix([0.0]*n)
    prob_matrix = np.transpose(prob_matrix)
    prob_matrix *= 1.0
    dp = Fraction(1,n)

    for i in topic:
        prob_matrix[i] = 1.0/len(topic)


    beta = 0.85
    
    adj_matrix *= 1.0
    for i in range(0,n):
        if( sum(adj_matrix[:,i]) == 0):
            adj_matrix[:,i] = 1.0/n
        else: adj_matrix[:,i] *= 1.0/sum(adj_matrix[:,i])

    #the probabilty matrix
    A = adj_matrix * beta + (( 1 - beta) * prob_matrix)

    """ power iteration """
    
    r = np.matrix([dp]*n)
    r = np.transpose(r)

    previous_r = r

    for it in range(1,100):
        r = A*r
        if( previous_r == r).all():
            break
        previous_r = r

    
    ratings = r
    ratings = [i[0] for i in sorted(enumerate(ratings),key=lambda x:x[1], reverse = True)]
    
    #show the top 10 searches
    
    f = open("nodes",'r')
    lines = f.readlines()

    #number of nodes 
    n =  float(lines[0])

    a = {}
    i = 2
    while ( i < len(lines)):
        line = lines[i]

        no = float(line.split(None, 1)[0])
        l = lines[i+1]
        a[no] = l

        i += 5

    print "the top 10 results of the topic specific search: "
    for i in range(0,10):
      print a[ratings[i]]
      print "\n"

###########################################################################################


if __name__ == "__main__":
    main() 
