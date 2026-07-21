from .luraph import LuraphDeobfuscator
from .coming_soon import make_coming_soon

REGISTRY = {
    "luraph": LuraphDeobfuscator(),
    "prometheus": make_coming_soon("Prometheus")(),
    "moonveil": make_coming_soon("Moonveil")(),
    "moonsec": make_coming_soon("MoonSec")(),
}
