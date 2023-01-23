import subprocess
import shutil
import asyncio
from discord.ext import commands
import discord
import requests
import json
import re
import sys
import os
import base64
import hashlib
import uuid
import time
import random
import string
import datetime
import asyncio
from distutils.version import StrictVersion

import basic
GLOBAL_versions_default = {"NSO": "1.11.0", "A": "1.5.11", "date": 0}
GLOBAL_versions_saved = GLOBAL_versions_default
GLOBAL_splat_dir = basic.const_paths["splat_dir"]
GLOBAL_tmp_dir = basic.const_paths["tmp_dir"]
GLOBAL_isHeroku = basic.IsHeroku

# # functions


def decomposeKey(key=""):
    return {
        "name": re.sub(r"_\d{10}$", "", key),
        "key": key,
        "time": (re.findall(r"(?<=_)\d{10}$", key)+[0])[0]
    }


def obtainAccNames():
    name_keys = []
    if GLOBAL_isHeroku is True:  # for Heroku
        before_config_tmp = json.loads(os.getenv("iksm_configs", "{}"))
        before_config_jsons = eval(before_config_tmp) if isinstance(
            before_config_tmp, str) else before_config_tmp
        name_keys = list(before_config_jsons.keys())
    else:
        name_keys = [path.replace("_config.txt", "") for path in os.listdir(
            GLOBAL_tmp_dir) if path.endswith("_config.txt")]
    return [decomposeKey(s) for s in name_keys]


def obtainAccInfo(acc_name_key: str):
    if GLOBAL_isHeroku:
        before_config_tmp = json.loads(os.getenv("iksm_configs", "{}"))
        before_config_jsons = eval(before_config_tmp) if isinstance(
            before_config_tmp, str) else before_config_tmp
        json_file = before_config_jsons[acc_name_key]
    else:
        with open(f"{GLOBAL_tmp_dir}/{acc_name_key}_config.txt", "r") as f:
            json_file = json.loads(f.read())
    return json_file


def obtainDate(timestamp=0):
    timestamp_int = int(timestamp) if f"{timestamp}".isdecimal() else 0
    if timestamp_int == 0:
        return ""
    else:
        date_tmp = datetime.datetime.fromtimestamp(timestamp_int)
        return date_tmp.date().isoformat()


async def checkAcc(ctx: commands.Context, acc_name: str):
    acc_name_sets = obtainAccNames()
    valid_name_keys = [s for s in acc_name_sets if s["name"] == acc_name]
    if len(valid_name_keys) == 1:
        return valid_name_keys[0]
    elif len(valid_name_keys) > 1:

        content = f"There are {len(valid_name_keys)} accounts with the same name, `{acc_name}`.\n" +\
            f"Select with the number.(1-{len(valid_name_keys)})\n" +\
            "\t"+"\n\t".join(["**{}**: `{}` on {}".format(num+1, s["name"],
                                                          obtainDate(s["key"])) for num, s in enumerate(valid_name_keys)])
        await ctx.channel.send(content)

        def check_msg(msg):
            authorIsValid = (msg.author.id == ctx.author.id)
            contentIsValid = msg.content.isdecimal() and int(
                msg.content) in range(1, len(valid_name_keys)+1)
            return authorIsValid and contentIsValid
        input_msg = await ctx.bot.wait_for("message", check=check_msg)
        input_content = input_msg.content
        return valid_name_keys[int(input_content)-1]
    else:  # len(valid_name_keys)==0
        await ctx.channel.send(f"`{acc_name}` is not registered.")
        return {"name": ""}


