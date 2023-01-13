# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/04_code_utils.ipynb.

# %% auto 0
__all__ = ['comment_regex', 'delimit_regex', 'multi_regex', 'ending_sc_delimiter', 'standardize_code',
           'is_start_of_program_block', 'break_out_prog_blocks']

# %% ../nbs/04_code_utils.ipynb 4
import re

# %% ../nbs/04_code_utils.ipynb 7
# Detect comments spanning multiple lines
comment_regex = re.compile(r'(((?: |\t)\/\/\/)(.)*(\n|\r)|(\/\*)(.|\s)*?(\*\/))')

def _remove_multi_line_comments(code):
    return comment_regex.sub(' ',code)

# %% ../nbs/04_code_utils.ipynb 13
def _is_cr_delimiter(delimiter):
    return delimiter in {'cr', None}

# %% ../nbs/04_code_utils.ipynb 14
delimit_regex = re.compile(r'#delimit(.*$)', flags=re.MULTILINE)
def _replace_delimiter(code, sc_delimiter=False):
    # Recursively replace custom delimiter with newline

    split = delimit_regex.split(code.strip(),maxsplit=1)

    if len(split) == 3:
        before = split[0]
        after = _replace_delimiter(split[2],not _is_cr_delimiter(split[1].strip()))
    else:
        before = code
        after = ''

    if sc_delimiter:
        before = before.replace('\r', ' ').replace('\n', ' ')
        before = before.replace(';','\n')

    return before + after

# %% ../nbs/04_code_utils.ipynb 19
def ending_sc_delimiter(code, sc_delimiter=False):
    code = _remove_multi_line_comments(code)
    # Recursively determine ending delimiter
    split = delimit_regex.split(code.strip(),maxsplit=1)
    if len(split) == 3:
        sc_delimiter = ending_sc_delimiter(split[2], not _is_cr_delimiter(split[1].strip()))
    elif len(split) == 2:
        sc_delimiter = not _is_cr_delimiter(split[1].strip())
    return sc_delimiter

# %% ../nbs/04_code_utils.ipynb 23
# Detect Multiple whitespace
multi_regex = re.compile(r' +')

def standardize_code(code, sc_delimiter=False):
    """Remove comments spanning multiple lines and replace custom delimiters"""
    code = _remove_multi_line_comments(code)
    
    # After removing multi-line comments, which could include "#delimit;"
    code = _replace_delimiter(code, sc_delimiter) 
    
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

# %% ../nbs/04_code_utils.ipynb 34
def _startswith_stata_abbrev(string, full_command, shortest_abbrev):
    for j in range(len(shortest_abbrev), len(full_command)+1):
        if string.startswith(full_command[0:j] + ' '):
            return True
    return False

# %% ../nbs/04_code_utils.ipynb 36
def _remove_prog_prefixes(cs):
    if (_startswith_stata_abbrev(cs, 'quietly', 'qui')
        or cs.startswith('capture ')
        or _startswith_stata_abbrev(cs, 'noisily', 'n')):
        return _remove_prog_prefixes(cs.split(None, maxsplit=1)[1])
    else:
        return cs

# %% ../nbs/04_code_utils.ipynb 38
def is_start_of_program_block(std_code_line):
    cs = _remove_prog_prefixes(std_code_line)
    _starts_program = (_startswith_stata_abbrev(cs, 'program', 'pr')
                       and not (cs.split()[1] in ['di', 'dir', 'drop', 'l', 'li', 'lis', 'list']))
    return (_starts_program
            or (cs in {'mata', 'mata:'})
            or (cs in {'python', 'python:'}))

# %% ../nbs/04_code_utils.ipynb 40
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

# %% ../nbs/04_code_utils.ipynb 41
def break_out_prog_blocks(code, sc_delimiter=False):
    std_code_lines = standardize_code(code, sc_delimiter).splitlines()
    return list(_prog_blocks(std_code_lines))
