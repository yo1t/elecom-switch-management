#!/usr/bin/env python3
"""
スイッチングハブ情報取得スクリプト（統合版）

使用方法:
  python3 get_switch_data.py [オプション]

オプション:
  --all              すべての情報を取得
  --port             ポート情報
  --vlan             VLAN情報
  --mac              MACアドレステーブル
  --traffic          トラフィック統計（全ポート）
  --status           ポートステータス
  --main             スイッチ基本情報
  --pretty           整形されたJSON出力

例:
  python3 get_switch_data.py --port --vlan --pretty
  python3 get_switch_data.py --mac --pretty
  python3 get_switch_data.py --traffic --pretty
  python3 get_switch_data.py --all --pretty
"""

import urllib.request
import urllib.parse
import urllib.error
import http.cookiejar
import base64
import json
import time
import argparse
import os

# ポート一覧（物理ポート + LAG）
PORTS = ["GE1", "GE2", "GE3", "GE4", "GE5", "GE6", "GE7", "GE8", "LAG1", "LAG2", "LAG3", "LAG4"]

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

# 取得可能な情報の定義
AVAILABLE_COMMANDS = {
    'status': [('panel_info', 'ポートステータス')],
    'port': [('port_port', 'ポート設定'), ('panel_layout', 'パネルレイアウト')],
    'vlan': [('vlan_port', 'VLANポート設定'), ('vlan_conf', 'VLAN設定'), ('vlan_membership', 'VLANメンバーシップ')],
    'mac': [('mac_dynamic', 'ダイナミックMACアドレステーブル'), ('mac_static', 'スタティックMACアドレステーブル')],
    'main': [('home_main', 'スイッチ基本情報')],
}

def get_switch_data(switch_url, username, password, commands_to_fetch, get_all_port_traffic=False):
    """スイッチにログインして指定された情報を取得"""
    
    cookie_jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
    
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    auth_header = f"Basic {encoded_credentials}"
    
    headers = {
        'Authorization': auth_header,
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    }
    
    result = {}
    
    try:
        # ステップ1: トップページにアクセス
        request = urllib.request.Request(switch_url)
        for key, value in headers.items():
            request.add_header(key, value)
        
        with opener.open(request, timeout=10) as response:
            pass
        
        time.sleep(0.2)
        
        # ステップ2: login.htmlにアクセス
        request = urllib.request.Request(f"{switch_url}/login.html")
        for key, value in headers.items():
            request.add_header(key, value)
        request.add_header('Referer', switch_url + '/')
        
        with opener.open(request, timeout=10) as response:
            pass
        
        time.sleep(0.2)
        
        # ステップ3: home_loginを呼び出してCookieを取得
        home_login_url = f"{switch_url}/cgi/get.cgi?cmd=home_login&dummy={int(time.time() * 1000)}"
        
        request = urllib.request.Request(home_login_url)
        for key, value in headers.items():
            request.add_header(key, value)
        request.add_header('Referer', f"{switch_url}/login.html")
        request.add_header('Accept', 'application/json, text/javascript, */*; q=0.01')
        request.add_header('X-Requested-With', 'XMLHttpRequest')
        
        with opener.open(request, timeout=10) as response:
            login_data = response.read().decode('utf-8', errors='ignore')
        
        time.sleep(0.3)
        
        # ステップ4: home.htmlにアクセス
        request = urllib.request.Request(f"{switch_url}/home.html")
        for key, value in headers.items():
            request.add_header(key, value)
        request.add_header('Referer', f"{switch_url}/login.html")
        
        with opener.open(request, timeout=10) as response:
            pass
        
        time.sleep(0.5)
        
        # ステップ5: 指定された情報を取得
        for cmd in commands_to_fetch:
            api_url = f"{switch_url}/cgi/get.cgi?cmd={cmd}&dummy={int(time.time() * 1000)}"
            
            request = urllib.request.Request(api_url)
            for key, value in headers.items():
                request.add_header(key, value)
            request.add_header('Referer', f"{switch_url}/home.html")
            request.add_header('Accept', 'application/json, text/javascript, */*; q=0.01')
            request.add_header('X-Requested-With', 'XMLHttpRequest')
            
            try:
                with opener.open(request, timeout=10) as response:
                    content = response.read().decode('utf-8', errors='ignore')
                    
                    if len(content) > 50 and 'notAuth' not in content and 'Bad Request' not in content:
                        try:
                            data = json.loads(content)
                            result[cmd] = data
                        except json.JSONDecodeError:
                            result[cmd] = {"error": "JSON parse error"}
                    else:
                        result[cmd] = {"error": "Authentication failed or no data"}
            except Exception as e:
                result[cmd] = {"error": str(e)}
        
        # 全ポートのトラフィック統計を取得
        if get_all_port_traffic:
            result['port_traffic_all'] = {}
            
            # 各ポートの統計を取得（home.htmlからの参照を維持）
            for port in PORTS:
                api_url = f"{switch_url}/cgi/get.cgi?cmd=port_cnt&port={port}&dummy={int(time.time() * 1000)}"
                
                request = urllib.request.Request(api_url)
                for key, value in headers.items():
                    request.add_header(key, value)
                request.add_header('Referer', f"{switch_url}/home.html")
                request.add_header('Accept', 'application/json, text/javascript, */*; q=0.01')
                request.add_header('X-Requested-With', 'XMLHttpRequest')
                
                try:
                    with opener.open(request, timeout=10) as response:
                        content = response.read().decode('utf-8', errors='ignore')
                        
                        if len(content) > 50 and 'notAuth' not in content and 'Bad Request' not in content:
                            try:
                                data = json.loads(content)
                                result['port_traffic_all'][port] = data
                            except json.JSONDecodeError:
                                result['port_traffic_all'][port] = {"error": "JSON parse error"}
                        else:
                            result['port_traffic_all'][port] = {"error": "Authentication failed or no data"}
                except Exception as e:
                    result['port_traffic_all'][port] = {"error": str(e)}
        
        # ステップ6: ログアウト
        request = urllib.request.Request(f"{switch_url}/login.html?reason=logout")
        for key, value in headers.items():
            request.add_header(key, value)
        request.add_header('Referer', f"{switch_url}/home.html")
        
        try:
            with opener.open(request, timeout=5) as response:
                pass
        except:
            pass
        
    except Exception as e:
        result["error"] = str(e)
    
    return result

