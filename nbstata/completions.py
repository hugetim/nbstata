# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/05_completions.ipynb.

# %% auto 0
__all__ = ['relevant_suggestion_keys', 'CompletionsManager', 'Env']

# %% ../nbs/05_completions.ipynb 4
from .utils import ending_delimiter, is_cr_delimiter
from .helpers import run_noecho
from .stata_session import StataSession
from fastcore.basics import patch_to
from enum import IntEnum
from typing import Tuple
import os
import re
import platform

# %% ../nbs/05_completions.ipynb 5
class CompletionsManager():
    def __init__(self, stata_session: StataSession):
        self.stata_session = stata_session

        self.last_chunk = re.compile(
            r'[\s"=][^\s"=]*?\Z', flags=re.MULTILINE).search
        
        # Path completion
        self.path_search = re.compile(
            r'^(?P<fluff>.*")(?P<path>[^"]*)\Z').search

#         # Magic completion
#         self.magic_completion = re.compile(
#             r'\A%(?P<magic>\S*)\Z', flags=re.DOTALL + re.MULTILINE).match

#         self.set_magic_completion = re.compile(
#             r'\A%set (?P<setting>\S*)\Z', flags=re.DOTALL + re.MULTILINE).match

#         self.matainline = re.compile(r"^m(ata)?\b").search

#         self.matacontext = re.compile(
#             r'(^|\s+)(?P<st>_?st_)'
#             r'(?P<context>\S+?)\('
#             r'(?P<quote>[^\)]*?")'
#             r'(?P<pre>[^\)]*?)\Z', flags=re.MULTILINE + re.DOTALL).search

        # Match context; this is used to determine if the line starts
        # with matrix or scalar. It also matches constructs like
        #
        #     (`=)?scalar(
        pre = (
            r'(cap(t|tu|tur|ture)?'
            r'|qui(e|et|etl|etly)?'
            r'|n(o|oi|ois|oisi|oisil|oisily)?)')
        kwargs = {'flags': re.MULTILINE}
        self.fcontext = {
            'function':
                re.compile(
                    r"(\s+|\=|`=)\s*(?P<name>\w+?)"
                    r"\([^\)]*?(?P<last_word>\w*)\Z", **kwargs).search,
#             'local_function':
#                 re.compile(
#                     r"\s.*?`\=\s*(?P<name>\w+?)"
#                     r"\([^\)]*?\Z", **kwargs).search,
        }
        self.context = {
            'line':
                re.compile(
                    r"^(?P<last_line>\s*({0}\s+)*(?P<first_word>\S+) .*?)\Z".format(pre),
                    **kwargs).search,
            'delimit_line':
                re.compile(
                    r"(?:\A|;)(?P<last_line>\s*({0}\s+)*(?P<first_word>\S+)\s[^;]*?)\Z".format(pre),
                    **kwargs).search
        }

# %% ../nbs/05_completions.ipynb 6
@patch_to(CompletionsManager)
def _scalar_f_pos_rcomp(self, code, r2chars):
    scalar_f = False
#     lfuncontext = self.fcontext['local_function'](code)
#     if lfuncontext:
#         lfunction = lfuncontext.groupdict()['name']
#         if lfunction == 'scalar':
#             scalar_f = True
#             pos =
#             if r2chars == ")'":
#                 rcomp = ""
#             elif r2chars[0:1] == ")":
#                 rcomp = ""
#             elif r2chars[0:1] == "'":
#                 rcomp = ")"
#             else:
#                 rcomp = ")'"
#     else:
    funcontext = self.fcontext['function'](code)
    if funcontext:
        function = funcontext.group('name')
        if function == 'scalar':
            scalar_f = True
            pos = funcontext.start('last_word') if funcontext.start('last_word') else len(code)
            rcomp = "" if (r2chars[0:1] == ")" or r2chars == " )") else ")"
    if scalar_f:
        return True, pos, rcomp
    else:
        return False, None, None

# %% ../nbs/05_completions.ipynb 13
@patch_to(CompletionsManager)
def _last_line_first_word(self, code, sc_delimit_mode=False):
    if sc_delimit_mode:
        linecontext = self.context['delimit_line'](code)
    else:
        linecontext = self.context['line'](code)
    if linecontext:
        last_line = linecontext.groupdict()['last_line']
        first_word = linecontext.groupdict()['first_word']
        return last_line, first_word
    else:
        return None, None

