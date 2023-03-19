# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/04_code_utils.ipynb.

# %% auto 0
__all__ = ['comment_regex', 'stata_lexer', 'delimit_regex', 'multi_regex', 'pre', 'kwargs', 'local_def_in', 'preserve_restore_in',
           'remove_comments', 'ends_in_comment_block', 'valid_single_line_code', 'ending_sc_delimiter',
           'standardize_code', 'ending_code_version', 'is_start_of_program_block', 'break_out_prog_blocks']

# %% ../nbs/04_code_utils.ipynb 4
import re
from decimal import Decimal

# %% ../nbs/04_code_utils.ipynb 5
from pygments import lexers
from pygments.token import Comment

# %% ../nbs/04_code_utils.ipynb 8
# Detect comments spanning multiple lines
comment_regex = re.compile(r'(((?: |\t)\/\/\/)(.)*(\n|\r)|(\/\*)(.|\s)*?(\*\/))')

def _remove_multi_line_comments(code):
    return comment_regex.sub(' ',code)

# %% ../nbs/04_code_utils.ipynb 14
stata_lexer = lexers.get_lexer_by_name('stata')

def _lex_tokens(code):
    return stata_lexer.get_tokens_unprocessed(code)

# %% ../nbs/04_code_utils.ipynb 16
def remove_comments(code):
    return "".join(token[2] for token in _lex_tokens(code) if token[1] not in Comment)

# %% ../nbs/04_code_utils.ipynb 20
def _end_block_followed_by_non_comment_block(code):
    return (
        code.rfind('*/') != -1
        and not ends_in_comment_block(code[code.rfind('*/')+2:])
    )

# %% ../nbs/04_code_utils.ipynb 21
def ends_in_comment_block(code):
    last_token = list(_lex_tokens(code))[-1]
    last_token_type = last_token[1]
    return (
        last_token_type == Comment.Multiline
        and code.strip()[-2:] != "*/"
        and not _end_block_followed_by_non_comment_block(code)
    )

# %% ../nbs/04_code_utils.ipynb 25
def _is_not_cr_delimiter(delimiter):
    return delimiter != 'cr'

# %% ../nbs/04_code_utils.ipynb 26
delimit_regex = re.compile(r'^[ \t]*#delimit(.*$)', flags=re.MULTILINE)
def _replace_delimiter(code, sc_delimiter=False):
    # Recursively replace custom delimiter with newline

    split = delimit_regex.split(code.strip(), maxsplit=1)

    if len(split) == 3:
        before = split[0]
        after = _replace_delimiter(split[2], _is_not_cr_delimiter(split[1].strip()))
    else:
        before = code
        after = ''

    if sc_delimiter:
        before_last_sc_pos = before.rfind(';')
        if before_last_sc_pos < len(before.strip()) - 1:
            before = before[:before_last_sc_pos+1]
            if len(split) > 1:
                after = _replace_delimiter(before[before_last_sc_pos+1:]+" ".join(split[1:]), sc_delimiter=True)
        before = before.replace('\r', ' ').replace('\n', ' ')
        before = before.replace(';','\n')

    return before + after

# %% ../nbs/04_code_utils.ipynb 35
def valid_single_line_code(code):
    code = remove_comments(code)
    if delimit_regex.match(code):
        return ""
    else:
        return code

# %% ../nbs/04_code_utils.ipynb 37
def ending_sc_delimiter(code, sc_delimiter=False):
    code = _remove_multi_line_comments(code)
    # Recursively determine ending delimiter
    split = delimit_regex.split(code.strip(),maxsplit=1)
    
    if len(split) == 3:
        before = split[0]
    else:
        before = code
    if sc_delimiter:
        before_last_sc_pos = before.rfind(';')
        if before_last_sc_pos < len(before.strip()) - 1:
            if len(split) > 1:
                return ending_sc_delimiter(before[before_last_sc_pos+1:]+" ".join(split[1:]), sc_delimiter=True)
            
    if len(split) == 3:
        sc_delimiter = ending_sc_delimiter(split[2], _is_not_cr_delimiter(split[1].strip()))
    elif len(split) == 2:
        sc_delimiter = _is_not_cr_delimiter(split[1].strip())

    return sc_delimiter

