from dataclasses import dataclass


@dataclass
class DeobfuscationResult:
    success: bool
    message: str
    output_path: str | None = None


class Deobfuscator:
    name: str = "Unnamed"
    enabled: bool = False

    async def run(self, input_path: str, workdir: str) -> DeobfuscationResult:
        raise NotImplementedError
