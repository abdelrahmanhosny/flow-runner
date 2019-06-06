import subprocess

def run_utd_box_router(live_monitor, options, router_script_file, def_file):
    logs = 'Started Global Routing using UTDBoxRouter ..<br>'
    live_monitor.append(logs)

    with open(router_script_file, 'w') as f:
        f.write('orparam lef { /openroad/lib/asap7_tech_4x_170803.lef /openroad/lib/asap7sc7p5t_24_L_4x_170912_mod.lef /openroad/lib/asap7sc7p5t_24_R_4x_170912_mod.lef /openroad/lib/asap7sc7p5t_24_SL_4x_170912_mod.lef /openroad/lib/asap7sc7p5t_24_SRAM_4x_170912_mod.lef }\n')
        f.write('orparam def ' + def_file + '\n')
        f.write('orparam output ' + options['top_level_module'] + '.out\n')
        f.write('orparam gcell rows 2\n')
        f.write('orparam gcell tracks 24\n')
        f.write('orparam gscale 2000.0\n\n')
        f.write('orgroute::params\n')
        f.write('ordesign read\n')
        f.write('ordesign route\n')
        f.write('ordesign output\n')

    args = ['./utdBoxRouter', '-do', router_script_file, options['top_level_module']]
    p = subprocess.Popen(args, cwd='/openroad/tools/Linux-x86_64', stdout=subprocess.PIPE)
    for line in iter(p.stdout.readline, b''):
        logs = str(line).replace('\n', '<br>')
        live_monitor.append(logs)

    logs = '<br><br>Global Routing completed successfully ..<br><br>'
    live_monitor.append(logs)