# %% ../nbs/05_completions.ipynb 18
@patch_to(CompletionsManager)
def get_file_paths(self, chunk):
    """Get file paths based on chunk
    Args:
        chunk (str): chunk of text after last space. Doesn't include string
            punctuation characters
    Returns:
        (List[str]): folders and files at that location
    """
    from sfi import SFIToolkit
    # If local exists, return empty list
    if re.search(r'[`\']', chunk):
        return []

    # Define directory separator
    dir_sep = '/'
    if platform.system() == 'Windows':
        if '/' not in chunk:
            dir_sep = '\\'

    # Get directory without ending file, and without / or \
    if any(x in chunk for x in ['/', '\\']):
        ind = max(chunk.rfind('/'), chunk.rfind('\\'))
        user_folder = chunk[:ind + 1]
        user_starts = chunk[ind + 1:]

        # Replace multiple consecutive / with a single /
        user_folder = re.sub(r'/+', '/', user_folder)
        user_folder = re.sub(r'\\+', r'\\', user_folder)

    else:
        user_folder = ''
        user_starts = chunk

    # Replace globals with their values
    globals_re = r'\$\{?((?![0-9_])\w{1,32})\}?'
    try:
        folder = re.sub(
            globals_re, lambda x: self.globals[x.group(1)], user_folder)
    except KeyError:
        # If the global doesn't exist in self.globals (aka it hasn't been
        # defined in the Stata environment yet), then there are no paths to
        # check
        return []

    # Use Stata's relative path
    abspath = re.search(r'^([/~]|[a-zA-Z]:)', folder)
    if not abspath:
        folder = SFIToolkit.getWorkingDir() + '/' + folder

    try:
        top_dir, dirs, files = next(os.walk(os.path.expanduser(folder)))
        results = [x + dir_sep for x in dirs] + files
        results = [
            user_folder + x for x in results if not x.startswith('.')
            and re.match(re.escape(user_starts), x, re.I)]

    except StopIteration:
        results = []

    return sorted(results)

# %% ../nbs/05_completions.ipynb 21
class Env(IntEnum):
#     -2: %set magic, %set x*
#     -1: magics, %x*
    GENERAL = 0    # varlist and/or file path
    LOCAL = 1      # `x* completed with `x*'
    GLOBAL = 2     # $x* completed with $x* or ${x* completed with ${x*}
    SCALAR = 4     # scalar .* x* completed with x* or scalar(x* completed with scalar(x*)
    MATRIX = 6     # matrix .* x* completed with x*
    SCALAR_VAR = 7 # scalars and varlist, scalar .* = x* completed with x*
    MATRIX_VAR = 8 # matrices and varlist, matrix .* = x* completed with x*
    MATA = 9       # inline or in mata environment

# %% ../nbs/05_completions.ipynb 22
@patch_to(CompletionsManager)
def _start_of_last_chunk(self, code):
    #any word at the end of a string that is not immediately preceded by one of the characters `, $, ", {, or /
#     search = re.search(r'(?<![`$"{/])\b\w+\Z', code, flags=re.MULTILINE)   
#     searchpos = -1 #if search is None else search.start() - 1
#     return max(code.rfind(' '), code.rfind('"'), searchpos) + 1
    search = self.last_chunk(code)
    return search.start() + 1 if search else 0

# %% ../nbs/05_completions.ipynb 25
@patch_to(CompletionsManager)
def get_env(self, 
            code: str, # Right-truncated to cursor position
            r2chars: str, # The two characters immediately after `code`, used to accurately determine rcomp
            starting_delimiter,
            mata_mode: bool = False, # Whether mata is on
           ) -> Tuple[Env, int, str, str]:
    """Returns completions environment
    
    Returns
    -------
    env : Env    
    pos : int
        Where the completions start. This is set to the start of the word to be completed.
    out_chunk : str
        Word to match.
    rcomp : str
        How to finish the completion (defaulting to nothing):
        locals: '
        globals (if start with ${): }
        scalars: )
        scalars (if start with `): )'
    """

#     lcode = code.lstrip()
#     if self.magic_completion(lcode):
#         pos = code.rfind("%") + 1
#         env = -1
#         rcomp = ""
#         return env, pos, code[pos:], rcomp
#     elif self.set_magic_completion(lcode):
#         pos = max(code.rfind(' '), code.rfind('"')) + 1
#         env = -2
#         rcomp = ""
#         return env, pos, code[pos:], rcomp
    delimiter = ending_delimiter(code, starting_delimiter)
    env = Env.GENERAL
    rcomp = ''
    
    # Detect space-delimited word.
    pos = self._start_of_last_chunk(code)

