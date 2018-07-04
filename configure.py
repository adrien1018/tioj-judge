#!/usr/bin/env python3

import argparse, subprocess, sys, os

parser = argparse.ArgumentParser(description = '')
parser.add_argument('--boxpath', default = '/tmp/tioj-box', help = 'Directory to make sandboxes (default: /tmp/tioj-box)')
parser.add_argument('--datapath', default = '/var/lib/tioj-judge', help = 'Directory to store judge data (default: /var/lib/tioj-judge)')
args = parser.parse_args()

def c_string(s):
    return '"' + s.translate(str.maketrans({'\\': r'\\', '"': r'\"'})) + '"'

def c_string_list(lst):
    ret = '{'
    for i in lst: ret += c_string(i) + ', '
    return ret[:-2] + '}'

def get_path(name):
    ps = subprocess.Popen(['which', name], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    return ps.communicate()[0][:-1].decode()

def get_stats(cmd, input = ''):
    ps = subprocess.Popen(['strace', '-fc'] + cmd, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    result = ps.communicate(input = input.encode())[1].decode()
    lns = result.split('\n')
    # print(result)
    pos = [i for i in range(len(lns)) if lns[i].find('----') != -1][0]
    return [ln.split()[-1] for ln in result.split('\n')[pos+1:-3]]

def combine_stats(*res):
    ret = []
    for i in res: ret += i
    ret = [*{*ret}]
    return ret

prog_list = ['gcc', 'g++', 'mono', 'mcs', 'gfortran', 'ghc', 'javac', 'java', 'node', 'fpc', 'perl', 'python2', 'python3', 'ruby', 'rustc']
prog_path = {}

for prog in prog_list:
    print('Getting path to', prog, '... ', end = '')
    prog_path[prog] = get_path(prog)
    if prog_path[prog] == '':
        print('\nCannot find', prog)
        sys.exit(1)
    print(prog_path[prog])

os.chdir('config')
print('Entering ./config ...')

compile_stats = {}
run_stats = {}

# C/C++
print('Getting system call list of C/C++...')
compile_stats['CCpp'] = combine_stats(
    get_stats(['g++', '-std=c++14', '-static', 'cpp_ce.cpp', '-o', 'cpp_ce']), # compilation error
    get_stats(['g++', '-std=c++14', '-static', 'cpp_1.cpp', '-o', 'cpp_1']), # linking error
    get_stats(['g++', '-std=c++14', '-static', '-c', 'cpp_1.cpp', '-o', 'cpp_1.o']),
    get_stats(['g++', '-std=c++14', '-static', '-c', 'cpp_header.cpp', '-o', 'cpp_header.o']),
    get_stats(['g++', '-o', 'cpp_1', 'cpp_1.o', 'cpp_header.o']))
run_stats['CCpp'] = combine_stats(
    get_stats(['./cpp_1'], '0'),
    get_stats(['./cpp_1'], '1'),
    get_stats(['./cpp_1'], '2'))

# TODO: Add other langs, query dynamic linking libs and processes count

# Fortran95
print('Getting system call list of Fortran...')
compile_stats['Fortran'] = combine_stats(
    get_stats(['gfortran', '-std=f95', 'fortran_ce.f95', '-o', 'fortran_ce']), # compilation error
    get_stats(['gfortran', '-std=f95', 'fortran_1.f95', '-o', 'fortran_1']))
run_stats['Fortran'] = combine_stats(
    get_stats(['./fortran_1'], '2\n2\n3'),
    get_stats(['./fortran_1'], '2'))

# C#
print('Getting system call list of C#...')
compile_stats['CSharp'] = combine_stats(
    get_stats(['mcs', 'csharp_ce.cs']), # compilation error
    get_stats(['mcs', 'csharp_1.cs']))
run_stats['CSharp'] = combine_stats(
    get_stats(['mono', './rust_1'], '19235\n21903\n'),
    get_stats(['mono', './rust_1'], '19235'))

# Python 2/3
print('Getting system call list of Python...')
run_stats['Python'] = combine_stats(
    get_stats(['python3', 'python3_1.py'], '0'),
    get_stats(['python3', 'python3_1.py'], '1'))

# Ruby
print('Getting system call list of Ruby...')
run_stats['Ruby'] = combine_stats(
    get_stats(['ruby', 'ruby_1.rb'], '1 1\n1'),
    get_stats(['ruby', 'ruby_1.rb'], '2 1\n1'))

# Rust
print('Getting system call list of Rust...')
compile_stats['Rust'] = combine_stats(
    get_stats(['rustc', 'rust_ce.rs']), # compilation error
    get_stats(['rustc', 'rust_1.rs']))
run_stats['Rust'] = combine_stats(
    get_stats(['./rust_1'], '19235\n21903\n'),
    get_stats(['./rust_1'], '19235\n021903\n'))

os.chdir('../')
print('Leaving directory...')

print('Generating src/config.cpp...')
with open('src/config.cpp', 'w') as f:
    f.write('#include "config.h"\n\n')
    f.write('const std::string kBoxPath = ' + c_string(args.boxpath) + ';\n')
    f.write('const std::string kDataPath = ' + c_string(args.datapath) + ';\n')
    for i in prog_path.items():
        if i[0] == 'g++': i = ('gpp', i[1])
        f.write('const std::string k_' + i[0] + 'Path = ' + c_string(i[1]) + ';\n')
    for i in compile_stats.items():
        f.write('const std::vector<std::string> k' + i[0] + 'CompileSyscalls = ' + c_string_list(i[1]) + ';\n')
    f.write('\n')
    for i in run_stats.items():
        f.write('const std::vector<std::string> k' + i[0] + 'RunSyscalls = ' + c_string_list(i[1]) + ';\n')

# C: gcc
# Cpp: g++
# CSharp: mono, mcs
# Fortran: gfortran
# Haskell: ghc
# Java: javac, java (version!)
# JavaScript: node
# Pascal: fpc
# Perl: perl
# Python: python2, python3
# Ruby: ruby
# Rust: rustc
