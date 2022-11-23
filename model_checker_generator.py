#!/usr/bin/env python3
import sys
import re

allowed_instructions = {'pop', 'push', 'goto', 'load', 'store', 'if', 'halt'}
allowed_mem_values = ('low', 'lo', 'l', 'high', 'hi', 'h', 'null')
n_instructions = 0
memory_size = 3
instruction_list = []
memory_list = []
inst_delimiter_start = '/-- Instruction initialization start --/'
inst_delimiter_end = '/-- Instruction initialization end --/'
mem_delimeter_start = '/-- Memory initialization start --/'
mem_delimeter_end = '/-- Memory initialization end --/'


def init_instructions(instruction_list):
    instructions = inst_delimiter_start + '\n\n\t\t'
    for j in range(len(instruction_list)):
        instructions += 'init(inst[{}]) := {};\n\t\tinit(arg[{}]) := {};\n\t\tinit(ipd[{}]) := {};\n\t\t'.format(
            j, instruction_list[j]['inst'], j, instruction_list[j]['arg'], j, instruction_list[j]['ipd'])
    instructions += '\n\t\t' + inst_delimiter_end
    return instructions


def init_memory(memory_list):
    memory = mem_delimeter_start + '\n\n\t\t'
    for j in range(len(memory_list)):
        memory += 'init(memory[{}]) := {};\n\t\t'.format(j, memory_list[j])
    memory += '\n\t\t' + mem_delimeter_end
    return memory


def export_bytecode(instruction_list, filename):
    with open(filename, 'w') as f:
        for i, inst in enumerate(instruction_list):
            if i:
                f.write('\n')
            f.write('{} {} {}'.format(inst['inst'], inst['arg'], inst['ipd']))


if len(sys.argv) == 2 and (sys.argv[1] == '-h' or sys.argv[1] == '--help'):
    print(f'Usage: {sys.argv[0]} [bytecode_file].')
    exit(0)

if len(sys.argv) == 1:

    n_instructions = input('Enter number of instructions: ')
    try:
        n_instructions = int(n_instructions)
    except ValueError:
        sys.stderr.write('Number of instructions must be numerical!\n')
        exit(1)

    for i in range(n_instructions):
        ok = False
        while not ok:
            instruction = input(f'Enter instruction number {i + 1}: ').strip().split(' ')
            inst = instruction[0].lower()
            if inst in allowed_instructions:
                if inst in {'pop', 'push', 'halt'}:
                    arg = 0
                elif len(instruction) >= 2:
                    try:
                        arg = int(instruction[1])
                    except ValueError:
                        sys.stderr.write('The argument must be numerical!\n')
                        continue
                else:
                    sys.stderr.write('Numerical argument must be provided!\n')
                    continue
                if 0 <= arg < n_instructions:
                    while not ok:
                        ipd = input(
                            f'Enter ipd for instruction number {i + 1} (leave blank for default value): ').strip()
                        if ipd == '':
                            ipd = 0
                            ok = True
                            instruction_list.append({'inst': inst, 'arg': arg, 'ipd': ipd})
                        else:
                            try:
                                ipd = int(ipd)
                                if 0 <= ipd < n_instructions:
                                    ok = True
                                    instruction_list.append({'inst': inst, 'arg': arg, 'ipd': ipd})
                                else:
                                    sys.stderr.write('The ipd must be in range [0, {}]!\n'.format(n_instructions - 1))
                            except ValueError:
                                sys.stderr.write('IPD must be numerical!\n')
                                continue
                else:
                    sys.stderr.write('The argument must be in range [0, {}]!\n'.format(n_instructions - 1))
                    continue
            else:
                sys.stderr.write('Allowed instructions are {}.\n'.format(str(allowed_instructions)))
                continue

    # Export the bytecode in a file
    export_bytecode(instruction_list, 'bytecode')


else:
    try:
        with open(sys.argv[1], 'r') as f:
            for line in f:
                try:
                    instruction = line.replace('\n', '').strip().split(' ')
                    if instruction[0] in {'pop', 'push', 'halt'}:
                        arg = 0
                    else:
                        arg = instruction[1]
                    if len(instruction) == 3 and instruction[0] == 'if':
                        ipd = instruction[2]
                    else:
                        ipd = 0
                    instruction_list.append({'inst': instruction[0], 'arg': arg, 'ipd': ipd})
                    n_instructions += 1
                except:
                    sys.stderr.write('Problem with file!\n')
                    exit(1)
    except FileNotFoundError:
        sys.stderr.write('No such file or directory: {}.\n'.format(sys.argv[1]))
        exit(1)

for i in range(memory_size):
    ok = False
    while not ok:
        mem_value = input(f'Enter memory value number {i + 1}: ').strip().lower()
        if mem_value in allowed_mem_values:
            if mem_value in allowed_mem_values[:3]:
                memory_list.append('lo')
            elif mem_value in allowed_mem_values[4:6]:
                memory_list.append('hi')
            else:
                memory_list.append('null')
            ok = True
        elif mem_value == '':
            memory_list.append('null')
            ok = True
        else:
            sys.stderr.write('Allowed values are {} (case insensitive).\n'.format(str(allowed_mem_values)))
            continue

# Open model
try:
    nusmv_model = open('SIF.smv', 'r').read()
except FileNotFoundError:
    sys.stderr.write('Cannot find template model in current directory.\n')
    exit(1)

# Substitute instruction section
instructions = init_instructions(instruction_list)
memory = init_memory(memory_list)
nusmv_model = nusmv_model.split(inst_delimiter_start)[0] + instructions + nusmv_model.split(inst_delimiter_end)[1]
# Substitute instruction number
nusmv_model = re.sub('n_inst := [0-9]+;', f'n_inst := {n_instructions};', nusmv_model)
# Substitute memory section
nusmv_model = nusmv_model.split(mem_delimeter_start)[0] + memory + nusmv_model.split(mem_delimeter_end)[1]

# Substitute specification to model

spec = 'SPEC\n\t\tAG ('
lo_mem = [i for i in range(len(memory_list)) if memory_list[i] == 'lo']

for k in range(len(lo_mem)):
    spec += f'state.memory[{lo_mem[k]}] = lo'
    if k != len(lo_mem) - 1:
        spec += ' & '

spec += ')'

nusmv_model = nusmv_model.split('SPEC')[0] + spec

with open('generated_model.smv', 'w') as f:
    f.write(nusmv_model)
