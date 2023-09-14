from glob import glob

from .common import *

for name in glob(os.path.dirname(__file__) + '/*/*.??'):
    if os.path.isfile(name) and not name.endswith('__.py'):
        tmp = name.split(os.sep)
        api = tmp[-3]
        version = tmp[-2]
        name = tmp[-1][:-3]
        expression = f'from {api}.{version}.{name} import bp as {name}_{version}_bp'
        exec(expression)

# Blueprints用于在创建app时动态注册蓝图
Blueprints = [module for name, module in globals().items() if name.endswith('_bp') and isinstance(module, Blueprint)]
