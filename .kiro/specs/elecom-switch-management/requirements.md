# 要件ドキュメント

## はじめに

本ドキュメントは、ELECOM EHB-SQ2A08スイッチングハブ管理スクリプトプロジェクトの要件を定義します。このプロジェクトは、ネットワーク管理者がELECOMスイッチングハブから情報を取得し、セッションを管理するためのPythonベースのコマンドラインツールを提供します。

## 用語集

- **Switch**: ELECOM EHB-SQ2A08スイッチングハブデバイス
- **Script**: Pythonで実装されたコマンドラインツール
- **Session**: SwitchへのHTTP認証済み接続
- **Port**: Switchの物理ポート（GE1-GE8）またはリンクアグリゲーショングループ（LAG1-LAG4）
- **Environment_File**: スイッチ接続情報を含む.env設定ファイル
- **MAC_Table**: Switchが学習したMACアドレスとポートのマッピング
- **VLAN**: 仮想LAN設定
- **Traffic_Statistics**: ポートごとの送受信パケット数、バイト数、エラーカウンタ
- **API_Endpoint**: Switch上のHTTP CGIエンドポイント（/cgi/get.cgi）
- **Credential**: SwitchへのアクセスにはIPアドレス、ユーザー名、パスワードが必要

## 要件

### 要件1: スイッチ認証

**ユーザーストーリー:** ネットワーク管理者として、スイッチに安全に認証したい。そうすることで、スイッチ情報にアクセスできるようになる。

#### 受入基準

1. WHEN Environment_Fileが提供される、THE Script SHALL Environment_Fileから認証情報（IPアドレス、ユーザー名、パスワード）を読み込む
2. WHEN コマンドライン引数で認証情報が提供される、THE Script SHALL コマンドライン引数の値をEnvironment_Fileの値より優先する
3. WHEN 認証情報が不足している、THE Script SHALL エラーメッセージを表示して終了する
4. THE Script SHALL HTTP Basic認証を使用してSwitchに認証する
5. WHEN 認証が成功する、THE Script SHALL 後続のリクエストのためにセッションCookieを保持する
6. WHEN 認証が失敗する、THE Script SHALL エラーメッセージを返す

### 要件2: 複数スイッチ管理

**ユーザーストーリー:** ネットワーク管理者として、複数のスイッチを個別の設定ファイルで管理したい。そうすることで、異なるスイッチに簡単に切り替えられる。

#### 受入基準

1. THE Script SHALL --env-fileパラメータを受け入れてEnvironment_Fileのパスを指定できるようにする
2. WHEN --env-fileが指定されない、THE Script SHALL デフォルトで.envファイルを使用する
3. THE Script SHALL 複数のEnvironment_Fileを同じディレクトリに共存させることができる
4. WHEN 異なるEnvironment_Fileが指定される、THE Script SHALL 対応するSwitchに接続する
5. THE Script SHALL Environment_Fileの例として.env.exampleファイルを提供する

### 要件3: ポートステータス取得

**ユーザーストーリー:** ネットワーク管理者として、全ポートのステータスを取得したい。そうすることで、どのポートがアクティブかを確認できる。

#### 受入基準

1. WHEN --statusオプションが指定される、THE Script SHALL panel_info API_Endpointを呼び出す
2. THE Script SHALL 各Portのリンク状態（UP/DOWN）を取得する
3. THE Script SHALL 各Portの速度（1G/2.5G）を取得する
4. THE Script SHALL 各Portのデュプレックスモード（Full/Half）を取得する
5. THE Script SHALL ポートステータス情報をJSON形式で返す

### 要件4: ポート設定情報取得

**ユーザーストーリー:** ネットワーク管理者として、ポートの詳細設定を取得したい。そうすることで、ポート設定を確認できる。

#### 受入基準

1. WHEN --portオプションが指定される、THE Script SHALL port_portおよびpanel_layout API_Endpointを呼び出す
2. THE Script SHALL ポート詳細設定を取得する
3. THE Script SHALL パネルレイアウト情報を取得する
4. THE Script SHALL ポート設定情報をJSON形式で返す

### 要件5: VLAN情報取得

