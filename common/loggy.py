import datetime
import os

def getTimestamp():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

def log(outText: str):
    fLog = '[{0}] {1}'.format(getTimestamp(), outText)
    print(fLog)
    if not os.path.exists('./logs'):
        os.mkdir('./logs')
    with open('./logs/{0}.log'.format(datetime.datetime.now().strftime('%Y-%m-%d')), 'a') as lFile:
        lFile.write(fLog + '\n')
