import json

import disnake

color = 0x2b2d31
long_slash = "—"

with open("./tools/config.json", "r") as f:
    emoji = json.load(f)["emoji"]


def welcome_ticket():
    embed = disnake.Embed(color=color, title="Тикеты",
                          description="В тикетах вы можете напрямую обратиться к администрации по следующим вопросам:")

    embed.add_field(name=" ",
                    value="- Жалобы на игрока, гриферство или кражу\n"
                          "- Задать вопрос\n"
                          "- Запросить доступ к закрытому каналу с обновлениями (если у вас есть Bloomy Plus)\n"
                          "- Сообщить о баге и возможно получить за это вознаграждение\n"
                          "- Попросить откат инвентаря после смерти\n"
                          "- Сменить ник с переносом данных со старого аккаунта на новый\n"
                          "- Попросить помощи с оплатой из  другой страны\n"
                          "- Попросить помощи с проблемой оплаты\n"
                          "```yaml\n"
                          "Соблюдение правил в тикетах обязательно!\n"
                          "```", inline=False)

    embed.set_image(url="https://i.imgur.com/noCEmiC.png")

    embed.set_footer(text="Версия: 0.1")

    return embed


def warning_get_plus():
    embed = disnake.Embed(color=color, description=f"# {emoji['error']} Внимание!")

    embed.add_field(name="",
                    value=f">>> Роль выдается только вы покупали Bloomy+ **НАВСЕГДА**, если вы\nпокупали на месяц, то в таком случаи роль не выдаётся!",
                    inline=False)
    embed.add_field(name=" ",
                    value="```Для получения роли необходимо отправить чек о покупке\nэтой привилегии в тикет. В противном случае мы можем не\nпроверить ваш тикет.```")

    return embed


def warning_bug():
    embed = disnake.Embed(color=color, description=f"# {emoji['error']} Внимание!")
    embed.add_field(name="",
                    value="При публикации бага не нужно указывать, какое вознаграждение вы хотите получить за его нахождение.\n"
                          "Также рекомендуем прикреплять фото или видео, демонстрирующие баг.\n\n>>> Обратите внимание, что мы не будем уведомлять вас о процессе фикса бага.",
                    inline=False)

    return embed


def warning_inventory():
    embed = disnake.Embed(color=color, description=f"# {emoji['error']} Внимание!")
    embed.add_field(name="",
                    value=f"Мы откатываем вещи только по следующим причинам:\n"
                          f"- Смерть из-за бага или проблема с тпс\n"
                          f"- Смерть от незаконного убийства игрока\n"
                          f"- Смерть из-за непредвиденного обстоятельства (например от отката сервера)\n"
                          f">>> Если причина смерти не является одной из перечисленных или вы\nзапрашивали откаты больше трёх раз за неделю, то мы можем отказать\nоткатывать ваши вещи.",
                    inline=False)

    return embed


def warning_change_name():
    embed = disnake.Embed(color=color, title="", description=f"# {emoji['error']} Внимание!")
    embed.add_field(name="",
                    value="\n\nПри смене ника мы можем перенести с вашего старого аккаунта следующие данные:\n"
                          "- Вещи из инвентаря и эндер-сундука\n"
                          "- Вашу активную медаль, доступные темы для ника, и блуми плюс (при наличии)\n\n"
                          f">>> Обратите внимание, что мы не сможем перенести ваше наигранное время.\nПоэтому вам придётся заново наиграть 5 часов, чтобы открывать любые\nсундуки, поставленные не вами.",
                    inline=False)

    return embed


def ticket_complaint(user, nick, nick_complaint, reason, coord):
    embed = disnake.Embed(color=color, description=f"# {emoji['ticket']} Обращение создано - {user.author.mention}")
    embed.add_field(name="Игровой никнейм пострадавшего",
                    value=f">>> {nick}", inline=False)
    embed.add_field(name="Игровой никнейм нарушителя",
                    value=f">>> {nick_complaint}", inline=False)
    embed.add_field(name="Суть нарушения",
                    value=f">>> {reason}", inline=False)
    embed.add_field(name="Координаты",
                    value=f">>> {coord}", inline=False)

    return embed


def ticket_askserver(user, nick, ask):
    embed = disnake.Embed(color=color, description=f"# {emoji['ticket']} Обращение создано - {user.author.mention}")
    embed.add_field(name="Игровой никнейм",
                    value=f">>> {nick}", inline=False)
    embed.add_field(name="Ваш вопрос",
                    value=f">>> {ask}", inline=False)

    return embed


def ticket_donate(user, nick):
    embed = disnake.Embed(color=color, description=f"# {emoji['ticket']} Обращение создано - {user.author.mention}")
    embed.add_field(name="Игровой никнейм",
                    value=f">>> {nick}", inline=False)

    return embed


def ticket_bug(user, nick, bug):
    embed = disnake.Embed(color=color, description=f"# {emoji['ticket']} Обращение создано - {user.author.mention}")
    embed.add_field(name="Игровой никнейм",
                    value=f">>> {nick}", inline=False)
    embed.add_field(name="Описание бага",
                    value=f">>> {bug}", inline=False)

    return embed


def ticket_inventory(user, nick, inventory, reason):
    embed = disnake.Embed(color=color, description=f"# {emoji['ticket']} Обращение создано - {user.author.mention}")
    embed.add_field(name="Игровой никнейм",
                    value=f">>> {nick}", inline=False)
    embed.add_field(name="Какие вещи были до смерти",
                    value=f">>> {inventory}", inline=False)
    embed.add_field(name="Причина вашей смерти",
                    value=f">>> {reason}", inline=False)

    return embed


def ticket_changename(user, nick, new_nick, reason):
    embed = disnake.Embed(color=color, description=f"# {emoji['ticket']} Обращение создано - {user.author.mention}")
    embed.add_field(name="Действующий игроков никнейм",
                    value=f">>> {nick}", inline=False)
    embed.add_field(name="Желаемый игровой никнейм",
                    value=f">>> {new_nick}", inline=False)
    embed.add_field(name="Причина переноса",
                    value=f">>> {reason}", inline=False)

    return embed


def ticket_payment(user, nick, reason, donate):
    embed = disnake.Embed(color=color, description=f"# {emoji['ticket']} Обращение создано - {user.author.mention}")
    embed.add_field(name="Игровой никнейм",
                    value=f">>> {nick}", inline=False)
    embed.add_field(name="Причина обращения",
                    value=f">>> {reason}", inline=False)
    embed.add_field(name="Какой донат вы хотите купить",
                    value=f">>> {donate}", inline=False)

    return embed


def ticket_other(user, nick, reason):
    embed = disnake.Embed(color=color, description=f"# {emoji['ticket']} Обращение создано - {user.author.mention}")
    embed.add_field(name="Игровой никнейм",
                    value=f">>> {nick}", inline=False)
    embed.add_field(name="С какой целью обратились",
                    value=f">>> {reason}", inline=False)

    return embed


def error(ctx_id, message):
    embed = disnake.Embed(color=color)
    embed.set_author(icon_url=ctx_id.author.display_avatar, name=ctx_id.author.display_name)
    embed.add_field(name=f"{emoji['error']} Произошла ошибка", value=f"{message}")
    return embed


def successfully(ctx_id, description):
    embed = disnake.Embed(color=color)
    embed.set_author(icon_url=ctx_id.author.display_avatar, name=ctx_id.author.display_name)
    embed.add_field(name=f"{emoji['successfully']} Успешно!", value=f"{description}")
    return embed
