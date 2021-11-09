from discord.ext import commands
from Music import Music

# TODO: Move to a separate file
TOKEN = "OTA1NDk2NzMzMDE3MDU1MzIy.YYK7jA.gMwm60xlrtLscfh77_rPMeMZg0k"
GUILD_NAME = "MelodyTest"


bot = commands.Bot(command_prefix="!")

bot.add_cog(Music(bot))

bot.run(TOKEN)
