from utils import admin_roles_utils, message_utils
import datetime
import discord
import os
import ast

from discord_slash.utils.manage_components import create_button, create_actionrow, ButtonStyle, ComponentContext
from dotenv import load_dotenv

load_dotenv()
SUGGEST_DB = int(os.getenv('SUGGEST_CHANNEL_DB_ID'))


def get_suggestion_message(suggester: discord.Member, title: str, description: str):
    suggestion_embed = discord.Embed(title=title,
                                     description=description,
                                     colour=discord.Colour.dark_blue())
    suggestion_embed.add_field(name="Buena",
                               value=str(0),
                               inline=True)
    suggestion_embed.add_field(name="Normal",
                               value=str(0),
                               inline=True)
    suggestion_embed.add_field(name="Mala",
                               value=str(0),
                               inline=True)
    suggestion_embed.set_footer(text="Puedes cambiar tu decisión en cualquier momento.")
    suggestion_embed.set_author(name=suggester.display_name, icon_url=suggester.avatar_url)
    suggestion_embed.set_thumbnail(url="https://i.imgur.com/8s0um1f.png")

    suggestion_buttons = [
        create_button(style=ButtonStyle.green,
                      label="¡Buena idea!",
                      custom_id=str(suggester.id) + "_G"),
        create_button(style=ButtonStyle.grey,
                      label="Ok.",
                      custom_id=str(suggester.id) + "_N"),
        create_button(style=ButtonStyle.red,
                      label="¡Es horrible!",
                      custom_id=str(suggester.id) + "_B"),
    ]
    components = [create_actionrow(*suggestion_buttons)]

    suggestion_message = {
        "embed": suggestion_embed,
        "components": components
    }

    return suggestion_message


async def store_suggestion_db(bot: discord.Client, suggester: discord.Member, title: str, description: str,
                              suggestion_type: str, created_at: datetime.datetime):
    suggestion_db = discord.Embed(title=str(suggester.id))
    suggestion_db.add_field(name="created_at", value=created_at, inline=False)
    suggestion_db.add_field(name="type", value=suggestion_type, inline=False)
    suggestion_db.add_field(name="title", value=title, inline=False)
    suggestion_db.add_field(name="description", value=description, inline=False)
    suggestion_db.add_field(name="good", value="[]", inline=False)
    suggestion_db.add_field(name="normal", value="[]", inline=False)
    suggestion_db.add_field(name="bad", value="[]", inline=False)

    channel = bot.get_channel(SUGGEST_DB)
    await channel.send(embed=suggestion_db)


async def get_suggestion_db(bot: discord.Client, custom_id: str, created_at: datetime.datetime):
    suggestion_db = None
    channel = bot.get_channel(SUGGEST_DB)
    suggestions = await channel.history().flatten()

    for suggestion_partial in suggestions:
        suggestion_msg = await channel.fetch_message(suggestion_partial.id)
        suggestion_embed = suggestion_msg.embeds[0]
        if suggestion_embed.title == custom_id and suggestion_embed.fields[0].value == created_at.strftime(
                "%Y-%m-%d %H:%M:%S.%f"):
            suggestion_db = suggestion_msg

    return suggestion_db


async def on_component_suggestion(bot: discord.Client, ctx: ComponentContext):
    # Get suggestion_embed by primary key
    custom_id_button = ctx.component.get("custom_id")
    custom_id = custom_id_button.split("_")[0]
    created_at = ctx.origin_message.created_at
    suggestion_db = await get_suggestion_db(bot, custom_id, created_at)

    # Get suggestion info
    suggestion = message_utils.get_fields(suggestion_db)

    member = ctx.guild.get_member(ctx.author_id)

    good_members = ast.literal_eval(suggestion.get("good"))
    good = len(good_members)
    normal_members = ast.literal_eval(suggestion.get("normal"))
    normal = len(normal_members)
    bad_members = ast.literal_eval(suggestion.get("bad"))
    bad = len(bad_members)

    action = custom_id_button.split("_")[1]

    # Check if user can do action and update values
    voted = False

    if action == "G":
        if member.id not in good_members:
            voted = True
            good_members.append(member.id)
            good = good + 1
            if member.id in normal_members:
                normal_members.remove(member.id)
                normal = normal - 1
            if member.id in bad_members:
                bad_members.remove(member.id)
                bad = bad - 1
        else:
            await message_utils.answer_interaction(ctx, 'Ya has votado de esta forma esta sugerencia antes.',
                                                   "Comprueba que no te has equivocado de botón.")
    elif action == "N":
        if member.id not in normal_members:
            voted = True
            normal_members.append(member.id)
            normal = normal + 1
            if member.id in good_members:
                good_members.remove(member.id)
                good = good - 1
            if member.id in bad_members:
                bad_members.remove(member.id)
                bad = bad - 1
        else:
            await message_utils.answer_interaction(ctx, 'Ya has votado de esta forma esta sugerencia antes.',
                                                   "Comprueba que no te has equivocado de botón.")
    elif action == "B":
        if member.id not in bad_members:
            voted = True
            bad_members.append(member.id)
            bad = bad + 1
            if member.id in normal_members:
                normal_members.remove(member.id)
                normal = normal - 1
            if member.id in good_members:
                good_members.remove(member.id)
                good = good - 1
        else:
            await message_utils.answer_interaction(ctx, 'Ya has votado de esta forma esta sugerencia antes.',
                                                   "Comprueba que no te has equivocado de botón.")

    if voted:
        # Update suggestion in database
        suggestion_db_embed = suggestion_db.embeds[0]
        suggestion_db_embed.set_field_at(index=4,
                                         name="good",
                                         value=str(good_members),
                                         inline=False)
        suggestion_db_embed.set_field_at(index=5,
                                         name="normal",
                                         value=str(normal_members),
                                         inline=False)
        suggestion_db_embed.set_field_at(index=6,
                                         name="bad",
                                         value=str(bad_members),
                                         inline=False)

        await suggestion_db.edit(embed=suggestion_db_embed)

        # Update suggestion in channel
        suggestion_msg = ctx.origin_message.embeds[0]
        suggestion_msg.set_field_at(index=0,
                                    name="Buena",
                                    value=str(good),
                                    inline=True)
        suggestion_msg.set_field_at(index=1,
                                    name="Normal",
                                    value=str(normal),
                                    inline=True)
        suggestion_msg.set_field_at(index=2,
                                    name="Mala",
                                    value=str(bad),
                                    inline=True)

        await ctx.origin_message.edit(embed=suggestion_msg)

        await message_utils.answer_interaction(ctx, 'Tu voto para la sugerencia ha sido registrado correctamente.',
                                               "Puedes comprobar como han cambiado los valores.")
