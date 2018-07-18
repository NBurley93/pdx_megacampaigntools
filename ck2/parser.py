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

    
    def numDataElements(self):
        return len(self.data)


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

    
    def findNode(self, root: CK2SaveNode, name: str):
        for dat in root.data:
            key = dat[0]
            value = dat[1]
            if isinstance(value, CK2SaveNode):
                if key == name:
                    return value
        return None


    def findPair(self, root: CK2SaveNode, name: str):
        for dat in root.data:
            key = dat[0]
            value = dat[1]
            if key == name:
                return value
        return 'undefined'


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
                        value.replace('\"', '')

                    # Boolean parsing
                    if value == 'yes':
                        value = True
                    elif value == 'no':
                        value = False

                    node.data.append((key, value))
                else:
                    # Node start
                    nodeName = tL[0]
                    newNode = CK2SaveNode(nodeName, node)
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
                        loggy.log('Reached end of file!')
                else:
                    pass
    

def writeNode(baseName: str, parser: CK2ParseEngine, nodeName: str):
    if nodeName == 'root':
        with open('{0}.{1}.parsed'.format(baseName, nodeName), 'w') as outParse:
            # Write root non-recursively
            outParse.write(stringifyNode(parser.rootNode, 0, False))
    else:
        rqstNode = parser.findNode(parser.rootNode, nodeName)
        if not rqstNode == None:
            with open('{0}.{1}.parsed'.format(baseName, nodeName), 'w') as outParse:
                outParse.write(stringifyNode(rqstNode))
        else:
            loggy.log('Failed to find node {0}! Cannot write non-existing node'.format(nodeName))


def saveDynasties(parser: CK2ParseEngine, db: SaveDatabase):
    loggy.log('Writing Dynasties...')
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
    loggy.log('Writing Characters...')
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
        ('attributes', 'text'),
        ('traits', 'text'),
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
            attributes = parser.findPair(value, 'att')
            traits = parser.findPair(value, 'traits')
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
                death_cause, killer, father, mother, spouse, attributes, traits, prestige,
                piety, host
            ))

    
def execute(inputFile: str, outputFile: str):
    src = inputFile
    loggy.log('Loading savegame')
    with open('{0}'.format(src), 'r') as saveFile:
        lines = saveFile.readlines()

    linesstripped = []
    for line in lines:
        linesstripped.append(line.strip())
    loggy.log('Savegame loaded')

    # Parse and save data
    dst = outputFile
    loggy.log('Parsing savegame data [1/5] - Initialize Parse Engine')
    engine = CK2ParseEngine(linesstripped)
    loggy.log('Parsing savegame data [2/5] - Tokenizing data')
    engine.tokenize()
    loggy.log('Parsing savegame data [3/5] - Generate data nodes')
    engine.nodify()
    loggy.log('Parsed data with {0} nodes under root'.format(engine.rootNode.numDataElements()))
    loggy.log('Parsing savegame data [4/5] - Writing parse dump')
    #writeNode(dst, engine, 'root')
    #writeNode(dst, engine, 'character')
    #writeNode(dst, engine, 'player')
    #writeNode(dst, engine, 'game_rules')
    #writeNode(dst, engine, 'flags')
    #writeNode(dst, engine, 'character')
    #writeNode(dst, engine, 'dynasties')
    loggy.log('Parsing savegame data [5/5] - Writing output database')
    db = SaveDatabase('{0}.sqlite'.format(dst))
    saveDynasties(engine, db)
    saveCharacters(engine, db)
    db.export()
    loggy.log('Finished parsing savegame!')
