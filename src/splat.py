import discord
from discord.ext import commands
import os, re
import json
import datetime
import sys
import iksm_discord
import traceback
import asyncio

import basic

config_dir = basic.const_paths["tmp_dir"]


class Splat(commands.Cog):
    "Splatoonに関するコマンドがいくつもあります。"

    def __init__(self, bot):
        self.bot = bot

    ### start
    @commands.command(description="", pass_context=True)
    async def startIksm(self, ctx: commands.Context, STAT_INK_API_KEY=""):
        """新たにiksm_sessionを取得し、botにアカウントを登録します。\nstat.inkの登録を完了し、API KEYを取得しておいてください。"""
        # 各種API KEYの入力確認
        if len(STAT_INK_API_KEY)!=43 and STAT_INK_API_KEY!="skip": # 例外としてskipはOK。skipの場合、戦績のuploadはされません。
            await ctx.channel.send("引数としてstat.inkのAPI KEYが入力されていない、または入力に不備があります。")
            return
        if basic.IsHeroku and not os.getenv("HEROKU_APIKEY", False):
            await ctx.channel.send("Herokuの環境変数としてHerokuのAPI KEYが入力されていません。")
            return
        #try:
        try:
            acc_name = await iksm_discord.make_config_discord(STAT_INK_API_KEY, config_dir, ctx)
        except Exception as e:
            error_message = f"エラーが発生しました。\n{traceback.format_exc()}"
            print(error_message)
            await ctx.channel.send(f"エラーが発生しました。詳細はbotのログを確認してください。")
            return
        success_message="新たに次のアカウントが登録されました。\n" +\
            f"\t\t`{acc_name}`\n"+\
             ("\nこの後botは再起動されます。次の操作はしばらくお待ちください。" if basic.IsHeroku else "")
        await ctx.channel.send(success_message)
        #except Exception as e:
        #    error_message = f"エラーが発生しました。\n{traceback.format_exc()}"
        #    await ctx.channel.send(error_message)

    ### check
    @commands.command(description="", pass_context=True)
    async def checkIksm(self, ctx: commands.Context, acc_name):
        """指定されたアカウントのiksm_sessionを表示します。"""
        acc_name_set=await iksm_discord.checkAcc(ctx, acc_name)
        if acc_name_set["name"]=="":
            return
        acc_info=iksm_discord.obtainAccInfo(acc_name_set["key"])
        await ctx.channel.send(f"`{acc_name}`'s iksm_session is following:\n")
        await ctx.channel.send(acc_info["session_token"])

    ### rm
    @commands.command(description="", pass_context=True)
    async def rmIksm(self, ctx: commands.Context, acc_name:str):
        """指定されたアカウントの情報を削除します。"""
        def removeConfigFile(acc_name_key:str):
            if basic.IsHeroku: # for Heroku
                before_config_tmp=json.loads(os.getenv("iksm_configs", "{}"))
                before_config_jsons=eval(before_config_tmp) if type(before_config_tmp)==str else before_config_tmp
                json_files={k:before_config_jsons[k] for k in before_config_jsons.keys() if k!=acc_name_key}
                res=basic.update_env({"iksm_configs":json.dumps(json_files)})
            else:
                os.remove(f"{config_dir}/{acc_name_key}_config.txt")

        # check
        acc_name_set=await iksm_discord.checkAcc(ctx, acc_name)
        await ctx.channel.send(f"Do you want to remove `{acc_name}`'s config file?(`yes/no`)")

        def check_msg(msg):
            authorIsValid = (msg.author.id == ctx.message.author.id)
            contentIsValid = msg.content in ["yes", "no"]
            return authorIsValid and contentIsValid
        try:
            input_msg = await ctx.bot.wait_for("message", check=check_msg, timeout=600)
            if input_msg.content=="yes":
                removeConfigFile(acc_name_set["key"])
                await ctx.channel.send("Removed.")
            elif input_msg.content=="no":
                await ctx.channel.send("The command has been canceled.")
        except asyncio.TimeoutError:
            await ctx.channel.send("The command has been timeout, and please retry.")
            return

    ### show
    @commands.command(description="", pass_context=True)
    async def showIksm(self, ctx: commands.Context):
        """登録されているnintendoアカウント一覧を表示します。"""
        acc_name_sets=iksm_discord.obtainAccNames()
        content=f"{len(acc_name_sets)} accounts are registered:\n"+\
            "\t\t"+"\n\t\t".join([
                "**{}** :\t`{}`\t\ton {}".format(num+1, acc["name"], iksm_discord.obtainDate(acc["time"]))
                for num, acc in enumerate(acc_name_sets)])
        await ctx.channel.send(content)


def setup(bot):
    bot.add_cog(Splat(bot))
