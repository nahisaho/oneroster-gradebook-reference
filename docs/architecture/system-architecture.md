# OneRoster Gradebook サービス - システムアーキテクチャ設計書

## バージョン情報
- **文書バージョン**: 1.0.0
- **作成日**: 2025-10-30
- **ステータス**: Draft

## 1. システム概要

### 1.1 アーキテクチャスタイル

本実装は**RESTful APIアーキテクチャ**を採用し、以下の原則に基づいています。

- **リソース指向**: Categories、LineItems、Resultsをリソースとして扱う
- **ステートレス**: サーバーはクライアントの状態を保持しない
- **キャッシュ可能**: OAuth 2.0トークンをクライアント側でキャッシュ
- **階層化システム**: API層、ビジネスロジック層、データアクセス層の分離

### 1.2 システム構成図

```
┌─────────────────┐
│   LMS/SIS       │  Consumer（クライアント）
│   Consumer      │
└────────┬────────┘
         │ HTTPS + OAuth 2.0
         │
┌────────▼────────────────────────────────────────┐
│         OneRoster Gradebook Service             │
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │  API Layer (Controllers/Endpoints)      │   │
│  │  - Categories Controller                │   │
│  │  - LineItems Controller                 │   │
│  │  - Results Controller                   │   │
│  └──────────────┬──────────────────────────┘   │
│                 │                               │
│  ┌──────────────▼──────────────────────────┐   │
│  │  Security Layer                         │   │
│  │  - OAuth 2.0 Authentication             │   │
│  │  - Scope-based Authorization            │   │
│  └──────────────┬──────────────────────────┘   │
│                 │                               │
│  ┌──────────────▼──────────────────────────┐   │
│  │  Business Logic Layer (Services)        │   │
│  │  - Validation                           │   │
│  │  - Pagination/Filtering                 │   │
│  │  - External API calls (Rostering)       │   │
│  └──────────────┬──────────────────────────┘   │
│                 │                               │
│  ┌──────────────▼──────────────────────────┐   │
│  │  Data Access Layer (Models/Repository)  │   │
│  │  - ORM (Sequelize/SQLAlchemy/JPA)       │   │
│  │  - Database Queries                     │   │
│  └──────────────┬──────────────────────────┘   │
│                 │                               │
└─────────────────┼───────────────────────────────┘
                  │
         ┌────────▼────────┐
         │  PostgreSQL     │
         │  Database       │
         └─────────────────┘
```

### 1.3 デプロイ構成

```
                    ┌──────────────┐
                    │ Load Balancer│
                    └───────┬──────┘
                            │
        ┏━━━━━━━━━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━━━┓
        ▼                                        ▼
┌───────────────┐                      ┌───────────────┐
│ App Instance 1│                      │ App Instance 2│
│  (Container)  │                      │  (Container)  │
└───────┬───────┘                      └───────┬───────┘
        │                                      │
        └──────────────┬───────────────────────┘
                       ▼
              ┌─────────────────┐
              │ PostgreSQL      │
              │ (Primary)       │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ PostgreSQL      │
              │ (Read Replica)  │
              └─────────────────┘
```

## 2. 技術スタック比較

### 2.1 Node.js実装

| レイヤー | 技術 | 理由 |
|---------|------|------|
| **Webフレームワーク** | Express.js 4.x | 軽量、柔軟、豊富なミドルウェア |
| **ORM** | Sequelize 6.x | PostgreSQL完全対応、マイグレーション機能 |
| **OAuth 2.0サーバー** | oauth2-server | OAuth 2.0標準準拠 |
| **HTTPクライアント** | axios | Promise対応、インターセプター機能 |
| **バリデーション** | express-validator | Expressとの統合が容易 |
| **テスト** | Jest + Supertest | スナップショットテスト、モック機能 |

