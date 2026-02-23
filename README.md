# ELECOM EHB-SQ2A08 スイッチングハブ管理スクリプト

## スクリプト一覧

### 1. get_elecom_swhub_info.py
スイッチから直接データを取得するスクリプト

```bash
# スイッチごとの.envファイルを指定して実行（推奨）
python3 get_elecom_swhub_info.py --env-file .env.office-floor1 --mac --pretty
python3 get_elecom_swhub_info.py --env-file .env.datacenter-rack1 --vlan --pretty

# スイッチ情報の概要を表示（推奨）
python3 get_elecom_swhub_info.py --env-file .env.office-floor1 --summary

# 全ポート統計取得（GE1-GE8 + LAG1-LAG4）
python3 get_elecom_swhub_info.py --env-file .env.office-floor1 --traffic --pretty

# 全情報取得
python3 get_elecom_swhub_info.py --env-file .env.office-floor1 --all --pretty

# コマンドライン引数で直接指定（非推奨：履歴に残る）
python3 get_elecom_swhub_info.py --ip 192.168.1.1 --user username --password pass --mac --pretty
```

### 2. disconnect_all_sessions.py
スイッチの全セッションを切断するスクリプト

```bash
# スイッチごとの.envファイルを指定して実行（推奨）
python3 disconnect_all_sessions.py --env-file .env.office-floor1
python3 disconnect_all_sessions.py --env-file .env.datacenter-rack1

# コマンドライン引数で直接指定（非推奨：履歴に残る）
python3 disconnect_all_sessions.py --ip 192.168.1.1 --user username --password pass
```

## オプション

### get_elecom_swhub_info.py
- `--env-file`: .envファイルのパス（推奨、デフォルト: .env）
- `--ip`: スイッチのIPアドレス（直接指定、非推奨）
- `--user`: ユーザー名（直接指定、非推奨）
- `--password`: パスワード（直接指定、非推奨）
- `--summary`: スイッチ情報の概要を表示（推奨）
- `--status`: ポートステータス
- `--port`: ポート設定情報
- `--vlan`: VLAN情報
- `--mac`: MACアドレステーブル
- `--traffic`: トラフィック統計（全ポート）
- `--main`: スイッチ基本情報
- `--all`: すべての情報
- `--pretty`: 整形されたJSON出力

### disconnect_all_sessions.py
- `--env-file`: .envファイルのパス（推奨、デフォルト: .env）
- `--ip`: スイッチのIPアドレス（直接指定、非推奨）
- `--user`: ユーザー名（直接指定、非推奨）
- `--password`: パスワード（直接指定、非推奨）

## セキュリティ注意事項

### 認証情報の管理

1. **.envファイルの作成（推奨方法）**
   ```bash
   # .env.exampleをコピーして各スイッチ用の.envファイルを作成
   cp .env.example .env.switch1
   cp .env.example .env.switch2
   
   # 各.envファイルを編集して実際の認証情報を設定
   nano .env.switch1
   nano .env.switch2
   
   # パーミッションを600に設定（所有者のみ読み書き可能）
   chmod 600 .env.switch*
   ```

2. **.envファイルの内容例**
   ```
   SWITCH_IP=192.168.1.1
   SWITCH_USER=your_username
   SWITCH_PASSWORD=your_password
   ```

3. **複数スイッチの管理**
   ```bash
   # スイッチごとに.envファイルを作成
   .env.office-floor1    # オフィス1階のスイッチ
   .env.office-floor2    # オフィス2階のスイッチ
   .env.datacenter-rack1 # データセンターラック1のスイッチ
   .env.home-main        # 自宅メインスイッチ
   
   # 使用時に--env-fileで対象スイッチを指定
   python3 get_elecom_swhub_info.py --env-file .env.office-floor1 --mac --pretty
   python3 get_elecom_swhub_info.py --env-file .env.datacenter-rack1 --all --pretty
   ```

4. **重要な注意事項**
   - .envファイルをバージョン管理システムにコミットしないでください
   - 認証情報を他人と共有しないでください
   - 定期的にパスワードを変更してください
   - 信頼できるネットワークからのみアクセスしてください
   - コマンドライン引数での認証情報指定は避けてください（シェル履歴に残るため）
   - 必ず`--env-file`オプションで.envファイルを明示的に指定してください
   - 各スイッチごとに個別の.envファイルを作成して管理してください

## 取得可能な情報

1. **ポートステータス** (--status)
   - リンク状態（UP/DOWN）
   - 速度（1G/2.5G）
   - デュプレックス（Full/Half）

2. **ポート情報** (--port)
   - ポート詳細設定
   - パネルレイアウト

3. **VLAN情報** (--vlan)
   - VLAN設定
   - ポートVLAN設定
   - VLANメンバーシップ

4. **MACアドレステーブル** (--mac)
   - ダイナミックMACアドレス
   - スタティックMACアドレス

5. **トラフィック統計** (--traffic)
   - 全ポート（GE1-GE8 + LAG1-LAG4）の統計情報
   - 受信/送信バイト数
   - 受信/送信パケット数
   - エラーカウンタ

6. **スイッチ基本情報** (--main)
   - システム情報
   - ポート一覧
   - メニュー構造

## 使用上の注意事項

- スイッチへの同時接続数に制限があります（1セッションのみ）
- スクリプトは自動的にセッション管理を行います：
  - 実行前に既存セッションを自動切断
  - データ取得後に自動ログアウト
  - セッション競合時は自動リトライ（最大2回）
- ブラウザでスイッチにログインしている場合は、ログアウトしてからスクリプトを実行してください
- `--summary`オプションで、スイッチの状態を素早く確認できます
- 通常は`disconnect_all_sessions.py`を手動で実行する必要はありません（自動管理されます）
