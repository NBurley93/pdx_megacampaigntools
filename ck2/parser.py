import json
import os
from common import loggy


with open('settings.json', 'r') as sFile:
    _settings = json.loads(sFile.read())['ck2-parser']


class CK2SaveNode(object):
    def __init__(self, name: str, parent):
        self.node_name = name
        self.data = []
        self.parent = parent

    def __str__(self):
        return '{0}: parent={1}; data={2}'.format(self.node_name, self.parent, self.parent)


def stringifyNode(node: CK2SaveNode, indentLevel=0):
    outStr = '\t'*indentLevel + '{0}=\n'.format(node.node_name)
    for item in node.data:
        if not isinstance(item[1], CK2SaveNode):
            outStr += '\t'*indentLevel + '\t{0}={1}\n'.format(item[0], item[1])
        else:
            outStr += stringifyNode(item[1], indentLevel + 1)
    return outStr

class CK2ParseEngine(object):
    def __init__(self, lineData: list):
        self.rawData = lineData
        self.tokenLines = []
        self.rootNode = CK2SaveNode('root', None)

    def tokenize(self):
        for line in self.rawData:
            tLine = line.split('=')
            self.tokenLines.append(tLine)


    def nodify(self):
        node = self.rootNode
        for tL in self.tokenLines:
            lLength = len(tL)
            if lLength == 2:
                # Determine if key/value pair
                if not tL[1] == '':
                    # Is keyvalue pair

                    # Additional value parsing
                    key = tL[0]
                    value = tL[1]

                    # Strip quotes
                    if value.find('"') >= 0:
                        value.replace('"', '')

                    # Boolean parsing
                    if value == 'yes':
                        value = True
                    elif value == 'no':
                        value == False

                    node.data.append((key, value))
                else:
                    # Node start
                    newNode = CK2SaveNode(tL[0], node)
                    node.data.append((tL[0], newNode))
                    node = newNode
            elif lLength == 1:
                # Is open bracket?
                if tL[0] == '{':
                    pass
                elif tL[0] == '}':
                    # End of node, set node to parent
                    node = node.parent
                else:
                    pass
    
def execute():
    src = _settings['source-file']
    loggy.log('Loading savegame')
    with open('{0}'.format(src), 'r') as saveFile:
        lines = saveFile.readlines()

    linesstripped = []
    for line in lines:
        linesstripped.append(line.strip())
    loggy.log('Savegame loaded')

    # Parse and save data
    dst = _settings['destination']
    loggy.log('Parsing savegame data [1/4] - Initialize Parse Engine')
    engine = CK2ParseEngine(linesstripped)
    loggy.log('Parsing savegame data [2/4] - Tokenizing data')
    engine.tokenize()
    loggy.log('Parsing savegame data [3/4] - Generate data nodes')
    engine.nodify()
    loggy.log('Parsing savegame data [4/4] - Writing parsed data output for verification')
    with open('{0}.ck2parsed'.format(dst), 'w') as writeSave:
        writeSave.write(stringifyNode(engine.rootNode))
    loggy.log('Finished parsing savegame!')
