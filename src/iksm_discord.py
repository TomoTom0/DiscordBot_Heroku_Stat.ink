import requests, json, re, sys
import os, base64, hashlib
import uuid, time, random, string

session = requests.Session()

import json
import shutil, subprocess

sys.path.append(f"{os.path.dirname(__file__)}/../splatnet2statink")
from iksm import call_flapg_api, get_session_token
import discord
from discord.ext import commands
import asyncio

import basic
splat_path=basic.const_paths["splat_dir"]
tmp_dir=basic.const_paths["tmp_dir"]

# ------------/ discord functions /-----------------

# make config file
async def make_config_discord(API_KEY, conifg_dir, ctx: commands.Context, print_session=False):
	USER_LANG="ja-JP"
	A_VERSION="1.5.6"

	try:
		post_login, auth_code_verifier = log_in_discord(A_VERSION, ctx.channel)
	except Exception as e:
		ctx.channel.send(f"エラーが発生しました。{e}\nもう一度「?startIksm <API KEY>」からやり直してください。")
		return
	print_content=f"リンクをクリックしてログインし, 「この人にする」ボタンを長押し(PCなら右クリック)してリンク先のURLをコピーします\
		\n**注意: ボタンをそのままクリックするのではありません。**"
	await ctx.channel.send(post_login)
	new_token=""
	while new_token=="":
		try:
			await ctx.channel.send("URLをペーストしてください。キャンセルする場合は「cancel」と入力してください。")
			def check_url(msg):
				return msg.author.id==ctx.message.author.id and (msg.content.startswith("npf71b963c1b7b6d119://") or msg.content == "cancel")
			try:
				input_url = await ctx.bot.wait_for("message", check=check_url, timeout=600)
			except asyncio.TimeoutError:
				await ctx.channel.send("Timeoutです。もう一度「?startIksm <API KEY>」からやり直してください。")
				return

			if input_url.content == "cancel":
				await ctx.channel.send("Canceled.")
				return
			session_token_code = re.search('de=(.*)&', input_url.content)
			new_token = get_session_token(session_token_code.group(1), auth_code_verifier)
		except AttributeError:
			await ctx.channel.send("不適切なURLです。\nもう一度コピーしてきてください。")
		except KeyError: # session_token not found
			await ctx.channel.send("\niksm_sessionが見つかりませんでした。Nintendo Accountをログアウトしてから、もう一度行ってください。")

	acc_name, new_cookie = get_cookie_discord(new_token, USER_LANG, A_VERSION, ctx.channel)
	config_data = {"api_key": API_KEY, "cookie": new_cookie, "user_lang": USER_LANG, "session_token": new_token}

	# save config
	before_config_jsons=json.loads(os.getenv("iksm_configs", "{}"))
	try:
		before_config_jsons.update({acc_name: config_data})
	except:
		before_config_jsons={acc_name: config_data}
	json_configs=json.dumps(before_config_jsons)
	basic.update_env({"iksm_configs":json.dumps(json_configs)})

def auto_upload_iksm():
	# auto upload
	before_config_jsons=json.loads(os.getenv("iksm_configs", "{}"))
	for acc_name, v in before_config_jsons.items():
		# make config from ENV
		with open(f"{tmp_dir}/config.txt", "w") as f:
			f.dump(v)
		subprocess.run(["python3", f"{splat_path}/splatnet2statink.py", "-r"])

# -----------/ remake functions for discord_bot /-----------

def log_in_discord(ver, ctx_channel: commands.Context.channel):
	'''Logs in to a Nintendo Account and returns a session_token.'''

	version = ver

	auth_state = base64.urlsafe_b64encode(os.urandom(36))

	auth_code_verifier = base64.urlsafe_b64encode(os.urandom(32))
	auth_cv_hash = hashlib.sha256()
	auth_cv_hash.update(auth_code_verifier.replace(b"=", b""))
	auth_code_challenge = base64.urlsafe_b64encode(auth_cv_hash.digest())

	app_head = {
		'Host':                      'accounts.nintendo.com',
		'Connection':                'keep-alive',
		'Cache-Control':             'max-age=0',
		'Upgrade-Insecure-Requests': '1',
		'User-Agent':                'Mozilla/5.0 (Linux; Android 7.1.2; Pixel Build/NJH47D; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/59.0.3071.125 Mobile Safari/537.36',
		'Accept':                    'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8n',
		'DNT':                       '1',
		'Accept-Encoding':           'gzip,deflate,br',
	}

	body = {
		'state':                               auth_state,
		'redirect_uri':                        'npf71b963c1b7b6d119://auth',
		'client_id':                           '71b963c1b7b6d119',
		'scope':                               'openid user user.birthday user.mii user.screenName',
		'response_type':                       'session_token_code',
		'session_token_code_challenge':        auth_code_challenge.replace(b"=", b""),
		'session_token_code_challenge_method': 'S256',
		'theme':                               'login_form'
	}

	url = 'https://accounts.nintendo.com/connect/1.0.0/authorize'
	r = session.get(url, headers=app_head, params=body)

	post_login = r.history[0].url

	return post_login, auth_code_verifier


