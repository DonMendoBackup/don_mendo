import os

from dotenv import load_dotenv
import discord
from discord_slash.context import InteractionContext
from discord_slash import SlashCommand
from discord_slash.utils.manage_components import create_select, create_select_option, create_actionrow, \
    wait_for_component

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = int(os.getenv('GUILD_ID'))
BOT = int(os.getenv('BOT_ID'))

bot = discord.Client(intents=discord.Intents.all())
slash = SlashCommand(bot, sync_commands=True)

game_list = ["League of Legends", "Dead by Deadlight", "Genshin Impact", "Pokémon", "Phasmophobia", "Among Us"]

game_options = [
    create_select_option("Ninguno", value="Ninguno", emoji="❌"),
    create_select_option("League of Legends", value="League of Legends", emoji="👊"),
    create_select_option("Dead by Deadlight", value="Dead by Deadlight", emoji="🔪"),
    create_select_option("Genshin Impact", value="Genshin Impact", emoji="🌕"),
    create_select_option("Pokémon", value="Pokémon", emoji="🐌"),
    create_select_option("Phasmophobia", value="Phasmophobia", emoji="👻"),
    create_select_option("Among Us", value="Among Us", emoji="🐁"),
]

games_select = create_select(
    options=game_options,
    placeholder="Selecciona todos los roles que quieras",
    min_values=1,
    max_values=len(game_options),
)

games_action_row = create_actionrow(games_select)


@slash.slash(name='register', description='Completa tu registro en el servidor', guild_ids=[GUILD])
async def register(ctx):
    try:
        guild = bot.get_guild(GUILD)
        user = guild.get_member(ctx.author.id)

        if len(user.roles) == 1:
            await ctx.send('Roles relacionados con juegos:', components=[games_action_row], hidden=True)
            game_roles: InteractionContext = await wait_for_component(bot, components=games_action_row, timeout=120)

            # Default roles
            default_role = discord.utils.get(guild.roles, name='LIL KONGS')
            admin_separator = discord.utils.get(guild.roles, name='━━━━ Administración ━━━━━')
            games_separator = discord.utils.get(guild.roles, name='━━━━━ Videojuegos ━━━━━')
            await user.add_roles(default_role)
            await user.add_roles(admin_separator)
            await user.add_roles(games_separator)

            # Game roles
            if "Ninguno" not in game_roles.selected_options:
                for role in game_roles.selected_options:
                    guild_role = discord.utils.get(guild.roles, name=role)
                    await user.add_roles(guild_role)

            await game_roles.send(user.name + ', tus roles han sido asignados con éxito.', hidden=True)

        else:
            await ctx.send('Ya estás registrado en el servidor.', hidden=True)

    except Exception as e:
        await ctx.send('Se ha producido un error al registrarte. Comunica el siguiente mensaje al administrador:',
                       hidden=True)
        await ctx.send(str(e), hidden=True)


@slash.slash(name='games', description='Modifica tus roles de juegos', guild_ids=[GUILD])
async def games(ctx):
    try:
        guild = bot.get_guild(GUILD)
        user = guild.get_member(ctx.author.id)
        games_separator = discord.utils.get(guild.roles, name='━━━━━ Videojuegos ━━━━━')
        await user.add_roles(games_separator)

        await ctx.send('Elige aquellos juegos que te interesen:', components=[games_action_row], hidden=True)
        game_roles: InteractionContext = await wait_for_component(bot, components=games_action_row, timeout=120)

        if "Ninguno" not in game_roles.selected_options:
            for game in game_list:
                guild_role = discord.utils.get(guild.roles, name=game)
                if game in game_roles.selected_options:
                    if guild_role not in user.roles:
                        await user.add_roles(guild_role)
                else:
                    if guild_role in user.roles:
                        await user.remove_roles(guild_role)

        else:
            for game in game_list:
                guild_role = discord.utils.get(guild.roles, name=game)
                if guild_role in user.roles:
                    await user.remove_roles(guild_role)

        await game_roles.send(user.name + ', tus roles han sido actualizados con éxito.', hidden=True)

    except Exception as e:
        await ctx.send(
            'Se ha producido un error al actualizar tus roles. Comunica el siguiente mensaje al administrador:',
            hidden=True)
        await ctx.send(str(e), hidden=True)


@bot.event
async def on_message(message):
    if message.channel.name == '📜𝐑𝐞𝐠𝐢𝐬𝐭𝐫𝐨' and message.author.id != BOT:
        await message.delete()


@bot.event
async def on_ready():
    print('Ready!')


bot.run(TOKEN)
