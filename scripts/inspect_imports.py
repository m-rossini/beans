import sys

print("sys.path", sys.path[:5])
import beans.world as w

print("beans.world.__file__ =", w.__file__)
print("has initialize", hasattr(w.World, "initialize"))
print("World attributes", [a for a in dir(w.World) if not a.startswith("__")])
