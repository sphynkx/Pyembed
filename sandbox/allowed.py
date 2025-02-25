allowed_builtins = {
    'abs', 'all', 'any', 'bool', 'dict', 'enumerate', 'filter', 'float', 'int',
    'len', 'list', 'map', 'max', 'min', 'print', 'range', 'round', 'set', 'str', 
    'sum', 'tuple', 'zip', '__name__'
}

allowed_objects = {
    'abc': {'abc.ABC', 'abc.ABCMeta', 'abc.abstractclassmethod', 'abc.abstractmethod', 'abc.abstractproperty', 'abc.abstractstaticmethod', 'abc.update_abstractmethods'},
    'asyncio': {'asyncio.all_tasks', 'asyncio.cancel', 'asyncio.create_task', 'asyncio.gather', 'asyncio.Queue', 'asyncio.run', 'asyncio.sleep', 'asyncio.wait'},
    'base64': {'base64.b64decode', 'base64.b64encode', 'base64.decode', 'base64.encode'},
    'calendar': {'calendar.month', 'calendar.weakheader'},
    'datetime': {'datetime.date', 'datetime.dateime', 'datetime.time', 'datetime.timedelta'},
    'functools': {'functools.lru_cache', 'functools.partial', 'functools.reduce', 'functools.singledispatch', 'functools.wraps'},
    'gmpy2': {'gmpy2.fib', 'gmpy2.is_prime', 'gmpy2.mpc', 'gmpy2.mpfr', 'gmpy2.mpq', 'gmpy2.mpz'},
    'html': {'html.escape', 'html.unescape'},
    'io': {'BytesIO', 'BytesIO.close', 'BytesIO.read', 'BytesIO.seek'},
    'ipaddress': {'ipaddress.ip_address', 'ipaddress.IPv4Address', 'ipaddress.IPv6Address'},
    'itertools': {'itertools.accumulate', 'itertools.batched', 'itertools.chain', 'itertools.combinations', 'itertools.combinations_with_replacement', 'itertools.compress', 'itertools.count', 'itertools.cycle', 'itertools.dropwhile', 'itertools.filterfalse', 'itertools.groupby', 'itertools.islice', 'itertools.pairwise', 'itertools.permutations', 'itertools.product', 'itertools.repeat', 'itertools.starmap', 'itertools.takewhile', 'itertools.tee', 'itertools.zip_longest'},
    'json': {'json.dumps', 'json.JSONDecoder', 'json.JSONEncoder', 'json.loads'},
    'matplotlib.pyplot': {'matplotlib.pyplot.figure', 'matplotlib.pyplot.plot', 'matplotlib.pyplot.savefig', 'matplotlib.pyplot.show', 'matplotlib.pyplot.title', 'matplotlib.pyplot.xlabel', 'matplotlib.pyplot.ylabel'},
    'math': {'sqrt', 'cos', 'sin', 'pi', 'log', 'exp', 'factorial'},
    'mpl_toolkits.mplot3d': {'Axes3D'},
    'numpy': {'array', 'arange', 'linspace', 'zeros', 'ones', 'empty', 'eye', 'dot', 'inner'},
    'pandas': {'pandas.DataFrame', 'pandas.describe', 'pandas.head', 'pandas.info', 'pandas.Series', 'pandas.tail'},
    'random': {'random.Random', 'random.Random.randint', 'random.Random.choice', 'random.Random.shuffle'},
    'time': {'time.ctime', 'time.gmtime', 'time.localtime', 'time.sleep', 'time.strftime', 'time.strptime'}
}
