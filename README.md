# Discord Bot for Stat.ink X Heroku

PC初心者でも、スマホしかない人でも、**stat.inkにSplatoonの戦績を自動アップロードするdiscord bot**を作れるようにしたいと考え、このscriptを書きました。

- Botの起動からやりたい (Heroku利用・初心者はこちら) -> [#事前準備](#事前準備), [#Bot起動まで](#Bot起動まで)
- Botの起動からやりたい (Heroku以外利用) -> [#事前準備・Bot起動まで(Heroku以外)](#事前準備・Bot起動まで(Heroku以外))
- すでにBotの起動ができている -> [#Botの使い方](#Botの使い方)
- 連絡先 -> [#Contact Me](#contact-me)

## 事前準備
### サービスへの登録など
無料でやるために、いくつかのサービスを利用します。アカウントをすでに持っているなら、追加で作成する必要はありません。
以下のstat.inkのAPI KEYやDISCORD BOT TOKENはメモ帳にでもコピーしておいてください。

- stat.ink : アカウント作成、API KEYコピー
- Heroku : アカウント作成、API KEYコピー
    - URL : https://signup.heroku.com/
- discord : アカウント作成、DISCORD BOT TOKENコピー、BOTのserverへの追加
    - 参考 [Discord Botアカウント初期設定ガイド for Developer](https://qiita.com/1ntegrale9/items/cb285053f2fa5d0cccdf)のうち**はじめに~サーバーへの登録**

### heroku API KEY取得

1. アカウントのアイコンマークをクリックし、Account settingsをクリックします。
<img with="80%" src="img/heroku_api_ss1.png"/>

2. API Keyの欄でRevealをクリックし、表示されたAPI KEYをメモ帳などにコピーしておきます。
<img with="80%" src="img/heroku_api_ss2.png"/>

### stat.ink API KEY取得

1. stat.inkの自分のアカウントをクリックし、「プロフィールと設定」をクリックします。
2. APIキーの欄で「APIキーを表示」をクリックし、表示されたAPI KEYをメモ帳などにコピーしておきます。

<img with="80%" src="img/statink_apikey.png"/>

## Bot起動まで
### HerokuへDeploy
1. **あらかじめブラウザまたはアプリのHerokuにログインしておきます。**
2. ↓このボタンをクリックします。

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

3. しばらく待機します。画面が切り替わらなければページをリロード。
4. app-nameに好みの名前を入力して
    - PC : `Deploy app`をクリックし、しばらく待機してDeployが完了したら`Manage App`をクリック。
    - スマホ : `Create app`をクリックする。

<img with="80%" src="img/heroku_deploy.png"/>

### 環境変数の登録 (API KEY、TOKENなど)

続けて、環境変数としてTOKENなどを登録します。
1. Setting<img height="20px" src="img/heroku_icon_setting.png"></img> の中のConfig Varsの欄へ。
2. Reveal Config Varsをクリックして、以下の環境変数を入力していきます。  
   KEYとVALUEを1組入力するごとに`Add`をクリックします。  

|KEY|VALUE|
|-|-|
|DISCORD_BOT_TOKEN|コピーしておいたDISCORD BOT TOKEN|
|HEROKU_APP_NAME|HEROKUのapp-name|
|HEROKU_APIKEY|コピーしておいたHEROKUのAPI KEY|

<img with="80%" src="img/heroku_env.png"/>

### Botを起動

メニューの欄のResources<img height="20px" src="img/heroku_icon_resource.png"></img>へ。
1. 鉛筆マーク<img height="20px" src="img/heroku_icon_pencil.png"></img>をクリックし、バー<img height="20px" src="img/heroku_toggle_off.png"></img>を右にスライドして青く<img height="20px" src="img/heroku_toggle_on.png"></img>なればOK。
2. `Confirm`をクリックすれば、しばらくするとDiscord Botが起動します。

Botのいるサーバーで`?help`と入力してBotから反応があれば起動完了です。
<img with="80%" src="img/discord_help.png"/>

## 事前準備・Bot起動まで(Heroku以外)
GCPなどHeroku以外のサービスでDiscord Botを利用する方法を解説します。ある程度初心者でないことを想定して、こちらの解説は簡単にしています。

### 事前準備
- stat.ink : アカウント作成、API KEYコピー
- discord : アカウント作成、DISCORD BOT TOKENコピー、BOTのserverへの追加
    - 参考 [Discord Botアカウント初期設定ガイド for Developer](https://qiita.com/1ntegrale9/items/cb285053f2fa5d0cccdf)のうち**はじめに~サーバーへの登録**

### Bot起動まで
`git clone`などでダウンロードし、`pip3 install -r requirements.txt`で必要なライブラリをインストールします。最後に`python3 src/main.py`でdiscord botを起動します。terminalにエラーメッセージが出なければ大丈夫です。`screen`は必要に応じて利用してください。

## Botの使い方
### BotへのNintendoアカウント登録
`?startIksm <STATINK_API_KEY>`
1. stat.inkのAPI KEYを用意しておきます。
2. botとのDMなどで`?startIksm <STATINK_API_KEY>`のように、`?startIksm`に続けてAPI KEYを入力して送信します。
(**botと同じサーバーに加入していれば、アカウントの設定にもよりますが、そのbotとDMを行うことが可能です。**)

> ※注意
**API KEYやTOKENなどと呼ばれるものは、すべてアカウント名とパスワードのセットと等価です。他人にばれることはとても危険なことです。**
家族やごく親しい友人しかいないサーバーでは大丈夫かもしれませんが、できるだけbotとのDMで`?startIksm`は行ってください。

3. すると、botからURLが送られてくるのでそのリンクをタップします。
<img with="80%" src="img/discord_startIksm.png"/>
4. リンク先でログインすると、連携アカウントの選択画面になるので、
**「この人にする」を右クリック(スマホなら長押し)して、リンク先のURLをコピーします。**
<img with="80%" src="img/nintendo_select.png"/>

5. discordに戻り、コピーしたリンクを貼り付け、少し待つと`新たにアカウントが登録されました。`と表示されます。
<img with="80%" src="img/discord_startIksm2.png"/>

ここまでできれば、戦績の定期アップロードは自動で15分ごとに行われます。(毎時00/15/30/45分です。)
お疲れ様です。

### 各種コマンド
`?help Splat`とBotに入力することでも確認できます。

|コマンド|引数|説明|
|-|-|-|
|`?startIksm`|STAT_INK_API_KEY| 新たにiksm_sessionを取得し、botにアカウントを登録します。 事前にstat.inkの登録を完了し、API KEYを取得しておいてください。|
|`?checkIksm`|acc_name|指定されたアカウントのiksm_sessionを表示します。|
|`?rmIksm`|acc_name|指定されたアカウントの情報を削除します。|
|`?showIksm`|なし|登録されているnintendoアカウント一覧を表示します。|

## Botがうまく動かない

よく分からないかもしれませんが、logを確認しましょう。  
Herokuを開いて、Open appの横のMore->view logsをクリック。そこで表示されるlogから原因を探ってください。

<img height="300px" src="img/heroku_menu_more.png"/>

同じIPアドレスから短時間に何度もtokenの取得を行おうとした場合、spamとみなされて、しばらくiksm sessionの取得が出来なくなる可能性があります。
logには _This access has been administratively prohibited by the site operator_ と表示されます。IPアドレスを変更する、あるいはしばらく時間をおくことで解決できます。

## Botを自分好みに改造したくなったら
[Discord Bot 最速チュートリアル【Python&Heroku&GitHub】](https://qiita.com/1ntegrale9/items/aa4b373e8895273875a8#8-dynos%E3%81%AE%E8%A8%AD%E5%AE%9A)を参考にしてください。  

## Reference
- [Discord Bot 最速チュートリアル【Python&Heroku&GitHub】](https://qiita.com/1ntegrale9/items/aa4b373e8895273875a8#8-dynos%E3%81%AE%E8%A8%AD%E5%AE%9A)
- [Discord Botアカウント初期設定ガイド for Developer](https://qiita.com/1ntegrale9/items/cb285053f2fa5d0cccdf)
- [frozenpandaman/splatnet2statink](https://github.com/frozenpandaman/splatnet2statink)

## Contact Me

- Gmail: TomoIris427@gmail.com

## LICENSE
MIT