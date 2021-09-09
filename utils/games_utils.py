from discord_slash.utils.manage_components import create_select, create_select_option, create_actionrow


def get_games_list():
    games_list = [
        "Among Us",
        "Cookie Clicker",
        "Dead by Deadlight",
        "Genshin Impact",
        "League of Legends",
        "Phasmophobia",
        "Pokémon"
    ]

    return games_list


def get_games_select():
    game_options = [
        create_select_option("Ninguno", value="Ninguno", emoji="❌"),
        create_select_option("Among Us", value="Among Us", emoji="🐁"),
        create_select_option("Cookie Clicker", value="Cookie Clicker", emoji="🍪"),
        create_select_option("Dead by Deadlight", value="Dead by Deadlight", emoji="🔪"),
        create_select_option("Genshin Impact", value="Genshin Impact", emoji="🌕"),
        create_select_option("League of Legends", value="League of Legends", emoji="👊"),
        create_select_option("Phasmophobia", value="Phasmophobia", emoji="👻"),
        create_select_option("Pokémon", value="Pokémon", emoji="🐌"),
    ]
    games_select = create_select(
        options=game_options,
        placeholder="Selecciona todos los roles que quieras",
        min_values=1,
        max_values=len(game_options),
    )
    games_action_row = create_actionrow(games_select)

    return games_action_row
