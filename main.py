import discord
import asyncio
from PIL import Image, ImageDraw, ImageFont
import mysql.connector
import os
import nacl

intents = discord.Intents.all()
client = discord.Client(intents=intents)

photo_files = [
    "classement1.png",
    "classement2.png",
    "classement3.png"
]

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
        
        for i, header in enumerate(column_headers):
            draw.text((column_header_position[0] + sum(column_header_spacing[:i]), column_header_position[1]), header, fill=text_color, font=font)
        
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
            FROM prog
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
        cursor.close()
        conn.close()
        await asyncio.sleep(120)
        for file_name in photo_files:
            if os.path.exists(file_name):
                os.remove(file_name)
        await send_embed_with_photos()


@client.event
async def on_ready():
    print('Connecté en tant que', client.user)
    await send_embed_with_photos()

client.run(os.getenv("TOKEN"))
