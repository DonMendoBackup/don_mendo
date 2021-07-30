import os
import discord
from dotenv import load_dotenv

load_dotenv()


def get_admin_roles():
    admin_roles = {
        int(os.getenv('ROLE_ADMIN_0_ID')): 0,
        int(os.getenv('ROLE_ADMIN_1_ID')): 1,
        int(os.getenv('ROLE_ADMIN_2_ID')): 2,
        int(os.getenv('ROLE_ADMIN_3_ID')): 3,
    }

    return admin_roles


def get_admin_roles_reversed():
    admin_roles_reversed = {
        0: {
            "role_id": int(os.getenv('ROLE_ADMIN_0_ID')),
            "promote_image": None,
        },
        1: {
            "role_id": int(os.getenv('ROLE_ADMIN_1_ID')),
            "promote_image": "https://i.imgur.com/gAaoZQO.png",
        },
        2: {
            "role_id": int(os.getenv('ROLE_ADMIN_2_ID')),
            "promote_image": "https://i.imgur.com/P4rz7cb.png",
        },
        3: {
            "role_id": int(os.getenv('ROLE_ADMIN_3_ID')),
            "promote_image": "https://i.imgur.com/5GNS4Zg.png",
        },
    }

    return admin_roles_reversed


def get_admin_role(admin_role_id: int):
    return get_admin_roles().get(admin_role_id)


def get_member_admin_role(guild: discord.Guild, member: discord.Member):
    member_admin_role = None

    for role_id in get_admin_roles():
        admin_role = discord.utils.get(guild.roles, id=role_id)
        if admin_role in member.roles:
            member_admin_role = admin_role
            break

    return member_admin_role


def get_next_admin_role(guild: discord.Guild, old_role: discord.Role):
    next_role_rank = get_admin_roles().get(old_role.id) + 1
    next_role_entry = get_admin_roles_reversed().get(next_role_rank)
    role = discord.utils.get(guild.roles, id=next_role_entry.get("role_id"))
    promote_image = next_role_entry.get("promote_image")

    next_role = {
        "role": role,
        "promote_image": promote_image
    }

    return next_role