async def auto_upload_iksm():
    # auto upload
    splat_path = GLOBAL_splat_dir
    if GLOBAL_isHeroku is True:  # for Heroku
        before_config_tmp = json.loads(os.getenv("iksm_configs", "{}"))
        before_config_jsons = eval(before_config_tmp) if isinstance(
            before_config_tmp, str) else before_config_tmp
        for acc_name, v in before_config_jsons.items():
            if v["api_key"] in ["0"*43, "skip"]:  # API_KEY is not setted
                continue
            # make config from ENV
            with open(f"{GLOBAL_tmp_dir}/config.txt", "w") as f:
                json.dump(v, f)
            subprocess.run(
                ["python3", f"{splat_path}/splatnet2statink.py", "-r"])
            with open(f"{GLOBAL_tmp_dir}/config.txt") as f:
                v = json.load(f)
            before_config_jsons[acc_name] = v
    else:  # for not Heroku
        config_names = [path for path in os.listdir(
            GLOBAL_tmp_dir) if path.endswith("_config.txt")]
        for config_name in config_names:
            shutil.copy(f"{GLOBAL_tmp_dir}/{config_name}",
                        f"{GLOBAL_tmp_dir}/config.txt")
            with open(f"{GLOBAL_tmp_dir}/config.txt") as f:
                config_json = json.load(f)
            api_key = config_json["api_key"]
            if api_key in ["0"*43, "skip"]:  # API_KEY is not setted
                continue
            subprocess.run(
                ["python3", f"{splat_path}/splatnet2statink.py", "-r"])
            shutil.copy(f"{GLOBAL_tmp_dir}/config.txt",
                        f"{GLOBAL_tmp_dir}/{config_name}")
        # if len(config_names)!=0:
        #	os.remove(f"{GLOBAL_tmp_dir}/config.txt")


async def autoUploadCycle(next_time=900):
    config_dir = GLOBAL_tmp_dir if GLOBAL_isHeroku else GLOBAL_splat_dir
    config_path = config_dir+"/config.txt"
    if not os.path.isfile(config_path):
        with open(config_path, "w") as f:
            f.write(json.dumps({}))
    nowtime = datetime.datetime.now()
    tmp_next_time = next_time-(nowtime.minute*60 + nowtime.second) % next_time
    print(f"{datetime.datetime.now()} / Next Check Time : in {tmp_next_time} sec")
    await asyncio.sleep(tmp_next_time)

    while True:
        # for splatoon2, stat.ink
        await auto_upload_iksm()
        nowtime = datetime.datetime.now()
        tmp_next_time = next_time - \
            (nowtime.minute*60+nowtime.second) % next_time
        print(f"Next Check Time : in {tmp_next_time} sec")
        await asyncio.sleep(tmp_next_time)

# # ------------/ class /---------------


