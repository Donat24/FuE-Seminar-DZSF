from re import X, template
from typing import Text
import scipy.stats as stats
import plotly.express as px
import pandas as pd
import numpy as np

# Später auslagern
# __________________________________________________________


#def run_mcs(next_train_incoming, train_hit_passenger):
def run_mcs(nodes):

    #HIER MÜSSTE MIT TREE GERECHNET WERDEN

    train_stopped_continued = [[nodes[1].ew,nodes[1].var]]
    tunnel_types = [[nodes[4].ew,nodes[4].var]]
    next_train_incoming = [[nodes[5].ew,nodes[5].var]]
    train_hit_passenger = [[nodes[6].ew,nodes[6].var]]

    crash_probabilities = []
    lap = 0
    # num simulations
    N = 10_000

    while lap < N:
        crash = 0
        for tunnel_type in range(0, len(tunnel_types)):
            next_train_rnd = get_normal_rnd(next_train_incoming[tunnel_type][0], next_train_incoming[tunnel_type][1])
            train_hit_rnd = get_normal_rnd(train_hit_passenger[tunnel_type][0], train_hit_passenger[tunnel_type][1])
            train_stop_go_rnd = get_normal_rnd(train_stopped_continued[tunnel_type][0], train_stopped_continued[tunnel_type][1])
            tunnel_type_rnd = get_normal_rnd(tunnel_types[tunnel_type][0], tunnel_types[tunnel_type][1])


            #ACHTUNG: train_stop_go_rnd kommt im gesamten Baum nicht in iteration

            # print(next_train_rnd)
            # print(train_hit_rnd)
            # print(train_stop_go_rnd)
            # print(tunnel_type_rnd)

            crash += get_subtree_probability(train_stop_go_rnd, tunnel_type_rnd, next_train_rnd, train_hit_rnd)

        crash_probabilities.append(crash)        
        lap += 1

    avg_crash_prob = sum(crash_probabilities) / len(crash_probabilities)
    print("Accident Probability " + str(avg_crash_prob))
    
    return crash_probabilities
    # todo: Plot erstellen

    # plt.hist(crash_probabilities,  bins=50)
    # plt.xlabel('Accident Probability')
    # plt.ylabel('Count')
    # plt.axvline(avg_crash_prob, color='k', linestyle='dashed', linewidth=2)

    # min_ylim, max_ylim = plt.ylim()
    # plt.text(avg_crash_prob, max_ylim*1.02, 'Mean: {:.4f}'.format(avg_crash_prob))
    # st.pyplot()
    

def get_normal_rnd(ew, var):
    """Return a normal distributed random number between 0 and 1.
    ew -- Erwartungswert
    var -- Varianz
    """
    lower, upper = 0, 1
    if var > 0.0:
        return float(stats.truncnorm.rvs((lower-ew) / var, (upper-ew) / var, loc=ew, scale=var))
    else:
        return ew


def plot(crash_probabilities):

    fig = px.histogram(crash_probabilities, nbins=100, template='plotly_dark', color_discrete_sequence=["cadetblue"])
    
    fig.update_layout(
        hoverlabel=dict(
            bgcolor="#2c2f35",
            font=dict(color='#d8d8d8', size=30),
            font_size=30,
            font_family="Open Sans Semi Bold"
            ),

        paper_bgcolor='rgba(0, 0, 0, 0)',
        plot_bgcolor='rgba(0, 0, 0, 0)',
    )
    fig.layout.update(showlegend=False)
    fig.update_yaxes(title_text='count',row=1, col=1, tickfont = dict(size=30), title=dict(font=dict(size=30)))
    fig.update_xaxes(title_text='crash probability',row=1, col=1, tickfont=dict(size=30), title=dict(font=dict(size=30)))
    fig.add_vline(x=np.median(crash_probabilities), line_dash = 'dash', line_color = 'Black', line_width=5)

    return fig

def get_subtree_probability(*args):
    result = 1
    for probability in args:
        result = result * probability
    return result


def get_label_of_node(nodes, id):
    for node in nodes:
        if node[0] == id:
            return (node[0],node[1])

class EventNode(object):
    def __init__(self, id, label, type):
        if 'µ=' in label and 'σ²=' in label:
            self.ew = float(label.split(' ')[-2].strip()[2:])
            self.var = float(label.split(' ')[-1].strip()[3:])
        else: 
            self.ew = None
            self.var = None
        self.id = id
        self.label = label
        self.node_type = type



        


# __________________________________________________________
