import discord
from discord.ext import commands
import os, re
import json
import datetime
import sys
import iksm_discord

import basic

conifg_dir=basic.const_paths["tmp_dir"]

class Splat(commands.Cog):
    "Splatoonに関するコマンドがいくつもあります。"

    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="あらかじめstat.inkのアカウントを用意し、API KEYを用意しておいてください。", pass_context=True)
    async def startIksm(self, ctx: commands.Context, STAT_INK_API_KEY="0"*43):
        """新たにiksm_sessionを取得し、config.txtを作成します。\nstat.inkの登録を完了し、API KEYを取得しておいてください。"""
        await iksm_discord.make_config_discord(STAT_INK_API_KEY, conifg_dir, ctx)
        await ctx.channel.send(f"アカウントは登録され、新たにconfig.txtが作られました。\nこの後botは再起動されます。次の操作はしばらくお待ちください。")

    @commands.command(description="", pass_context=True)
    async def checkIksmSession(self, ctx: commands.Context, acc_name):
        """指定されたアカウントのiksm_sessionを表示します。"""
        before_config_jsons=eval(json.loads(os.getenv("iksm_configs", "{}")))
        json_file=before_config_jsons[acc_name]
        await ctx.channel.send(f"{acc_name}'s iksm_session is\n----\n")
        await ctx.channel.send(json_file["session_token"])

    @commands.command(description="", pass_context=True)
    async def changeAPI(self, ctx: commands.Context, acc_name, NEW_API_KEY):
        """指定されたアカウントのstat.inkのAPI KEYを変更します。"""
        before_config_jsons=eval(json.loads(os.getenv("iksm_configs", "{}")))
        new_config_jsons={acc: conf if acc!=acc_name
            else {k: v if k!="API_KEY" else NEW_API_KEY for k,v in conf.items()}
            for acc, conf in before_config_jsons.items()}
        basic.update_env({"iksm_configs":json.dumps(new_config_jsons)})
        await ctx.channel.send(f"{acc_name}'s API_KEY is updated.")

    @commands.command(description="", pass_context=True)
    async def rmIksm(self, ctx: commands.Context, acc_name):
        """指定されたアカウントの情報を削除します。"""
        before_config_jsons=eval(json.loads(os.getenv("iksm_configs", "{}")))
        json_files={k:v for k, v in before_config_jsons.items() if k!=acc_name}
        basic.update_env({"iksm_configs":json.dumps(json_files)})
        await ctx.channel.send("Removed.")

    @commands.command(description="", pass_context=True)
    async def showIksmAcc(self, ctx: commands.Context):
        """登録されているnintendoアカウント一覧を表示します。"""
        before_config_jsons=eval(json.loads(os.getenv("iksm_configs", "{}")))
        acc_names = [k for k, v in before_config_jsons.items() ]
        await ctx.channel.send(f"There is {len(acc_names)} accounts.\n----\n"+"\n".join(acc_names))


def setup(bot):
    bot.add_cog(Splat(bot))
