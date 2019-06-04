import subprocess

def run_yosys(live_monitor, options, design_files, netlist_file):
    logs = 'Started Logic Synthesis using Yosys ..<br>'
    live_monitor.append(logs)		
    
    args = ['./yosys', '-Q', '-T', '-q', '-o', netlist_file, design_files, '/openroad/tools/synth.ys']
    p = subprocess.Popen(args, cwd='/openroad/tools', stdout=subprocess.PIPE)
    for line in iter(p.stdout.readline, b''):
        logs = str(line).replace('\n', '<br>')
        live_monitor.append(logs)

    logs = '<br><br>Logic synthesis completed successfully ..<br><br>'
    live_monitor.append(logs)