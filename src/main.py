#! /usr/bin/env python3
import discord
from discord.ext import commands
import subprocess
import re
import os, sys
import asyncio
import datetime
import json
import basic
import iksm_discord

TOKEN = basic.DISCORD_TOKENS["0"]
startup_extensions = ["splat"]  # cogの導入

description = ("stat.inkへ戦績自動アップロードを行うbotです。\
\nまずはstat.inkのAPI KEYを用意してください。\
\n詳しい使い方はこちら -> https://github.com/TomoTom0/DiscordBot_Heroku_Stat.ink")

bot = commands.Bot(command_prefix='?', description=description)

# 起動時に動作する処理
@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

    config_path=f"{basic.const_paths['tmp_dir']}/config.txt"
    if not os.path.isfile(config_path):
        with open(config_path, "w") as f:
            f.write(json.dumps({}))
    next_time = 900
    nowtime=datetime.datetime.now()
    tmp_next_time=next_time-(nowtime.minute*60+nowtime.second)%next_time
    print(f"{datetime.datetime.now()} / Next Check Time : in {tmp_next_time} sec")
    await asyncio.sleep(tmp_next_time)

    while True:
        # for splatoon2, stat.ink
        iksm_discord.auto_upload_iksm()

        nowtime=datetime.datetime.now()
        tmp_next_time=next_time-(nowtime.minute*60+nowtime.second)%next_time
        print(f"Next Check Time : in {tmp_next_time} sec")
        await asyncio.sleep(tmp_next_time)

# メッセージ受信時に動作する処理
@bot.event
async def on_message(message):
    # メッセージ送信者がBotだった場合は無視する
    if message.author.bot:
        return
    if message.content == '腹が鳴る':
        await message.channel.send('腕が鳴るだろ……')

    # bot.commandにmessageを流す
    await bot.process_commands(message)


@bot.event  # error時にprint
async def on_command_error(*args):
    print(f"{datetime.datetime.now()} / Error occured - {type(args[-1]).__name__}: {args[-1]}")

if __name__ == "__main__":  # cogを導入
    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = f'{e}: {e.args}'
            print(f'Failed to load extension {extension}\n{exc}')


# Botの起動とDiscordサーバーへの接続
bot.run(TOKEN)