#     if mata_mode:
#         env = Env.MATA
#     else:
    if pos >= 1:
        # Figure out if current statement is a matrix or scalar
        # statement. If so, will add them to completions list.
        last_line, first_word = self._last_line_first_word(code, not is_cr_delimiter(delimiter))
        if first_word:
            equals_present = (last_line.find('=') > 0)
            if re.match(r'^sca(lar|la|l)?$', first_word): #.strip()
                env = Env.SCALAR_VAR if equals_present else Env.SCALAR
            elif re.match(r'^mat(rix|ri|r)?$', first_word): #.strip()
                env = Env.MATRIX_VAR if equals_present else Env.MATRIX
    #                 elif self.matainline(first_word.strip()):
    #                     env = 9

        # Constructs of the form scalar(x<tab> will be filled only
        # with scalars. This can be preceded by = or `=
        if env is Env.GENERAL:
            scalar_f, new_pos, new_rcomp = self._scalar_f_pos_rcomp(code, r2chars)
            if scalar_f:
                env = Env.SCALAR
                pos = new_pos
                rcomp = new_rcomp

    # Figure out if this is a local or global; env = 0 (default)
    # will suggest variables in memory.
    chunk = code[pos:]
    lfind = chunk.rfind('`')
    gfind = chunk.rfind('$')
    path_chars = any(x in chunk for x in ['/', '\\', '~'])
    chunk_quoted = chunk[lfind:].startswith('`"')

    if lfind >= 0 and (lfind > gfind) and not chunk_quoted:
        pos += lfind + 1
        env = Env.LOCAL
        rcomp = "" if r2chars[0:1] == "'" else "'"
    elif gfind >= 0 and not path_chars:
        bfind = chunk.rfind('{')
        if bfind >= 0 and (bfind == gfind+1):
            pos += bfind + 1
            env = Env.GLOBAL
            rcomp = "" if r2chars[0:1] == "}" else "}"
        else:
            env = Env.GLOBAL
            pos += gfind + 1
    elif chunk.startswith('"'):
        pos += 1
    elif chunk.startswith('`"'):
        pos += 2
    else:
        # Set to matrix or scalar environment, if applicable. Note
        # that matrices and scalars can be set to variable values,
        # so varlist is still a valid completion in a matrix or
        # scalar context.
        pass

#     if env == 9:
#         matacontext = self.matacontext(code)
#         if matacontext:
#             st, context, quote, pre = matacontext.groupdict().values()
#             varlist = [
#                 'data', 'sdata', 'store', 'sstore', 'view', 'sview',
#                 'varindex', 'varrename', 'vartype', 'isnumvar', 'isstrvar',
#                 'vartype', 'varformat', 'varlabel', 'varvaluelabel',
#                 'dropvar', 'keepvar']
#             _globals = ['global', 'global_hcat']
#             _locals = ['local']
#             scalars = ['numscalar', 'strscalar', 'numscalar_hcat']
#             matrices = [
#                 'matrix', 'matrix_hcat', 'matrixrowstripe',
#                 'matrixcolstripe', 'replacematrix']

#             posextra = 0
#             # if st:
#             #     posextra += len(st)
#             # if context:
#             #     posextra += len(context)
#             # if quote:
#             #     posextra += len(quote) + 1

#             if context in varlist:
#                 env = 0
#             elif context in _globals:
#                 env = 2
#                 rcomp = ''
#             elif context in _locals:
#                 env = 1
#                 rcomp = ''
#             elif context in scalars:
#                 env = 4
#                 rcomp = ''
#             elif context in matrices:
#                 env = 6
#                 rcomp = ''
#             else:
#                 posextra = 0

#             pos += posextra

    closing_symbol = True #config.get('autocomplete_closing_symbol', 'False')
#     closing_symbol = closing_symbol.lower() == 'true'
    if not closing_symbol:
        rcomp = ''
    out_chunk = code[pos:]
    return env, pos, out_chunk, rcomp

# %% ../nbs/05_completions.ipynb 26
relevant_suggestion_keys = {
    Env.GENERAL: ['varlist', 'scalars'],
    Env.LOCAL: ['locals'],
    Env.GLOBAL: ['globals'],
    Env.SCALAR: ['scalars'],
    Env.MATRIX: ['matrices'],
    Env.SCALAR_VAR: ['scalars', 'varlist'],
    Env.MATRIX_VAR: ['matrices', 'varlist'],
}

@patch_to(CompletionsManager)
def get(self, starts, env, rcomp):
    """Return environment-aware completions list."""
    relevant_suggestions = [var + rcomp 
                            for key in relevant_suggestion_keys[env]
                            for var in self.stata_session.suggestions[key]
                            if var.startswith(starts)]
    if env is Env.GENERAL:
        relevant_suggestions += self.get_file_paths(starts)
    return relevant_suggestions

#     elif env == 9:
#         if len(starts) > 1:
#             builtins = [
#                 var for var in mata_builtins if var.startswith(starts)]
#         else:
#             builtins = []

#         if re.search(r'[/\\]', starts):
#             paths = self.get_file_paths(starts)
#         else:
#             paths = []

#         return [
#             var for var in self.stata_session.suggestions['mata']
#             if var.startswith(starts)] + builtins + paths

# %% ../nbs/05_completions.ipynb 27
@patch_to(CompletionsManager)
def do(self, code, cursor_pos, starting_delimiter=None):
    env, pos, chunk, rcomp = self.get_env(
        code[:cursor_pos], 
        code[cursor_pos:(cursor_pos + 2)],
        starting_delimiter,
    )
    return pos, cursor_pos, self.get(chunk, env, rcomp)
