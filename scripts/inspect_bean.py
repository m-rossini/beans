import inspect

import beans.bean as b

print("Bean.__init__ signature:", inspect.signature(b.Bean.__init__))
print("Bean class source file:", b.__file__)
