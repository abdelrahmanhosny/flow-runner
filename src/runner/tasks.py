import requests
import shutil
import os
import subprocess
import yaml
import docker
import rethinkdb as r
import time
import zipfile
from django.conf import settings
from celery.decorators import task
from celery.utils.log import get_task_logger
from git import Repo
from storage import aws

logger = get_task_logger(__name__)

def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))

def notify_started(flow_id, storage_url=aws.get_flow_readme()):
    r = requests.post(settings.OPENROAD_URL + '/start',
                      data={'flow_uuid': flow_id,
                            'storage_url': storage_url,
                            'live_monitoring_url': settings.LIVE_MONITORING_URL})
    logger.info('Notified OpenROAD of flow ' + flow_id + ' start ..')
    logger.info('OpenROAD responded ' + r.text)


def notify_success(flow_id, result_url='#'):
    r = requests.post(settings.OPENROAD_URL + '/success', \
            data={'flow_uuid': flow_id, \
                    'storage_url': result_url,})
    logger.info('Notified OpenROAD of flow ' + flow_id + ' success ..')
    logger.info('OpenROAD responded ' + r.text)


def notify_fail(flow_id, result_url='#'):
    r = requests.post(settings.OPENROAD_URL + '/fail', \
            data={'flow_uuid': flow_id, \
                    'storage_url': result_url,})
    logger.info('Notified OpenROAD of flow ' + flow_id + ' fail ..')
    logger.info('OpenROAD responded ' + r.text)