**ユーザーストーリー:** ネットワーク管理者として、VLAN設定を取得したい。そうすることで、ネットワークセグメンテーションを確認できる。

#### 受入基準

1. WHEN --vlanオプションが指定される、THE Script SHALL vlan_port、vlan_conf、vlan_membership API_Endpointを呼び出す
2. THE Script SHALL VLANポート設定を取得する
3. THE Script SHALL VLAN設定を取得する
4. THE Script SHALL VLANメンバーシップ情報を取得する
5. THE Script SHALL VLAN情報をJSON形式で返す

### 要件6: MACアドレステーブル取得

**ユーザーストーリー:** ネットワーク管理者として、MACアドレステーブルを取得したい。そうすることで、どのデバイスがどのポートに接続されているかを確認できる。

#### 受入基準

1. WHEN --macオプションが指定される、THE Script SHALL mac_dynamicおよびmac_static API_Endpointを呼び出す
2. THE Script SHALL ダイナミックMAC_Tableエントリを取得する
3. THE Script SHALL スタティックMAC_Tableエントリを取得する
4. THE Script SHALL MAC_Table情報をJSON形式で返す

### 要件7: トラフィック統計取得

**ユーザーストーリー:** ネットワーク管理者として、全ポートのトラフィック統計を取得したい。そうすることで、ネットワーク使用状況を監視できる。

#### 受入基準

1. WHEN --trafficオプションが指定される、THE Script SHALL 全Port（GE1-GE8およびLAG1-LAG4）のport_cnt API_Endpointを呼び出す
2. THE Script SHALL 各Portの受信バイト数を取得する
3. THE Script SHALL 各Portの送信バイト数を取得する
4. THE Script SHALL 各Portの受信パケット数を取得する
5. THE Script SHALL 各Portの送信パケット数を取得する
6. THE Script SHALL 各Portのエラーカウンタを取得する
7. THE Script SHALL Traffic_Statistics情報をJSON形式で返す

### 要件8: スイッチ基本情報取得

**ユーザーストーリー:** ネットワーク管理者として、スイッチの基本情報を取得したい。そうすることで、スイッチのシステム情報を確認できる。

#### 受入基準

1. WHEN --mainオプションが指定される、THE Script SHALL home_main API_Endpointを呼び出す
2. THE Script SHALL システム情報を取得する
3. THE Script SHALL ポート一覧を取得する
4. THE Script SHALL メニュー構造を取得する
5. THE Script SHALL スイッチ基本情報をJSON形式で返す

### 要件9: 全情報取得

**ユーザーストーリー:** ネットワーク管理者として、すべての情報を一度に取得したい。そうすることで、スイッチの完全な状態を把握できる。

#### 受入基準

1. WHEN --allオプションが指定される、THE Script SHALL すべてのAPI_Endpointを呼び出す
2. THE Script SHALL ポートステータス、ポート設定、VLAN情報、MAC_Table、Traffic_Statistics、スイッチ基本情報を取得する
3. THE Script SHALL すべての情報を単一のJSON構造で返す

### 要件10: JSON出力フォーマット

**ユーザーストーリー:** ネットワーク管理者として、読みやすい形式でデータを表示したい。そうすることで、情報を簡単に確認できる。

#### 受入基準

1. THE Script SHALL デフォルトでコンパクトなJSON形式で出力する
2. WHEN --prettyオプションが指定される、THE Script SHALL インデントされた読みやすいJSON形式で出力する
3. THE Script SHALL 日本語文字を正しく表示する（ensure_ascii=False）

### 要件11: セッション管理

**ユーザーストーリー:** ネットワーク管理者として、スイッチセッションを適切に管理したい。そうすることで、セッション制限の問題を回避できる。

#### 受入基準

1. WHEN データ取得が完了する、THE Script SHALL Switchからログアウトする
2. THE Script SHALL ログアウトリクエストを/login.html?reason=logoutに送信する
3. IF ログアウトが失敗する、THE Script SHALL エラーを無視して続行する
4. THE Script SHALL 各API呼び出しの間に適切な遅延（0.2-0.5秒）を挿入する

