#! /usr/bin/env python3
import os
import shutil
import discord
from discord.ext import commands
import requests

# heroku or not
IsHeroku = bool(os.getenv("DYNO", False))

# 環境変数からDiscord bot tokenを読み取る
DISCORD_TOKENS = {
    "0": os.environ["DISCORD_BOT_TOKEN"]}

# localかherokuかでpathを調整する
const_paths = {
    "tmp_dir": "/tmp" if IsHeroku else f"{os.path.dirname(__file__)}/../configs",
    "splat_dir": f"{os.path.dirname(__file__)}/../splatnet2statink"
}


def update_env(new_envs={}):  # for Heroku
    """環境変数の変更とherokuの環境変数の更新を行います。その後、botは再起動されます。"""
    if not IsHeroku:
        return
    for k, v in new_envs.items():
        os.environ[k] = v
    # HEROKU_APP_NAME, set default value
    app_name = os.getenv("HEROKU_APP_NAME", "")
    if app_name=="":
        print("環境変数のHEROKU_APP_NAMEが定義されていません。")
        return
    patch_url = f"https://api.heroku.com/apps/{app_name}/config-vars"
    headers = {"Authorization": f"Bearer {os.environ['HEROKU_APIKEY']}",
               "Content-Type": "application/json",
               "Accept": "application/vnd.heroku+json; version=3"}
    res = requests.patch(patch_url, headers=headers, json=new_envs)
    print(res.json())
    return res