# %% ../nbs/04_code_utils.ipynb 44
# Detect Multiple whitespace
multi_regex = re.compile(r'(?P<char>\S) +')

def standardize_code(code, sc_delimiter=False):
    """Remove comments spanning multiple lines and replace custom delimiters"""
    code = _remove_multi_line_comments(code)
    
    # After removing multi-line comments, which could include "#delimit;"
    code = _replace_delimiter(code, sc_delimiter) 
    
    # Replace multiple interior whitespace with one
    code = multi_regex.sub('\g<char> ',code)
    
    # Delete blank lines and whitespace at end of lines
    code_lines = code.splitlines()
    std_lines = []
    for code_line in code_lines:
        cs = code_line.rstrip()
        if cs:
            std_lines.append(cs)
    return '\n'.join(std_lines)

# %% ../nbs/04_code_utils.ipynb 57
def _startswith_stata_abbrev(string, full_command, shortest_abbrev):
    for j in range(len(shortest_abbrev), len(full_command)+1):
        if string.startswith(full_command[0:j] + ' '):
            return True
    return False

# %% ../nbs/04_code_utils.ipynb 59
def _remove_prefixes(std_code_line):
    std_code_line = std_code_line.lstrip()
    if (_startswith_stata_abbrev(std_code_line, 'quietly', 'qui')
        or std_code_line.startswith('capture ')
        or _startswith_stata_abbrev(std_code_line, 'noisily', 'n')):
        return _remove_prefixes(std_code_line.split(None, maxsplit=1)[1])
    else:
        return std_code_line

# %% ../nbs/04_code_utils.ipynb 63
def ending_code_version(code, sc_delimiter=False, code_version=None, stata_version='17.0'):
    if 'version' not in code:
        return code_version
    std_code = standardize_code(code, sc_delimiter)
    for std_code_line in reversed(std_code.splitlines()):
        if 'version ' not in std_code_line:
            continue
        m = re.match(r'\A\s*version ([0-9]+(?:\.[0-9][0-9]?)?)\Z', _remove_prefixes(std_code_line))
        if m:
            _version = Decimal(m.group(1)).normalize()
            if Decimal('1') <= _version <= Decimal(stata_version):
                code_version = None if _version == Decimal(stata_version).normalize() else str(_version)
                break
    return code_version

# %% ../nbs/04_code_utils.ipynb 67
pre = (
    r'(cap(t|tu|tur|ture)?'
    r'|qui(e|et|etl|etly)?'
    r'|n(o|oi|ois|oisi|oisil|oisily)?)')
kwargs = {'flags': re.MULTILINE}
local_def_in = re.compile(
    r"(^\s*({0} )*(loc(a|al)?|tempname|tempvar|tempfile|gettoken|token(i|iz|ize)?|levelsof)\s)|st_local\(".format(pre),
    **kwargs,
).search

# %% ../nbs/04_code_utils.ipynb 69
preserve_restore_in = re.compile(
    r"(^({0} )*(preserve|restore)[,\s]?\.*?$)|(;({0} )*(preserve|restore)[,\s]?\.*?$)".format(pre),
    **kwargs,
).search

# %% ../nbs/04_code_utils.ipynb 72
def is_start_of_program_block(std_code_line):
    cs = _remove_prefixes(std_code_line)
    _starts_program = (_startswith_stata_abbrev(cs, 'program', 'pr')
                       and not (cs.split()[1] in ['di', 'dir', 'drop', 'l', 'li', 'lis', 'list']))
    return (_starts_program
            or (cs in {'mata', 'mata:'})
            or (cs in {'python', 'python:'}))

# %% ../nbs/04_code_utils.ipynb 74
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

# %% ../nbs/04_code_utils.ipynb 75
def break_out_prog_blocks(code, sc_delimiter=False):
    std_code_lines = standardize_code(code, sc_delimiter).splitlines()
    return list(_prog_blocks(std_code_lines))
