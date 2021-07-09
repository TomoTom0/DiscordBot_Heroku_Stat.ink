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

conifg_dir = basic.const_paths["tmp_dir"]

class Splat(commands.Cog):
    "Splatoonに関するコマンドがいくつもあります。"

    def __init__(self, bot):
        self.bot = bot

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
            await iksm_discord.make_config_discord(STAT_INK_API_KEY, conifg_dir, ctx)
        except Exception as e:
            error_message = f"エラーが発生しました。\n{traceback.format_exc()}"
            print(error_message)
            await ctx.channel.send(f"エラーが発生しました。詳細はbotのログを確認してください。")
            return
        success_message="新たにアカウントが登録されました。" + ("\nこの後botは再起動されます。次の操作はしばらくお待ちください。" if basic.IsHeroku else "")
        await ctx.channel.send(success_message)
        #except Exception as e:
        #    error_message = f"エラーが発生しました。\n{traceback.format_exc()}"
        #    await ctx.channel.send(error_message)


    @commands.command(description="", pass_context=True)
    async def checkIksmSession(self, ctx: commands.Context, acc_name):
        """指定されたアカウントのiksm_sessionを表示します。"""
        if basic.IsHeroku:
            before_config_tmp=json.loads(os.getenv("iksm_configs", "{}"))
            before_config_jsons=eval(before_config_tmp) if type(before_config_tmp)==str else before_config_tmp
            json_file=before_config_jsons[acc_name]
        else:
            with open(f"{conifg_dir}/{acc_name}_config.txt", "r") as f:
                json_file=json.loads(f.read())
        await ctx.channel.send(f"{acc_name}'s iksm_session is\n----\n")
        await ctx.channel.send(json_file["session_token"])

    @commands.command(description="", pass_context=True)
    async def rmIksm(self, ctx: commands.Context, acc_index: int):
        """番号で指定されたアカウントの情報を削除します。\nまずは`?showIksmAcc`を利用してください。"""
        def obtainAccName(acc_idnex, isHeroku:bool):
            if basic.IsHeroku: # for Heroku
                before_config_tmp=json.loads(os.getenv("iksm_configs", "{}"))
                before_config_jsons=eval(before_config_tmp) if type(before_config_tmp)==str else before_config_tmp
                acc_name=list(before_config_jsons.keys())[acc_index-1]
            else:
                acc_names = [path.replace("_config.txt", "") for path in os.listdir(conifg_dir) if path.endswith("_config.txt")]
                acc_name = acc_names[acc_index-1]
            return acc_name
        def removeConfigFile(acc_name, isHeroku:bool):
            if basic.IsHeroku: # for Heroku
                before_config_tmp=json.loads(os.getenv("iksm_configs", "{}"))
                before_config_jsons=eval(before_config_tmp) if type(before_config_tmp)==str else before_config_tmp
                json_files={k:before_config_jsons[k] for k in before_config_jsons.keys() if k!=acc_name}
                res=basic.update_env({"iksm_configs":json.dumps(json_files)})
            else:
                os.remove(f"{conifg_dir}/{acc_name}_config.txt")

        acc_name = obtainAccName(acc_index, isHeroku=basic.IsHeroku)
        # check
        await ctx.channel.send(f"Do you want to remove `{acc_name}`'s config file?(`yes/no`)")

        def check_msg(msg):
            authorIsValid = (msg.author.id == ctx.message.author.id)
            contentIsValid = msg.content in ["yes", "no"]
            return authorIsValid and contentIsValid
        try:
            input_msg = await ctx.bot.wait_for("message", check=check_msg, timeout=600)
            if input_msg.content=="yes":
                removeConfigFile(acc_name, basic.IsHeroku)
                await ctx.channel.send("Removed.")
            elif input_msg.content=="no":
                await ctx.channel.send("The command has been canceled.")
        except asyncio.TimeoutError:
            await ctx.channel.send("The command has been timeout, and please retry.")
            return


    @commands.command(description="", pass_context=True)
    async def showIksmAcc(self, ctx: commands.Context):
        """登録されているnintendoアカウント一覧を表示します。"""
        if basic.IsHeroku: # for Heroku
            before_config_tmp=json.loads(os.getenv("iksm_configs", "{}"))
            before_config_jsons=eval(before_config_tmp) if type(before_config_tmp)==str else before_config_tmp
            acc_names = [k for k, v in before_config_jsons.items() ]
        else: # for not Heroku
            acc_names = [path.replace("_config.txt", "") for path in os.listdir(conifg_dir) if path.endswith("_config.txt")]
        await ctx.channel.send(f"There are {len(acc_names)} accounts registered in this bot.\n----\n\t"+"\n\t".join([f"{num+1} :\t`{acc}`"  for num, acc in enumerate(acc_names)]))


def setup(bot):
    bot.add_cog(Splat(bot))