**ディレクトリ構造**:
```
gradebook-nodejs/
├── src/
│   ├── config/
│   │   ├── database.js
│   │   └── oauth.js
│   ├── models/
│   │   ├── index.js
│   │   ├── category.js
│   │   ├── lineItem.js
│   │   └── result.js
│   ├── controllers/
│   │   ├── categoryController.js
│   │   ├── lineItemController.js
│   │   └── resultController.js
│   ├── middleware/
│   │   ├── auth.js
│   │   ├── pagination.js
│   │   └── errorHandler.js
│   ├── services/
│   │   ├── oauthClient.js
│   │   └── rosteringService.js
│   ├── routes/
│   │   └── index.js
│   ├── utils/
│   │   └── logger.js
│   └── app.js
├── tests/
│   ├── unit/
│   └── integration/
├── migrations/
├── .env.example
├── package.json
└── README.md
```

### 2.2 Python実装

| レイヤー | 技術 | 理由 |
|---------|------|------|
| **Webフレームワーク** | FastAPI 0.100+ | 高速、自動ドキュメント生成、型安全 |
| **ORM** | SQLAlchemy 2.0 | 業界標準、柔軟なクエリビルダー |
| **OAuth 2.0** | Authlib | OAuth 2.0/OpenID Connect完全対応 |
| **HTTPクライアント** | httpx | async対応、HTTP/2サポート |
| **バリデーション** | Pydantic | FastAPI統合、型ヒント |
| **テスト** | pytest + httpx | フィクスチャ、パラメータ化テスト |

**ディレクトリ構造**:
```
gradebook-python/
├── app/
│   ├── api/
│   │   └── v1p2/
│   │       ├── endpoints/
│   │       │   ├── categories.py
│   │       │   ├── line_items.py
│   │       │   └── results.py
│   │       ├── dependencies.py
│   │       └── router.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   └── security.py
│   ├── models/
│   │   ├── category.py
│   │   ├── line_item.py
│   │   └── result.py
│   ├── schemas/
│   │   └── gradebook.py
│   ├── services/
│   │   ├── oauth_client.py
│   │   └── rostering_service.py
│   └── main.py
├── tests/
│   ├── unit/
│   └── integration/
├── alembic/
│   └── versions/
├── .env.example
├── requirements.txt
└── README.md
```

### 2.3 Java実装

| レイヤー | 技術 | 理由 |
|---------|------|------|
| **Webフレームワーク** | Spring Boot 3.0+ | エンタープライズ標準、自動設定 |
| **ORM** | Spring Data JPA | Hibernate統合、リポジトリパターン |
| **OAuth 2.0** | Spring Security OAuth2 | Spring統合、包括的なセキュリティ |
| **HTTPクライアント** | RestTemplate / WebClient | Spring標準 |
| **バリデーション** | Jakarta Validation | Bean Validation標準 |
| **テスト** | JUnit 5 + MockMvc | Spring Test統合 |

**ディレクトリ構造**:
```
gradebook-java/
├── src/
│   ├── main/
│   │   ├── java/com/example/gradebook/
│   │   │   ├── GradebookApplication.java
│   │   │   ├── config/
│   │   │   │   ├── SecurityConfig.java
│   │   │   │   ├── DatabaseConfig.java
│   │   │   │   └── OAuth2Config.java
│   │   │   ├── controller/
│   │   │   │   ├── CategoryController.java
│   │   │   │   ├── LineItemController.java
│   │   │   │   └── ResultController.java
│   │   │   ├── model/
│   │   │   │   ├── Category.java
│   │   │   │   ├── LineItem.java
│   │   │   │   └── Result.java
│   │   │   ├── repository/
│   │   │   │   ├── CategoryRepository.java
│   │   │   │   ├── LineItemRepository.java
│   │   │   │   └── ResultRepository.java
│   │   │   ├── service/
│   │   │   │   ├── CategoryService.java
│   │   │   │   ├── OAuth2ClientService.java
│   │   │   │   └── RosteringService.java
│   │   │   ├── dto/
│   │   │   │   └── OneRosterResponse.java
│   │   │   └── exception/
│   │   │       └── GlobalExceptionHandler.java
│   │   └── resources/
│   │       ├── application.yml
│   │       └── db/migration/
│   └── test/
│       └── java/com/example/gradebook/
├── pom.xml
└── README.md
```

