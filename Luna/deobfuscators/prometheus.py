import os
import glob
import shutil
import asyncio
import subprocess

from .base import Deobfuscator, DeobfuscationResult

PROMETHEUS_TOOL_DIR = os.environ.get("PROMETHEUS_TOOL_DIR", "/app/tools/prometheus-deobfuscator")
PYTHON_BIN = os.environ.get("PYTHON_BIN", "python3")
SUBPROCESS_TIMEOUT = 90


def _run(args, cwd, timeout=SUBPROCESS_TIMEOUT):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=timeout)


class PrometheusDeobfuscator(Deobfuscator):
    name = "Prometheus"
    enabled = True

    # Shared implementation lives here; MoonSecDeobfuscator below just
    # reuses this run() method since it's the same underlying tool/pipeline.

    async def run(self, input_path: str, workdir: str) -> DeobfuscationResult:
        if not os.path.isdir(PROMETHEUS_TOOL_DIR):
            return DeobfuscationResult(
                success=False,
                message="Prometheus deobfuscator isn't set up on this bot yet.",
            )

        local_input_name = "input.lua"
        local_input_path = os.path.join(PROMETHEUS_TOOL_DIR, local_input_name)
        shutil.copyfile(input_path, local_input_path)

        before_files = set(glob.glob(os.path.join(PROMETHEUS_TOOL_DIR, "*.lua"))) | \
            set(glob.glob(os.path.join(PROMETHEUS_TOOL_DIR, "*.luac")))

        try:
            result = await asyncio.to_thread(
                _run, [PYTHON_BIN, "pol.py", local_input_name], PROMETHEUS_TOOL_DIR
            )
        except subprocess.TimeoutExpired:
            os.remove(local_input_path)
            return DeobfuscationResult(success=False, message="Timed out running Prometheus deobfuscator.")

        after_files = set(glob.glob(os.path.join(PROMETHEUS_TOOL_DIR, "*.lua"))) | \
            set(glob.glob(os.path.join(PROMETHEUS_TOOL_DIR, "*.luac")))
        new_files = [f for f in (after_files - before_files) if os.path.basename(f) != local_input_name]

        os.remove(local_input_path)

        if new_files:
            output_path = os.path.join(workdir, os.path.basename(new_files[0]))
            shutil.move(new_files[0], output_path)
            for f in new_files[1:]:
                try:
                    os.remove(f)
                except OSError:
                    pass
            return DeobfuscationResult(
                success=True,
                message="Done — deobfuscated output attached.",
                output_path=output_path,
            )

        if result.returncode == 0 and result.stdout.strip():
            output_path = os.path.join(workdir, "deobfuscated_output.txt")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(result.stdout)
            return DeobfuscationResult(
                success=True,
                message="Done — no separate output file was produced, so here's the tool's full log/output.",
                output_path=output_path,
            )

        error_snippet = (result.stderr or result.stdout or "unknown error")[-1500:]
        return DeobfuscationResult(
            success=False,
            message=f"Deobfuscation failed:\n```\n{error_snippet}\n```",
        )


class MoonSecDeobfuscator(PrometheusDeobfuscator):
    # 0x251/Prometheus-Deobfuscator's own README states it also handles
    # MoonSec V2/V3 scripts through the same pipeline, so this just reuses
    # PrometheusDeobfuscator.run() with a different display name.
    name = "MoonSec"
    enabled = True
