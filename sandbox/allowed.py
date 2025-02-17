allowed_builtins = {
    'print', 'len', 'range', 'sum', 'max', 'min', 'any', 'all',
    'str', 'int', 'float', 'bool', 'list', 'dict', 'set', 'tuple',
    'abs', 'round', 'zip', 'map', 'filter', 'enumerate', '__name__'
}

allowed_objects = {
    'mpl_toolkits.mplot3d': {'Axes3D'},
    'io': {'BytesIO'},
    'json': {'dumps', 'loads', 'JSONEncoder', 'JSONDecoder'},
    'pandas': {'DataFrame', 'Series', 'head', 'tail', 'describe', 'info'},
    'random': {'Random', 'randint', 'choice', 'shuffle'},
    'time': {'time', 'sleep', 'ctime', 'strftime', 'strptime', 'gmtime', 'localtime'},
    'datetime': {'datetime', 'timedelta', 'date', 'time'},
    'math': {'sqrt', 'cos', 'sin', 'pi', 'log', 'exp', 'factorial'},
    'gmpy2': {'mpz', 'mpq', 'mpfr', 'mpc', 'is_prime', 'fib'},
    'functools': {'reduce', 'partial', 'wraps', 'lru_cache', 'singledispatch'},
    'itertools': {'count', 'cycle', 'repeat', 'combinations', 'permutations'},
    'abc': {'ABC', 'abstractmethod'},
    'asyncio': {'all_tasks', 'create_task', 'gather', 'wait', 'sleep', 'run', 'cancel', 'Queue'},
    'html': {'escape', 'unescape'},
    'matplotlib.pyplot': {'plot', 'show', 'figure', 'title', 'xlabel', 'ylabel'},
    'base64': {'b64encode', 'b64decode', 'encode', 'decode'},
    'numpy': {'array', 'arange', 'linspace', 'zeros', 'ones', 'empty', 'eye', 'dot', 'inner'},
    'mpl_toolkits.mplot3d': {'Axes3D'},
}
