"""
Class encodings allows to convert labels/ids to class names on importing annotations or do
convert other way around on exporting annotations.

Available class encodings:
    - GoogleKnowledgeGraph
    - WordNet
"""

custom = 'custom'
autodetect = 'autodetect'
google_knowledge_graph = 'GoogleKnowledgeGraph'
word_net = 'WordNet'

predefined = [word_net, google_knowledge_graph]