def get_cookie_discord(session_token, userLang, ver, ctx_channel:commands.Context.channel):
	'''Returns a new cookie provided the session_token.'''

	version = ver

	timestamp = int(time.time())
	guid = str(uuid.uuid4())

	app_head = {
		'Host':            'accounts.nintendo.com',
		'Accept-Encoding': 'gzip',
		'Content-Type':    'application/json; charset=utf-8',
		'Accept-Language': userLang,
		'Content-Length':  '439',
		'Accept':          'application/json',
		'Connection':      'Keep-Alive',
		'User-Agent':      'OnlineLounge/1.9.0 NASDKAPI Android'
	}

	body = {
		'client_id':     '71b963c1b7b6d119', # Splatoon 2 service
		'session_token': session_token,
		'grant_type':    'urn:ietf:params:oauth:grant-type:jwt-bearer-session-token'
	}

	url = "https://accounts.nintendo.com/connect/1.0.0/api/token"

	r = requests.post(url, headers=app_head, json=body)
	id_response = json.loads(r.text)

	# get user info
	try:
		app_head = {
			'User-Agent':      'OnlineLounge/1.9.0 NASDKAPI Android',
			'Accept-Language': userLang,
			'Accept':          'application/json',
			'Authorization':   'Bearer {}'.format(id_response["access_token"]),
			'Host':            'api.accounts.nintendo.com',
			'Connection':      'Keep-Alive',
			'Accept-Encoding': 'gzip'
		}
	except:
		ctx_channel.send(f"Not a valid autho ization request. Please delete config.txt and try again. \
		Error from Nintendo (in api/token step): \
		{json.dumps(id_response, indent=2)}")
		return -1
	url = "https://api.accounts.nintendo.com/2.0.0/users/me"

	r = requests.get(url, headers=app_head)
	user_info = json.loads(r.text)

	nickname = user_info["nickname"]

	# get access token
	app_head = {
		'Host':             'api-lp1.znc.srv.nintendo.net',
		'Accept-Language':  userLang,
		'User-Agent':       'com.nintendo.znca/1.9.0 (Android/7.1.2)',
		'Accept':           'application/json',
		'X-ProductVersion': '1.9.0',
		'Content-Type':     'application/json; charset=utf-8',
		'Connection':       'Keep-Alive',
		'Authorization':    'Bearer',
		# 'Content-Length':   '1036',
		'X-Platform':       'Android',
		'Accept-Encoding':  'gzip'
	}

	body = {}
	try:
		idToken = id_response["access_token"]

		flapg_nso = call_flapg_api(idToken, guid, timestamp, "nso")

		parameter = {
			'f':          flapg_nso["f"],
			'naIdToken':  flapg_nso["p1"],
			'timestamp':  flapg_nso["p2"],
			'requestId':  flapg_nso["p3"],
			'naCountry':  user_info["country"],
			'naBirthday': user_info["birthday"],
			'language':   user_info["language"]
		}
	except SystemExit:
		return -1
	except:
		ctx_channel.send(f"Error(s) from Nintendo: \
		{json.dumps(id_response, indent=2)} \
		{json.dumps(user_info, indent=2)}")
		return -2
	body["parameter"] = parameter

	url = "https://api-lp1.znc.srv.nintendo.net/v1/Account/Login"

	r = requests.post(url, headers=app_head, json=body)
	splatoon_token = json.loads(r.text)

	try:
		idToken = splatoon_token["result"]["webApiServerCredential"]["accessToken"]
		flapg_app = call_flapg_api(idToken, guid, timestamp, "app")
	except:
		ctx_channel.send("Error from Nintendo (in Account/Login step):"+\
		json.dumps(splatoon_token, indent=2))
		return -1

	# get splatoon access token
	try:
		app_head = {
			'Host':             'api-lp1.znc.srv.nintendo.net',
			'User-Agent':       'com.nintendo.znca/1.9.0 (Android/7.1.2)',
			'Accept':           'application/json',
			'X-ProductVersion': '1.9.0',
			'Content-Type':     'application/json; charset=utf-8',
			'Connection':       'Keep-Alive',
			'Authorization':    'Bearer {}'.format(splatoon_token["result"]["webApiServerCredential"]["accessToken"]),
			'Content-Length':   '37',
			'X-Platform':       'Android',
			'Accept-Encoding':  'gzip'
		}
	except:
		ctx_channel.send(f"Error from Nintendo (in Account/Login step):\
		{json.dumps(splatoon_token, indent=2)}")
		return -1

	body = {}
	parameter = {
		'id':                5741031244955648,
		'f':                 flapg_app["f"],
		'registrationToken': flapg_app["p1"],
		'timestamp':         flapg_app["p2"],
		'requestId':         flapg_app["p3"]
	}
	body["parameter"] = parameter

	url = "https://api-lp1.znc.srv.nintendo.net/v2/Game/GetWebServiceToken"

	r = requests.post(url, headers=app_head, json=body)
	splatoon_access_token = json.loads(r.text)

	# get cookie
	try:
		app_head = {
			'Host':                    'app.splatoon2.nintendo.net',
			'X-IsAppAnalyticsOptedIn': 'false',
			'Accept':                  'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
			'Accept-Encoding':         'gzip,deflate',
			'X-GameWebToken':          splatoon_access_token["result"]["accessToken"],
			'Accept-Language':         userLang,
			'X-IsAnalyticsOptedIn':    'false',
			'Connection':              'keep-alive',
			'DNT':                     '0',
			'User-Agent':              'Mozilla/5.0 (Linux; Android 7.1.2; Pixel Build/NJH47D; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/59.0.3071.125 Mobile Safari/537.36',
			'X-Requested-With':        'com.nintendo.znca'
		}
	except:
		ctx_channel.send("Error from Nintendo (in Game/GetWebServiceToken step):"+\
		json.dumps(splatoon_access_token, indent=2))
		return -1

	url = "https://app.splatoon2.nintendo.net/?lang={}".format(userLang)
	r = requests.get(url, headers=app_head)
	return nickname, r.cookies["iksm_session"]

