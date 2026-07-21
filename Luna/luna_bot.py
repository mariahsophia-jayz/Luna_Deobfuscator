import os
import tempfile

import discord
from discord import app_commands
from discord.ext import commands

from deobfuscators import REGISTRY

DISCORD_BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN", "")
MAX_FILE_SIZE_BYTES = 2 * 1024 * 1024  # 2 MB

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Luna is online as {bot.user} (id: {bot.user.id})")
    for key, plugin in REGISTRY.items():
        status = "enabled" if plugin.enabled else "coming soon"
        print(f"  - {plugin.name} ({key}): {status}")


OBFUSCATOR_CHOICES = [
    app_commands.Choice(name=plugin.name, value=key)
    for key, plugin in REGISTRY.items()
]


@bot.tree.command(name="deobfuscate", description="Deobfuscate a Lua script")
@app_commands.describe(obfuscator="Which obfuscator was used", file="The obfuscated .lua file")
@app_commands.choices(obfuscator=OBFUSCATOR_CHOICES)
async def deobfuscate(interaction: discord.Interaction, obfuscator: app_commands.Choice[str], file: discord.Attachment):
    plugin = REGISTRY[obfuscator.value]

    if not file.filename.lower().endswith(".lua"):
        await interaction.response.send_message("Please attach a `.lua` file.", ephemeral=True)
        return

    if file.size > MAX_FILE_SIZE_BYTES:
        await interaction.response.send_message("File too large — max 2 MB.", ephemeral=True)
        return

    if not plugin.enabled:
        await interaction.response.send_message(
            f"**{plugin.name}** support isn't available yet — coming soon.", ephemeral=True
        )
        return

    await interaction.response.defer(thinking=True)

    with tempfile.TemporaryDirectory() as workdir:
        input_path = os.path.join(workdir, "input.lua")
        await file.save(input_path)

        result = await plugin.run(input_path, workdir)

        if result.success and result.output_path:
            await interaction.followup.send(
                content=f"[{plugin.name}] {result.message}",
                file=discord.File(result.output_path),
            )
        else:
            await interaction.followup.send(content=f"[{plugin.name}] {result.message}")


@bot.command(name="ping")
async def ping(ctx: commands.Context):
    await ctx.reply("pong — Luna is awake")


if __name__ == "__main__":
    if not DISCORD_BOT_TOKEN:
        raise SystemExit("Set the DISCORD_BOT_TOKEN environment variable before running.")
    bot.run(DISCORD_BOT_TOKEN)
