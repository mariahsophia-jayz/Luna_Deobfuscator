from .prometheus import PrometheusDeobfuscator, MoonSecDeobfuscator
from .coming_soon import make_coming_soon

REGISTRY = {
    "prometheus": PrometheusDeobfuscator(),
    "moonsec": MoonSecDeobfuscator(),
    "luraph": make_coming_soon("Luraph")(),
    "moonveil": make_coming_soon("Moonveil")(),
}
