import discord
import asyncio
from PIL import Image, ImageDraw, ImageFont
import mysql.connector
import os
import nacl
import datetime
import time

intents = discord.Intents.all()
client = discord.Client(intents=intents)

photo_files = [
    "classement1.png",
    "classement2.png",
    "classement3.png"
]
def timer(end_date):
    current_time = datetime.datetime.now()
    if current_time >= end_date:
        print()
    else:
        time_remaining = end_date - current_time
        days = time_remaining.days
        hours, remainder = divmod(time_remaining.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return "{}j {}h {}min".format(days, hours, minutes)

async def generator_img(player_data_1, player_data_2, player_data_3):
    image_width = 1400
    image_height = 400
    background_color = (255, 255, 255)
    text_color = (255, 255, 255)
    background_image = Image.open("bg.png")
    background_image = background_image.resize((1400, 600))
    
    font_path = "Roboto-Regular.ttf"
    font_size = 22
    font = ImageFont.truetype(font_path, font_size)
    
    title_position = (50, 50)
    column_header_position = (50, 100)
    column_header_spacing = [150, 170, 110, 110, 110, 180, 180, 180]
    column_header_spacing2 = [350, 390, 270, 410]
    
    for i, file_name in enumerate(photo_files, 1):
        if i == 1:
            player_data = player_data_1
            title = "Classement - Python"
            column_headers = ["Position", "Nom", "Flag 1", "Flag 2", "Flag 3", "Time 1", "Time 2", "Time 3"]
            player_start_y = 150
        elif i == 2:
            player_data = player_data_2
            title = "Classement - Programmation"
            player_start_y = 150
        else:
            player_data = player_data_3
            title = "Classement - Réseaux sociaux"
            column_headers = ["Position", "Nom", "Flag 1","Time 1"]
            player_start_y = 150
        
        image = Image.new("RGB", (image_width, image_height), background_color)
        image.paste(background_image, (0, 0))
        draw = ImageDraw.Draw(image)
        
        draw.text(title_position, title, fill=text_color, font=font)
        
        if i == 1 or i == 2:
            for i, header in enumerate(column_headers):
                draw.text((column_header_position[0] + sum(column_header_spacing[:i]), column_header_position[1]), header, fill=text_color, font=font)
        else:
            for i, header in enumerate(column_headers):
                draw.text((column_header_position[0] + sum(column_header_spacing2[:i]), column_header_position[1]), header, fill=text_color, font=font)

        player_position = 1
        row_spacing = 40
        for player, data in player_data.items():
            player_info = [str(player_position), player]
            if i == 1 or i == 2:
                player_info += [str(flag) for flag in data["flags"]]
                player_info += data["times"]
            else:
                player_info += [str(flag) for flag in data["flags"]]
                player_info += data["times"]
            player_y = player_start_y + (player_position - 1) * row_spacing
            for j, info in enumerate(player_info):
                x = column_header_position[0] + sum(column_header_spacing[:j]) if i != 3 else column_header_position[0] + sum(column_header_spacing2[:j])
                draw.text((x, player_y), info, fill=text_color, font=font, spacing=3)
            player_position += 1
        
        image.save(file_name)

async def send_embed_with_photos():
    while True:
        conn = mysql.connector.connect(
            host=os.getenv("IP"),
            user=os.getenv("USER"),
            password=os.getenv("PASSWORD"),
            database=os.getenv("DB")
        )
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                nom,
                IF(flag1 = 'triche', 0, flag1) AS flag1,
                IF(flag2 = 'triche', 0, flag2) AS flag2,
                IF(flag3 = 'triche', 0, flag3) AS flag3,
                time_flag_1,
                time_flag_2,
                time_flag_3
            FROM python
            ORDER BY
                flag1 DESC,
                flag2 DESC,
                flag3 DESC,
                time_flag_1 ASC,
                time_flag_2 ASC,
                time_flag_3 ASC
            LIMIT 5
        """)
        player_data_1 = {}
        for row in cursor.fetchall():
            player_name = row[0]
            player_flags = [row[1], row[2], row[3]]
            player_times = [row[4], row[5], row[6]]
            player_data_1[player_name] = {"flags": player_flags, "times": player_times}

        cursor.execute("""
            SELECT
                nom,
                IF(flag1 = 'triche', 0, flag1) AS flag1,
                IF(flag2 = 'triche', 0, flag2) AS flag2,
                IF(flag3 = 'triche', 0, flag3) AS flag3,
                time_flag_1,
                time_flag_2,
                time_flag_3
            FROM prog
            ORDER BY
                flag1 DESC,
                flag2 DESC,
                flag3 DESC,
                time_flag_1 ASC,
                time_flag_2 ASC,
                time_flag_3 ASC
            LIMIT 5
        """)
        player_data_2 = {}
        for row in cursor.fetchall():
            player_name = row[0]
            player_flags = [row[1], row[2], row[3]]
            player_times = [row[4], row[5], row[6]]
            player_data_2[player_name] = {"flags": player_flags, "times": player_times}

        cursor.execute("""
            SELECT
                nom,
                IF(flag1 = 'triche', 0, flag1) AS flag1,
                time_flag_1
            FROM rsociaux
            ORDER BY
                flag1 DESC,
                time_flag_1 ASC
            LIMIT 5
        """)
        player_data_3 = {}
        for row in cursor.fetchall():
            player_name = row[0]
            player_flags = [row[1]]
            player_times = [row[2]]
            player_data_3[player_name] = {"flags": player_flags, "times": player_times}
        await generator_img(player_data_1, player_data_2, player_data_3)

        name, first_value = next(iter(player_data_1.items()))
        name2, first_value = next(iter(player_data_2.items()))
        name3, first_value = next(iter(player_data_3.items()))

        cursor.execute("SELECT COUNT(*) FROM ctfuser")
        result = cursor.fetchone()
        nombre_utilisateurs = result[0]
        await updateNumber(nombre_utilisateurs, name, name2, name3)
        cursor.close()
        conn.close()

        channel = client.get_channel(1239873140553678849)
        await channel.purge(limit=10)
        embed = discord.Embed(title="", description="", color=0x999999)
        for file in photo_files:
            with open(file, "rb") as f:
                photo = discord.File(f)
                embed.set_image(url=f"attachment://{file}")
                await channel.send(embed=embed, file=photo)
        await asyncio.sleep(60)
        for file_name in photo_files:
            if os.path.exists(file_name):
                os.remove(file_name)
        await send_embed_with_photos()

async def updateNumber(nombre_utilisateurs, python, prog, rsociaux):
    annee = 2024
    mois = 5
    jour = 23
    heure = 8
    minute = 0
    seconde = 0

    date_future = datetime.datetime(annee, mois, jour, heure, minute, seconde)
    val = timer(date_future)

    channel = client.get_channel(1239966679686185020)
    message = f"⏲️ | Timer : {str(val)}"
    await channel.edit(name=message)

    channel = client.get_channel(1235582369830932560)
    message = f"🔥 | Utilisateurs : {str(nombre_utilisateurs)}"
    await channel.edit(name=message)

    channel2 = client.get_channel(1187758370380337202)
    online_count = sum(member.status != discord.Status.offline for member in client.get_all_members())
    message2 = f"🟢｜ En ligne : {str(online_count)}"
    await channel2.edit(name=message2)

    channel3 = client.get_channel(1187449742138032179)
    message3 = f"✨｜ Membres : {str(client.get_guild(1187287455590780948).member_count)}"
    await channel3.edit(name=message3)

    channel4 = client.get_channel(1239899944035418172)
    message4 = f"🐍｜ Python : {str(python)}"
    await channel4.edit(name=message4)

    channel5 = client.get_channel(1239900208528101497)
    message5 = f"🦿｜ Programmation : {str(prog)}"
    await channel5.edit(name=message5)

    channel6 = client.get_channel(1239901146978586685)
    message6 = f"💻｜ Reseaux sociaux : {str(rsociaux)}"
    await channel6.edit(name=message6)


@client.event
async def on_ready():
    print('Connecté en tant que', client.user)
    await send_embed_with_photos()

client.run(os.getenv("TOKEN"))
