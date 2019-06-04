import subprocess

def run_replace(live_monitor, options, def_pins_placed_file ,netlist_file, constraint_file, output_dir):
    logs = 'Started Placement using RePlAce ..<br>'
    live_monitor.append(logs)  
    
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

    logs = '<br><br>Placement completed successfully ..<br><br>'
    live_monitor.append(logs)