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
    subprocess.run(args, cwd='/openroad/tools', stdout=log_file_handle, stderr=error_file_handle)

    logs = '<br><br>Logic synthesis completed successfully ..<br><br>'
    live_monitor.append(logs)
    log_file_handle.close()
    error_file_handle.close()