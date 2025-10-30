# OneRoster Gradebook サービス - 機能要件定義書

## バージョン情報
- **文書バージョン**: 1.0.0
- **OneRosterバージョン**: 1.2
- **作成日**: 2025-10-30
- **ステータス**: Draft

## 1. プロジェクト概要

### 1.1 目的
OneRoster Gradebook Service 1.2の標準準拠リファレンス実装を提供し、教育機関とベンダーがOneRoster対応システムを開発する際の実装ガイドとして活用できるようにする。

### 1.2 スコープ
本プロジェクトは以下を含む：
- **Provider実装**: Gradebook APIエンドポイントの提供
- **Consumer実装**: 他システムのGradebook APIの利用
- **3言語実装**: Node.js、Python、Javaでの完全な実装例
- **認証機能**: OAuth 2.0 Client Credentials Grantの実装
- **データ永続化**: PostgreSQLを使用したデータ管理

### 1.3 スコープ外
- Rostering Service実装（別サービスとして扱う）
- Resources Service実装
- フロントエンドUI実装
- 本番環境用のスケーリング・高可用性構成

## 2. ステークホルダー

| ステークホルダー | 役割 | 期待事項 |
|----------------|------|---------|
| **教育機関IT管理者** | システム導入・運用 | 容易な導入、安定した動作 |
| **アプリケーション開発者** | 統合開発 | 明確なAPI仕様、実装例 |
| **LMS/SISベンダー** | 製品統合 | 標準準拠、相互運用性 |
| **IMS Global** | 標準化団体 | OneRoster 1.2仕様への準拠 |

## 3. 機能要件

### 3.1 Provider機能（API提供側）

#### 3.1.1 Categories API

**FR-CAT-001: 全カテゴリー取得**
- **エンドポイント**: `GET /ims/oneroster/gradebook/v1p2/categories`
- **説明**: システム内の全成績カテゴリーを取得
- **必須パラメータ**: なし
- **オプションパラメータ**: 
  - `limit` (整数, 1-1000): 返却する最大レコード数
  - `offset` (整数, ≥0): スキップするレコード数
  - `filter` (文字列): フィルター条件
  - `sort` (文字列): ソートフィールド
  - `orderBy` (文字列): ソート順序（asc/desc）
  - `fields` (文字列): 返却フィールドのカンマ区切りリスト
- **レスポンス**: 200 OK、カテゴリーの配列
- **認証**: OAuth 2.0スコープ `gradebook.readonly`

**FR-CAT-002: 単一カテゴリー取得**
- **エンドポイント**: `GET /ims/oneroster/gradebook/v1p2/categories/{id}`
- **説明**: 指定されたsourcedIdのカテゴリーを取得
- **パスパラメータ**: `id` (文字列): カテゴリーのsourcedId
- **レスポンス**: 200 OK（成功）、404 Not Found（存在しない）
- **認証**: OAuth 2.0スコープ `gradebook.readonly`

**FR-CAT-003: カテゴリー作成/更新**
- **エンドポイント**: `PUT /ims/oneroster/gradebook/v1p2/categories/{id}`
- **説明**: カテゴリーを作成または更新
- **リクエストボディ**: 
  ```json
  {
    "category": {
      "sourcedId": "category-123",
      "status": "active",
      "title": "Homework",
      "weight": 0.3
    }
  }
  ```
- **レスポンス**: 200 OK（更新）、201 Created（新規作成）
- **認証**: OAuth 2.0スコープ `gradebook.createput`
- **バリデーション**:
  - `title`: 必須、1-255文字
  - `weight`: 任意、0.0-1.0の範囲

**FR-CAT-004: カテゴリー削除**
- **エンドポイント**: `DELETE /ims/oneroster/gradebook/v1p2/categories/{id}`
- **説明**: カテゴリーを論理削除（status='tobedeleted'）
- **レスポンス**: 204 No Content（成功）、404 Not Found（存在しない）
- **認証**: OAuth 2.0スコープ `gradebook.delete`

