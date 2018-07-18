import ck2
import argparse
import common

def getArgs():
    aParser = argparse.ArgumentParser()
    aParser.add_argument('-g', '--game', help='The game to run a parser for', type=str, default='ck2')
    aParser.add_argument('-s', '--save', help='Input save file location', type=str)
    aParser.add_argument('-o', '--output', help='Output location of parsed data', type=str)
    return aParser.parse_args()

if __name__ == '__main__':
    a = getArgs()
    if a.game == 'ck2':
        ck2.parser.execute(a.save, a.output)
    else:
        common.loggy.log('Invalid game specified! {0}'.format(a.game))