import yaml
import os
import argparse
import datetime
import src.orchestration.docker_runner as docker_runner
import src.orchestration.preprocessing as preprocessing
from pyfiglet import Figlet

def log(message):
    print('[OpenROAD {:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()) + "] " + message)

class CapitalisedHelpFormatter(argparse.ArgumentDefaultsHelpFormatter):
    def add_usage(self, usage, actions, groups, prefix=None):
        if prefix is None:
            prefix = 'Usage: '
            return super(CapitalisedHelpFormatter, self).add_usage(usage, actions, groups, prefix)

if __name__ == '__main__':
    f = Figlet(font='slant')
    print(f.renderText('OpenROAD Flow'))

    parser = argparse.ArgumentParser(add_help=True, formatter_class=CapitalisedHelpFormatter, \
        description='Runs OpenROAD layout generation flow (RTL-to-GDS)')
    parser._positionals.title = 'Positional arguments'
    parser._optionals.title = 'Optional arguments'
    parser.add_argument('-v', '--version', action='version', version = 'OpenROAD Flow v0.1-alpha', \
        help = "Shows flow's version number and exit")
    parser.add_argument('flow', type=open, help='Path to the openroad-flow.yml file')
    args = parser.parse_args()
    
    options = yaml.load(args.flow, Loader=yaml.FullLoader)

    log('Loaded the flow file ' + args.flow.name)

    preprocessing.preprocess(options)
    docker_runner.run(options)