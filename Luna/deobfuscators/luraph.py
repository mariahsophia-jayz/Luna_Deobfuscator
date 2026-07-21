import os
import asyncio
import subprocess

from .base import Deobfuscator, DeobfuscationResult

LURAPH_JAR_PATH = os.environ.get("LURAPH_JAR_PATH", "./jars/LuraphDeobfuscator.jar")
UNLUAC_JAR_PATH = os.environ.get("UNLUAC_JAR_PATH", "./jars/unluac.jar")
JAVA_BIN = os.environ.get("JAVA_BIN", "java")
SUBPROCESS_TIMEOUT = 60


def _run(args, timeout=SUBPROCESS_TIMEOUT):
    return subprocess.run(args, capture_output=True, text=True, timeout=timeout)


class LuraphDeobfuscator(Deobfuscator):
    name = "Luraph"
    enabled = True

    async def run(self, input_path: str, workdir: str) -> DeobfuscationResult:
        if not os.path.isfile(LURAPH_JAR_PATH):
            return DeobfuscationResult(
                success=False,
                message="LuraphDeobfuscator.jar isn't configured on this bot.",
            )

        luac_path = os.path.join(workdir, "output.luac")
        final_lua_path = os.path.join(workdir, "deobfuscated.lua")

        try:
            result = await asyncio.to_thread(
                _run,
                [JAVA_BIN, "-jar", LURAPH_JAR_PATH, "-i", input_path, "-o", luac_path],
            )
        except subprocess.TimeoutExpired:
            return DeobfuscationResult(success=False, message="Timed out running Luraph deobfuscator.")

        if result.returncode != 0 or not os.path.isfile(luac_path):
            error_snippet = (result.stderr or result.stdout or "unknown error")[-1500:]
            return DeobfuscationResult(
                success=False,
                message=f"Deobfuscation failed:\n```\n{error_snippet}\n```",
            )

        if os.path.isfile(UNLUAC_JAR_PATH):
            try:
                decompile_result = await asyncio.to_thread(
                    _run, [JAVA_BIN, "-jar", UNLUAC_JAR_PATH, luac_path]
                )
                if decompile_result.returncode == 0:
                    with open(final_lua_path, "w", encoding="utf-8") as f:
                        f.write(decompile_result.stdout)
                    return DeobfuscationResult(
                        success=True,
                        message="Done — decompiled output attached.",
                        output_path=final_lua_path,
                    )
            except subprocess.TimeoutExpired:
                pass

        return DeobfuscationResult(
            success=True,
            message="Done — here's the decrypted bytecode (`.luac`). Add unluac.jar for readable Lua source.",
            output_path=luac_path,
        )
