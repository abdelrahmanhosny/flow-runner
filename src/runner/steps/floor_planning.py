import subprocess

def run_floor_planner(live_monitor, options, netlist_file, netlist_def_file, def_pins_placed_file):
    logs = 'Started Floor Planning ..<br>'
    live_monitor.append(logs)

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
        logs = str(line).replace('\n', '<br>')
        live_monitor.append(logs)
    
    args = ['python', 'pins_placer.py', '-def', netlist_def_file, '-output', def_pins_placed_file]

    p = subprocess.Popen(args, cwd='/openroad/tools', stdout=subprocess.PIPE)
    for line in iter(p.stdout.readline, b''):
        logs = str(line).replace('\n', '<br>')
        live_monitor.append(logs)

    logs = '<br><br>Floor Planning completed successfully ..<br><br>'
    live_monitor.append(logs)
