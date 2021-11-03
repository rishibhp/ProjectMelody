import discord

# TODO: Move to a separate file
TOKEN = "OTA1NDk2NzMzMDE3MDU1MzIy.YYK7jA.gMwm60xlrtLscfh77_rPMeMZg0k"
GUILD_NAME = "MelodyTest"

client = discord.Client()


@client.event
async def on_ready():
    print(f'{client.user} has connected to discord!')
    print([guild.name for guild in client.guilds])

    for guild in client.guilds:
        if guild.name == GUILD_NAME:
            break

    print(
        f"{client.user} is connected to the following guilds:\n"
        f"{guild.name}(id: {guild.id})"
    )


client.run(TOKEN)
