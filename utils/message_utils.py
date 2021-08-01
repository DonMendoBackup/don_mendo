import discord
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
LOG = int(os.getenv('LOG_CHANNEL_ID'))


def list_to_bullet_list(list_to_convert: list):
    list_str = ""
    for i in range(len(list_to_convert)):
        list_str = list_str + "\n• " + list_to_convert[i]

    return list_str


async def answer_interaction(ctx, title: str, description: str, colour=discord.Colour.from_rgb(158, 200, 204)):
    embed = discord.Embed(title=title, description=description, colour=colour)
    await ctx.send(embed=embed, hidden=True)


async def log_interaction(bot: discord.Client, user: discord.Member, action: str):
    channel = bot.get_channel(LOG)
    log_embed = discord.Embed(title=action)
    log_embed.add_field(name="user_id", value=user.id, inline=False)
    log_embed.add_field(name="interacted_at", value=datetime.now(), inline=False)
    await channel.send(embed=log_embed)


def get_fields(message: discord.Message):
    embed_dict = {}
    fields = message.embeds[0].to_dict()["fields"]
    for field in fields:
        embed_dict[field['name']] = field['value']

    return embed_dict
