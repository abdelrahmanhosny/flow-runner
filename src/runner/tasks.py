import requests
import shutil
import os
import subprocess
import yaml
import docker
import time
import zipfile
from django.conf import settings
from celery.decorators import task
from celery.utils.log import get_task_logger
from git import Repo
from storage import aws
from .steps.logic_synthesis import run_yosys
from .steps.floor_planning import run_floor_planner
from .live_monitor import LiveMonitor

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
    live_monitor = LiveMonitor(flow_id)

    # notify openroad with start
    notify_started(flow_id)

    # load flow options
    flow_options_file = os.path.join(flow_dir, 'openroad-flow.yml')
    with open(flow_options_file, 'r') as stream:
        options = yaml.safe_load(stream)

    ######## Logic Synthesis #########
    netlist_file = os.path.join(flow_result_directory, options['design_name'] + '-netlist.v')
    design_files = os.path.join(flow_dir, 'design/*.v')

    run_yosys(live_monitor, options, design_files, netlist_file)
    
    
    ######## Floor Planning #########
    netlist_def_file = os.path.join(flow_result_directory, options['design_name'] + '-netlist.def')
    def_pins_placed_file = os.path.join(flow_result_directory, options['design_name'] + '-netlist-floor-planned.def')

    run_floor_planner(live_monitor, options, netlist_file, netlist_def_file, def_pins_placed_file)

    ######## Placement #########
    logs = 'Started Placement using RePlAce ..<br>'
    live_monitor.append(logs)
    
    constraint_file = os.path.join(flow_dir, 'design', options['sdc_file'])
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
        logs = str(line).replace('\n', '<br>')
        live_monitor.append(logs)

    logs = 'Placement completed successfully ..<br>'
    live_monitor.append(logs)

    ######## Routing #########
    # utdBoxRouter -do ispd01.gdo ispd01
    
    ######## STA #########
    logs = 'Started Static Timing Analysis using OpenSTA ..<br>'
    live_monitor.append(logs)

    os.mkdir(os.path.join(flow_result_directory, 'sta'))
    sta_report_file = os.path.join(flow_result_directory, 'sta', 'report.txt')
    sta_script_file = os.path.join(flow_result_directory, 'sta', 'sta.src')
    spef_file = os.path.join(flow_result_directory, 'placement', 'etc', options['design_name'] + '-netlist-floor-planned', \
        'experiment000', options['design_name'] + '-netlist-floor-planned_dp.spef')
    with open(sta_script_file, 'w') as f:
        f.write('read_liberty /openroad/lib/asap7.lib\n')
        f.write('read_verilog ' + netlist_file + '\n')
        f.write('link_design ' + options['top_level_module'] + '\n')
        f.write('set_units -time ps\n')
        f.write('read_sdc ' + constraint_file + '\n')
        f.write('read_spef ' + spef_file + '\n')
        f.write('report_checks > ' + sta_report_file + '\n')
        f.write('exit')
    
    args = ['./sta', '-f', sta_script_file]
    p = subprocess.Popen(args, cwd='/openroad/tools', stdout=subprocess.PIPE)
    for line in iter(p.stdout.readline, b''):
        logs = str(line).replace('\n', '<br>')
        live_monitor.append(logs)

    logs = 'Static Timing Analysis completed successfully ..<br>'
    live_monitor.append(logs)

    # Zip the flow_dir and store it to AWS
    flow_result_zipped_file = str(flow_id) + '.zip'
    zipf = zipfile.ZipFile(flow_result_zipped_file, 'w', zipfile.ZIP_DEFLATED)
    zipdir(flow_dir, zipf)
    zipf.close()
    result_url = aws.upload_file(flow_result_zipped_file, str(flow_id) + '.zip')

    # close connection to the live monitoring db
    live_monitor.close()

    # notify openroad with completion (success/failure)
    notify_success(flow_id, result_url)

    return True
