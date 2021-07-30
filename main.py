from utils import admin_roles_utils, games_utils, message_utils, promotions_utils
import discord
import os

from discord_slash import SlashCommand
from discord_slash.context import InteractionContext
from discord_slash.utils.manage_components import wait_for_component, ComponentContext
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = int(os.getenv('GUILD_ID'))
BOT = int(os.getenv('BOT_ID'))
REGISTER = int(os.getenv('REGISTER_CHANNEL_ID'))
PROMOTE = int(os.getenv('PROMOTE_CHANNEL_ID'))
PROMOTE_DB = int(os.getenv('PROMOTE_CHANNEL_DB_ID'))

bot = discord.Client(intents=discord.Intents.all())
slash = SlashCommand(bot, sync_commands=True)


@slash.slash(name='register', description='Completa tu registro en el servidor', guild_ids=[GUILD])
async def register(ctx):
    try:
        user = ctx.guild.get_member(ctx.author.id)

        if len(user.roles) == 1:
            # Default roles
            default_role = discord.utils.get(ctx.guild.roles, id=int(os.getenv('ROLE_ADMIN_0_ID')))
            admin_separator = discord.utils.get(ctx.guild.roles, id=int(os.getenv('ROLE_CONF_ADMIN')))
            games_separator = discord.utils.get(ctx.guild.roles, id=int(os.getenv('ROLE_CONF_GAMES')))
            await user.add_roles(default_role)
            await user.add_roles(admin_separator)
            await user.add_roles(games_separator)

            games_embed = discord.Embed(title='Elige aquellos videojuegos que te interesen:',
                                        colour=games_separator.color)
            games_action_row = games_utils.get_games_select()
            await ctx.send(embed=games_embed, components=[games_action_row], hidden=True)
            game_roles: InteractionContext = await wait_for_component(bot, components=games_action_row, timeout=120)

            # Game roles
            if "Ninguno" not in game_roles.selected_options:
                for role in game_roles.selected_options:
                    guild_role = discord.utils.get(ctx.guild.roles, name=role)
                    await user.add_roles(guild_role)

            await message_utils.answer_interaction(game_roles, 'Tu registro se ha completado con éxito',
                                                   'Tu rol actual de **administración** es:\n• ' + default_role.name + "\n" +
                                                   "\nTus roles actuales de **videojuegos** son:  "
                                                   + message_utils.list_to_bullet_list(game_roles.selected_options))

        else:
            await message_utils.answer_interaction(ctx, 'Ya estás registrado en el servidor.',
                                                   'Comprueba si has utilizado el comando correcto.')

    except Exception as e:
        await message_utils.answer_interaction(ctx, 'Se ha producido un error al registrarte. '
                                                    'Comunica el siguiente mensaje al administrador:', str(e))


@slash.slash(name='games', description='Modifica tus roles de videojuegos', guild_ids=[GUILD])
async def games(ctx):
    try:
        user = ctx.guild.get_member(ctx.author.id)
        games_separator = discord.utils.get(ctx.guild.roles, id=int(os.getenv('ROLE_CONF_GAMES')))
        await user.add_roles(games_separator)

        games_embed = discord.Embed(title='Elige aquellos videojuegos que te interesen:', colour=games_separator.color)
        games_action_row = games_utils.get_games_select()
        await ctx.send(embed=games_embed, components=[games_action_row], hidden=True)
        game_roles: InteractionContext = await wait_for_component(bot, components=games_action_row, timeout=120)

        if "Ninguno" not in game_roles.selected_options:
            for game in games_utils.get_games_list():
                guild_role = discord.utils.get(ctx.guild.roles, name=game)
                if game in game_roles.selected_options:
                    if guild_role not in user.roles:
                        await user.add_roles(guild_role)
                else:
                    if guild_role in user.roles:
                        await user.remove_roles(guild_role)

        else:
            for game in games_utils.get_games_list():
                guild_role = discord.utils.get(ctx.guild.roles, name=game)
                if guild_role in user.roles:
                    await user.remove_roles(guild_role)

        await message_utils.answer_interaction(game_roles, 'Tus videojuegos han sido actualizados con éxito.',
                                               "Tus roles actuales de **videojuegos** son:  " + message_utils.list_to_bullet_list(
                                                   game_roles.selected_options),
                                               games_separator.color)

    except Exception as e:
        await message_utils.answer_interaction(ctx, 'Se ha producido un error al actualizar tus roles. '
                                                    'Comunica el siguiente mensaje al administrador:', str(e))


@slash.slash(name='promote', description='Asciende a un miembro de rango inferior', guild_ids=[GUILD])
async def promote(ctx: InteractionContext, member: discord.Member):
    try:
        promoter = ctx.author
        promoter_role = admin_roles_utils.get_member_admin_role(ctx.guild, promoter)
        old_role = admin_roles_utils.get_member_admin_role(ctx.guild, member)

        if promoter_role is not None and old_role is not None:
            if admin_roles_utils.get_admin_role(promoter_role.id) > admin_roles_utils.get_admin_role(old_role.id):
                channel = bot.get_channel(PROMOTE)
                new_role = admin_roles_utils.get_next_admin_role(ctx.guild, old_role)
                prom_exists = await promotions_utils.promotion_exists(bot, new_role.get("role").id, member.id)

                if not prom_exists:
                    promotion_message, promotion_complete = promotions_utils.get_promotion_message(promoter,
                                                                                                   promoter_role,
                                                                                                   member, new_role)

                    if promotion_complete:
                        await member.add_roles(new_role.get("role"))
                        await member.remove_roles(old_role)
                        msg = await channel.send(embed=promotion_message.get("embed"))

                    else:
                        msg = await channel.send(embed=promotion_message.get("embed"),
                                                 components=promotion_message.get("components"))

                    await promotions_utils.store_promotion_db(bot, promoter, promoter_role, member,
                                                              new_role.get("role"),
                                                              msg.created_at)

                    await message_utils.answer_interaction(ctx, "Propuesta de promoción ejecutada con éxito.",
                                                           "Consulta el canal:  " + bot.get_channel(PROMOTE).name)

                else:
                    await message_utils.answer_interaction(ctx, "Ya existe una promoción activa para ese miembro.",
                                                           "Comprueba que no te has equivocado de usuario.")

            else:
                await message_utils.answer_interaction(ctx, 'No puedes proponer un ascenso para ese miembro.',
                                                       "Consulta los requisitos en el canal: " + bot.get_channel(
                                                           REGISTER).name)
        else:
            await message_utils.answer_interaction(ctx, 'No puedes proponer un ascenso para ese miembro.',
                                                   "Consulta los requisitos en el canal: " + bot.get_channel(
                                                       REGISTER).name)

    except Exception as e:
        await message_utils.answer_interaction(ctx, 'Se ha producido un error al proponer el ascenso del miembro. '
                                                    'Comunica el siguiente mensaje al administrador:', str(e))


@bot.event
async def on_component(ctx: ComponentContext):
    if ctx.channel_id == PROMOTE:
        await promotions_utils.on_component_promotion(bot, ctx)


@bot.event
async def on_message(message):
    if message.channel.id == REGISTER and message.author.id != BOT:
        await message.delete()


@bot.event
async def on_ready():
    print('Ready!')


bot.run(TOKEN)
