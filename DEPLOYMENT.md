# 47都道府県 毎日10問 — 運用・デプロイ手順

中学入試向けの都道府県学習アプリ。既存の Flask + PostgreSQL 実装を継続して開発します。

## Render の起動設定
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`
- 環境変数（Render の Environment に設定。値を GitHub に書かない）:
  - `SECRET_KEY`: 十分に長いランダムな秘密鍵
  - `ADMIN_PASSWORD`: 教師用の強いパスワード
  - `ADMIN_ID`: 任意。未設定時は `teacher`
  - `DATABASE_URL`: PostgreSQL の接続URL（Render PostgreSQL の Internal Database URL など）

**注意:** `DATABASE_URL` がないと起動時の管理者初期化で失敗します。PostgreSQL 側に `quiz_users`, `quiz_daily`, `quiz_answers` のテーブルが必要です。スキーマが未導入なら先に作成してください。Render の無料枠・DBの期限や料金は契約画面で確認してください。

## 現行コードで確認した仕様
- 生徒はIDでログイン、教師はIDとパスワードでログイン
- 日本時間の日付ごとに10県をランダム抽出しDBへ保存
- 地図番号・地方区分・都道府県名の3項目すべて一致で正解
- ヒント最大3件、利用数に応じて正解時100/70/40点
- 教師が生徒IDを登録し、当日の集計を閲覧可能

## 未完成・要確認
- **実際の全国地図の画像／県境／番号表示は未実装。** 現状の地図欄は代替表示。
- `data.json` の各キーワード解説は仮文。教材として監修が必要。
- `/api/answer` はヒント数を1〜3に限定しており、ヒント0回での提出を受け付けない。UIとの整合性を確認する。
- 生徒IDのみのログインは、IDを知る第三者によるなりすましリスクがある。公開前に認証設計を再検討する。
- DBテーブル作成用SQLとRenderの実際のデプロイ状況は別途確認する。

## 次の開発順
1. Render起動に必要なDBスキーマと環境変数を整備
2. 正確な47都道府県の境界を含む全国地図を導入
3. 地図番号と解答画面を連動
4. 47都道府県の解説とヒントを監修
5. 生徒ID・教師画面・学習履歴の動作検証
