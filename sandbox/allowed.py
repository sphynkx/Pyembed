allowed_builtins = {
    'abs', 'all', 'any', 'bool', 'dict', 'enumerate', 'filter', 'float', 'int',
    'len', 'list', 'map', 'max', 'min', 'print', 'range', 'round', 'set', 'str', 
    'sum', 'tuple', 'zip', '__name__'
}

allowed_objects = {
    'abc': {'ABC', 'abstractmethod'},
    'asyncio': {'all_tasks', 'create_task', 'gather', 'wait', 'sleep', 'run', 'cancel', 'Queue'},
    'base64': {'b64encode', 'b64decode', 'encode', 'decode'},
    'datetime': {'datetime', 'timedelta', 'date', 'time'},
    'functools': {'reduce', 'partial', 'wraps', 'lru_cache', 'singledispatch'},
    'gmpy2': {'mpz', 'mpq', 'mpfr', 'mpc', 'is_prime', 'fib'},
    'html': {'escape', 'unescape'},
    'io': {'BytesIO'},
    'itertools': {'count', 'cycle', 'repeat', 'combinations', 'permutations'},
    'json': {'dumps', 'loads', 'JSONEncoder', 'JSONDecoder'},
    'matplotlib.pyplot': {'plot', 'show', 'figure', 'title', 'xlabel', 'ylabel'},
    'math': {'sqrt', 'cos', 'sin', 'pi', 'log', 'exp', 'factorial'},
    'mpl_toolkits.mplot3d': {'Axes3D'},
    'numpy': {'array', 'arange', 'linspace', 'zeros', 'ones', 'empty', 'eye', 'dot', 'inner'},
    'pandas': {'DataFrame', 'Series', 'head', 'tail', 'describe', 'info'},
    'random': {'Random', 'randint', 'choice', 'shuffle'},
    'time': {'time', 'sleep', 'ctime', 'strftime', 'strptime', 'gmtime', 'localtime'}
}
