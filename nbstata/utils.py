# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/01_utils.ipynb.

# %% auto 0
__all__ = ['parse_code_if_in_regex', 'comment_regex', 'delimit_regex', 'multi_regex', 'parse_code_if_in', 'in_range',
           'is_cr_delimiter', 'ending_delimiter', 'standardize_code', 'is_start_of_program_block',
           'break_out_prog_blocks', 'HiddenPrints', 'print_red']

# %% ../nbs/01_utils.ipynb 3
import re
import sys
import os

# %% ../nbs/01_utils.ipynb 5
parse_code_if_in_regex = re.compile(
    r'\A(?P<code>(?!if\s)(?!\sif)(?!in\s)(?!\sin).+?)?(?P<if>\s*if\s+.+?)?(?P<in>\s*in\s.+?)?\Z',
    flags=re.DOTALL + re.MULTILINE
)

# %% ../nbs/01_utils.ipynb 6
def parse_code_if_in(code):
    """Parse line of Stata code into code, if, in"""
    match = parse_code_if_in_regex.match(code.strip())
    if match:
        args = match.groupdict()
        for k in args:
            args[k] = args[k] if isinstance(args[k],str) else ''   
    else:
        args = {'code':code,
                'if':'',
                'in':''}    
    return args

# %% ../nbs/01_utils.ipynb 11
def in_range(stata_in_code):
    """Return in-statement range"""    
    stata_range_code = stata_in_code.replace(' in ','').strip()
    slash_pos = stata_range_code.find('/')
    if slash_pos == -1:
        return (None, None)
    start = stata_range_code[:slash_pos]
    end = stata_range_code[slash_pos+1:]
    if start.strip() == 'f': start = 1
    if end.strip() == 'l': end = count()
    return (int(start)-1, int(end))

# %% ../nbs/01_utils.ipynb 16
# Detect comments spanning multiple lines
comment_regex = re.compile(r'(((?: |\t)\/\/\/)(.)*(\n|\r)|(\/\*)(.|\s)*?(\*\/))')

def _remove_multi_line_comments(code):
    return comment_regex.sub(' ',code)

# %% ../nbs/01_utils.ipynb 22
def is_cr_delimiter(delimiter):
    return delimiter in {'cr', None}

# %% ../nbs/01_utils.ipynb 23
delimit_regex = re.compile(r'#delimit(.*$)', flags=re.MULTILINE)
def _replace_delimiter(code, starting_delimiter=None):
    # Recursively replace custom delimiter with newline

    split = delimit_regex.split(code.strip(),maxsplit=1)

    if len(split) == 3:
        before = split[0]
        after = _replace_delimiter(split[2],split[1].strip())
    else:
        before = code
        after = ''

    if not is_cr_delimiter(starting_delimiter):
        before = before.replace('\r', ' ').replace('\n', ' ')
        before = before.replace(';','\n')

    return before + after

# %% ../nbs/01_utils.ipynb 27
def ending_delimiter(code, starting_delimiter=None):
    code = _remove_multi_line_comments(code)
    # Recursively determine ending delimiter
    split = delimit_regex.split(code.strip(),maxsplit=1)
    if len(split) == 3:
        delimiter = ending_delimiter(split[2],split[1].strip())
    elif len(split) == 2:
        delimiter = split[1].strip()
    else:
        delimiter = starting_delimiter
    return None if is_cr_delimiter(delimiter) else ';'

# %% ../nbs/01_utils.ipynb 31
# Detect Multiple whitespace
multi_regex = re.compile(r' +')

def standardize_code(code, starting_delimiter=None):
    """Remove comments spanning multiple lines and replace custom delimiters"""
    code = _remove_multi_line_comments(code)
    
    # After removing multi-line comments, which could include "#delimit;"
    code = _replace_delimiter(code, starting_delimiter) 
    
    # Replace multiple whitespace with one
    code = multi_regex.sub(' ',code)
    
    # Delete blank lines and whitespace at start and end of lines
    code_lines = code.splitlines()
    std_lines = []
    for code_line in code_lines:
        cs = code_line.strip()
        if cs:
            std_lines.append(cs)
    return '\n'.join(std_lines)

# %% ../nbs/01_utils.ipynb 40
def _startswith_stata_abbrev(string, full_command, shortest_abbrev):
    for j in range(len(shortest_abbrev), len(full_command)+1):
        if string.startswith(full_command[0:j] + ' '):
            return True
    return False

# %% ../nbs/01_utils.ipynb 42
def _remove_prog_prefixes(cs):
    if (_startswith_stata_abbrev(cs, 'quietly', 'qui')
        or cs.startswith('capture ')
        or _startswith_stata_abbrev(cs, 'noisily', 'n')):
        return _remove_prog_prefixes(cs.split(None, maxsplit=1)[1])
    else:
        return cs

# %% ../nbs/01_utils.ipynb 44
def is_start_of_program_block(std_code_line):
    cs = _remove_prog_prefixes(std_code_line)
    _starts_program = (_startswith_stata_abbrev(cs, 'program', 'pr')
                       and not (cs == 'program di'
                                or cs == 'program dir'
                                or cs.startswith('program drop ')
                                or _startswith_stata_abbrev(cs, 'program list', 'program l')))
    return (_starts_program
            or (cs in {'mata', 'mata:'})
            or (cs in {'python', 'python:'}))

# %% ../nbs/01_utils.ipynb 46
def break_out_prog_blocks(code, starting_delimiter=None):
    std_code_lines = standardize_code(code, starting_delimiter).splitlines()
    return list(_prog_blocks(std_code_lines))

# %% ../nbs/01_utils.ipynb 47
def _prog_blocks(std_code_lines):
    next_block_lines = []
    in_program = False
    for std_code_line in std_code_lines:         
        if is_start_of_program_block(std_code_line):
            if next_block_lines: # previous lines
                yield _block(next_block_lines, is_prog=in_program)
                next_block_lines = []
            in_program = True
        next_block_lines.append(std_code_line)
        if std_code_line == 'end': # regardless of whether in_program
            yield _block(next_block_lines, is_prog=True)
            next_block_lines = []
            in_program = False
    if next_block_lines:
        yield _block(next_block_lines, in_program)
        

def _block(block_lines, is_prog):
    return {"is_prog": is_prog, "std_code": '\n'.join(block_lines)}

# %% ../nbs/01_utils.ipynb 51
class HiddenPrints:
    """A context manager for suppressing `print` output"""
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout

# %% ../nbs/01_utils.ipynb 54
def print_red(text):
    print(f"\x1b[31m{text}\x1b[0m")
