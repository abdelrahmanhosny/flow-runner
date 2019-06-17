import subprocess
import os

def run_yosys(live_monitor, options, log_dir, design_files, netlist_file):
    logs = 'Started Logic Synthesis using Yosys ..<br>'
    live_monitor.append(logs)		
    
    args = ['./yosys', '-Q', '-T', '-o', netlist_file, design_files, '/openroad/tools/synth.ys']
    log_file = os.path.join(log_dir, 'log.txt')
    log_file_handle = open(log_file, 'w')
    error_file = os.path.join(log_dir, 'error.txt')
    error_file_handle = open(error_file, 'w')
    p = subprocess.Popen(args, cwd='/openroad/tools', stdout=subprocess.PIPE, stderr=error_file_handle)
    for line in iter(p.stdout.readline, b''):
        logs = str(line).replace('\n', '<br>')
        live_monitor.append(logs)
        log_file_handle.write(str(line))

    logs = '<br><br>Logic synthesis completed successfully ..<br><br>'
    live_monitor.append(logs)
    log_file_handle.close()
    error_file_handle.close()