## 3. データベース設計

### 3.1 ER図

```
┌─────────────────────┐
│     Categories      │
│─────────────────────│
│ PK sourced_id       │
│    status           │
│    date_last_mod    │
│    title            │
│    weight           │
└──────────┬──────────┘
           │
           │ 1
           │
           │ *
┌──────────▼──────────┐
│     LineItems       │
│─────────────────────│
│ PK sourced_id       │
│    status           │
│    date_last_mod    │
│    title            │
│    description      │
│    assign_date      │
│    due_date         │
│    class_sourced_id │ ◄─── Rostering Service
│ FK category_src_id  │
│    result_val_min   │
│    result_val_max   │
└──────────┬──────────┘
           │
           │ 1
           │
           │ *
┌──────────▼──────────┐
│      Results        │
│─────────────────────│
│ PK sourced_id       │
│    status           │
│    date_last_mod    │
│ FK line_item_src_id │
│    student_src_id   │ ◄─── Rostering Service
│    score_status     │
│    score            │
│    text_score       │
│    score_date       │
│    comment          │
│    late             │
│    missing          │
└─────────────────────┘
```

### 3.2 テーブル定義

#### Categories テーブル

| カラム名 | データ型 | 制約 | 説明 |
|---------|---------|------|------|
| sourced_id | VARCHAR(255) | PK | 一意識別子 |
| status | ENUM | NOT NULL | 'active' / 'tobedeleted' |
| date_last_modified | TIMESTAMP | NOT NULL | 最終更新日時 |
| title | VARCHAR(255) | NOT NULL | カテゴリー名 |
| weight | DECIMAL(5,4) | NULL | 加重値（0.0～1.0） |
| created_at | TIMESTAMP | DEFAULT NOW() | 作成日時 |

**インデックス**:
- PRIMARY KEY (sourced_id)
- INDEX idx_category_status (status)

#### LineItems テーブル

| カラム名 | データ型 | 制約 | 説明 |
|---------|---------|------|------|
| sourced_id | VARCHAR(255) | PK | 一意識別子 |
| status | ENUM | NOT NULL | 'active' / 'tobedeleted' |
| date_last_modified | TIMESTAMP | NOT NULL | 最終更新日時 |
| title | VARCHAR(255) | NOT NULL | 課題名 |
| description | TEXT | NULL | 説明 |
| assign_date | DATE | NULL | 割り当て日 |
| due_date | DATE | NULL | 期限日 |
| class_sourced_id | VARCHAR(255) | NOT NULL | クラスID |
| category_sourced_id | VARCHAR(255) | FK | カテゴリーID |
| grading_period_sourced_id | VARCHAR(255) | NULL | 成績期間ID |
| academic_session_sourced_id | VARCHAR(255) | NULL | 学期ID |
| school_sourced_id | VARCHAR(255) | NULL | 学校ID |
| score_scale_sourced_id | VARCHAR(255) | NULL | 評価スケールID |
| result_value_min | DECIMAL(10,2) | NULL | 最小スコア |
| result_value_max | DECIMAL(10,2) | NULL | 最大スコア |
| learning_objective_set | JSONB | NULL | 学習目標セット |
| created_at | TIMESTAMP | DEFAULT NOW() | 作成日時 |

**インデックス**:
- PRIMARY KEY (sourced_id)
- FOREIGN KEY (category_sourced_id) REFERENCES categories(sourced_id)
- INDEX idx_lineitem_class (class_sourced_id)
- INDEX idx_lineitem_category (category_sourced_id)
- INDEX idx_lineitem_status (status)

#### Results テーブル