def main():
    parser = argparse.ArgumentParser(
        description='スイッチングハブ情報取得スクリプト（統合版）',
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
  python3 %(prog)s --env-file .env.office-floor1 --mac --pretty
  python3 %(prog)s --env-file .env.datacenter-rack1 --all --pretty
  
  # 複数スイッチの管理
  python3 %(prog)s --env-file .env.office-floor1 --status --pretty
  python3 %(prog)s --env-file .env.office-floor2 --status --pretty
  
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
    
    parser.add_argument('--all', action='store_true', help='すべての情報を取得')
    parser.add_argument('--status', action='store_true', help='ポートステータスを取得')
    parser.add_argument('--port', action='store_true', help='ポート情報を取得')
    parser.add_argument('--vlan', action='store_true', help='VLAN情報を取得')
    parser.add_argument('--mac', action='store_true', help='MACアドレステーブルを取得')
    parser.add_argument('--traffic', action='store_true', help='全ポートのトラフィック統計を取得')
    parser.add_argument('--main', action='store_true', help='スイッチ基本情報を取得')
    parser.add_argument('--pretty', action='store_true', help='整形されたJSON出力')
    
    args = parser.parse_args()
    
    # 設定値を優先順位に従って取得
    switch_ip = get_config_value(args.ip, env_vars.get('SWITCH_IP'))
    switch_user = get_config_value(args.user, env_vars.get('SWITCH_USER'))
    switch_password = get_config_value(args.password, env_vars.get('SWITCH_PASSWORD'))
    
    # 接続情報の検証
    if not switch_ip or not switch_user or not switch_password:
        parser.error('接続情報が不足しています。--ip, --user, --password を指定するか、.envファイルを設定してください。')
    
    # スイッチURLを構築
    switch_url = f"http://{switch_ip}"
    
    # 取得するコマンドを決定
    commands_to_fetch = []
    get_all_port_traffic = False
    
    if args.all:
        for commands in AVAILABLE_COMMANDS.values():
            commands_to_fetch.extend([cmd for cmd, _ in commands])
        get_all_port_traffic = True
    else:
        if args.status:
            commands_to_fetch.extend([cmd for cmd, _ in AVAILABLE_COMMANDS['status']])
        if args.port:
            commands_to_fetch.extend([cmd for cmd, _ in AVAILABLE_COMMANDS['port']])
        if args.vlan:
            commands_to_fetch.extend([cmd for cmd, _ in AVAILABLE_COMMANDS['vlan']])
        if args.mac:
            commands_to_fetch.extend([cmd for cmd, _ in AVAILABLE_COMMANDS['mac']])
        if args.main:
            commands_to_fetch.extend([cmd for cmd, _ in AVAILABLE_COMMANDS['main']])
        if args.traffic:
            get_all_port_traffic = True
    
    # コマンドが指定されていない場合はヘルプを表示
    if not commands_to_fetch and not get_all_port_traffic:
        parser.print_help()
        return
    
    # データ取得
    result = get_switch_data(switch_url, switch_user, switch_password, commands_to_fetch, get_all_port_traffic)
    
    # JSON出力
    if args.pretty:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()