class makeConfig():
    def __init__(self):
        self.versions = self.obtainVersions()
        self.USER_LANG = "ja-JP"
        self.session = requests.Session()
        self.ctx = None
        self.isHeroku = GLOBAL_isHeroku
        self.config_dir = GLOBAL_tmp_dir

    # ## obtain versions
    """def obtainGitHubContent(self, user: str, repo: str, path: str):
        gitHubToken = os.environ.get("GitHubToken", False)
        headers_base = {"Accept": "application/vnd.github.v3+json"}
        headers_auth = {} if gitHubToken is False else {
            "Authorization": f"Token {gitHubToken}"}
        headers_base.update(headers_auth)
        git_content_url = f"https://api.github.com/repos/{user}/{repo}/contents/{path}"
        res = requests.request(url=git_content_url,
                               method="get", headers=headers_base)
        content = res.json()["content"]
        return base64.b64decode(content).decode()"""

    def obtainVersions(self):
        global GLOBAL_versions_saved
        # update check
        time_now = time.time()
        old_versions = GLOBAL_versions_saved

        if time_now - old_versions["date"] < 6 * 3600:
            return old_versions

        versions = {"date": time_now}
        versions_default = GLOBAL_versions_default
        try:
            # NSO_VERSION
            # from Ninendo Home page
            url = "https://www.nintendo.co.jp/support/app/nintendo_switch_online_app/index.html"
            res = requests.get(url)
            NSO_version_lines = re.findall(
                r"Ver.\s*\d+\.\d+\.\d+", res.text)+[versions_default["NSO"]]
            NSO_versions = [re.findall(r"\d+\.\d+\.\d+", s)[0]
                            for s in NSO_version_lines]
            versions["NSO"] = sorted(NSO_versions, key=StrictVersion)[-1]

            # A_VERSION
            repoInfo_splat = {"user": "frozenpandaman",
                              "repo": "splatnet2statink", "path": "splatnet2statink.py"}
            #splat_content = self.obtainGitHubContent(**repoInfo_splat)
            #A_lines = re.findall(r"(?<=A_VERSION).*\d+\.\d+\.\d+.*", splat_content)

            def obtainGitHubUrl(user, repo, path):
                return f"https://github.com/{user}/{repo}/blob/master/{path}"
            gitHubUrl = obtainGitHubUrl(**repoInfo_splat)
            res_splat = requests.get(gitHubUrl)
            A_lines = re.findall(
                r"A_VERSION.*&quot;\d+\.\d+\.\d+&quot;", res_splat.text)
            versions["A"] = re.findall(
                r"\d+\.\d+\.\d+", A_lines[0])[0] if len(A_lines) > 0 else versions_default["A"]
        except Exception as e:
            versions = versions_default

        GLOBAL_versions_saved = versions
        return versions

    async def send_msg(self, content: str, isError=False):
        ctx = self.ctx
        if isinstance(ctx, commands.Context) and isError is False:
            await ctx.channel.send(content)
        else:
            print(content)

    # ## make config
    async def make_config_discord(self, API_KEY, ctx=None, print_session=False):
        self.ctx = ctx
        config_dir = self.config_dir
        userLang = self.USER_LANG
        NSO_VERSION = self.versions["NSO"]

        self.log_in_discord()
        post_login = self.post_login
        print_content = f"リンクをクリックしてログインし、「この人にする」ボタンを長押し(PCなら右クリック)してリンク先のURLをコピーしてください。" +\
            "**注意: ボタンをそのままクリックするのではありません。**\n"+post_login+"\n" +\
            "URLをペーストしてください。キャンセルする場合は`cancel`と入力してください。"
        await self.send_msg(print_content)

        while True:
            def check_content(content: str):
                contentIsValidUrl = content.startswith("npf71b963c1b7b6d119://") and\
                    re.findall(
                        r"(?<=session_token_code=)[^&]*(?=&)", content) != []
                contetnIsValidCommand = content in ["cancel"]
                return contentIsValidUrl or contetnIsValidCommand
            if isinstance(ctx, commands.Context):
                def check_url(msg):
                    authorIsValid = (msg.author.id == ctx.message.author.id)
                    contentIsValid = check_content(msg.content)
                    return authorIsValid and contentIsValid
                try:
                    input_url = await ctx.bot.wait_for("message", check=check_url, timeout=600)
                    input_content = input_url.content
                except asyncio.TimeoutError:
                    await self.send_msg("Timeoutです。\nもう一度`?startIksm <API KEY>`からやり直してください。")
                    return
            else:
                input_content = input()
                if check_content(input_content) is False:
                    continue
            if input_content == "cancel":
                await self.send_msg("Canceled.")
                return
            break
        session_token_code_tmp = re.findall(
            r"(?<=session_token_code=)[^&]*(?=&)", input_content)
        session_token_code = session_token_code_tmp[0]
        new_token = self.get_session_token_discord(
            session_token_code)
        if new_token is None:
            await self.send_msg("\niksm_sessionが見つかりませんでした。Nintendo Accountからログアウトし、もう一度はじめからやり直してください。")
            return

        await self.send_msg("操作中です。しばらくお待ちください。")
        await self.get_cookie_discord(new_token)
        if self.iksm_session is None:
            return
        acc_name = self.nickname
        new_cookie = self.iksm_session

        config_data = {"api_key": API_KEY, "cookie": new_cookie,
                       "user_lang": userLang, "session_token": new_token}
        # save config
        time_10 = format(int(time.time()), "010")
        if self.isHeroku is True:  # for Heroku
            before_config_tmp = json.loads(os.getenv("iksm_configs", "{}"))
            before_config_jsons = eval(before_config_tmp) if isinstance(
                before_config_tmp, str) else before_config_tmp
            new_config = {f"{acc_name}_{time_10}": config_data}
            if isinstance(before_config_jsons, dict):
                before_config_jsons.update(new_config)
            else:
                before_config_jsons = new_config
            json_configs = json.dumps(before_config_jsons)
            basic.update_env({"iksm_configs": json.dumps(json_configs)})
        else:  # for not Heroku
            os.makedirs(config_dir, exist_ok=True)
            with open(f"{config_dir}/{acc_name}_{time_10}_config.txt", "w") as f:
                f.write(json.dumps(config_data, indent=4,
                                   sort_keys=True, separators=(",", ": ")))
        return acc_name

    # # -----------/ remake functions for discord_bot /-----------

    # ## log_in

    def log_in_discord(self):
        """Logs in to a Nintendo Account and returns a session_token."""
        NSO_VERSION = self.versions["NSO"]
        A_VERSION = self.versions["A"]

        session = self.session

        auth_state = base64.urlsafe_b64encode(os.urandom(36))

        auth_code_verifier = base64.urlsafe_b64encode(os.urandom(32))
        auth_cv_hash = hashlib.sha256()
        auth_cv_hash.update(auth_code_verifier.replace(b"=", b""))
        auth_code_challenge = base64.urlsafe_b64encode(auth_cv_hash.digest())

        app_head = {
            "Host":                      "accounts.nintendo.com",
            "Connection":                "keep-alive",
            "Cache-Control":             "max-age=0",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent":                "Mozilla/5.0 (Linux; Android 7.1.2; Pixel Build/NJH47D; wv) " +
            "AppleWebKit/537.36 (KHTML, like Gecko) " +
            "Version/4.0 Chrome/59.0.3071.125 Mobile Safari/537.36",
            "Accept":                    "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8n",
            "DNT":                       "1",
            "Accept-Encoding":           "gzip,deflate,br",
        }

        body = {
            "state":                               auth_state,
            "redirect_uri":                        "npf71b963c1b7b6d119://auth",
            "client_id":                           "71b963c1b7b6d119",
            "scope":                               "openid user user.birthday user.mii user.screenName",
            "response_type":                       "session_token_code",
            "session_token_code_challenge":        auth_code_challenge.replace(b"=", b""),
            "session_token_code_challenge_method": "S256",
            "theme":                               "login_form"
        }

        url = "https://accounts.nintendo.com/connect/1.0.0/authorize"
        r = session.get(url, headers=app_head, params=body)

        self.post_login = r.history[0].url
        self.auth_code_verifier = auth_code_verifier

        # return post_login, auth_code_verifier

    # ##  -------get_cookie------

    async def get_cookie_discord(self, session_token):
        """Returns a new cookie provided the session_token."""

        userLang = self.USER_LANG
        NSO_VERSION = self.versions["NSO"]
        A_VERSION = self.versions["A"]
        self.iksm_session = None
        self.nickname = None

        # step 1: obtain id_response
        timestamp = int(time.time())
        guid = str(uuid.uuid4())

        app_head = {
            "Host":            "accounts.nintendo.com",
            "Accept-Encoding": "gzip",
            "Content-Type":    "application/json; charset=utf-8",
            "Accept-Language": userLang,
            "Content-Length":  "439",
            "Accept":          "application/json",
            "Connection":      "Keep-Alive",
            "User-Agent":      f"OnlineLounge/{NSO_VERSION} NASDKAPI Android"
        }

        body = {
            "client_id":     "71b963c1b7b6d119",  # Splatoon 2 service
            "session_token": session_token,
            "grant_type":    "urn:ietf:params:oauth:grant-type:jwt-bearer-session-token"
        }

        url = "https://accounts.nintendo.com/connect/1.0.0/api/token"

        r = requests.post(url, headers=app_head, json=body)
        id_response = json.loads(r.text)
        self.id_response = id_response

        # check whether idToken is Valid or not
        idToken = id_response.get("access_token", None)
        if idToken is None:
            content = "Not a valid authorization request. Please delete config.txt and try again. \
            Error from Nintendo (in api/token step)"
            await self.send_msg(content)
            content2 = "id_response is:\n"+json.dumps(id_response, indent=2)
            await self.send_msg(content+"\n"+content2, isError=True)
            return

        # idToken is Valid
        # step2: get user info
        app_head = {
            "User-Agent":      f"OnlineLounge/{NSO_VERSION} NASDKAPI Android",
            "Accept-Language": userLang,
            "Accept":          "application/json",
            "Authorization":   f"Bearer {idToken}",
            "Host":            "api.accounts.nintendo.com",
            "Connection":      "Keep-Alive",
            "Accept-Encoding": "gzip"
        }
        url = "https://api.accounts.nintendo.com/2.0.0/users/me"

        r = requests.get(url, headers=app_head)
        user_info = json.loads(r.text)
        self.user_info = user_info

        # get access token
        # step3: splatoon token
        app_head = {
            "Host":             "api-lp1.znc.srv.nintendo.net",
            "Accept-Language":  userLang,
            "User-Agent":       f"com.nintendo.znca/{NSO_VERSION} (Android/7.1.2)",
            "Accept":           "application/json",
            "X-ProductVersion": f"{NSO_VERSION}",
            "Content-Type":     "application/json; charset=utf-8",
            "Connection":       "Keep-Alive",
            "Authorization":    "Bearer",
            # "Content-Length":   "1036",
            "X-Platform":       "Android",
            "Accept-Encoding":  "gzip"
        }

        # step3-1: flapg api
        flapg_nso = await self.call_flapg_api_discord(idToken, guid, timestamp, "nso")

        keysAreNotExisting = not all([
            isinstance(flapg_nso, dict),
            isinstance(user_info, dict)
        ]) or not all([
            set(["f", "p1", "p2", "p3"]) <= set(flapg_nso.keys()),
            set(["country", "birthday", "language"]) <= set(user_info.keys())
        ])
        if keysAreNotExisting is True:
            await self.send_msg(f"Error(s) from Nintendo with flapg_api")
            return

        parameter = {
            "f":          flapg_nso["f"],
            "naIdToken":  flapg_nso["p1"],
            "timestamp":  flapg_nso["p2"],
            "requestId":  flapg_nso["p3"],
            "naCountry":  user_info["country"],
            "naBirthday": user_info["birthday"],
            "language":   user_info["language"]
        }
        # except SystemExit:
        #    return -1
        body = {"parameter": parameter}
        url = "https://api-lp1.znc.srv.nintendo.net/v1/Account/Login"
        r = requests.post(url, headers=app_head, json=body)
        splatoon_token = json.loads(r.text)

        # step4: splatoon access token
        splat_idToken = splatoon_token.get("result", {}).get(
            "webApiServerCredential", {}).get("accessToken", None)
        if splat_idToken is None:
            await self.send_msg("Error from Nintendo (in Account/Login step):" +
                                json.dumps(splatoon_token, indent=2))
            return
        # step4-1: flapg api
        flapg_app = await self.call_flapg_api_discord(splat_idToken, guid, timestamp, "app")

        # get splatoon access token
        app_head = {
            "Host":             "api-lp1.znc.srv.nintendo.net",
            "User-Agent":       f"com.nintendo.znca/{NSO_VERSION} (Android/7.1.2)",
            "Accept":           "application/json",
            "X-ProductVersion": f"{NSO_VERSION}",  # update
            "Content-Type":     "application/json; charset=utf-8",
            "Connection":       "Keep-Alive",
            "Authorization":    f"Bearer {splat_idToken}",
            "Content-Length":   "37",
            "X-Platform":       "Android",
            "Accept-Encoding":  "gzip"
        }

        # step5: splatoon access token
        if not isinstance(flapg_app, dict) or not set(["f", "p1", "p2", "p3"]) <= set(flapg_app.keys()):
            await self.send_msg(f"Error(s) from Nintendo with flapg_api")
            return
        parameter = {
            "id":                5741031244955648,
            "f":                 flapg_app["f"],
            "registrationToken": flapg_app["p1"],
            "timestamp":         flapg_app["p2"],
            "requestId":         flapg_app["p3"]
        }
        body = {"parameter": parameter}

        url = "https://api-lp1.znc.srv.nintendo.net/v2/Game/GetWebServiceToken"

        r = requests.post(url, headers=app_head, json=body)
        splatoon_access_token = json.loads(r.text)

        # get cookie
        X_GameWebToken = splatoon_access_token.get(
            "result", {}).get("accessToken", None)
        try:
            app_head = {
                "Host":                    "app.splatoon2.nintendo.net",
                "X-IsAppAnalyticsOptedIn": "false",
                "Accept":                  "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Encoding":         "gzip,deflate",
                "X-GameWebToken":          X_GameWebToken,
                "Accept-Language":         userLang,
                "X-IsAnalyticsOptedIn":    "false",
                "Connection":              "keep-alive",
                "DNT":                     "0",
                "User-Agent":              "Mozilla/5.0 (Linux; Android 7.1.2; Pixel Build/NJH47D; wv) " +
                "AppleWebKit/537.36 (KHTML, like Gecko) " +
                "Version/4.0 Chrome/59.0.3071.125 Mobile Safari/537.36",
                "X-Requested-With":        "com.nintendo.znca"
            }
        except:
            await self.send_msg("Error from Nintendo (in Game/GetWebServiceToken step):" +
                                json.dumps(splatoon_access_token, indent=2))
            return

        url = "https://app.splatoon2.nintendo.net/?lang={}".format(userLang)
        r = requests.get(url, headers=app_head)

        nickname = user_info.get("nickname", None)
        iksm_session = r.cookies.get("iksm_session", None)
        self.iksm_session = iksm_session
        self.nickname = nickname

    # ## get_session_token

    # use for discord
    def get_session_token_discord(self, session_token_code):
        """Helper function for log_in()."""

        NSO_VERSION = self.versions["NSO"]
        session = self.session
        auth_code_verifier = self.auth_code_verifier

        app_head = {
            "User-Agent":      f"OnlineLounge/{NSO_VERSION} NASDKAPI Android",
            "Accept-Language": "en-US",
            "Accept":          "application/json",
            "Content-Type":    "application/x-www-form-urlencoded",
            "Content-Length":  "540",
            "Host":            "accounts.nintendo.com",
            "Connection":      "Keep-Alive",
            "Accept-Encoding": "gzip"
        }

        body = {
            "client_id":                   "71b963c1b7b6d119",
            "session_token_code":          session_token_code,
            "session_token_code_verifier": auth_code_verifier.replace(b"=", b"")
        }

        url = "https://accounts.nintendo.com/connect/1.0.0/api/session_token"
        r = session.post(url, headers=app_head, data=body)
        return json.loads(r.text).get("session_token", None)

    # ## call_flapg_api

    # use for discord
    async def call_flapg_api_discord(self, id_token, guid, timestamp, typeIn):
        """Passes in headers to the flapg API (Android emulator) and fetches the response."""
        A_VERSION = self.versions["A"]
        x_hash = await self.get_hash_from_s2s_api_discord(id_token, timestamp)
        if x_hash is None:
            await self.send_msg("Errors from splatnet2statink API")
            return None

        url = "https://flapg.com/ika2/api/login?public"
        api_app_head = {
            "x-token": id_token,
            "x-time":  str(timestamp),
            "x-guid":  guid,
            "x-hash": x_hash,
            "x-ver":   "3",
            "x-iid":   typeIn
        }
        # print(api_app_head)
        try:
            api_response = requests.get(url, headers=api_app_head)
            # print(api_response.text)
        except Exception as e:
            error_message = api_response.text + "\n"+e
            print(error_message)
            return None

        f = json.loads(api_response.text).get("result", None)
        # print(f)
        return f

    # ## hash_from_s2s

    # use for discord
    async def get_hash_from_s2s_api_discord(self, id_token, timestamp):
        """Passes an id_token and timestamp to the s2s API and fetches the resultant hash from the response."""
        A_VERSION = self.versions["A"]

        # proceed normally
        api_app_head = {"User-Agent": "splatnet2statink/{}".format(A_VERSION)}
        api_body = {"naIdToken": id_token, "timestamp": timestamp}
        url = "https://elifessler.com/s2s/api/gen2"
        api_response = requests.post(
            url, headers=api_app_head, data=api_body)
        #print(api_response.ok, api_response.content)
        if not api_response.ok:
            print(api_response.text)
            return None
        return json.loads(api_response.text).get("hash", None)
