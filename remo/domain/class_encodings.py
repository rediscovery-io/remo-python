"""
Class encodings allow conversion between label IDs and label names when importing and exporting annotations.

Remo supports some default class encodings and upload of custom ones.

`class_encoding` can be expressed as:

- one of predefined value: ``WordNet``, ``GoogleKnowledgeGraph``

- local path to csv file with labels and classes::

    '/Users/admin/Downloads/class_encoding.csv'

- raw content of a csv file, like::

    id,name
    DR3,person
    SP2,rock

- dictionary with label IDs and label names, like::

    {
        'DR3': 'person',
        'SP2': 'rock'
    }

"""
import os

custom = 'custom'
autodetect = 'autodetect'
google_knowledge_graph = 'GoogleKnowledgeGraph'
word_net = 'WordNet'

predefined = [word_net, google_knowledge_graph]


def for_upload(class_encoding):
    class_encoding = for_linking(class_encoding)
    if isinstance(class_encoding, dict):
        if 'local_path' in class_encoding:
            local_path = class_encoding.pop('local_path')
            class_encoding['raw_content'] = ''.join(open(local_path).readlines())
            return class_encoding

        if 'classes' in class_encoding:
            classes = class_encoding.pop('classes')
            lines = map(lambda v: '{},{}'.format(v[0], v[1]), classes.items())
            class_encoding['raw_content'] = '\n'.join(lines)
            return class_encoding

    return class_encoding


def for_linking(class_encoding):
    custom_class_encoding = {'type': custom}

    if isinstance(class_encoding, dict):
        custom_class_encoding['classes'] = class_encoding
        return custom_class_encoding

    if isinstance(class_encoding, str):
        if os.path.exists(class_encoding):
            custom_class_encoding['local_path'] = class_encoding
            return custom_class_encoding

        if class_encoding in predefined:
            return {'type': class_encoding}

        if '\n' in class_encoding:
            custom_class_encoding['raw_content'] = class_encoding
            return custom_class_encoding

    return class_encoding
