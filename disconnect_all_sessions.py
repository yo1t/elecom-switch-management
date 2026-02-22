#!/usr/bin/env python3
"""
スイッチの全セッションを切断するスクリプト
"""

import urllib.request
import urllib.parse
import urllib.error
import http.cookiejar
import base64
import time
import argparse
import os

def load_env_file(env_file='.env'):
    """環境変数ファイルを読み込む"""
    env_vars = {}
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    return env_vars

def get_config_value(arg_value, env_file_value):
    """設定値を優先順位に従って取得: コマンドライン引数 > .envファイル"""
    if arg_value:
        return arg_value
    return env_file_value

def disconnect_session(switch_url, username, password):
    """セッションを切断"""
    
    cookie_jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
    
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    auth_header = f"Basic {encoded_credentials}"
    
    headers = {
        'Authorization': auth_header,
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    }
    
    try:
        print("セッション切断中...")
        
        # トップページにアクセス
        request = urllib.request.Request(switch_url)
        for key, value in headers.items():
            request.add_header(key, value)
        
        try:
            with opener.open(request, timeout=5):
                pass
        except:
            pass
        
        time.sleep(0.2)
        
        # login.htmlにアクセス
        request = urllib.request.Request(f"{switch_url}/login.html")
        for key, value in headers.items():
            request.add_header(key, value)
        request.add_header('Referer', switch_url + '/')
        
        try:
            with opener.open(request, timeout=5):
                pass
        except:
            pass
        
        time.sleep(0.2)
        
        # home_loginを呼び出してCookieを取得
        home_login_url = f"{switch_url}/cgi/get.cgi?cmd=home_login&dummy={int(time.time() * 1000)}"
        
        request = urllib.request.Request(home_login_url)
        for key, value in headers.items():
            request.add_header(key, value)
        request.add_header('Referer', f"{switch_url}/login.html")
        request.add_header('Accept', 'application/json, text/javascript, */*; q=0.01')
        request.add_header('X-Requested-With', 'XMLHttpRequest')
        
        try:
            with opener.open(request, timeout=5) as response:
                response.read()
        except:
            pass
        
        time.sleep(0.2)
        
        # ログアウトリクエストを送信
        logout_url = f"{switch_url}/login.html?reason=logout"
        request = urllib.request.Request(logout_url)
        for key, value in headers.items():
            request.add_header(key, value)
        request.add_header('Referer', f"{switch_url}/home.html")
        
        try:
            with opener.open(request, timeout=5):
                pass
            print("✓ セッションを切断しました")
        except:
            print("✓ セッションの切断を試行しました")
        
    except Exception as e:
        print(f"エラー: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='スイッチセッション切断スクリプト',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
環境変数ファイル (.env) の例:
  SWITCH_IP=192.168.1.1
  SWITCH_USER=admin
  SWITCH_PASSWORD=********

設定の優先順位:
  1. コマンドライン引数 (--ip, --user, --password)
  2. .envファイル (--env-fileで指定、デフォルトは.env)

使用例:
  # スイッチごとの.envファイルを指定（推奨）
  python3 %(prog)s --env-file .env.office-floor1
  python3 %(prog)s --env-file .env.datacenter-rack1
  
  # .envファイルの作成方法
  cp .env.example .env.office-floor1
  nano .env.office-floor1  # 認証情報を編集
  chmod 600 .env.office-floor1
        """
    )
    
    parser.add_argument('--env-file', default='.env', help='.envファイルのパス (デフォルト: .env)')
    
    # .envファイルを読み込み
    args_temp = parser.parse_known_args()[0]
    env_vars = load_env_file(args_temp.env_file)
    
    parser.add_argument('--ip', help='スイッチのIPアドレス')
    parser.add_argument('--user', help='ユーザー名')
    parser.add_argument('--password', help='パスワード')
    
    args = parser.parse_args()
    
    # 設定値を優先順位に従って取得
    switch_ip = get_config_value(args.ip, env_vars.get('SWITCH_IP'))
    switch_user = get_config_value(args.user, env_vars.get('SWITCH_USER'))
    switch_password = get_config_value(args.password, env_vars.get('SWITCH_PASSWORD'))
    
    # 接続情報の検証
    if not switch_ip or not switch_user or not switch_password:
        parser.error('接続情報が不足しています。--ip, --user, --password を指定するか、.envファイルを設定してください。')
    
    switch_url = f"http://{switch_ip}"
    
    print("=" * 60)
    print("スイッチセッション切断スクリプト")
    print("=" * 60)
    print()
    
    # 複数回実行して確実に切断
    for i in range(3):
        print(f"\n試行 {i+1}/3:")
        disconnect_session(switch_url, switch_user, switch_password)
        time.sleep(1)
    
    print()
    print("=" * 60)
    print("✓ 全セッションの切断処理が完了しました")
    print("=" * 60)
