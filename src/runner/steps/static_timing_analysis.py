import subprocess

def run_opensta(live_monitor, options, sta_script_file, netlist_file, constraint_file, spef_file, sta_report_file):
    logs = 'Started Static Timing Analysis using OpenSTA ..<br>'
    live_monitor.append(logs)

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

    logs = '<br><br>Static Timing Analysis completed successfully ..<br><br>'
    logs += 'Refresh the page and click Download Output Files<br><br>'
    live_monitor.append(logs)
