import subprocess
import os

def run_alpha_release(live_monitor, options, flow_result_directory):
    # Setting up directories
    output_dir = os.path.join(flow_result_directory, 'results')
    log_dir = os.path.join(flow_result_directory, 'logs')
    objects_dir = os.path.join(flow_result_directory, 'objects')
    reports_dir = os.path.join(flow_result_directory, 'reports')
    tech_dir = os.path.join(flow_result_directory, 'tech')

    log_file = os.path.join(log_dir, 'cloud_log.txt')
    error_file = os.path.join(log_dir, 'cloud_error.txt')

    env_variables = []
    if options['design_name'] == 'AES':
        env_variables += ['DESIGN_CONFIG=./designs/aes_nangate45.mk']
    elif options['design_name'] == 'GCD':
        env_variables += ['DESIGN_CONFIG=./designs/gcd_nangate45.mk']
    elif options['design_name'] == 'IBEX':
        env_variables += ['DESIGN_CONFIG=./designs/ibex_nangate45.mk']
    else:
        logs = 'Your design is not yet supported! <br>Please, check again later.'
        live_monitor.append(logs)
        with open(log_file, 'w') as f:
            f.write(logs.replace('<br>', '\n'))
        return

    logs = 'Setting up your sandbox environment ..<br><br>'
    live_monitor.append(logs)

    env_variables += ['LOG_DIR=' + log_dir]
    env_variables += ['OBJECTS_DIR=' + objects_dir]
    env_variables += ['REPORTS_DIR=' + reports_dir]
    env_variables += ['RESULTS_DIR=' + output_dir]
    env_variables += ['TECH_DIR=' + tech_dir]

    logs = 'Sandbox set up successfully .. <br><br>'
    live_monitor.append(logs)

    logs = 'Starting OpenROAD flow .. Live reporting is currently limited in streaming .. <br><br>'
    live_monitor.append(logs)

    args = ['make'] + env_variables
    log_file_handle = open(log_file, 'w')
    error_file_handle = open(error_file, 'w')
    subprocess.run(args, cwd='/flow', stdout=log_file_handle, stderr=error_file_handle)

    logs = 'Flow run finished. Refresh the page and check output files .. <br><br>'
    live_monitor.append(logs)
    
    log_file_handle.close()
    error_file_handle.close()