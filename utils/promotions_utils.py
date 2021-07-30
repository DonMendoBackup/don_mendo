from utils import admin_roles_utils, message_utils
import datetime
import discord
import os
import ast

from discord_slash.utils.manage_components import create_button, create_actionrow, ButtonStyle, ComponentContext
from dotenv import load_dotenv

load_dotenv()
REGISTER = int(os.getenv('REGISTER_CHANNEL_ID'))
PROMOTE = int(os.getenv('PROMOTE_CHANNEL_ID'))
PROMOTE_DB = int(os.getenv('PROMOTE_CHANNEL_DB_ID'))


def get_promotion_message(promoter: discord.Member, promoter_role: discord.Role,
                          member: discord.Member, new_role: dict):
    role = new_role.get("role")
    points_achieved = admin_roles_utils.get_admin_role(promoter_role.id)
    points_needed = admin_roles_utils.get_admin_role(role.id) * 3
    promotion_complete = points_achieved >= points_needed

    if promotion_complete:
        promotion_title = 'Ascenso logrado con éxito'
    else:
        promotion_title = 'Nueva propuesta de ascenso'

    promotion_embed = discord.Embed(title=promotion_title,
                                    colour=role.color)
    promotion_embed.add_field(name="Miembro propuesto:",
                              value=member.display_name,
                              inline=True)
    promotion_embed.add_field(name="Ascenso a:",
                              value=role.name,
                              inline=True)
    promotion_embed.add_field(name="Puntos para el ascenso:",
                              value="(" + str(points_achieved) + "/" + str(points_needed) + ")",
                              inline=True)
    promotion_embed.add_field(name="Apoyado por:",
                              value=promoter.display_name,
                              inline=False)
    promotion_embed.set_thumbnail(url=new_role.get("promote_image"))

    components = None
    if not promotion_complete:
        promotion_embed.set_footer(text="El apoyo para el ascenso es irrevocable.")
        promotion_id = str(role.id + member.id)
        support_button = [create_button(style=ButtonStyle.green,
                                        label="Apoyar ascenso",
                                        custom_id=promotion_id), ]
        components = [create_actionrow(*support_button)]

    promotion_message = {
        "embed": promotion_embed,
        "components": components
    }

    return promotion_message, promotion_complete


async def store_promotion_db(bot: discord.Client, promoter: discord.Member, promoter_role: discord.Role,
                             member: discord.Member, new_role: discord.Role, created_at: datetime.datetime):
    promotion_id = str(new_role.id + member.id)
    member_id = member.id
    promoters = [promoter.id]
    points_achieved = admin_roles_utils.get_admin_role(promoter_role.id)
    points_needed = admin_roles_utils.get_admin_role(new_role.id) * 3

    promotion_db = discord.Embed(title=promotion_id)
    promotion_db.add_field(name="created_at", value=created_at, inline=False)
    promotion_db.add_field(name="member_id", value=member_id, inline=False)
    promotion_db.add_field(name="new_role_id", value=new_role.id, inline=False)
    promotion_db.add_field(name="promoters", value=promoters, inline=False)
    promotion_db.add_field(name="points_achieved", value=points_achieved, inline=False)
    promotion_db.add_field(name="points_needed", value=points_needed, inline=False)

    channel = bot.get_channel(PROMOTE_DB)
    await channel.send(embed=promotion_db)


async def promotion_exists(bot: discord.Client, new_role_id: int, member_id: int):
    exists = False
    channel = bot.get_channel(PROMOTE_DB)
    promotions = await channel.history().flatten()

    for promotion_partial in promotions:
        msg = await channel.fetch_message(promotion_partial.id)
        promotion = message_utils.get_fields(msg)
        if int(promotion.get("member_id")) == member_id and int(promotion.get("new_role_id")) == new_role_id \
                and int(promotion.get("points_achieved")) < int(promotion.get("points_needed")):
            exists = True
            break

    return exists


async def get_promotion_db(bot: discord.Client, custom_id: str, created_at: datetime.datetime):
    promotion_db = None
    channel = bot.get_channel(PROMOTE_DB)
    promotions = await channel.history().flatten()

    for promotion_partial in promotions:
        promotion_msg = await channel.fetch_message(promotion_partial.id)
        promotion_embed = promotion_msg.embeds[0]
        if promotion_embed.title == custom_id and promotion_embed.fields[0].value == created_at.strftime("%Y-%m-%d %H:%M:%S.%f"):
            promotion_db = promotion_msg

    return promotion_db


async def on_component_promotion(bot: discord.Client, ctx: ComponentContext):
    # Get promotion_embed by primary key
    custom_id = ctx.component.get("custom_id")
    created_at = ctx.origin_message.created_at
    promotion_db = await get_promotion_db(bot, custom_id, created_at)

    # Get promotion info
    promotion = message_utils.get_fields(promotion_db)

    promoter = ctx.guild.get_member(ctx.author_id)
    promoter_role = admin_roles_utils.get_member_admin_role(ctx.guild, promoter)
    promoter_rank = admin_roles_utils.get_admin_role(promoter_role.id)

    member = ctx.guild.get_member(int(promotion.get("member_id")))
    old_role = admin_roles_utils.get_member_admin_role(ctx.guild, member)
    new_role = discord.utils.get(ctx.guild.roles, id=int(promotion.get("new_role_id")))
    new_role_rank = admin_roles_utils.get_admin_role(new_role.id)

    promoters = ast.literal_eval(promotion.get("promoters"))

    # Check if user can support promotion
    if promoter_rank >= new_role_rank:
        if promoter.id not in promoters:
            # Update promotion info
            points_achieved = int(promotion.get("points_achieved")) + promoter_rank
            points_needed = int(promotion.get("points_needed"))
            if points_achieved > points_needed:
                points_achieved = points_needed
            promoters.append(promoter.id)

            # Update promotion in database
            promotion_db_embed = promotion_db.embeds[0]
            promotion_db_embed.set_field_at(index=4,
                                            name="points_achieved",
                                            value=str(points_achieved),
                                            inline=False)
            promotion_db_embed.set_field_at(index=3,
                                            name="promoters",
                                            value=str(promoters),
                                            inline=False)

            await promotion_db.edit(embed=promotion_db_embed)

            # Update promotion in channel
            promotion_msg = ctx.origin_message.embeds[0]
            promotion_msg.set_field_at(index=2,
                                       name="Puntos para el ascenso:",
                                       value="(" + str(points_achieved) + "/" + str(points_needed) + ")",
                                       inline=True)
            supporters = promotion_msg.to_dict()['fields'][3]['value'] + "\n" + promoter.display_name
            promotion_msg.set_field_at(index=3,
                                       name="Apoyado por:",
                                       value=supporters,
                                       inline=False)

            await ctx.origin_message.edit(embed=promotion_msg)

            # Promote member
            if points_achieved == points_needed:
                # Update promotion in channel
                promotion_msg.title = "Ascenso completado"
                await ctx.origin_message.edit(embed=promotion_msg, components=None)

                # Update member roles
                await member.add_roles(new_role)
                await member.remove_roles(old_role)

            await message_utils.answer_interaction(ctx, 'Tu apoyo para el ascenso ha sido registrado correctamente.',
                                                   "Tu nombre debe aparecer en el campo **Apoyado por**.")

        else:
            await message_utils.answer_interaction(ctx, 'Ya has apoyado este ascenso',
                                                   "Solo puedes hacerlo una vez.")

    else:
        await message_utils.answer_interaction(ctx, 'No cumples los requisitos para apoyar el ascenso',
                                               "Consúltalos en el canal: " + bot.get_channel(REGISTER).mention)
