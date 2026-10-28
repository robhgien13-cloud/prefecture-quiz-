# Supabase セットアップ（無料枠）

1. Supabase の prefecture-quiz プロジェクトで **SQL Editor → New query** を開く。
2. [schema.sql](schema.sql) の全文を貼り付けて **Run** を押す。
3. **Table Editor** に `quiz_users`, `quiz_daily`, `quiz_answers` が表示されれば完了。

## 設計

- 生徒はランダムなIDのみでログイン。氏名・メール・生年月日は保存しない。
- 先生は別IDとパスワードでログイン。
- 毎日10問の出題内容は `quiz_daily` に固定して保存。
- 正誤・得点・ヒント数は `quiz_answers` に保存。
- テーブルはRLS有効・匿名アクセス禁止。サーバーのみDBへアクセスする。

## 公開前の必須作業

- FlaskアプリをSQLiteからPostgreSQLへ変更し、接続情報を環境変数に保存する。
- サーバーの秘密鍵と先生の初期パスワードを安全に設定する。
- 生徒IDのみのログインはなりすましを防げないため、本名等の個人情報は収集しない。
- 無料枠の休止・容量制限とバックアップ方法を確認する。

**SQL登録だけではWebアプリは公開されません。**
