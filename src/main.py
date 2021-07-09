#! /usr/bin/env python3
import discord
from discord.ext import commands
import subprocess
import re
import os, sys
import json
import basic
import datetime
import traceback
import iksm_discord

TOKEN = basic.DISCORD_TOKENS["0"]
startup_extensions = ["splat"]  # cogの導入

description = f"stat.inkへ戦績自動アップロードを行うbotです。\nまずはstat.inkのAPI KEYを用意してください。"+\
'\nHerokuのAPI KEYとapp-nameを環境変数として入力しておいてください。' if os.getenv('DYNO', False) else '' +\
"\n詳しい使い方はこちら -> https://github.com/TomoTom0/DiscordBot_Heroku_Stat.ink"

bot = commands.Bot(command_prefix="?", description=description)

# 起動時に動作する処理
@bot.event
async def on_ready():
    print(f"Logged in as\n{bot.user.name}\n{bot.user.id}\n------")

    await iksm_discord.autoUploadCycle(next_time = 900)


# メッセージ受信時に動作する処理
@bot.event
async def on_message(message):
    # メッセージ送信者がBotだった場合は無視する
    if message.author.bot is True:
        return

    # bot.commandにmessageを流す
    try:
        await bot.process_commands(message)
    except Exception as e:
            error_message = f"エラーが発生しました。\n{traceback.format_exc()}"
            print(error_message)


if __name__ == "__main__":  # cogを導入
    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = f'{e}: {e.args}'
            print(f'Failed to load extension {extension}\n{exc}')


# Botの起動とDiscordサーバーへの接続
bot.run(TOKEN)