### 要件12: セッション切断ユーティリティ

**ユーザーストーリー:** ネットワーク管理者として、すべてのスイッチセッションを強制的に切断したい。そうすることで、セッション制限エラーから回復できる。

#### 受入基準

1. THE Script SHALL disconnect_all_sessions.pyユーティリティを提供する
2. WHEN disconnect_all_sessions.pyが実行される、THE Script SHALL Switchにログインしてすぐにログアウトする
3. THE Script SHALL セッション切断を3回繰り返して確実に切断する
4. THE Script SHALL 各試行の間に1秒の遅延を挿入する
5. THE Script SHALL 切断処理の進捗を表示する

### 要件13: エラーハンドリング

**ユーザーストーリー:** ネットワーク管理者として、エラーが発生したときに明確なメッセージを受け取りたい。そうすることで、問題を診断できる。

#### 受入基準

1. WHEN API呼び出しが失敗する、THE Script SHALL エラーメッセージをJSON構造に含める
2. WHEN 認証が失敗する、THE Script SHALL "Authentication failed or no data"エラーを返す
3. WHEN JSONパースが失敗する、THE Script SHALL "JSON parse error"エラーを返す
4. WHEN ネットワークタイムアウトが発生する、THE Script SHALL タイムアウトエラーメッセージを返す
5. THE Script SHALL 部分的なエラーが発生しても他のデータ取得を続行する

### 要件14: セキュリティ

**ユーザーストーリー:** ネットワーク管理者として、認証情報を安全に保存したい。そうすることで、不正アクセスを防止できる。

#### 受入基準

1. THE Script SHALL Environment_Fileから認証情報を読み込む
2. THE Script SHALL .gitignoreにEnvironment_Fileパターンを含める
3. THE Script SHALL Environment_Fileのパーミッションを600（所有者のみ読み書き可能）に設定することを推奨する
4. THE Script SHALL コマンドライン引数での認証情報指定を非推奨とする（シェル履歴に残るため）
5. THE Script SHALL .env.exampleファイルにセキュリティ注意事項を記載する

### 要件15: HTTPプロトコル実装

**ユーザーストーリー:** 開発者として、スイッチのHTTP APIと正しく通信したい。そうすることで、データを確実に取得できる。

#### 受入基準

1. THE Script SHALL HTTP Basic認証ヘッダーを使用する
2. THE Script SHALL Cookie管理のためにhttp.cookiejar.CookieJarを使用する
3. THE Script SHALL 適切なUser-Agentヘッダーを設定する
4. THE Script SHALL X-Requested-WithヘッダーをXMLHttpRequestに設定する
5. THE Script SHALL Refererヘッダーを適切に設定する
6. THE Script SHALL タイムスタンプパラメータ（dummy）をAPI呼び出しに含める
7. THE Script SHALL 10秒のタイムアウトをAPI呼び出しに設定する

### 要件16: コマンドラインインターフェース

**ユーザーストーリー:** ネットワーク管理者として、直感的なコマンドラインインターフェースを使用したい。そうすることで、スクリプトを簡単に実行できる。

#### 受入基準

1. THE Script SHALL argparseを使用してコマンドライン引数を解析する
2. WHEN オプションが指定されない、THE Script SHALL ヘルプメッセージを表示する
3. THE Script SHALL 詳細な使用例をヘルプメッセージに含める
4. THE Script SHALL Environment_File管理の説明をヘルプメッセージに含める
5. THE Script SHALL 日本語のヘルプメッセージを提供する

### 要件17: ドキュメント

**ユーザーストーリー:** ネットワーク管理者として、包括的なドキュメントを読みたい。そうすることで、スクリプトの使い方を理解できる。

#### 受入基準

1. THE Script SHALL README.mdファイルを提供する
2. THE Script SHALL .env.exampleファイルを提供する
3. THE Script SHALL 各スクリプトファイルにdocstringを含める
4. THE Script SHALL セキュリティのベストプラクティスをドキュメントに記載する
5. THE Script SHALL 複数スイッチ管理の例をドキュメントに記載する
6. THE Script SHALL トラブルシューティングガイドをドキュメントに記載する
