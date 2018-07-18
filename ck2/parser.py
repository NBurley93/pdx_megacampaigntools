import json
import os
from common import loggy
import sys
from ck2.databuilder import SaveDatabase


class CK2SaveNode(object):
    def __init__(self, name: str, parent):
        self.node_name = name
        self.data = []
        self.parent = parent
        self.node_occurrence = {}
        self.data_occurrence = {}

    
    def printStatistics(self):
        r = '{0}-node-statistics:\n'.format(self.node_name)
        r += '\tdata-entries:\n'
        for key in self.data_occurrence.keys():
            r += '\t\t{0} {1} entries\n'.format(self.data_occurrence[key], key)
        r += '\tnodes:\n'
        for key in self.node_occurrence.keys():
            r += '\t\t{0} {1} nodes\n'.format(self.node_occurrence[key], key)
        return r

    
    def numDataElements(self):
        return len(self.data)


class ExpKey(object):
    def __init__(self, key: str, k_id: int):
        self.key = key
        self.id = k_id


def stringifyNode(node: CK2SaveNode, indentLevel=0, recursive=True):
    outStr = '\t'*indentLevel + '{0}=\n'.format(node.node_name)
    for item in node.data:
        if not isinstance(item[1], CK2SaveNode):
            outStr += '\t'*indentLevel + '\t{0}={1}\n'.format(item[0], item[1])
        else:
            if recursive:
                outStr += stringifyNode(item[1], indentLevel + 1)
            else:
                outStr += '\t'*indentLevel + '\t{0}={1}\n'.format(item[0], item[1])
    return outStr


class CK2ParseEngine(object):
    def __init__(self, lineData: list):
        self.rawData = lineData
        self.tokenLines = []
        self.rootNode = CK2SaveNode('root', None)


    def hasNode(self, root: CK2SaveNode, name: str):
        if name in root.key_occurrence.keys():
            return True
        else:
            return False

    
    def findNode(self, root: CK2SaveNode, name: str):
        for dat in root.data:
            value = dat[1]
            if isinstance(value, CK2SaveNode):
                if value.node_name == name:
                    return value
        return None


    def findPair(self, root: CK2SaveNode, name: str):
        for dat in root.data:
            value = dat[1]
            if dat[0] == name:
                return value
        return 'undefined'


    def findAllNodes(self, root: CK2SaveNode, name: str):
        # Return orphaned node with all found nodes
        n = CK2SaveNode('root', None)
        i = 0
        for dat in root.data:
            value = dat[1]
            if isinstance(value, CK2SaveNode):
                if value.node_name == name:
                    n.data.append((str(i), value))
                    i += 1
        return n


    def tokenize(self):
        for line in self.rawData:
            tLine = line.split('=')
            self.tokenLines.append(tLine)


    def nodify(self):
        node = self.rootNode
        nodeLevel = 0
        nodeName = 'UnnamedNode'
        for tL in self.tokenLines:
            lLength = len(tL)
            if lLength == 2:
                # Determine if key/value pair
                if not tL[1] == '' and not tL[1] == '{':
                    # Is keyvalue pair

                    # Additional value parsing
                    key = tL[0]
                    value = tL[1]

                    # Strip quotes
                    if value.find('\"') >= 0:
                        value = value.replace('\"', '')

                    # Data array parsing
                    if value.find('{') == 0:
                        value = value[1:-1].split(' ')

                    # Boolean parsing, MUST BE DONE LAST
                    if value == 'yes':
                        value = True
                    elif value == 'no':
                        value = False


                    # Calculate occurrence
                    if not key in node.data_occurrence.keys():
                        node.data_occurrence[key] = 1
                    else:
                        node.data_occurrence[key] += 1
                    node.data.append((key, value))
                else:
                    # Node start
                    key = tL[0]
                    nodeName = tL[0]
                    newNode = CK2SaveNode(nodeName, node)

                    # Calculate occurrence
                    if not key in node.node_occurrence.keys():
                        node.node_occurrence[key] = 1
                    else:
                        node.node_occurrence[key] += 1

                    node.data.append((nodeName, newNode))
                    nodeLevel += 1
                    if tL[1] == '{':
                        nodeName = 'UnnamedNode'
                    node = newNode
            elif lLength == 1:
                # Is open bracket?
                if tL[0] == '{':
                    if nodeName == 'UnnamedNode':
                        # Create unnamed node
                        newNode = CK2SaveNode(nodeName, node)

                        key = 'UnnamedNode'

                        # Calculate occurrence
                        if not key in node.node_occurrence.keys():
                            node.node_occurrence[key] = 1
                        else:
                            node.node_occurrence[key] += 1

                        node.data.append((nodeName, newNode))
                        nodeLevel += 1
                        node = newNode
                    else:
                        nodeName = 'UnnamedNode'
                elif tL[0] == '}':
                    # End of node, set node to parent
                    if not node.parent == None:
                        nodeLevel -= 1
                        node = node.parent
                    else:
                        loggy.log('Node Generator - Reached end of data!')
                else:
                    pass


