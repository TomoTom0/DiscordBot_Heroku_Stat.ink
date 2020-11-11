import discord
from discord.ext import commands

import random
import os, re
import json
import datetime
import basic
import requests

class Tool(commands.Cog):
    "サイコロとかランダム選択とか、かゆいところに手が届くツールとなる関数だよ！要望があれば何でも言ってみて！"

    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="", pass_context=True)
    async def tmp1(self, ctx, a1="0", a2="0"):
        """tmp"""
        await ctx.channel.send(f"{os.environ['tmp_aaa']} {os.environ.items()}")

    @commands.command(description="", pass_context=True)
    async def tmp2(self, ctx, a1="0", a2="0"):
        """tmp"""
        app_name="maybe-python" #HEROKU_APP_NAME
        patch_url = f"https://api.heroku.com/apps/{app_name}/config-vars"
        body= {"tmp_aaa":a1}
        headers= {"Authorization": f"Bearer {os.environ['HEROKU_API']}",
            "Content-Type":"application/json",
            "Accept":"application/vnd.heroku+json; version=3"}
        os.environ["tmp_aaa"] = a1
        requests.patch(patch_url, headers=headers, json=body)
        await ctx.channel.send(os.environ["tmp_aaa"])


    @commands.command(description='「?dice 2d6」で「3, 5」などが得られます。', pass_context=True)
    async def dice(self, ctx, dice: str):
        """
        サイコロを振ることができます。TRPGで使われるNdN記法。
        2個の6面サイコロの結果がほしい場合は「?dice 2d6」と入力してください。"""
        try:
            rolls, limit = map(int, dice.split('d'))
        except Exception:
            await ctx.channel.send("「NdN」の形じゃないよ！")
            return 0

        result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
        await ctx.channel.send("ダイスロール！\n" + result)



def setup(bot):
    bot.add_cog(Tool(bot))
