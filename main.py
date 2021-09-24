from utils import admin_roles_utils, games_utils, message_utils, promotions_utils, suggestions_utils
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
SUGGEST = int(os.getenv('SUGGEST_CHANNEL_ID'))
SUGGEST_THEME = int(os.getenv('SUGGEST_THEME_CHANNEL_ID'))

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


@slash.slash(name='games_add', description='Únete a los videojuegos que te interesen', guild_ids=[GUILD])
async def games_add(ctx):
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

        await message_utils.answer_interaction(game_roles, 'Tus videojuegos han sido actualizados con éxito.',
                                               "Tus roles actuales de **videojuegos** son:  " + message_utils.list_to_bullet_list(
                                                   game_roles.selected_options),
                                               games_separator.color)

    except Exception as e:
        await message_utils.answer_interaction(ctx, 'Se ha producido un error al actualizar tus roles. '
                                                    'Comunica el siguiente mensaje al administrador:', str(e))


@slash.slash(name='games_remove', description='Deja los videojuegos que no te interesen', guild_ids=[GUILD])
async def games_remove(ctx):
    try:
        user = ctx.guild.get_member(ctx.author.id)
        games_separator = discord.utils.get(ctx.guild.roles, id=int(os.getenv('ROLE_CONF_GAMES')))
        await user.add_roles(games_separator)

        games_embed = discord.Embed(title='Elige aquellos videojuegos que NO te interesen:', colour=games_separator.color)
        games_action_row = games_utils.get_games_select()
        await ctx.send(embed=games_embed, components=[games_action_row], hidden=True)
        game_roles: InteractionContext = await wait_for_component(bot, components=games_action_row, timeout=120)

        if "Ninguno" not in game_roles.selected_options:
            for game in games_utils.get_games_list():
                guild_role = discord.utils.get(ctx.guild.roles, name=game)
                if game in game_roles.selected_options:
                    if guild_role not in user.roles:
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
                                                           "Consulta el canal:  " + bot.get_channel(PROMOTE).mention)

                else:
                    await message_utils.answer_interaction(ctx, "Ya existe una promoción activa para ese miembro.",
                                                           "Comprueba que no te has equivocado de usuario.")

            else:
                await message_utils.answer_interaction(ctx, 'No puedes proponer un ascenso para ese miembro.',
                                                       "Consulta los requisitos en el canal: " + bot.get_channel(
                                                           REGISTER).mention)
        else:
            await message_utils.answer_interaction(ctx, 'No puedes proponer un ascenso para ese miembro.',
                                                   "Consulta los requisitos en el canal: " + bot.get_channel(
                                                       REGISTER).mention)

    except Exception as e:
        await message_utils.answer_interaction(ctx, 'Se ha producido un error al proponer el ascenso del miembro. '
                                                    'Comunica el siguiente mensaje al administrador:', str(e))


@slash.slash(name='suggest', description='Realiza una sugerencia para el servidor', guild_ids=[GUILD])
async def suggest(ctx: InteractionContext, title: str, description: str):
    try:
        suggester = ctx.author
        channel = bot.get_channel(SUGGEST)
        suggestion_message = suggestions_utils.get_suggestion_message(suggester, title, description)

        msg = await channel.send(embed=suggestion_message.get("embed"), components=suggestion_message.get("components"))
        await suggestions_utils.store_suggestion_db(bot, suggester, title, description, "general", msg.created_at)
        await message_utils.answer_interaction(ctx, "Tu sugerencia ha sido creada con éxito.",
                                               "Consulta el canal:  " + channel.mention)

    except Exception as e:
        await message_utils.answer_interaction(ctx, 'Se ha producido un error al crear tu sugerencia. '
                                                    'Comunica el siguiente mensaje al administrador:', str(e))


@slash.slash(name='suggest_theme', description='Realiza una sugerencia de temática para el servidor', guild_ids=[GUILD])
async def suggest_theme(ctx: InteractionContext, title: str, description: str):
    try:
        suggester = ctx.author
        suggester_role = admin_roles_utils.get_member_admin_role(ctx.guild, suggester)
        rank = admin_roles_utils.get_admin_role(suggester_role.id)

        if rank > 0:
            channel = bot.get_channel(SUGGEST_THEME)
            suggestion_message = suggestions_utils.get_suggestion_message(suggester, title, description)

            msg = await channel.send(embed=suggestion_message.get("embed"),
                                     components=suggestion_message.get("components"))
            await suggestions_utils.store_suggestion_db(bot, suggester, title, description, "theme", msg.created_at)
            await message_utils.answer_interaction(ctx, "Tu sugerencia ha sido creada con éxito.",
                                                   "Consulta el canal:  " + channel.mention)
        else:
            await message_utils.answer_interaction(ctx, "No tienes suficiente rango para hacer este tipo de "
                                                        "sugerencia.",
                                                   "Consulta los requisitos en el canal:  "
                                                   + bot.get_channel(REGISTER).mention)

    except Exception as e:
        await message_utils.answer_interaction(ctx, 'Se ha producido un error al crear tu sugerencia. '
                                                    'Comunica el siguiente mensaje al administrador:', str(e))