**FR-CAT-005: クラス別カテゴリー取得**
- **エンドポイント**: `GET /ims/oneroster/gradebook/v1p2/classes/{class_id}/categories`
- **説明**: 指定クラスに関連するカテゴリーを取得
- **実装**: システム固有のロジックに基づく

#### 3.1.2 LineItems API

**FR-LI-001: 全LineItem取得**
- **エンドポイント**: `GET /ims/oneroster/gradebook/v1p2/lineItems`
- **説明**: システム内の全課題・評価項目を取得
- **パラメータ**: Categories APIと同様のクエリパラメータをサポート
- **レスポンス**: 200 OK、LineItemの配列
- **認証**: OAuth 2.0スコープ `gradebook.readonly`

**FR-LI-002: 単一LineItem取得**
- **エンドポイント**: `GET /ims/oneroster/gradebook/v1p2/lineItems/{id}`
- **説明**: 指定されたsourcedIdのLineItemを取得
- **レスポンス**: 200 OK、404 Not Found
- **認証**: OAuth 2.0スコープ `gradebook.readonly`

**FR-LI-003: LineItem作成/更新**
- **エンドポイント**: `PUT /ims/oneroster/gradebook/v1p2/lineItems/{id}`
- **説明**: LineItemを作成または更新
- **リクエストボディ**:
  ```json
  {
    "lineItem": {
      "sourcedId": "lineitem-456",
      "status": "active",
      "title": "Chapter 5 Quiz",
      "description": "Quiz covering chapter 5 material",
      "assignDate": "2024-10-01",
      "dueDate": "2024-10-15",
      "class": {
        "sourcedId": "class-789",
        "type": "class"
      },
      "category": {
        "sourcedId": "category-123",
        "type": "category"
      },
      "resultValueMin": 0,
      "resultValueMax": 100
    }
  }
  ```
- **レスポンス**: 200 OK（更新）、201 Created（新規作成）
- **認証**: OAuth 2.0スコープ `gradebook.createput`
- **バリデーション**:
  - `title`: 必須、1-255文字
  - `class.sourcedId`: 必須、Rostering Serviceで存在確認
  - `assignDate`, `dueDate`: ISO 8601日付形式
  - `resultValueMin` < `resultValueMax`

**FR-LI-004: LineItem削除**
- **エンドポイント**: `DELETE /ims/oneroster/gradebook/v1p2/lineItems/{id}`
- **説明**: LineItemを論理削除
- **レスポンス**: 204 No Content、404 Not Found
- **認証**: OAuth 2.0スコープ `gradebook.delete`

**FR-LI-005: クラス別LineItem取得**
- **エンドポイント**: `GET /ims/oneroster/gradebook/v1p2/classes/{class_id}/lineItems`
- **説明**: 指定クラスのLineItemを取得
- **パラメータ**: クエリパラメータをサポート
- **認証**: OAuth 2.0スコープ `gradebook.readonly`

#### 3.1.3 Results API

**FR-RES-001: 全Result取得**
- **エンドポイント**: `GET /ims/oneroster/gradebook/v1p2/results`
- **説明**: システム内の全成績を取得
- **パラメータ**: クエリパラメータをサポート
- **レスポンス**: 200 OK、Resultの配列
- **認証**: OAuth 2.0スコープ `gradebook.readonly`

**FR-RES-002: 単一Result取得**
- **エンドポイント**: `GET /ims/oneroster/gradebook/v1p2/results/{id}`
- **説明**: 指定されたsourcedIdのResultを取得
- **レスポンス**: 200 OK、404 Not Found
- **認証**: OAuth 2.0スコープ `gradebook.readonly`

