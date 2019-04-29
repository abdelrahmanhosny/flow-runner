import os
import shutil

def preprocess(options):
    '''
    Creates a folder to hold the flow artifacts
    Symbolic link the files to this folder
    '''
    if os.path.exists(options['output_folder']):
        shutil.rmtree(options['output_folder'])
    os.makedirs(options['output_folder'])
    
    # prepare directories
    ls_input_folder = os.path.join(options['output_folder'], 'LS', 'input')
    os.makedirs(ls_input_folder)
    library_folder = os.path.join(options['output_folder'], 'lib')
    os.makedirs(library_folder)
    ls_output_folder = os.path.join(options['output_folder'], 'LS', 'output')
    os.makedirs(ls_output_folder)

    # copy design files
    for design_file in options['design_files']:
        dst = os.path.join(ls_input_folder, design_file.split('/')[-1])
        shutil.copyfile(design_file, dst)
    
    # sym-link library
    for library_file in options['library_files']:
        dst = os.path.join(library_folder, library_file.split('/')[-1])
        shutil.copyfile(library_file, dst)
    
    # sym-link constraint file
    dst = os.path.join(ls_input_folder, options['constraints_file'].split('/')[-1])
    shutil.copyfile(options['constraints_file'], dst)

    