| カラム名 | データ型 | 制約 | 説明 |
|---------|---------|------|------|
| sourced_id | VARCHAR(255) | PK | 一意識別子 |
| status | ENUM | NOT NULL | 'active' / 'tobedeleted' |
| date_last_modified | TIMESTAMP | NOT NULL | 最終更新日時 |
| line_item_sourced_id | VARCHAR(255) | FK NOT NULL | LineItemID |
| student_sourced_id | VARCHAR(255) | NOT NULL | 学生ID |
| class_sourced_id | VARCHAR(255) | NULL | クラスID |
| score_status | ENUM | NULL | スコア状態 |
| score | DECIMAL(10,2) | NULL | 数値スコア |
| text_score | VARCHAR(255) | NULL | テキストスコア |
| score_date | DATE | NULL | 採点日 |
| comment | TEXT | NULL | コメント |
| score_scale_sourced_id | VARCHAR(255) | NULL | 評価スケールID |
| learning_objective_set | JSONB | NULL | 学習目標セット |
| in_progress | BOOLEAN | DEFAULT FALSE | 進行中 |
| incomplete | BOOLEAN | DEFAULT FALSE | 未完了 |
| late | BOOLEAN | DEFAULT FALSE | 遅延 |
| missing | BOOLEAN | DEFAULT FALSE | 未提出 |
| created_at | TIMESTAMP | DEFAULT NOW() | 作成日時 |

**インデックス**:
- PRIMARY KEY (sourced_id)
- FOREIGN KEY (line_item_sourced_id) REFERENCES line_items(sourced_id)
- INDEX idx_result_lineitem (line_item_sourced_id)
- INDEX idx_result_student (student_sourced_id)
- INDEX idx_result_class (class_sourced_id)
- INDEX idx_result_status (status)

### 3.3 データベースマイグレーション戦略

- **ツール**: 
  - Node.js: Sequelize Migrations
  - Python: Alembic
  - Java: Flyway
- **バージョン管理**: Gitでマイグレーションスクリプトを管理
- **適用順序**: タイムスタンプベースの順次適用
- **ロールバック**: 各マイグレーションにdownメソッドを実装

## 4. API設計

### 4.1 エンドポイント一覧

| リソース | HTTPメソッド | パス | 説明 |
|---------|------------|------|------|
| Categories | GET | /categories | 全カテゴリー取得 |
| Categories | GET | /categories/{id} | 単一カテゴリー取得 |
| Categories | PUT | /categories/{id} | カテゴリー作成/更新 |
| Categories | DELETE | /categories/{id} | カテゴリー削除 |
| Categories | GET | /classes/{class_id}/categories | クラス別カテゴリー |
| LineItems | GET | /lineItems | 全LineItem取得 |
| LineItems | GET | /lineItems/{id} | 単一LineItem取得 |
| LineItems | PUT | /lineItems/{id} | LineItem作成/更新 |
| LineItems | DELETE | /lineItems/{id} | LineItem削除 |
| LineItems | GET | /classes/{class_id}/lineItems | クラス別LineItem |
| Results | GET | /results | 全Result取得 |
| Results | GET | /results/{id} | 単一Result取得 |
| Results | PUT | /results/{id} | Result作成/更新 |
| Results | DELETE | /results/{id} | Result削除 |
| Results | GET | /lineItems/{lineitem_id}/results | LineItem別Result |
| Results | GET | /students/{student_id}/results | 学生別Result |

### 4.2 リクエスト/レスポンス例

**GET /categories?limit=2&offset=0**

レスポンス:
```json
{
  "categories": [
    {
      "sourcedId": "cat-001",
      "status": "active",
      "dateLastModified": "2024-10-30T10:00:00Z",
      "title": "Homework",
      "weight": 0.3
    },
    {
      "sourcedId": "cat-002",
      "status": "active",
      "dateLastModified": "2024-10-30T11:00:00Z",
      "title": "Exams",
      "weight": 0.7
    }
  ]
}
```

ヘッダー:
```
X-Total-Count: 10
Link: </categories?limit=2&offset=2>; rel="next"
```

### 4.3 エラーレスポンス例

```json
{
  "statusInfoSet": [
    {
      "imsx_codeMajor": "failure",
      "imsx_severity": "error",
      "imsx_description": "Category not found",
      "imsx_codeMinor": "unknown_object"
    }
  ]
}
```

