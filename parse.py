import ck2
import argparse
import common

def getArgs():
    aParser = argparse.ArgumentParser()
    aParser.add_argument('-g', '--game', help='The game to run a parser for', type=str, default='ck2')
    return aParser.parse_args()

if __name__ == '__main__':
    a = getArgs()
    if a.game == 'ck2':
        ck2.parser.execute()
    else:
        common.loggy.log('Invalid game specified! {0}'.format(a.game))