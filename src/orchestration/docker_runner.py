import datetime

def log(message):
    print('[OpenROAD {:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()) + "] " + message)

def run(options):
    pass