## 5. セキュリティアーキテクチャ

### 5.1 OAuth 2.0フロー

```
┌────────┐                                  ┌───────────┐
│ Client │                                  │  Auth     │
│ (LMS)  │                                  │  Server   │
└───┬────┘                                  └─────┬─────┘
    │                                             │
    │ 1. POST /oauth/token                        │
    │    grant_type=client_credentials            │
    │    client_id=xxx                            │
    │    client_secret=yyy                        │
    │────────────────────────────────────────────>│
    │                                             │
    │ 2. 200 OK                                   │
    │    {access_token, expires_in, scope}        │
    │<────────────────────────────────────────────│
    │                                             │
    │                                  ┌──────────▼────┐
    │                                  │  Gradebook    │
    │                                  │  API Server   │
    │                                  └──────────┬────┘
    │ 3. GET /categories                         │
    │    Authorization: Bearer {token}           │
    │───────────────────────────────────────────>│
    │                                            │
    │ 4. Validate token & scope                 │
    │                                            │
    │ 5. 200 OK                                  │
    │    {categories: [...]}                     │
    │<───────────────────────────────────────────│
    │                                            │
```

### 5.2 認可マトリクス

| エンドポイント | gradebook.readonly | gradebook.createput | gradebook.delete |
|--------------|-------------------|--------------------|-----------------| 
| GET /categories | ○ | ○ | ○ |
| GET /categories/{id} | ○ | ○ | ○ |
| PUT /categories/{id} | × | ○ | ○ |
| DELETE /categories/{id} | × | × | ○ |

## 6. 外部システム連携

### 6.1 Rostering Service連携

```
┌────────────────┐         ┌────────────────┐
│  Gradebook     │         │  Rostering     │
│  Service       │         │  Service       │
└────────┬───────┘         └────────┬───────┘
         │                          │
         │ Validate Class           │
         │ GET /classes/{id}        │
         │─────────────────────────>│
         │                          │
         │ 200 OK or 404            │
         │<─────────────────────────│
         │                          │
```

**検証タイミング**:
- LineItem作成時: class_sourced_idの存在確認
- Result作成時: student_sourced_idの存在確認

## 7. 監視・ロギングアーキテクチャ

### 7.1 ログ収集

```
┌───────────┐     ┌───────────┐     ┌───────────┐
│  App      │────>│ Log       │────>│ Log       │
│ Container │     │ Aggregator│     │ Storage   │
│           │     │(Fluentd)  │     │(ELK)      │
└───────────┘     └───────────┘     └───────────┘
```

### 7.2 メトリクス収集

```
┌───────────┐     ┌───────────┐     ┌───────────┐
│  App      │────>│ Metrics   │────>│ Dashboard │
│ Container │     │ Collector │     │(Grafana)  │
│           │     │(Prometheus│     │           │
└───────────┘     └───────────┘     └───────────┘
```

## 8. CI/CDパイプライン

```
┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐
│ Code │─>│ Build│─>│ Test │─>│Deploy│─>│Monitor│
│Commit│  │      │  │      │  │      │  │       │
└──────┘  └──────┘  └──────┘  └──────┘  └──────┘
   │         │         │         │         │
   │         │         │         │         │
   v         v         v         v         v
 GitHub   Docker   Jest/    Kubernetes  Grafana
          Build   Pytest    /Docker     /ELK
                  /JUnit   Compose
```

**パイプライン段階**:
1. **Code Commit**: GitHubへのプッシュ
2. **Build**: Dockerイメージビルド
3. **Test**: 単体/統合テスト実行
4. **Deploy**: ステージング環境へのデプロイ
5. **Monitor**: ヘルスチェック、メトリクス監視

## 9. 承認

| 役割 | 氏名 | 承認日 | 署名 |
|------|------|--------|------|
| アーキテクト | | | |
| テクニカルリード | | | |

## 変更履歴

| バージョン | 日付 | 変更者 | 変更内容 |
|-----------|------|--------|---------|
| 1.0.0 | 2025-10-30 | Initial | 初版作成 |
