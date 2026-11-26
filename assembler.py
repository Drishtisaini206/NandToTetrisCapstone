import sys

COMP = {
    '0': '0101010', '1': '0111111', '-1': '0111010', 'D': '0001100',
    'A': '0110000', '!D': '0001101', '!A': '0110001', '-D': '0001111',
    '-A': '0110011', 'D+1': '0011111', 'A+1': '0110111', 'D-1': '0001110',
    'A-1': '0110010', 'D+A': '0000010', 'D-A': '0010011', 'A-D': '0000111',
    'D&A': '0000000', 'D|A': '0010101',
    'M': '1110000', '!M': '1110001', '-M': '1110011', 'M+1': '1110111',
    'M-1': '1110010', 'D+M': '1000010', 'D-M': '1010011', 'M-D': '1000111',
    'D&M': '1000000', 'D|M': '1010101',
}
COMMUTE = {'A+D': 'D+A', 'M+D': 'D+M', 'A&D': 'D&A', 'M&D': 'D&M',
           'A|D': 'D|A', 'M|D': 'D|M', '1+D': 'D+1', '1+A': 'A+1', '1+M': 'M+1'}
DEST = {'': '000', 'M': '001', 'D': '010', 'MD': '011',
        'A': '100', 'AM': '101', 'AD': '110', 'AMD': '111'}
JUMP = {'': '000', 'JGT': '001', 'JEQ': '010', 'JGE': '011',
        'JLT': '100', 'JNE': '101', 'JLE': '110', 'JMP': '111'}
SYMBOLS = {'SP': 0, 'LCL': 1, 'ARG': 2, 'THIS': 3, 'THAT': 4,
           'SCREEN': 16384, 'KBD': 24576}
SYMBOLS.update({f'R{i}': i for i in range(16)})


def clean(line):
    return line.split('//')[0].replace(' ', '').replace('\t', '').strip()


def assemble(lines):
    symbols = dict(SYMBOLS)
    pc = 0
    first_seen = {}
    for n, raw in enumerate(lines, 1):
        line = clean(raw)
        if not line:
            continue
        if line.startswith('(') and line.endswith(')'):
            label = line[1:-1]
            if label in first_seen:
                print(f"Warning: Line {n}: label '{label}' already defined "
                      f"on line {first_seen[label]}")
            else:
                first_seen[label] = n
                symbols[label] = pc
        else:
            pc += 1

    out, next_var = [], 16
    for n, raw in enumerate(lines, 1):
        line = clean(raw)
        if not line or line.startswith('('):
            continue
        if line.startswith('@'):
            sym = line[1:]
            if sym.isdigit():
                val = int(sym)
            else:
                if sym not in symbols:
                    symbols[sym] = next_var
                    next_var += 1
                val = symbols[sym]
            out.append(format(val, '016b'))
        else:
            dest, comp, jump = '', line, ''
            if '=' in comp:
                dest, comp = comp.split('=', 1)
            if ';' in comp:
                comp, jump = comp.split(';', 1)
            comp = COMMUTE.get(comp, comp)
            if comp not in COMP or dest not in DEST or jump not in JUMP:
                raise ValueError(f"Line {n}: invalid instruction: {raw.strip()}")
            out.append('111' + COMP[comp] + DEST[dest] + JUMP[jump])
    return out


if __name__ == '__main__':
    path = sys.argv[1]
    with open(path) as f:
        result = assemble(f.read().splitlines())
    with open(path.rsplit('.', 1)[0] + '.hack', 'w') as f:
        f.write('\n'.join(result) + '\n')