**FR-RES-003: Result作成/更新**
- **エンドポイント**: `PUT /ims/oneroster/gradebook/v1p2/results/{id}`
- **説明**: Resultを作成または更新
- **リクエストボディ**:
  ```json
  {
    "result": {
      "sourcedId": "result-101",
      "status": "active",
      "lineItem": {
        "sourcedId": "lineitem-456",
        "type": "lineItem"
      },
      "student": {
        "sourcedId": "user-student-1",
        "type": "user"
      },
      "scoreStatus": "submitted",
      "score": 85,
      "scoreDate": "2024-10-14",
      "comment": "Good work!",
      "late": false,
      "missing": false
    }
  }
  ```
- **レスポンス**: 200 OK（更新）、201 Created（新規作成）
- **認証**: OAuth 2.0スコープ `gradebook.createput`
- **バリデーション**:
  - `lineItem.sourcedId`: 必須、LineItemの存在確認
  - `student.sourcedId`: 必須、Rostering Serviceで存在確認
  - `score`: LineItemのresultValueMin～Max範囲内
  - `scoreDate`: ISO 8601日付形式

**FR-RES-004: Result削除**
- **エンドポイント**: `DELETE /ims/oneroster/gradebook/v1p2/results/{id}`
- **説明**: Resultを論理削除
- **レスポンス**: 204 No Content、404 Not Found
- **認証**: OAuth 2.0スコープ `gradebook.delete`

**FR-RES-005: LineItem別Result取得**
- **エンドポイント**: `GET /ims/oneroster/gradebook/v1p2/lineItems/{lineitem_id}/results`
- **説明**: 指定LineItemの全Resultを取得
- **認証**: OAuth 2.0スコープ `gradebook.readonly`

**FR-RES-006: 学生別Result取得**
- **エンドポイント**: `GET /ims/oneroster/gradebook/v1p2/students/{student_id}/results`
- **説明**: 指定学生の全Resultを取得
- **認証**: OAuth 2.0スコープ `gradebook.readonly`

### 3.2 Consumer機能（APIクライアント側）

**FR-CON-001: OAuth 2.0トークン取得**
- **説明**: Client Credentials Grantを使用してアクセストークンを取得
- **パラメータ**: client_id、client_secret、scope
- **機能**: 
  - トークンのキャッシュ管理
  - 期限切れ前の自動更新
  - エラー時のリトライ

**FR-CON-002: Provider API呼び出し**
- **説明**: 認証済みリクエストでProvider APIを呼び出し
- **機能**:
  - Bearer Token認証ヘッダーの自動付与
  - 401エラー時のトークン再取得
  - レスポンスのパース

**FR-CON-003: Rostering Service連携**
- **説明**: Class、User、AcademicSessionの存在確認
- **機能**: Rostering APIへのHTTPリクエスト

### 3.3 共通機能

**FR-COM-001: ページネーション**
- **パラメータ**: `limit`, `offset`
- **デフォルト**: limit=100, offset=0
- **制限**: limit最大値=1000
- **レスポンスヘッダー**: 
  - `X-Total-Count`: 総レコード数
  - `Link`: 次ページのURL (rel="next")

**FR-COM-002: フィルタリング**
- **パラメータ**: `filter`
- **構文**: `field operator 'value'`
- **対応演算子**: =, !=, >, >=, <, <=, ~ (LIKE)
- **例**: `filter=status='active' AND title~'Quiz'`

**FR-COM-003: ソート**
- **パラメータ**: `sort`, `orderBy`
- **例**: `sort=dateLastModified&orderBy=desc`
- **対応順序**: asc、desc

**FR-COM-004: フィールド選択**
- **パラメータ**: `fields`
- **例**: `fields=sourcedId,title,status`
- **動作**: 指定フィールドのみ返却（sourcedIdは常に含む）

**FR-COM-005: エラーハンドリング**
- **形式**: OneRoster標準エラーレスポンス
- **構造**:
  ```json
  {
    "statusInfoSet": [{
      "imsx_codeMajor": "failure",
      "imsx_severity": "error",
      "imsx_description": "詳細なエラーメッセージ",
      "imsx_codeMinor": "エラーコード"
    }]
  }
  ```
