from .base import Deobfuscator, DeobfuscationResult


def make_coming_soon(obfuscator_name: str):
    class ComingSoonDeobfuscator(Deobfuscator):
        name = obfuscator_name
        enabled = False

        async def run(self, input_path: str, workdir: str) -> DeobfuscationResult:
            return DeobfuscationResult(
                success=False,
                message=f"{self.name} support isn't wired up yet — coming soon.",
            )

    return ComingSoonDeobfuscator
