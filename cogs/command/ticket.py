import asyncio
from disnake.ext import commands
from disnake.ui import View

from main import bot as bt
from main import cursor, db
from tools.embeds import *

with open("./tools/config.json", "r") as f:
    config = json.load(f)

    emoji = config["emoji"]
    ticket_emoji = config["ticket_emoji"]


class TicketSystem(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.persistents_view = False

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.wait_until_ready()
        if self.persistents_view:
            return

        view = DropdownView(bot=self.bot)
        self.bot.add_view(view)

    @commands.is_owner()
    @commands.slash_command(name="ticket", description="Отправить сообщение в канал", guild_ids=[1228090741600026684])
    async def ticket_command(self, interaction):
        await interaction.send("Начинаю обработку вашего запроса...", ephemeral=True)

        cursor.execute(f"""CREATE TABLE IF NOT EXISTS Tickets (
            user_id INTEGER,
            name TEXT,
            status INTEGER,
            channel INTEGER,
            PRIMARY KEY (user_id, name))""")
        db.commit()

        guild = self.bot.get_guild(1228090741600026684)
        channel = guild.get_channel(1280082305792217180)

        view = DropdownView(bot=self.bot)
        await channel.purge()
        await channel.send(embed=welcome_ticket(), view=view)
        await interaction.edit_original_message(content=None, embed=successfully(
            description=f"Тикет сообщение было отправлено в канал {channel.mention}", ctx_id=interaction))
        return


def execute_database_ticket(user, name, channel):
    cursor.execute('''
        INSERT INTO Tickets (user_id, name, status, channel)
        VALUES (?, ?, 1, ?)
        ON CONFLICT(user_id, name)
        DO UPDATE SET status = 1;
    ''', (user, f'{name}', channel))
    db.commit()


async def handle_ticket_close(interaction: disnake.Interaction, channel_id, bot):
    allowed_role_ids = [1228090741600026687, 1228090741600026687]

    # if any(role.id in allowed_role_ids for role in interaction.user.roles):
    cursor.execute('SELECT channel FROM Tickets WHERE channel = ?', (channel_id,))
    result = cursor.fetchone()

    if result:
        cursor.execute('DELETE FROM Tickets WHERE channel = ?', (channel_id,))
        db.commit()

        guild = bot.get_guild(1228090741600026684)
        channel = guild.get_channel(channel_id)
        if channel:
            await channel.delete(reason=f"Тикет закрыт {long_slash} {interaction.author.display_name}")

    else:
        await interaction.response.send_message("Канал не найден в базе данных", ephemeral=True)
    # else:
    #     await interaction.response.send_message(
    #         embed=error(ctx_id=interaction, message="Вы не можете закрыть тикет самостоятельно"), ephemeral=True)


class DropdownView(disnake.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.add_item(DropdownMenu(bot=bot))


# TODO ИЗМЕНЕНИЕ НАЗВАНИЙ КНОПОК
class DropdownMenu(disnake.ui.Select):
    def __init__(self, bot: commands.Bot):
        options = [
            disnake.SelectOption(label="Жалоба на игрока/гриф/кражу", value="complaint", emoji="⚠️"),
            disnake.SelectOption(label="Вопрос по серверу", value="question", emoji="⁉️"),
            disnake.SelectOption(label="Получить роль Plus", value="role_plus", emoji="📦"),
            disnake.SelectOption(label="Нашел баг", value="bug", emoji="💣"),
            disnake.SelectOption(label="Откат инвентаря", value="inventory_reset", emoji="💀"),
            disnake.SelectOption(label="Смена никнейма", value="nickname_change", emoji="🔖"),
            disnake.SelectOption(label="Оплата из другой страны/Проблема с оплатой", value="payment", emoji="🛒"),
            disnake.SelectOption(label="Прочее", value="other", emoji="✨")
        ]
        super().__init__(placeholder="Выберите тему тикета", options=options, custom_id="ticket_dropdown")
        self.bot = bot

    async def callback(self, interaction: disnake.MessageInteraction):
        selected_value = self.values[0]
        button = disnake.ui.Button(label="Продолжить", style=disnake.ButtonStyle.gray, custom_id="continue_button")
        view = disnake.ui.View(timeout=None)
        view.add_item(button)

        async def button_callback(inter: disnake.MessageInteraction):
            await self.continue_button_callback(ticket_type=f'{selected_value}', interaction=inter)

        def valid_ticket(user, name):
            res = cursor.execute(
                f"""SELECT status FROM Tickets WHERE user_id = {user.author.id} AND name = '{name}'""").fetchone()
            return res[0] if res is not None else 0

        if selected_value == "complaint":
            if valid_ticket(user=interaction, name="complaint") == 1:
                await interaction.send(embed=error(ctx_id=interaction, message="У вас уже создан тикет данного типа!"),
                                       ephemeral=True)
                return
            await asyncio.sleep(2)
            modal = TicketModal_complaint(bot=self.bot)
            await interaction.response.send_modal(modal=modal)
            return
        elif selected_value == "question":
            if valid_ticket(user=interaction, name="question") == 1:
                await interaction.send(embed=error(ctx_id=interaction, message="У вас уже создан тикет данного типа!"),
                                       ephemeral=True)
                return
            await asyncio.sleep(1)
            modal = TicketModal_AskServer(bot=self.bot)
            await interaction.response.send_modal(modal=modal)
            return
        elif selected_value == "role_plus":
            if valid_ticket(user=interaction, name="role_plus") == 1:
                await interaction.send(embed=error(ctx_id=interaction, message="У вас уже создан тикет данного типа!"),
                                       ephemeral=True)
                return
            embed = warning_get_plus()
            button.callback = button_callback
        elif selected_value == "bug":
            if valid_ticket(user=interaction, name="bug") == 1:
                await interaction.send(embed=error(ctx_id=interaction, message="У вас уже создан тикет данного типа!"),
                                       ephemeral=True)
                return
            embed = warning_bug()
            button.callback = button_callback
        elif selected_value == "inventory_reset":
            if valid_ticket(user=interaction, name="inventory_reset") == 1:
                await interaction.send(embed=error(ctx_id=interaction, message="У вас уже создан тикет данного типа!"),
                                       ephemeral=True)
                return
            embed = warning_inventory()
            button.callback = button_callback
        elif selected_value == "nickname_change":
            if valid_ticket(user=interaction, name="nickname_change") == 1:
                await interaction.send(embed=error(ctx_id=interaction, message="У вас уже создан тикет данного типа!"),
                                       ephemeral=True)
                return
            embed = warning_change_name()
            button.callback = button_callback
        elif selected_value == "payment":
            if valid_ticket(user=interaction, name="payment") == 1:
                await interaction.send(embed=error(ctx_id=interaction, message="У вас уже создан тикет данного типа!"),
                                       ephemeral=True)
                return
            await asyncio.sleep(1)
            modal = TicketModal_payment(bot=self.bot)
            await interaction.response.send_modal(modal=modal)
            return
        elif selected_value == "other":
            if valid_ticket(user=interaction, name="other") == 1:
                await interaction.send(embed=error(ctx_id=interaction, message="У вас уже создан тикет данного типа!"),
                                       ephemeral=True)
                return
            await asyncio.sleep(1)
            modal = TicketModal_other(bot=self.bot)
            await interaction.response.send_modal(modal=modal)
            return

        await interaction.send(embed=embed, view=view, ephemeral=True)

    async def continue_button_callback(self, ticket_type, interaction: disnake.MessageInteraction):
        if ticket_type == "role_plus":
            modal = TicketModal_donate(bot=self.bot)

        elif ticket_type == "bug":
            modal = TicketModal_bug(bot=self.bot)

        elif ticket_type == "inventory_reset":
            modal = TicketModal_inventory(bot=self.bot)

        elif ticket_type == "nickname_change":
            modal = TicketModal_ChangeName(bot=self.bot)

        await interaction.response.send_modal(modal)


class TicketModal_complaint(disnake.ui.Modal):
    def __init__(self, bot):
        self.bot = bot
        self.DM = DropdownMenu(bot=self.bot)
        components = [
            disnake.ui.TextInput(label="Ваш никнейм", placeholder="Укажите ваш игровой никнейм без ошибок",
                                 custom_id="nickname_input"),
            disnake.ui.TextInput(label="Никнейм нарушителя", placeholder="Введите никнейм нарушителя",
                                 custom_id="nickname_complaint_input", min_length=3),
            disnake.ui.TextInput(label="Суть нарушения во всех подробностях",
                                 placeholder="Опишите все подробности жалобы",
                                 style=disnake.TextInputStyle.paragraph, custom_id="reason_input"),
            disnake.ui.TextInput(label="Координаты", placeholder="Укажите координаты нарушения",
                                 min_length=3, custom_id="coord", style=disnake.TextInputStyle.short)
        ]
        super().__init__(title="Опишите вашу жалобу", components=components)

    async def callback(self, interaction: disnake.ModalInteraction):
        nickname = interaction.text_values['nickname_input']
        nickname_complaint = interaction.text_values['nickname_complaint_input']
        reason = interaction.text_values['reason_input']
        coord = interaction.text_values['coord']

        guild = interaction.guild
        category = guild.get_channel(1282387541139652759)
        channel = await category.create_text_channel(
            name=f"Жалоба-{nickname}",
            overwrites={
                guild.default_role: disnake.PermissionOverwrite(
                    view_channel=False
                ),
                interaction.author: disnake.PermissionOverwrite(
                    view_channel=True,
                    read_message_history=True,
                    send_messages=True,
                    attach_files=True,
                    embed_links=True
                ),
                guild.get_role(1280079528609185814): disnake.PermissionOverwrite(
                    view_channel=True,
                    read_message_history=True,
                    send_messages=True,
                    attach_files=True,
                    embed_links=True
                ),  # Owner
                guild.get_role(1280079550705045587): disnake.PermissionOverwrite(
                    view_channel=True,
                    read_message_history=True,
                    send_messages=True,
                    attach_files=True,
                    embed_links=True
                ),  # Admin
                self.bot.user: disnake.PermissionOverwrite(
                    view_channel=True,
                    read_message_history=True,
                    send_messages=True,
                    attach_files=True,
                    embed_links=True
                )
            }
        )
        view = ButtonClosed(bot=self.bot, channel_id=channel.id)

        await channel.send(content="<@&1228090741600026687>", embed=ticket_complaint(user=interaction, nick=nickname,
                                                                                     nick_complaint=nickname_complaint,
                                                                                     reason=reason, coord=coord),
                           view=view)

        await interaction.response.send_message(f"Тикет был успешно создан!\n{channel.mention}", ephemeral=True)

        execute_database_ticket(user=interaction.author.id, name="complaint", channel=channel.id)


class TicketModal_AskServer(disnake.ui.Modal):
    def __init__(self, bot):
        self.bot = bot
        self.DM = DropdownMenu(bot=self.bot)
        components = [
            disnake.ui.TextInput(label="Ваш никнейм", placeholder="Укажите ваш игровой никнейм без ошибок",
                                 custom_id="nickname_input"),
            disnake.ui.TextInput(label="Ваш вопрос", placeholder="Опишите ваш вопрос в подробностях",
                                 min_length=3, custom_id="value", style=disnake.TextInputStyle.short)
        ]
        super().__init__(title="Опишите ваш вопрос", components=components)

    async def callback(self, interaction: disnake.ModalInteraction):
        nickname = interaction.text_values['nickname_input']
        reason = interaction.text_values['value']

        guild = interaction.guild
        category = guild.get_channel(1282387541139652759)
        channel = await category.create_text_channel(
            name=f"Вопрос-по-серверу-{nickname}",
            overwrites={
                guild.default_role: disnake.PermissionOverwrite(
                    view_channel=False
                ),
                interaction.author: disnake.PermissionOverwrite(
                    view_channel=True,
                    read_message_history=True,
                    send_messages=True,
                    attach_files=True,
                    embed_links=True
                ),
                guild.get_role(1280079528609185814): disnake.PermissionOverwrite(
                    view_channel=True,
                    read_message_history=True,
                    send_messages=True,
                    attach_files=True,
                    embed_links=True
                ),  # Owner
                guild.get_role(1280079550705045587): disnake.PermissionOverwrite(
                    view_channel=True,
                    read_message_history=True,
                    send_messages=True,
                    attach_files=True,
                    embed_links=True
                ),  # Admin
                self.bot.user: disnake.PermissionOverwrite(
                    view_channel=True,
                    read_message_history=True,
                    send_messages=True,
                    attach_files=True,
                    embed_links=True
                )
            }
        )
        view = ButtonClosed(bot=self.bot, channel_id=channel.id)

        await channel.send(embed=ticket_askserver(user=interaction, nick=nickname, ask=reason), view=view)

        await interaction.response.send_message(f"Тикет был успешно создан!\n{channel.mention}", ephemeral=True)

        execute_database_ticket(user=interaction.author.id, name="question", channel=channel.id)


class TicketModal_donate(disnake.ui.Modal):
    def __init__(self, bot):
        self.bot = bot
        self.DM = DropdownMenu(bot=self.bot)
        components = [
            disnake.ui.TextInput(label="Ваш никнейм", placeholder="Укажите ваш игровой никнейм без ошибок",
                                 custom_id="nickname_input")
        ]
        super().__init__(title="Получение донат роли", components=components)

    async def callback(self, interaction: disnake.ModalInteraction):
        nickname = interaction.text_values['nickname_input']

        guild = interaction.guild
        category = guild.get_channel(1282387541139652759)
        channel = await category.create_text_channel(
            name=f"Получение-донат-роли-{nickname}",
            overwrites={
                guild.default_role: disnake.PermissionOverwrite(
                    view_channel=False
                ),
                interaction.author: disnake.PermissionOverwrite(
                    view_channel=True,
                    read_message_history=True,
                    send_messages=True,
                    attach_files=True,
                    embed_links=True
                ),
                guild.get_role(1280079528609185814): disnake.PermissionOverwrite(
                    view_channel=True,
                    read_message_history=True,
                    send_messages=True,
                    attach_files=True,
                    embed_links=True
                ),  # Owner
                guild.get_role(1280079550705045587): disnake.PermissionOverwrite(
                    view_channel=True,
                    read_message_history=True,
                    send_messages=True,
                    attach_files=True,
                    embed_links=True
                ),  # Admin
                self.bot.user: disnake.PermissionOverwrite(
                    view_channel=True,
                    read_message_history=True,
                    send_messages=True,
                    attach_files=True,
                    embed_links=True
                )
            }
        )
        view = ButtonClosed(bot=self.bot, channel_id=channel.id)

        await channel.send(embed=ticket_donate(user=interaction, nick=nickname), view=view)

        await interaction.response.send_message(f"Тикет был успешно создан!\n{channel.mention}", ephemeral=True)

        execute_database_ticket(user=interaction.author.id, name="role_plus", channel=channel.id)


class TicketModal_bug(disnake.ui.Modal):
    def __init__(self, bot):
        self.bot = bot
        self.DM = DropdownMenu(self.bot)
        components = [
            disnake.ui.TextInput(label="Ваш никнейм", placeholder="Укажите ваш игровой никнейм без ошибок",
                                 custom_id="nickname_input"),
            disnake.ui.TextInput(label="Описание бага", placeholder="Подробно опишите обнаруженный вами баг",
                                 custom_id="bug")
        ]
        super().__init__(title="Обнарушижи баг на сервере?", components=components)

    async def callback(self, interaction: disnake.ModalInteraction):
        nickname = interaction.text_values['nickname_input']
        bug = interaction.text_values['bug']

        guild = interaction.guild
        category = guild.get_channel(1282387541139652759)
        channel = await category.create_text_channel(
            name=f"Баг-сервера-{nickname}",
            overwrites={
                guild.default_role: disnake.PermissionOverwrite(
                    view_channel=False
                ),
                interaction.author: disnake.PermissionOverwrite(
                    view_channel=True,
                    read_message_history=True,
                    send_messages=True,
                    attach_files=True,
                    embed_links=True
                ),
                guild.get_role(1280079528609185814): disnake.PermissionOverwrite(
                    view_channel=True,
                    read_message_history=True,
                    send_messages=True,
                    attach_files=True,
                    embed_links=True
                ),  # Owner
                guild.get_role(1280079550705045587): disnake.PermissionOverwrite(
                    view_channel=True,
                    read_message_history=True,
                    send_messages=True,
                    attach_files=True,
                    embed_links=True
                ),  # Admin
                self.bot.user: disnake.PermissionOverwrite(
                    view_channel=True,
                    read_message_history=True,
                    send_messages=True,
                    attach_files=True,
                    embed_links=True
                )
            }
        )
        view = ButtonClosed(bot=self.bot, channel_id=channel.id)

        await channel.send(embed=ticket_bug(user=interaction, bug=bug, nick=nickname), view=view)

        await interaction.response.send_message(f"Тикет был успешно создан!\n{channel.mention}", ephemeral=True)

        execute_database_ticket(user=interaction.author.id, name="bug", channel=channel.id)


class TicketModal_inventory(disnake.ui.Modal):
    def __init__(self, bot):
        self.bot = bot
        self.DM = DropdownMenu(self.bot)
        components = [
            disnake.ui.TextInput(label="Ваш никнейм", placeholder="Укажите ваш игровой никнейм без ошибок",
                                 custom_id="nickname_input"),
            disnake.ui.TextInput(label="Какие вещи были до этой смерти?",
                                 placeholder="Перечислите все вещи, которые вы помните",
                                 custom_id="inventory"),
            disnake.ui.TextInput(label="Причина вашей смерти?",
                                 placeholder="Если это был игрок, то укажите его никнейм",
                                 custom_id="reason")
        ]
        super().__init__(title="Откат инвентаря", components=components)

    async def callback(self, interaction: disnake.ModalInteraction):
        nickname = interaction.text_values['nickname_input']
        inventory = interaction.text_values['inventory']
        reason = interaction.text_values['reason']

        guild = interaction.guild
        category = guild.get_channel(1282387541139652759)
        channel = await category.create_text_channel(
            name=f"Откат-Вещей-{nickname}",
            overwrites={
                guild.default_role: disnake.PermissionOverwrite(
                    view_channel=False
                ),
                interaction.author: disnake.PermissionOverwrite(
                    view_channel=True,
                    read_message_history=True,
                    send_messages=True,
                    attach_files=True,
                    embed_links=True
                ),
                guild.get_role(1280079528609185814): disnake.PermissionOverwrite(
                    view_channel=True,
                    read_message_history=True,
                    send_messages=True,
                    attach_files=True,
                    embed_links=True
                ),  # Owner
                guild.get_role(1280079550705045587): disnake.PermissionOverwrite(
                    view_channel=True,
                    read_message_history=True,
                    send_messages=True,
                    attach_files=True,
                    embed_links=True
                ),  # Admin
                self.bot.user: disnake.PermissionOverwrite(
                    view_channel=True,
                    read_message_history=True,
                    send_messages=True,
                    attach_files=True,
                    embed_links=True
                )
            }
        )
        view = ButtonClosed(bot=self.bot, channel_id=channel.id)

        await channel.send(embed=ticket_inventory(user=interaction, nick=nickname, inventory=inventory, reason=reason),
                           view=view)

        await interaction.response.send_message(f"Тикет был успешно создан!\n{channel.mention}", ephemeral=True)

        execute_database_ticket(user=interaction.author.id, name="inventory_reset", channel=channel.id)


class TicketModal_ChangeName(disnake.ui.Modal):
    def __init__(self, bot):
        self.bot = bot
        self.DM = DropdownMenu(self.bot)
        components = [
            disnake.ui.TextInput(label="Ваш старый никнейм",
                                 placeholder="Укажите ваш старый игровой никнейм без ошибок",
                                 custom_id="nickname_input"),
            disnake.ui.TextInput(label="Ваш новый никнейм", placeholder="Укажите ваш новый игровой никнейм без ошибок",
                                 custom_id="nickname_new"),
            disnake.ui.TextInput(label="Причина переноса", placeholder="Укажите почему вы решили сменить никнейм",
                                 custom_id="reason")
        ]
        super().__init__(title="Смена игрового никнейма", components=components)

    async def callback(self, interaction: disnake.ModalInteraction):
        nickname = interaction.text_values['nickname_input']
        new_nickname = interaction.text_values['nickname_new']
        reason = interaction.text_values['reason']

        guild = interaction.guild
        category = guild.get_channel(1282387541139652759)
        channel = await category.create_text_channel(
            name=f"Смена-ника-{nickname}",
            overwrites={
                guild.default_role: disnake.PermissionOverwrite(
                    view_channel=False
                ),
                interaction.author: disnake.PermissionOverwrite(
                    view_channel=True,
                    read_message_history=True,
                    send_messages=True,
                    attach_files=True,
                    embed_links=True
                ),
                guild.get_role(1280079528609185814): disnake.PermissionOverwrite(
                    view_channel=True,
                    read_message_history=True,
                    send_messages=True,
                    attach_files=True,
                    embed_links=True
                ),  # Owner
                guild.get_role(1280079550705045587): disnake.PermissionOverwrite(
                    view_channel=True,
                    read_message_history=True,
                    send_messages=True,
                    attach_files=True,
                    embed_links=True
                ),  # Admin
                self.bot.user: disnake.PermissionOverwrite(
                    view_channel=True,
                    read_message_history=True,
                    send_messages=True,
                    attach_files=True,
                    embed_links=True
                )
            }
        )
        view = ButtonClosed(bot=self.bot, channel_id=channel.id)

        await channel.send(
            embed=ticket_changename(user=interaction, nick=nickname, new_nick=new_nickname, reason=reason),
            view=view)

        await interaction.response.send_message(f"Тикет был успешно создан!\n{channel.mention}", ephemeral=True)

        execute_database_ticket(user=interaction.author.id, name="nickname_change", channel=channel.id)


class TicketModal_payment(disnake.ui.Modal):
    def __init__(self, bot):
        self.bot = bot
        self.DM = DropdownMenu(bot=self.bot)
        components = [
            disnake.ui.TextInput(label="Ваш никнейм", placeholder="Укажите ваш игровой никнейм без ошибок",
                                 custom_id="nickname_input"),
            disnake.ui.TextInput(label="Причина обращения", placeholder="Опишите проблему в подробностях",
                                 custom_id="reason"),
            disnake.ui.TextInput(label="Что вы хотели приобрести", placeholder="Укажите название товара",
                                 custom_id="donate_name", style=disnake.TextInputStyle.short)
        ]
        super().__init__(title="Оплата доната", components=components)

    async def callback(self, interaction: disnake.ModalInteraction):
        nickname = interaction.text_values['nickname_input']
        reason = interaction.text_values['reason']
        donate = interaction.text_values['donate_name']

        guild = interaction.guild
        category = guild.get_channel(1282387541139652759)
        channel = await category.create_text_channel(
            name=f"Проблема-с-оплатой-{nickname}",
            overwrites={
                guild.default_role: disnake.PermissionOverwrite(
                    view_channel=False
                ),
                interaction.author: disnake.PermissionOverwrite(
                    view_channel=True,
                    read_message_history=True,
                    send_messages=True,
                    attach_files=True,
                    embed_links=True
                ),
                guild.get_role(1280079528609185814): disnake.PermissionOverwrite(
                    view_channel=True,
                    read_message_history=True,
                    send_messages=True,
                    attach_files=True,
                    embed_links=True
                ),  # Owner
                guild.get_role(1280079550705045587): disnake.PermissionOverwrite(
                    view_channel=True,
                    read_message_history=True,
                    send_messages=True,
                    attach_files=True,
                    embed_links=True
                ),  # Admin
                self.bot.user: disnake.PermissionOverwrite(
                    view_channel=True,
                    read_message_history=True,
                    send_messages=True,
                    attach_files=True,
                    embed_links=True
                )
            }
        )
        view = ButtonClosed(bot=self.bot, channel_id=channel.id)

        await channel.send(embed=ticket_payment(user=interaction, nick=nickname, reason=reason, donate=donate),
                           view=view)

        await interaction.response.send_message(f"Тикет был успешно создан!\n{channel.mention}", ephemeral=True)

        execute_database_ticket(user=interaction.author.id, name="payment", channel=channel.id)


class TicketModal_other(disnake.ui.Modal):
    def __init__(self, bot):
        self.bot = bot
        self.DM = DropdownMenu(self.bot)
        components = [
            disnake.ui.TextInput(label="Ваш никнейм", placeholder="Укажите ваш игровой никнейм без ошибок",
                                 custom_id="nickname_input"),
            disnake.ui.TextInput(label="С какой целью обратились?", placeholder="Опишите в подробностях",
                                 custom_id="reason")
        ]
        super().__init__(title="Прочее", components=components)

    async def callback(self, interaction: disnake.ModalInteraction):
        nickname = interaction.text_values['nickname_input']
        reason = interaction.text_values['reason']

        guild = interaction.guild
        category = guild.get_channel(1282387541139652759)
        print(interaction.author)
        channel = await category.create_text_channel(
            name=f"Прочее-{nickname}",
            overwrites={
                guild.default_role: disnake.PermissionOverwrite(
                    view_channel=False
                ),
                interaction.author: disnake.PermissionOverwrite(
                    view_channel=True,
                    read_message_history=True,
                    send_messages=True,
                    attach_files=True,
                    embed_links=True
                ),
                guild.get_role(1280079528609185814): disnake.PermissionOverwrite(
                    view_channel=True,
                    read_message_history=True,
                    send_messages=True,
                    attach_files=True,
                    embed_links=True
                ),  # Owner
                guild.get_role(1280079550705045587): disnake.PermissionOverwrite(
                    view_channel=True,
                    read_message_history=True,
                    send_messages=True,
                    attach_files=True,
                    embed_links=True
                ),  # Admin
                self.bot.user: disnake.PermissionOverwrite(
                    view_channel=True,
                    read_message_history=True,
                    send_messages=True,
                    attach_files=True,
                    embed_links=True
                )
            }
        )
        view = ButtonClosed(bot=self.bot, channel_id=channel.id)

        await channel.send(embed=ticket_other(user=interaction, nick=nickname, reason=reason), view=view)

        await interaction.response.send_message(f"Тикет был успешно создан!\n{channel.mention}", ephemeral=True)

        execute_database_ticket(user=interaction.author.id, name="other", channel=channel.id)


class ButtonClosed(View):
    def __init__(self, bot, channel_id):
        self.bot = bot
        self.channel = channel_id
        super().__init__(timeout=None)

        close_button = disnake.ui.Button(
            label="Закрыть обращение",
            style=disnake.ButtonStyle.primary,
            custom_id="close_ticket_button"
        )

        self.add_item(close_button)


@bt.listen("on_button_click")
async def button_click_handler(interaction: disnake.MessageInteraction):
    if interaction.component.custom_id == "close_ticket_button":
        await handle_ticket_close(
            bot=bt,
            interaction=interaction,
            channel_id=interaction.channel_id
        )
    else:
        return


def setup(bot):
    bot.add_cog(TicketSystem(bot))