- **HTTPステータスコード**:
  - 200: 成功（GET, PUT更新）
  - 201: 作成成功（PUT新規）
  - 204: 削除成功（DELETE）
  - 400: 不正なリクエスト
  - 401: 認証エラー
  - 403: 権限エラー
  - 404: リソース未発見
  - 500: サーバーエラー

**FR-COM-006: ロギング**
- **レベル**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **記録内容**:
  - リクエスト/レスポンスのHTTPメソッド、URL、ステータスコード
  - OAuth 2.0トークン取得/更新イベント
  - エラー詳細（スタックトレース）
  - データベースクエリ（DEBUGレベル）

## 4. データ整合性要件

**DR-001: 参照整合性**
- LineItem.categorySourcedId → Categories.sourcedId（外部キー）
- Result.lineItemSourcedId → LineItems.sourcedId（外部キー）
- LineItem.classSourcedId → Rostering Service Classes（API検証）
- Result.studentSourcedId → Rostering Service Users（API検証）

**DR-002: データバリデーション**
- すべてのsourcedIdは一意
- statusは'active'または'tobedeleted'
- 日付はISO 8601形式
- weightは0.0～1.0の範囲

**DR-003: 論理削除**
- DELETE操作は物理削除ではなく、status='tobedeleted'に更新
- 論理削除されたレコードもGETで取得可能（filter=status='active'で除外可能）

## 5. セキュリティ要件

**SR-001: OAuth 2.0認証**
- すべてのAPIエンドポイントはOAuth 2.0で保護
- Client Credentials Grantのみサポート
- スコープベースの認可制御

**SR-002: TLS通信**
- すべてのHTTP通信はTLS 1.2以上で暗号化
- 開発環境では自己署名証明書を許可

**SR-003: 入力検証**
- すべてのユーザー入力をサニタイズ
- SQLインジェクション対策（パラメータ化クエリ）
- XSS対策（出力エスケープ）

## 6. パフォーマンス要件

**PR-001: レスポンスタイム**
- GETリクエスト: 平均500ms以下
- PUT/DELETEリクエスト: 平均1秒以下

**PR-002: スループット**
- 同時リクエスト: 最低100リクエスト/秒

**PR-003: データベース接続**
- コネクションプール管理
- アイドル接続の自動クローズ

## 7. 互換性要件

**CR-001: OneRoster 1.2準拠**
- IMS Global OneRoster Gradebook Service 1.2仕様に完全準拠
- IMS Certification準備可能な実装

**CR-002: データベース**
- PostgreSQL 12以上
- GUID、JSON、JSONB型のサポート

**CR-003: 言語・フレームワーク**
- Node.js 18+ / Express.js 4+
- Python 3.10+ / FastAPI 0.100+
- Java 17+ / Spring Boot 3.0+

## 8. テスト要件

**TR-001: 単体テスト**
- コードカバレッジ: 最低80%
- すべてのController、Service、Modelをテスト

**TR-002: 統合テスト**
- API全エンドポイントの統合テスト
- OAuth 2.0認証フローのテスト
- データベース操作のテスト

**TR-003: E2Eテスト**
- Provider-Consumer間の連携テスト
- Postman/Newmanによる自動APIテスト

## 9. ドキュメント要件

**DOC-001: API仕様書**
- OpenAPI 3.0形式のAPI定義
- Swagger UIによるインタラクティブドキュメント

**DOC-002: 開発者ガイド**
- セットアップ手順
- 実装例とサンプルコード
- トラブルシューティング

**DOC-003: アーキテクチャ設計書**
- システムアーキテクチャ図
- データモデル図（ER図）
- シーケンス図

## 10. 承認

| 役割 | 氏名 | 承認日 | 署名 |
|------|------|--------|------|
| プロジェクトマネージャー | | | |
| テクニカルリード | | | |
| 品質保証担当 | | | |

## 変更履歴

| バージョン | 日付 | 変更者 | 変更内容 |
|-----------|------|--------|---------|
| 1.0.0 | 2025-10-30 | Initial | 初版作成 |