@task(name='start_flow_task')
def start_flow_task(flow_id, repo_url):
    logger.info('Starting flow now ..')

    # initialize design directory
    flow_dir = os.path.join(settings.PLAYGROUND_DIR, str(flow_id))
    flow_result_directory = os.path.join(flow_dir, 'flow_output')
    try:
        shutil.rmtree(flow_dir, ignore_errors=True)
        logger.info('Initialized flow directory ..')
    except Exception as e:
        logger.info(e)
        return

    # clone repo to the design directory
    try:
        Repo.clone_from(repo_url, flow_dir)
        logger.info('Cloned the repo from GitHub..')
        os.mkdir(flow_result_directory)
    except Exception as e:
        # notify_fail(flow_id)
        logger.info(e)
        return

    # initialize live monitoring on the remote rethinkdb
    conn = r.connect(settings.LIVE_MONITORING_URL, password=settings.LIVE_MONITORING_PASSWORD)
    r.db('openroad').table('flow_log').insert({'openroad_uuid': flow_id,
                                               'logs': ''}).run(conn)

    # notify openroad with start
    notify_started(flow_id)

    # load flow options
    flow_options_file = os.path.join(flow_dir, 'openroad-flow.yml')
    with open(flow_options_file, 'r') as stream:
        options = yaml.safe_load(stream)

    logs = ''
    ######## Logic Synthesis #########
    logs += 'Started Logic Synthesis using Yosys ..<br>'
    r.db('openroad').table('flow_log').\
		filter(r.row['openroad_uuid'] == flow_id).\
			update({'logs': logs}).run(conn)
			
    netlist_file = os.path.join(flow_result_directory, options['design_name'] + '-netlist.v')
    design_files = os.path.join(flow_dir, 'design/*.v')
    args = ['./yosys', '-Q', '-T', '-q', '-o', netlist_file, design_files, '/openroad/tools/synth.ys']
    p = subprocess.Popen(args, cwd='/openroad/tools', stdout=subprocess.PIPE)
    for line in iter(p.stdout.readline, b''):
        logs += ''.join(str(line)[-1].replace('\n', '<br>'))
        r.db('openroad').table('flow_log').\
            filter(r.row['openroad_uuid'] == flow_id).\
                update({'logs': logs}).run(conn)

    logs += '<br><br>Logic synthesis completed successfully ..<br><br>'
    r.db('openroad').table('flow_log').\
            filter(r.row['openroad_uuid'] == flow_id).\
            update({'logs': logs}).run(conn)
    
    ######## Floor Planning #########
    logs += 'Started Floor Planning ..<br>'
    r.db('openroad').table('flow_log').\
            filter(r.row['openroad_uuid'] == flow_id).\
            update({'logs': logs}).run(conn)
    
    netlist_def_file = os.path.join(flow_result_directory, options['design_name'] + '-netlist.def')
    args = ['./defgenerator', '-lef', '/openroad/lib/asap7_tech_4x_170803.lef']
    args += ['-lef', '/openroad/lib/asap7sc7p5t_24_L_4x_170912_mod.lef']
    args += ['-lef', '/openroad/lib/asap7sc7p5t_24_R_4x_170912_mod.lef']
    args += ['-lef', '/openroad/lib/asap7sc7p5t_24_SL_4x_170912_mod.lef']
    args += ['-lef', '/openroad/lib/asap7sc7p5t_24_SRAM_4x_170912_mod.lef']
    args += ['-lib', '/openroad/lib/asap7.lib']
    args += ['-verilog', netlist_file]
    args += ['-defDbu', str(options['stages']['floor_planning']['params']['defDbu'])]
    args += ['-dieAreaInMicron'] + options['stages']['floor_planning']['params']['dieAreaInMicron'].strip().split(' ')
    args += ['-siteName', options['stages']['floor_planning']['params']['siteName']]
    args += ['-design', options['top_level_module']]
    args += ['-def', netlist_def_file]

    p = subprocess.Popen(args, cwd='/openroad/tools', stdout=subprocess.PIPE)
    for line in iter(p.stdout.readline, b''):
        logs += ''.join(str(line)[-1].replace('\n', '<br>'))
        r.db('openroad').table('flow_log').\
            filter(r.row['openroad_uuid'] == flow_id).\
                update({'logs': logs}).run(conn)
    
    def_pins_placed_file = os.path.join(flow_result_directory, options['design_name'] + '-netlist-floor-planned.def')
    args = ['python', 'pins_placer.py', '-def', netlist_def_file, '-output', def_pins_placed_file]

    p = subprocess.Popen(args, cwd='/openroad/tools', stdout=subprocess.PIPE)
    for line in iter(p.stdout.readline, b''):
        logs += ''.join(str(line)[-1].replace('\n', '<br>'))
        r.db('openroad').table('flow_log').\
            filter(r.row['openroad_uuid'] == flow_id).\
                update({'logs': logs}).run(conn)

    logs += '<br><br>Floor Planning completed successfully ..<br><br>'
    r.db('openroad').table('flow_log').\
            filter(r.row['openroad_uuid'] == flow_id).\
            update({'logs': logs}).run(conn)
    
    ######## Placement #########
    logs += 'Started Placement using RePlAce ..<br>'
    r.db('openroad').table('flow_log').\
            filter(r.row['openroad_uuid'] == flow_id).\
            update({'logs': logs}).run(conn)
    
    constraint_file = os.path.join(flow_dir, options['sdc_file'])
    output_dir = os.path.join(flow_result_directory, 'placement')
    args = ['./RePlAce', '-bmflag', options['stages']['placement']['params']['bmflag']]
    args += ['-lef', '/openroad/lib/asap7_tech_4x_170803.lef']
    args += ['-lef', '/openroad/lib/asap7sc7p5t_24_L_4x_170912_mod.lef']
    args += ['-lef', '/openroad/lib/asap7sc7p5t_24_R_4x_170912_mod.lef']
    args += ['-lef', '/openroad/lib/asap7sc7p5t_24_SL_4x_170912_mod.lef']
    args += ['-lef', '/openroad/lib/asap7sc7p5t_24_SRAM_4x_170912_mod.lef']
    args += ['-def', def_pins_placed_file]
    args += ['-verilog', netlist_file]
    args += ['-lib', '/openroad/lib/asap7.lib']
    args += ['-sdc', constraint_file]
    args += ['-output', output_dir]
    args += ['-t', str(options['stages']['placement']['params']['t'])]
    args += ['-dpflag', options['stages']['placement']['params']['dpflag']]
    args += ['-dploc', '/openroad/tools/ntuplace3']
    if options['stages']['placement']['params']['onlyDP']:
        args += ['-onlyDP']
    args += ['-unitY', str(options['stages']['placement']['params']['unitY'])]
    args += ['-resPerMicron', str(options['stages']['placement']['params']['resPerMicron'])]
    args += ['-capPerMicron', str(options['stages']['placement']['params']['capPerMicron'])]
    if options['stages']['placement']['params']['timing']:
        args += ['-timing']

    p = subprocess.Popen(args, cwd='/openroad/tools', stdout=subprocess.PIPE)
    for line in iter(p.stdout.readline, b''):
        logs += ''.join(str(line)[-1].replace('\n', '<br>'))
        r.db('openroad').table('flow_log').\
            filter(r.row['openroad_uuid'] == flow_id).\
                update({'logs': logs}).run(conn)

    logs += 'Placement completed successfully ..<br>'
    r.db('openroad').table('flow_log').\
            filter(r.row['openroad_uuid'] == flow_id).\
            update({'logs': logs}).run(conn)

    # Zip the flow_dir and store it to AWS
    flow_result_zipped_file = str(flow_id) + '.zip'
    zipf = zipfile.ZipFile(flow_result_zipped_file, 'w', zipfile.ZIP_DEFLATED)
    zipdir(flow_dir, zipf)
    zipf.close()
    result_url = aws.upload_file(flow_result_zipped_file, str(flow_id) + '.zip')

    # close connection to the live monitoring db
    conn.close()

    # notify openroad with completion (success/failure)
    notify_success(flow_id, result_url)

    return True
