#! /usr/bin/env python3
import os, shutil
import discord
from discord.ext import commands
import requests

# 環境変数からDiscord bot tokenを読み取る
DISCORD_TOKENS = {
    "0":os.environ["DISCORD_BOT_TOKEN"]}

# localかherokuかでpathを調整する
const_paths={
    "tmp_dir":"/tmp" if os.getenv("DYNO", False) else f"{os.path.dirname(__file__)}/../tmp",
    "splat_dir":f"{os.path.dirname(__file__)}/../splatnet2statink"
}


def update_env(new_envs={}):
    """環境変数の変更とherokuの環境変数の更新を行う。その後、botは再起動される。"""
    for k, v in new_envs.items():
        os.environ[k]=v
    app_name=os.getenv("HEROKU_APP_NAME", "app-splat") #HEROKU_APP_NAME
    if app_name=="":
        print("環境変数のHEROKU_APP_NAMEが定義されていません。")
        return
    patch_url = f"https://api.heroku.com/apps/{app_name}/config-vars"
    headers= {"Authorization": f"Bearer {os.getenv('HEROKU_API')}",
        "Content-Type":"application/json",
        "Accept":"application/vnd.heroku+json; version=3"}
    res=requests.patch(patch_url, headers=headers, json=new_envs)