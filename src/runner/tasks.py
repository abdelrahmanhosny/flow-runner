import requests
import shutil
import os
import subprocess
import yaml
import rethinkdb as r
from django.conf import settings
from celery.decorators import task
from celery.utils.log import get_task_logger
from git import Repo

logger = get_task_logger(__name__)


def notify_started(flow_id):
    r = requests.post(settings.OPENROAD_URL + '/start',
                      data={'flow_uuid': flow_id,
                            'storage_url': settings.STORAGE_URL + str(flow_id) + '/openroad',
                            'live_monitoring_url': settings.LIVE_MONITORING_URL})
    logger.info('Notified OpenROAD of flow ' + flow_id + ' start ..')
    logger.info('OpenROAD responded ' + r.text)


def notify_success(flow_id):
    r = requests.post(settings.OPENROAD_URL + '/success',
                      data={'flow_uuid': flow_id})
    logger.info('Notified OpenROAD of flow ' + flow_id + ' success ..')
    logger.info('OpenROAD responded ' + r.text)


def notify_fail(flow_id):
    r = requests.post(settings.OPENROAD_URL + '/fail',
                      data={'flow_uuid': flow_id})
    logger.info('Notified OpenROAD of flow ' + flow_id + ' fail ..')
    logger.info('OpenROAD responded ' + r.text)


@task(name='start_flow_task')
def start_flow_task(flow_id, repo_url):
    logger.info('Starting flow now ..')

    # copy template to storage location and give it a name = uuid
    try:
        flow_dir = os.path.join(settings.STORAGE_DIR, str(flow_id))
        shutil.rmtree(flow_dir, ignore_errors=True)
        shutil.copytree(settings.FLOW_TEMPLATE_DIR, flow_dir)
        logger.info('Initialized template directory ..')
    except Exception as e:
        notify_fail(flow_id)
        logger.info(e)
        return

    # clone repo to temporary location
    try:
        repo_dir = os.path.join(settings.REPOS_TMP_DIR, str(flow_id))
        Repo.clone_from(repo_url, repo_dir)
        logger.info('Cloned the repo from GitHub..')
    except Exception as e:
        notify_fail(flow_id)
        logger.info(e)
        return

    # copy files from design folder in the repo to the location above
    input_files_names = []
    try:
        flow_definition_file = os.path.join(repo_dir, 'openroad-flow.yml')
        with open(flow_definition_file, 'r') as f:
            flow_definition = yaml.load(f)
        for design_file_name in flow_definition['design_files']:
            src = os.path.join(repo_dir, 'design', design_file_name)
            dst = os.path.join(flow_dir, design_file_name)
            shutil.copy(src, dst)
            input_files_names.append(design_file_name)
        logger.info('Copied design files ..')
    except Exception as e:
        notify_fail(flow_id)
        logger.info(e)
        return

    # modify grand.init
    try:
        grand_init_file = os.path.join(flow_dir, 'grand.init')
        with open(grand_init_file, 'a') as f:
            f.write("\n\n#Parameters modified by the cloud flow task\n")
            # design name
            design_name_line = "set ::openroad::designNameS " + flow_definition['design_name'] + "\n"
            f.write(design_name_line)
            # input rtl files
            rtl_line = "set ::openroad::rtl_allS \"" + " ".join(input_files_names) + "\"\n"
            f.write(rtl_line)
            # top level module
            top_level_module_line = "set ::openroad::vtopS " + flow_definition['top_level_module'] + "\n"
            f.write(top_level_module_line)
            # clock definition
            clock_definition_line = "set ::openroad::clockS " + str(flow_definition['clock']) + "\n"
            f.write(clock_definition_line)
            # library file
            liberty_file_line = "set ::openroad::timing_fileS " + flow_definition['library'] + "\n"
            f.write(liberty_file_line)
            # netlist verilog
            netlist_verilog_line = "set ::openroad::verilog_fileS " + flow_definition['design_name'] + ".v\n"
            f.write(netlist_verilog_line)
            # SDC file
            sdc_file_line = "set ::openroad::sdc_fileS " + flow_definition['sdc_file'] + "\n"
            f.write(sdc_file_line)
            # lef file & def file
            lef_file_line = "set ::openroad::lef_fileS osu035.lef" + "\n"
            def_file_line = "set ::openroad::def_fileS riscv.def" + "\n"
            f.write(lef_file_line)
            f.write(def_file_line)
        logger.info('Modified task definition')
    except Exception as e:
        notify_fail(flow_id)
        logger.info(e)
        return

    # initialize live monitoring on the remote rethinkdb
    conn = r.connect(settings.LIVE_MONITORING_URL, password=settings.LIVE_MONITORING_PASSWORD)
    r.db('openroad').table('flow_log').insert({'openroad_uuid': flow_id,
                                               'logs': ''}).run(conn)

    # notify openroad with start and give it storage URL
    notify_started(flow_id)

    # cd to the location and run flow
    try:
        args = ['flow', '-v', '-n', '-do', 'grand.do', 'riscv']
        logs = ''
        p = subprocess.Popen(args, cwd=flow_dir, stdout=subprocess.PIPE)
        for line in iter(p.stdout.readline, b''):
            # notify the realtime database of this
            if 'Copyright' not in str(line):
                logs += str(line)[2:-1].replace('\n', '<br>')
            r.db('openroad').table('flow_log').\
                filter(r.row['openroad_uuid'] == flow_id).\
                update({'logs': logs}).run(conn)
        # once done, just let them know there is no available live stream. Check log files
        logs += 'Flow ended successfully. Live streaming is not available. Check logs in the output files.'
        r.db('openroad').table('flow_log'). \
            filter(r.row['openroad_uuid'] == flow_id). \
            update({'logs': logs}).\
            run(conn)
    except Exception as e:
        logs += 'Flow ended successfully. Live streaming is not available. Check logs in the output files.'
        r.db('openroad').table('flow_log'). \
            filter(r.row['openroad_uuid'] == flow_id). \
            update({'logs': logs}). \
            run(conn)
        notify_fail(flow_id)
        return

    # close connection to the live monitoring db
    conn.close()

    # notify openroad with completion (success/failure)
    logger.info('Return Code: ' + str(p.returncode))
    if p.returncode and p.returncode > 1:
        notify_fail(flow_id)
    else:
        notify_success(flow_id)

    return True
