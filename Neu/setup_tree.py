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

    and_node = AndNode(
        description="And",
        position=(350, 300)
    )

    old_tunnel_one_rail = ValueNode(
        expected_value=0.199,variance=0,
        description="Altbautunnel eingleisig",
        position=(350, 450)
    )

    next_train_incoming = ValueNode(
        #expected_value=0.199,variance=0,
        description="Nächster Zug nähert sich",
        position=(600, 450)
    )

    train_hits_passenger = ValueNode(
        description="Zug erfasst Reisenden",
        position=(100,450)
    )

    root.add_parent(train_stopped)
    root.add_parent(next_train_incoming)

    and_node.add_child(next_train_incoming)
    and_node.add_child(old_tunnel_one_rail)
    and_node.add_child(train_hits_passenger)

    and_node.add_parent(train_stopped_continued)
    