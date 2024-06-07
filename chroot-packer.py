#! /usr/bin/env python3

import argparse
import subprocess
import os
import shutil

def files_differ(file0, file1):
    # TODO this is GIGA SHIT

    with open(file0, 'rb') as f:
        data0 = f.read()

    with open(file1, 'rb') as f:
        data1 = f.read()

    return data0 != data1

def copy_file(root:str, file:str):
    assert file.startswith('/')

    copy_src = file
    copy_dst = root + file

    if os.path.isfile(copy_dst):
        if files_differ(file, copy_dst):
            print(f'ERROR: files `{file}` and `{copy_dst}` differ')
            exit(1)

    os.makedirs(os.path.dirname(copy_dst), exist_ok=True) # what about the folder permissions?
    shutil.copy2(copy_src, copy_dst)

def create_symlink(from_:str, to:str):

    if os.path.islink(from_):
        content = os.readlink(from_)
        if content == to:
            return
        else:
            print(f'ERROR: symlink `{from_}` already exists and points to `{content}`, rather than `{to}`')
            exit(1)

    os.symlink(to, from_)

def main(root:str, executable:str):

    if not executable.startswith('/'):
        print(f'ERROR: executable `{executable}` needs to be an absolute path')
        exit(1)

    # create some necessary symlinks

    create_symlink(os.path.join(root, 'lib'), 'usr/lib')
    create_symlink(os.path.join(root, 'lib64'), 'usr/lib64')

    # copy dependencies

    shell = subprocess.run(['ldd', executable], check=True, capture_output=True)
    
    ldd_output = shell.stdout.decode().replace('\t', '').split('\n')

    for line in ldd_output:
        sep = ' => '

        if sep not in line:
            continue
        
        name, path_and_shit = line.split(sep)

        path, _shit = path_and_shit.split(' ')

        assert path.endswith(name)

        copy_file(root, path)
    
    # copy executable

    copy_file(root, executable)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('root', help='chroot root folder')
    parser.add_argument('executable', help='executable to pack')
    args = parser.parse_args()

    main(args.root, args.executable)