# Uncomment to add info to server
# @slash.slash(name='welcome', description='Canal de bienvenida', guild_ids=[GUILD])
# async def welcome(ctx):
#     channel = bot.get_channel(REGISTER)
#     general_embed = discord.Embed(title="Información general",
#                                   colour=discord.Colour.dark_grey())
#     general_embed.add_field(name="Registro",
#                             value="Para acceder al resto de canales tienes primero que registrarte utilizando el "
#                                   "comando **/register**.\nDurante el registro podrás seleccionar los temas "
#                                   "disponibles que te interesen.\nAdemás se te asignará un rol correspondiente al "
#                                   "rango 0 del servidor, pero no te preocupes, puedes ascender.\n",
#                             inline=False)
#     general_embed.add_field(name="Videojuegos",
#                             value="Si quieres modificar los videojuegos que te interesan, puedes hacerlo utilizando el "
#                                   "comando **/games**.\n",
#                             inline=False)
#     general_embed.set_thumbnail(url="https://i.imgur.com/d45GUg7.png")
#     await channel.send(embed=general_embed)
#
#     promotions_embed = discord.Embed(title="Sistema de ascensos",
#                                      colour=discord.Colour.dark_grey())
#     promotions_embed.add_field(name="Cómo funciona",
#                                value="Para ascender de rango, lo primero que será necesario es que un miembro con "
#                                      "rango superior proponga tu ascenso.\nTras esto, necesitarás conseguir los puntos "
#                                      "necesarios con el apoyo de otros miembros para completarlo.\n",
#                                inline=False)
#     promotions_embed.add_field(name="Cómo proponer un ascenso",
#                                value="Si quieres proponer el ascenso de un miembro, puedes hacerlo utilizando el "
#                                      "comando **/promote** seguido de una mención al miembro en cuestión.\nPor "
#                                      "ejemplo:  **/promote @DonMendo**\n",
#                                inline=False)
#     promotions_embed.add_field(name="Cuántos puntos es un apoyo",
#                                value="Cada miembro dará con su apoyo tantos puntos como el rango al que pertenezca. "
#                                      "Eso sí, para apoyarte, será necesario que tenga un rango superior al tuyo.\n",
#                                inline=False)
#     promotions_embed.set_thumbnail(url="https://i.imgur.com/HO3OfyS.png")
#     await channel.send(embed=promotions_embed)
#
#     suggestions_embed = discord.Embed(title="Sistema de sugerencias",
#                                       colour=discord.Colour.from_rgb(255, 163, 70))
#     suggestions_embed.add_field(name="Sugerencias generales",
#                                 value="Si tienes alguna sugerencia para mejorar el servidor, puedes hacerlo utilizando "
#                                       "el comando **/suggest** seguido de un título y una descripción.\nPor ejemplo:  "
#                                       "**/suggest Nueva sugerencia Esto es una sugerencia**\nEstas sugerencias pueden "
#                                       "ser valoradas por cualquier miembro registrado del servidor.\n",
#                                 inline=False)
#     suggestions_embed.add_field(name="Sugerencias de temática",
#                                 value="Cada cierto tiempo el servidor cambia de temática. Para sugerir una es "
#                                       "necesario que tengas un rango superior al 0. Puedes realizar este tipo de "
#                                       "sugerencias utilizando el comando **/suggest_theme** seguido de un título y una "
#                                       "descripción. \nEstas sugerencias pueden ser valoradas por cualquier miembro "
#                                       "registrado del servidor con un rango superior a 0.\n",
#                                 inline=False)
#     suggestions_embed.set_thumbnail(url="https://i.imgur.com/kKMGg39.png")
#     await channel.send(embed=suggestions_embed)


@bot.event
async def on_component(ctx: ComponentContext):
    if ctx.channel_id == PROMOTE:
        await promotions_utils.on_component_promotion(bot, ctx)
    elif ctx.channel_id == SUGGEST or ctx.channel_id == SUGGEST_THEME:
        await suggestions_utils.on_component_suggestion(bot, ctx)


@bot.event
async def on_message(message):
    if (message.channel.id == REGISTER or message.channel.id == PROMOTE or message.channel.id == SUGGEST or message
            .channel.id == SUGGEST_THEME) and message.author.id != BOT:
        await message.delete()


@bot.event
async def on_ready():
    print('Ready!')


bot.run(TOKEN)