def saveDynasties(parser: CK2ParseEngine, db: SaveDatabase):
    loggy.log('DB Writer - Writing Dynasties...')
    db.addTable('dynasties', [
        ('id', 'text'),
        ('name', 'text'),
        ('culture', 'text'),
        ('religion', 'text')
    ])

    node = parser.findNode(parser.rootNode, 'dynasties')
    for item in node.data:
        key = item[0]
        value = item[1]
        if isinstance(value, CK2SaveNode):
            name = parser.findPair(value, 'name')
            culture = parser.findPair(value, 'culture')
            religion = parser.findPair(value, 'religion')

            # Remove extra quotes from strings
            name = name.replace('\"', '')
            name = name.replace('\'', '’') # Compatibility for French Guillemet
            culture = culture.replace('\"', '')
            religion = religion.replace('\"', '')
            db.addRow('dynasties', (
                key, name, culture, religion
            ))


def saveCharacters(parser: CK2ParseEngine, db: SaveDatabase):
    loggy.log('DB Writer - Writing Characters...')
    db.addTable('characters', [
        ('id', 'text'),
        ('name', 'text'),
        ('religion', 'text'),
        ('dynasty', 'text'),
        ('female', 'text'),
        ('culture', 'text'),
        ('birth_date', 'text'),
        ('death_date', 'text'),
        ('death_cause', 'text'),
        ('killer', 'text'),
        ('father', 'text'),
        ('mother', 'text'),
        ('spouse', 'text'),
        ('prestige', 'text'),
        ('piety', 'text'),
        ('host', 'text'),
    ])

    node = parser.findNode(parser.rootNode, 'character')
    for item in node.data:
        key = item[0]
        value = item[1]
        if isinstance(value, CK2SaveNode):
            name = parser.findPair(value, 'bn')
            religion = parser.findPair(value, 'rel')
            dynasty = parser.findPair(value, 'dnt')
            female = parser.findPair(value, 'fem')
            culture = parser.findPair(value, 'cul')
            birth_date = parser.findPair(value, 'b_d')
            death_date = parser.findPair(value, 'd_d')
            death_cause = parser.findPair(value, 'c_d')
            killer = parser.findPair(value, 'killer')
            father = parser.findPair(value, 'fat')
            mother = parser.findPair(value, 'mot')
            spouse = parser.findPair(value, 'spouse')
            prestige = parser.findPair(value, 'prs')
            piety = parser.findPair(value, 'piety')
            host = parser.findPair(value, 'host')

            # Remove extra quotes from strings
            name = name.replace('\"', '')
            # Compatibility for French Guillemet
            name = name.replace('\'', '’')

            birth_date = birth_date.replace('\"', '')
            death_date = death_date.replace('\"', '')
            culture = culture.replace('\"', '')
            religion = religion.replace('\"', '')
            db.addRow('characters', (
                key, name, religion, dynasty, female, culture, birth_date, death_date,
                death_cause, killer, father, mother, spouse, prestige, piety, host
            ))


def loadSave(inputFile: str):
    src = inputFile
    loggy.log('Load savegame data [1/4] - Load savegame into memory')
    with open('{0}'.format(src), 'r') as saveFile:
        lines = saveFile.readlines()

    linesstripped = []
    for line in lines:
        linesstripped.append(line.strip())

    # Parse data and return parse engine
    loggy.log('Load savegame data [2/4] - Initialize Parse Engine')
    engine = CK2ParseEngine(linesstripped)
    loggy.log('Load savegame data [3/4] - Tokenizing raw data')
    engine.tokenize()
    loggy.log('Load savegame data [4/4] - Generate save nodes')
    engine.nodify()
    return engine
    
def execute(inputFile: str, outputFile: str):
    engine = loadSave(inputFile)
    dst = outputFile

    # Debug dumps
    loggy.log('Parse Dumper [1/2] - Generating statistics')
    with open('parse-rootnode-stats.txt', 'w') as sFile:
        sFile.write(engine.rootNode.printStatistics())

    loggy.log('Parse Dumper [2/2] - Dumping root node recursively')
    with open('parse-rootnode-debugview.txt', 'w') as sFile:
        sFile.write(stringifyNode(engine.rootNode))

    loggy.log('Converting Data [1/1] - Writing output database')
    db = SaveDatabase('{0}.sqlite'.format(dst))
    saveDynasties(engine, db)
    saveCharacters(engine, db)
    db.export()
    loggy.log('Converted save to sqlite DB')
