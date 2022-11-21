# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/01_utils.ipynb.

# %% auto 0
__all__ = ['parse_code_if_in_regex', 'delimit_regex', 'comment_regex', 'left_regex', 'multi_regex', 'parse_code_if_in',
           'in_range', 'Selectvar', 'standardize_code', 'is_start_of_program_block', 'break_out_prog_blocks',
           'HiddenPrints', 'print_red']

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

# %% ../nbs/01_utils.ipynb 10
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

# %% ../nbs/01_utils.ipynb 14
class Selectvar():
    """Class for generating Stata selectvar for getAsDict"""
    
    varname = None
    
    def __init__(self, stata_if_code):
        condition = stata_if_code.replace('if ', '', 1).strip()
        if condition:
            cmd = f"tempvar __selectionVar\ngenerate `__selectionVar' = cond({condition},1,0)"
            pystata.stata.run(cmd, quietly=True)      
            self.varname = sfi.Macro.getLocal("__selectionVar")  

    def clear(self):
        """Remove temporary selectvar from Stata dataset"""
        if self.varname != None:
            pystata.stata.run(f"capture drop {self.varname}", quietly=True)  

# %% ../nbs/01_utils.ipynb 17
### Regex's for standardize_code() ###
# Detect delimiter. This would detect valid delimiters plus macros:
# delimit_regex = re.compile(r'#delimit( |\t)+(;|cr|`.+\'|\$_.+|\$.+)')
# but it's unnecessary, since Stata's #delimit x interprets any x other 
# than 'cr' as switching the delimiter to ';'.
delimit_regex = re.compile(r'#delimit(.*$)', flags=re.MULTILINE)
# Detect comments spanning multiple lines
comment_regex = re.compile(r'((\/\/\/)(.)*(\n|\r)|(\/\*)(.|\s)*?(\*\/))')
# Detect left Whitespace
left_regex = re.compile(r'\n +')
# Detect Multiple whitespace
multi_regex = re.compile(r' +')

def standardize_code(code):
    """Remove comments spanning multiple lines and replace custom delimiters"""

    def _replace_delimiter(code,delimiter=None):
        # Recursively replace custom delimiter with newline

        split = delimit_regex.split(code.strip(),maxsplit=1)

        if len(split) == 3:
            before = split[0]
            after = _replace_delimiter(split[2],split[1].strip())
        else:
            before = code
            after = ''

        if delimiter != 'cr' and delimiter != None:
            before = before.replace('\r', '').replace('\n', '')
            before = before.replace(';','\n')

        return before + after

    # Apply custom delimiter
    code = _replace_delimiter(code)

    # Delete comments spanning multiple lines
    code = comment_regex.sub(' ',code)

    # Replace multiple whitespace with one
    code = multi_regex.sub(' ',code)
    
    # Delete blank lines and whitespace at start and end of lines
    cl = code.splitlines()
    co = []
    for c in cl:
        cs = c.strip()
        if cs:
            co.append(cs)
    return '\n'.join(co)

# %% ../nbs/01_utils.ipynb 22
def _startswith_stata_abbrev(string, full_command, shortest_abbrev):
    for j in range(len(shortest_abbrev), len(full_command)+1):
        if string.startswith(full_command[0:j] + ' '):
            return True
    return False

# %% ../nbs/01_utils.ipynb 25
def _remove_prog_prefixes(cs):
    if (_startswith_stata_abbrev(cs, 'quietly', 'qui')
        or cs.startswith('capture ')
        or _startswith_stata_abbrev(cs, 'noisily', 'n')):
        return _remove_prog_prefixes(cs.split(None, maxsplit=1)[1])
    else:
        return cs

# %% ../nbs/01_utils.ipynb 27
def is_start_of_program_block(std_code_line):
    cs = _remove_prog_prefixes(std_code_line)
    _starts_program = (_startswith_stata_abbrev(cs, 'program', 'pr')
                       and not (cs == 'program di'
                                or cs == 'program dir'
                                or cs.startswith('program drop ')
                                or _startswith_stata_abbrev(cs, 'program list', 'program l')))
    return (_starts_program
            or (cs in ['mata', 'mata:'])
            or (cs in ['python', 'python:']))

# %% ../nbs/01_utils.ipynb 29
def break_out_prog_blocks(code):
    cl = standardize_code(code).splitlines()
    co = []
    blocks = []
    for c in cl:
        # Are we starting a program definition?
        if is_start_of_program_block(c):
            if co: # lines before the start of a program block
                blocks.append({"is_prog": False, "std_code": '\n'.join(co)})
                co = []

        co.append(c)

        # Are we ending a program definition?
        if c == 'end':
            blocks.append({"is_prog": True, "std_code": '\n'.join(co)})
            co = []

    if co: 
        blocks.append({"is_prog": False, "std_code": '\n'.join(co)})
    return blocks

# %% ../nbs/01_utils.ipynb 33
class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout

# %% ../nbs/01_utils.ipynb 36
def print_red(text):
    print(f"\x1b[31m{text}\x1b[0m")
