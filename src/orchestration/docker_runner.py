import os
import datetime
import docker

def log(message):
    print('[OpenROAD {:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()) + "] " + str(message))

def run(options):
    with open(os.path.join(options['output_folder'], 'LS', 'synth.ys'), 'w') as f:
        f.write('hierarchy; proc; opt; techmap; opt\n')

    client = docker.from_env()
    client.images.pull('openroad/yosys:latest')
    contrainer = client.containers.run('openroad/yosys:latest', \
        detach=True,
        auto_remove=True,
        volumes={
            os.path.join(os.getcwd(), options['output_folder'], 'LS'): {
                'bind': '/OpenROAD/LS',
                'mode': 'rw'
            },
            os.path.join(os.getcwd(), options['output_folder'], 'lib'): {
                'bind': '/OpenROAD/lib',
                'mode': 'rw'
            }
        })
    for line in contrainer.logs(stream=True):
        log(line.strip().decode('utf-8'))
    