from logging import root
from nodes import *
def setup_tree():
    
    root = ValueNode(
        description="Versagen der Tunnelnotrufeinrichtung bei Inanspruchnahme durch einen Reisenden",
        position=(750,750)
    )
    
    train_stopped_continued = ValueNode(
        expected_value=0.9997,variance=0,
        description="Zug hat kurz im Tunnel gehalten und ist weitergefahren. (Reisender im Tunnel)",
        position=(350,150))

    train_stopped = ValueNode(
        expected_value=0.0003,variance=0,
        description="Zug ist im Tunnel liegengeblieben",
        position=(1150, 600)
    )

    old_tunnel_one_rail = ValueNode(
        expected_value=0.199,variance=0,
        description="Zug ist im Tunnel liegengeblieben",
        position=(350, 450)
    )

    next_train_incoming = ValueNode(
        #expected_value=0.199,variance=0,
        description="Nächster Zug nähert sich",
        position=(600, 450)
    )

    train_hits_passenger = ValueNode(
        description="Nächster Zug nähert sich",
        position=(100,450)
    )

    #     ('root', 'Versagen der Tunnelnotrufeinrichtung bei Inanspruchnahme durch einen Reisenden', 750, 750, True, False, 'root'),
    #    ('train_stopped_continued', 'Zug hat kurz im Tunnel gehalten und ist weitergefahren. (Reisender im Tunnel) \nµ=0.9997 \nσ²=0', 350, 600, True, False, 'root'),
    #    ('train_stopped', 'Zug ist im Tunnel liegengeblieben \nµ=0.0003 \nσ²=0', 1150, 600, True, False, 'root'),
    #    ('and', 'AND', 350, 300, True, False, 'train_stopped_continued'),
    #    ('old_tunnel_one_rail', 'Altbautunnel eingleisig \nµ=0.199 \nσ²=0', 350, 450, True, False, 'and'),
    #    ('next_train_incoming', 'Nächster Zug nähert sich', 600, 450, True, True, 'and'),
    #    ('train_hits_passenger', 'Zug erfasst Reisenden', 100, 450, True, True, 'and'),
    #    ('_result', 'result', 350, 150, True, False, 'and')
    #)