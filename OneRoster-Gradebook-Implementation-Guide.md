title: OneRoster Gradebook Service 実装ガイド - 完全版

# 第1章 OneRoster Gradebook Serviceの理解

## 1.1 OneRoster Gradebook Serviceとは

OneRoster Gradebook Service 1.2は、K-12教育機関における成績・評価データの標準化された交換を実現する、IMS Global Learning Consortium（1EdTech）による仕様です。2022年9月19日に正式リリースされたバージョン1.2では、Gradebook機能が独立したサービスとして分離され、大幅な機能強化が実現されました。

### 解決する課題

従来、教育機関では以下のような課題がありました。

- **手動での二重入力**: 教員が同じ成績データをLMSとSISに手動で入力
- **システム間の互換性欠如**: ベンダー独自形式によるデータ連携の困難さ
- **詳細な評価情報の欠落**: 課題レベルでの成績転送ができない
- **標準準拠評価の未対応**: 学習目標との紐付けができない

OneRoster Gradebookは、これらの課題を解決し、**年間数百時間の教員負担を削減**します。

### アーキテクチャ概要

OneRoster 1.2は3つの独立したサービスに分離されています。

| サービス | エンドポイント | 管理対象 |
|---------|--------------|---------|
| **Rostering Service** | `/ims/oneroster/rostering/v1p2` | 学期、ユーザー、クラス、コース、組織、登録情報 |
| **Gradebook Service** | `/ims/oneroster/gradebook/v1p2` | 成績、課題、カテゴリー、スコアスケール |
| **Resources Service** | `/ims/oneroster/resources/v1p2` | 学習リソース割り当て |

**重要**: Gradebook ServiceはRostering Serviceに強く依存しており、Class、User、AcademicSessionなどのエンティティをsourcedIdで参照します。本ガイドでは、Rostering Serviceが既に存在することを前提とします。

## 1.2 データモデルの概要

### Gradebook行列の構造

Gradebookは成績の行列として構造化されています。

| 学生 | LineItem1<br>(課題1) | LineItem2<br>(課題2) | LineItem3<br>(小テスト1) |
|------|---------------------|---------------------|------------------------|
| **Student A** | 85点 | 90点 | A- |
| **Student B** | 92点 | 未提出 | B+ |
| **Student C** | 78点 | 85点 | A |

**グループ化**: Category（宿題: 30%, 試験: 70%）によって加重計算

### コアリソース

| リソース | 説明 | 例 |
|---------|------|-----|
| **Category** | LineItemをグループ化（加重値付き） | 「宿題」（30%）、「試験」（70%） |
| **LineItem** | 課題・評価項目（行列の列） | 「第5章小テスト」、「期末レポート」 |
| **Result** | 個別学生の成績（行列のセル） | 学生Aの第5章小テスト: 85点 |
| **ScoreScale** | 評価スケール定義（v1.2新機能） | A-F、0-100、ルーブリック |

### v1.2の新機能

- **ScoreScale**: システム間で統一された採点基準の交換
- **AssessmentLineItem/Result**: クラスに紐付かない階層型評価
- **一括操作**: POSTエンドポイントによる効率的なデータ作成
- **LearningObjectiveSet**: CASE仕様による標準準拠型評価
- **textScore**: 非数値スコア（ルーブリック、記述的評価）

## 1.3 実装タイプの選択

### Provider vs Consumer

| タイプ | 役割 | 実装内容 | 例 |
|--------|------|---------|-----|
| **Provider** | データ提供側 | GETエンドポイント実装、他システムからのリクエストに応答 | SISが成績を提供 |
| **Consumer** | データ利用側 | 他システムのAPIを呼び出してデータ取得 | LMSがSISのカテゴリー取得 |
| **両方** | 双方向連携 | 両方のエンドポイント実装 | LMS↔SIS相互連携 |

本ガイドでは、**Provider + Consumer両方の実装**を網羅します。

### システムタイプ別の実装スコープ

**LMS（学習管理システム）の場合:**
- Provider: LineItems、Resultsを提供（課題と成績の送信）
- Consumer: Categoriesを取得（SISの成績カテゴリーに合わせる）

**SIS（学生情報システム）の場合:**
- Provider: Categoriesを提供（成績カテゴリーの定義）
- Consumer: LineItems、Resultsを取得（LMSからの成績受信）

**評価システムの場合:**
- Provider: AssessmentLineItems、AssessmentResultsを提供
- Consumer: Rostering情報を取得（学生・クラス情報）

---

# 第2章 開発環境のセットアップ

## 2.1 技術スタックの選択

本ガイドでは、以下の3つの技術スタックでの実装例を提供します。

| 言語 | フレームワーク | ORM/DB | OAuth 2.0ライブラリ |
|------|--------------|--------|------------------|
| **Node.js** | Express.js | Sequelize / PostgreSQL | passport, oauth2-server |
| **Python** | FastAPI | SQLAlchemy / PostgreSQL | authlib, python-jose |
| **Java** | Spring Boot | Spring Data JPA / PostgreSQL | Spring Security OAuth2 |

### 共通要件

- **データベース**: PostgreSQL 12+ (GUID、JSON対応)
- **TLS**: TLS 1.2以上必須
- **OAuth 2.0**: Client Credentials Grant対応
- **HTTPクライアント**: REST API呼び出し用

## 2.2 Node.js (Express.js) 環境構築

:::note info
**Express.jsとは**

Express.jsは、Node.jsで最も広く使われている軽量なWebフレームワークです。OneRoster Gradebook実装に最適な理由：

- **シンプルで柔軟**: ミドルウェアベースのアーキテクチャで、OAuth 2.0やページネーションを自由に実装可能
- **豊富なエコシステム**: oauth2-server、Sequelize、Passportなど、OneRoster実装に必要なライブラリが充実
- **非同期処理**: async/awaitでOAuth トークン管理やデータベース操作を効率的に処理
- **実績と安定性**: 大規模な教育システムでの採用実績が豊富
- **学習コスト低**: JavaScriptエンジニアがすぐに習得でき、フロントエンドとの統一言語も可能

公式サイト: https://expressjs.com/
:::

### プロジェクト作成

```bash
mkdir gradebook-service
cd gradebook-service
npm init -y
```

### 依存パッケージのインストール

```bash
npm install express pg sequelize dotenv
npm install passport passport-oauth2-client-password oauth2-server
npm install express-validator helmet cors
npm install --save-dev jest supertest nodemon
```

### プロジェクト構造

```
gradebook-service/
├── src/
│   ├── config/
│   │   ├── database.js
│   │   └── oauth.js
│   ├── models/
│   │   ├── category.js
│   │   ├── lineItem.js
│   │   ├── result.js
│   │   └── scoreScale.js
│   ├── controllers/
│   │   ├── categoryController.js
│   │   ├── lineItemController.js
│   │   └── resultController.js
│   ├── routes/
│   │   └── gradebook.js
│   ├── middleware/
│   │   ├── auth.js
│   │   ├── pagination.js
│   │   └── errorHandler.js
│   └── app.js
├── tests/
├── .env
└── package.json
```

### 環境変数設定 (.env)

```bash
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=gradebook
DB_USER=postgres
DB_PASSWORD=your_password

# OAuth 2.0
OAUTH_CLIENT_ID=your_client_id
OAUTH_CLIENT_SECRET=your_client_secret
OAUTH_TOKEN_URL=https://provider.example.com/oauth/token

# Server
PORT=3000
BASE_URL=/ims/oneroster/gradebook/v1p2
```

## 2.3 Python (FastAPI) 環境構築

:::note info
**FastAPIとは**

FastAPIは、Python 3.7+の型ヒントを活用した高速なWebフレームワークです。OneRoster Gradebook実装に最適な理由：

- **高速**: Starlette、Pydanticベースで、NodeJSやGoに匹敵するパフォーマンス
- **自動ドキュメント生成**: OpenAPI/Swagger UIが自動生成され、IMS認定準備に有用
- **型安全**: Pydanticによる自動バリデーションで、OneRosterの厳密なスキーマ検証に対応
- **非同期対応**: `async/await`でOAuth 2.0トークン取得やDB操作を効率化
- **開発効率**: 型ヒントによるIDE補完で、開発速度が向上

公式サイト: https://fastapi.tiangolo.com/
:::

### プロジェクト作成

```bash
mkdir gradebook-service
cd gradebook-service
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 依存パッケージのインストール

```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary
pip install authlib python-jose[cryptography] passlib[bcrypt]
pip install pydantic python-dotenv
pip install pytest httpx
```

### requirements.txt作成

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
authlib==1.2.1
python-jose[cryptography]==3.3.0
python-dotenv==1.0.0
pydantic==2.5.0
pytest==7.4.3
httpx==0.25.1
```

### プロジェクト構造

```
gradebook-service/
├── app/
│   ├── api/
│   │   ├── v1p2/
│   │   │   ├── endpoints/
│   │   │   │   ├── categories.py
│   │   │   │   ├── line_items.py
│   │   │   │   └── results.py
│   │   │   └── router.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── database.py
│   ├── models/
│   │   ├── category.py
│   │   ├── line_item.py
│   │   └── result.py
│   ├── schemas/
│   │   └── gradebook.py
│   ├── services/
│   │   └── oauth_client.py
│   └── main.py
├── tests/
├── .env
└── requirements.txt
```

### 環境変数設定 (.env)

```bash
DATABASE_URL=postgresql://postgres:password@localhost:5432/gradebook
OAUTH_CLIENT_ID=your_client_id
OAUTH_CLIENT_SECRET=your_client_secret
OAUTH_TOKEN_URL=https://provider.example.com/oauth/token
BASE_URL=/ims/oneroster/gradebook/v1p2
```

## 2.4 Java (Spring Boot) 環境構築

:::note info
**Spring Bootとは**

Spring Bootは、Javaで最も人気のあるエンタープライズグレードのWebフレームワークです。OneRoster Gradebook実装に最適な理由：

- **エンタープライズ対応**: 大規模な教育機関や企業システムで実績豊富、Spring Security OAuth2で堅牢な認証を実現
- **統合されたエコシステム**: Spring Data JPA、Spring Security、Spring Bootが統合され、OneRosterの複雑な要件に対応
- **自動設定**: アノテーションベースの設定で、OAuth 2.0サーバーやJPAリポジトリを簡単に構築
- **プロダクション機能**: メトリクス、ヘルスチェック、監視機能が標準装備で、運用管理が容易
- **型安全性**: 静的型付けで、コンパイル時にエラーを検出し、OneRosterスキーマの厳密な実装に有利

公式サイト: https://spring.io/projects/spring-boot
:::

### プロジェクト作成 (Maven)

```bash
mvn archetype:generate -DgroupId=com.example.gradebook \
    -DartifactId=gradebook-service \
    -DarchetypeArtifactId=maven-archetype-quickstart
cd gradebook-service
```

### pom.xml設定

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.0</version>
    </parent>

    <groupId>com.example</groupId>
    <artifactId>gradebook-service</artifactId>
    <version>1.0.0</version>

    <dependencies>
        <!-- Spring Boot Web -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>

        <!-- Spring Data JPA -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>

        <!-- PostgreSQL -->
        <dependency>
            <groupId>org.postgresql</groupId>
            <artifactId>postgresql</artifactId>
            <scope>runtime</scope>
        </dependency>

        <!-- Spring Security OAuth2 -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-oauth2-client</artifactId>
        </dependency>

        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-oauth2-resource-server</artifactId>
        </dependency>

        <!-- Validation -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-validation</artifactId>
        </dependency>

        <!-- Testing -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>
</project>
```

### プロジェクト構造

```
gradebook-service/
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
│   │   │   │   └── OAuth2ClientService.java
│   │   │   └── dto/
│   │   │       └── OneRosterResponse.java
│   │   └── resources/
│   │       └── application.yml
│   └── test/
└── pom.xml
```

### application.yml設定

```yaml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/gradebook
    username: postgres
    password: your_password
    driver-class-name: org.postgresql.Driver
  jpa:
    hibernate:
      ddl-auto: update
    show-sql: true
    properties:
      hibernate:
        format_sql: true

server:
  port: 8080
  servlet:
    context-path: /ims/oneroster/gradebook/v1p2

oauth2:
  client:
    client-id: ${OAUTH_CLIENT_ID}
    client-secret: ${OAUTH_CLIENT_SECRET}
    token-uri: ${OAUTH_TOKEN_URL}
  resource-server:
    jwt:
      issuer-uri: ${OAUTH_ISSUER_URI}
```

## 2.5 データベースセットアップ

### PostgreSQLデータベース作成

```sql
CREATE DATABASE gradebook;

-- UUID拡張を有効化
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- タイムスタンプ用関数
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.date_last_modified = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

### テーブル作成スクリプト

```sql
-- Categories テーブル
CREATE TABLE categories (
    sourced_id VARCHAR(255) PRIMARY KEY,
    status VARCHAR(50) NOT NULL,
    date_last_modified TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    title VARCHAR(255) NOT NULL,
    weight DECIMAL(5,4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- LineItems テーブル
CREATE TABLE line_items (
    sourced_id VARCHAR(255) PRIMARY KEY,
    status VARCHAR(50) NOT NULL,
    date_last_modified TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    assign_date DATE,
    due_date DATE,
    class_sourced_id VARCHAR(255) NOT NULL,
    category_sourced_id VARCHAR(255),
    grading_period_sourced_id VARCHAR(255),
    academic_session_sourced_id VARCHAR(255),
    school_sourced_id VARCHAR(255),
    score_scale_sourced_id VARCHAR(255),
    result_value_min DECIMAL(10,2),
    result_value_max DECIMAL(10,2),
    learning_objective_set JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (category_sourced_id) REFERENCES categories(sourced_id)
);

-- Results テーブル
CREATE TABLE results (
    sourced_id VARCHAR(255) PRIMARY KEY,
    status VARCHAR(50) NOT NULL,
    date_last_modified TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    line_item_sourced_id VARCHAR(255) NOT NULL,
    student_sourced_id VARCHAR(255) NOT NULL,
    class_sourced_id VARCHAR(255),
    score_status VARCHAR(50),
    score DECIMAL(10,2),
    text_score VARCHAR(255),
    score_date DATE,
    comment TEXT,
    score_scale_sourced_id VARCHAR(255),
    learning_objective_set JSONB,
    in_progress BOOLEAN DEFAULT FALSE,
    incomplete BOOLEAN DEFAULT FALSE,
    late BOOLEAN DEFAULT FALSE,
    missing BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (line_item_sourced_id) REFERENCES line_items(sourced_id)
);

-- ScoreScales テーブル
CREATE TABLE score_scales (
    sourced_id VARCHAR(255) PRIMARY KEY,
    status VARCHAR(50) NOT NULL,
    date_last_modified TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    title VARCHAR(255) NOT NULL,
    type VARCHAR(100),
    course_sourced_id VARCHAR(255),
    class_sourced_id VARCHAR(255),
    score_scale_value JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- トリガー設定
CREATE TRIGGER update_category_modtime
    BEFORE UPDATE ON categories
    FOR EACH ROW EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_line_item_modtime
    BEFORE UPDATE ON line_items
    FOR EACH ROW EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_result_modtime
    BEFORE UPDATE ON results
    FOR EACH ROW EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_score_scale_modtime
    BEFORE UPDATE ON score_scales
    FOR EACH ROW EXECUTE FUNCTION update_modified_column();

-- インデックス作成
CREATE INDEX idx_line_items_class ON line_items(class_sourced_id);
CREATE INDEX idx_line_items_category ON line_items(category_sourced_id);
CREATE INDEX idx_results_line_item ON results(line_item_sourced_id);
CREATE INDEX idx_results_student ON results(student_sourced_id);
CREATE INDEX idx_results_class ON results(class_sourced_id);
CREATE INDEX idx_score_scales_class ON score_scales(class_sourced_id);
```

---

# 第3章 データモデルとアーキテクチャ

## 3.1 データモデル実装

### 3.1.1 Node.js (Sequelize) モデル

**models/category.js**

```javascript
const { DataTypes } = require('sequelize');

module.exports = (sequelize) => {
  const Category = sequelize.define('Category', {
    sourcedId: {
      type: DataTypes.STRING(255),
      primaryKey: true,
      field: 'sourced_id'
    },
    status: {
      type: DataTypes.ENUM('active', 'tobedeleted'),
      allowNull: false,
      defaultValue: 'active'
    },
    dateLastModified: {
      type: DataTypes.DATE,
      allowNull: false,
      defaultValue: DataTypes.NOW,
      field: 'date_last_modified'
    },
    title: {
      type: DataTypes.STRING(255),
      allowNull: false
    },
    weight: {
      type: DataTypes.DECIMAL(5, 4),
      allowNull: true,
      validate: {
        min: 0.0,
        max: 1.0
      }
    }
  }, {
    tableName: 'categories',
    timestamps: true,
    createdAt: 'created_at',
    updatedAt: false,
    hooks: {
      beforeUpdate: (category) => {
        category.dateLastModified = new Date();
      }
    }
  });

  return Category;
};
```

**models/lineItem.js**

```javascript
const { DataTypes } = require('sequelize');

module.exports = (sequelize) => {
  const LineItem = sequelize.define('LineItem', {
    sourcedId: {
      type: DataTypes.STRING(255),
      primaryKey: true,
      field: 'sourced_id'
    },
    status: {
      type: DataTypes.ENUM('active', 'tobedeleted'),
      allowNull: false,
      defaultValue: 'active'
    },
    dateLastModified: {
      type: DataTypes.DATE,
      allowNull: false,
      defaultValue: DataTypes.NOW,
      field: 'date_last_modified'
    },
    title: {
      type: DataTypes.STRING(255),
      allowNull: false
    },
    description: {
      type: DataTypes.TEXT,
      allowNull: true
    },
    assignDate: {
      type: DataTypes.DATEONLY,
      allowNull: true,
      field: 'assign_date'
    },
    dueDate: {
      type: DataTypes.DATEONLY,
      allowNull: true,
      field: 'due_date'
    },
    classSourcedId: {
      type: DataTypes.STRING(255),
      allowNull: false,
      field: 'class_sourced_id'
    },
    categorySourcedId: {
      type: DataTypes.STRING(255),
      allowNull: true,
      field: 'category_sourced_id'
    },
    gradingPeriodSourcedId: {
      type: DataTypes.STRING(255),
      allowNull: true,
      field: 'grading_period_sourced_id'
    },
    academicSessionSourcedId: {
      type: DataTypes.STRING(255),
      allowNull: true,
      field: 'academic_session_sourced_id'
    },
    schoolSourcedId: {
      type: DataTypes.STRING(255),
      allowNull: true,
      field: 'school_sourced_id'
    },
    scoreScaleSourcedId: {
      type: DataTypes.STRING(255),
      allowNull: true,
      field: 'score_scale_sourced_id'
    },
    resultValueMin: {
      type: DataTypes.DECIMAL(10, 2),
      allowNull: true,
      field: 'result_value_min'
    },
    resultValueMax: {
      type: DataTypes.DECIMAL(10, 2),
      allowNull: true,
      field: 'result_value_max'
    },
    learningObjectiveSet: {
      type: DataTypes.JSONB,
      allowNull: true,
      field: 'learning_objective_set'
    }
  }, {
    tableName: 'line_items',
    timestamps: true,
    createdAt: 'created_at',
    updatedAt: false,
    hooks: {
      beforeUpdate: (lineItem) => {
        lineItem.dateLastModified = new Date();
      }
    }
  });

  LineItem.associate = (models) => {
    LineItem.belongsTo(models.Category, {
      foreignKey: 'categorySourcedId',
      as: 'category'
    });
  };

  return LineItem;
};
```

**models/result.js**

```javascript
const { DataTypes } = require('sequelize');

module.exports = (sequelize) => {
  const Result = sequelize.define('Result', {
    sourcedId: {
      type: DataTypes.STRING(255),
      primaryKey: true,
      field: 'sourced_id'
    },
    status: {
      type: DataTypes.ENUM('active', 'tobedeleted'),
      allowNull: false,
      defaultValue: 'active'
    },
    dateLastModified: {
      type: DataTypes.DATE,
      allowNull: false,
      defaultValue: DataTypes.NOW,
      field: 'date_last_modified'
    },
    lineItemSourcedId: {
      type: DataTypes.STRING(255),
      allowNull: false,
      field: 'line_item_sourced_id'
    },
    studentSourcedId: {
      type: DataTypes.STRING(255),
      allowNull: false,
      field: 'student_sourced_id'
    },
    classSourcedId: {
      type: DataTypes.STRING(255),
      allowNull: true,
      field: 'class_sourced_id'
    },
    scoreStatus: {
      type: DataTypes.ENUM('earnedPartial', 'earnedFull', 'notEarned',
                           'notSubmitted', 'submitted', 'late',
                           'incomplete', 'missing', 'inProgress', 'withdrawn'),
      allowNull: true,
      field: 'score_status'
    },
    score: {
      type: DataTypes.DECIMAL(10, 2),
      allowNull: true
    },
    textScore: {
      type: DataTypes.STRING(255),
      allowNull: true,
      field: 'text_score'
    },
    scoreDate: {
      type: DataTypes.DATEONLY,
      allowNull: true,
      field: 'score_date'
    },
    comment: {
      type: DataTypes.TEXT,
      allowNull: true
    },
    scoreScaleSourcedId: {
      type: DataTypes.STRING(255),
      allowNull: true,
      field: 'score_scale_sourced_id'
    },
    learningObjectiveSet: {
      type: DataTypes.JSONB,
      allowNull: true,
      field: 'learning_objective_set'
    },
    inProgress: {
      type: DataTypes.BOOLEAN,
      defaultValue: false,
      field: 'in_progress'
    },
    incomplete: {
      type: DataTypes.BOOLEAN,
      defaultValue: false
    },
    late: {
      type: DataTypes.BOOLEAN,
      defaultValue: false
    },
    missing: {
      type: DataTypes.BOOLEAN,
      defaultValue: false
    }
  }, {
    tableName: 'results',
    timestamps: true,
    createdAt: 'created_at',
    updatedAt: false,
    hooks: {
      beforeUpdate: (result) => {
        result.dateLastModified = new Date();
      }
    }
  });

  Result.associate = (models) => {
    Result.belongsTo(models.LineItem, {
      foreignKey: 'lineItemSourcedId',
      as: 'lineItem'
    });
  };

  return Result;
};
```

### 3.1.2 Python (SQLAlchemy) モデル

**models/category.py**

```python
from sqlalchemy import Column, String, Numeric, Enum, DateTime, func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class StatusEnum(enum.Enum):
    active = "active"
    tobedeleted = "tobedeleted"

class Category(Base):
    __tablename__ = "categories"

    sourced_id = Column(String(255), primary_key=True)
    status = Column(Enum(StatusEnum), nullable=False, default=StatusEnum.active)
    date_last_modified = Column(DateTime(timezone=True), nullable=False,
                                server_default=func.now(), onupdate=func.now())
    title = Column(String(255), nullable=False)
    weight = Column(Numeric(5, 4), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # リレーション
    line_items = relationship("LineItem", back_populates="category")

    def to_dict(self):
        return {
            "sourcedId": self.sourced_id,
            "status": self.status.value,
            "dateLastModified": self.date_last_modified.isoformat(),
            "title": self.title,
            "weight": float(self.weight) if self.weight else None
        }
```

**models/line_item.py**

```python
from sqlalchemy import Column, String, Text, Date, Numeric, ForeignKey, Enum, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base

class LineItem(Base):
    __tablename__ = "line_items"

    sourced_id = Column(String(255), primary_key=True)
    status = Column(Enum("active", "tobedeleted", name="status_enum"),
                   nullable=False, default="active")
    date_last_modified = Column(DateTime(timezone=True), nullable=False,
                                server_default=func.now(), onupdate=func.now())
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    assign_date = Column(Date, nullable=True)
    due_date = Column(Date, nullable=True)
    class_sourced_id = Column(String(255), nullable=False)
    category_sourced_id = Column(String(255), ForeignKey("categories.sourced_id"),
                                 nullable=True)
    grading_period_sourced_id = Column(String(255), nullable=True)
    academic_session_sourced_id = Column(String(255), nullable=True)
    school_sourced_id = Column(String(255), nullable=True)
    score_scale_sourced_id = Column(String(255), nullable=True)
    result_value_min = Column(Numeric(10, 2), nullable=True)
    result_value_max = Column(Numeric(10, 2), nullable=True)
    learning_objective_set = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # リレーション
    category = relationship("Category", back_populates="line_items")
    results = relationship("Result", back_populates="line_item")

    def to_dict(self):
        result = {
            "sourcedId": self.sourced_id,
            "status": self.status,
            "dateLastModified": self.date_last_modified.isoformat(),
            "title": self.title,
            "class": {
                "sourcedId": self.class_sourced_id,
                "type": "class"
            }
        }

        if self.description:
            result["description"] = self.description
        if self.assign_date:
            result["assignDate"] = self.assign_date.isoformat()
        if self.due_date:
            result["dueDate"] = self.due_date.isoformat()
        if self.category_sourced_id:
            result["category"] = {
                "sourcedId": self.category_sourced_id,
                "type": "category"
            }
        if self.result_value_min is not None:
            result["resultValueMin"] = float(self.result_value_min)
        if self.result_value_max is not None:
            result["resultValueMax"] = float(self.result_value_max)

        return result
```

**models/result.py**

```python
from sqlalchemy import Column, String, Text, Date, Numeric, Boolean, ForeignKey, Enum, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base

class Result(Base):
    __tablename__ = "results"

    sourced_id = Column(String(255), primary_key=True)
    status = Column(Enum("active", "tobedeleted", name="status_enum"),
                   nullable=False, default="active")
    date_last_modified = Column(DateTime(timezone=True), nullable=False,
                                server_default=func.now(), onupdate=func.now())
    line_item_sourced_id = Column(String(255), ForeignKey("line_items.sourced_id"),
                                  nullable=False)
    student_sourced_id = Column(String(255), nullable=False)
    class_sourced_id = Column(String(255), nullable=True)
    score_status = Column(Enum("earnedPartial", "earnedFull", "notEarned",
                               "notSubmitted", "submitted", "late",
                               "incomplete", "missing", "inProgress", "withdrawn",
                               name="score_status_enum"), nullable=True)
    score = Column(Numeric(10, 2), nullable=True)
    text_score = Column(String(255), nullable=True)
    score_date = Column(Date, nullable=True)
    comment = Column(Text, nullable=True)
    score_scale_sourced_id = Column(String(255), nullable=True)
    learning_objective_set = Column(JSONB, nullable=True)
    in_progress = Column(Boolean, default=False)
    incomplete = Column(Boolean, default=False)
    late = Column(Boolean, default=False)
    missing = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # リレーション
    line_item = relationship("LineItem", back_populates="results")

    def to_dict(self):
        result = {
            "sourcedId": self.sourced_id,
            "status": self.status,
            "dateLastModified": self.date_last_modified.isoformat(),
            "lineItem": {
                "sourcedId": self.line_item_sourced_id,
                "type": "lineItem"
            },
            "student": {
                "sourcedId": self.student_sourced_id,
                "type": "user"
            },
            "scoreStatus": self.score_status
        }

        if self.score is not None:
            result["score"] = float(self.score)
        if self.text_score:
            result["textScore"] = self.text_score
        if self.score_date:
            result["scoreDate"] = self.score_date.isoformat()
        if self.comment:
            result["comment"] = self.comment
        if self.in_progress:
            result["inProgress"] = self.in_progress
        if self.incomplete:
            result["incomplete"] = self.incomplete
        if self.late:
            result["late"] = self.late
        if self.missing:
            result["missing"] = self.missing

        return result
```

### 3.1.3 Java (Spring Data JPA) モデル

**model/Category.java**

```java
package com.example.gradebook.model;

import jakarta.persistence.*;
import jakarta.validation.constraints.*;
import lombok.Data;
import java.math.BigDecimal;
import java.time.ZonedDateTime;

@Entity
@Table(name = "categories")
@Data
public class Category {

    @Id
    @Column(name = "sourced_id", length = 255)
    private String sourcedId;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 50)
    private StatusEnum status = StatusEnum.active;

    @Column(name = "date_last_modified", nullable = false)
    private ZonedDateTime dateLastModified = ZonedDateTime.now();

    @NotBlank
    @Column(nullable = false, length = 255)
    private String title;

    @DecimalMin("0.0")
    @DecimalMax("1.0")
    @Column(precision = 5, scale = 4)
    private BigDecimal weight;

    @Column(name = "created_at", updatable = false)
    private ZonedDateTime createdAt = ZonedDateTime.now();

    @PreUpdate
    protected void onUpdate() {
        this.dateLastModified = ZonedDateTime.now();
    }

    public enum StatusEnum {
        active, tobedeleted
    }
}
```

**model/LineItem.java**

```java
package com.example.gradebook.model;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;
import org.hibernate.annotations.Type;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.ZonedDateTime;

@Entity
@Table(name = "line_items")
@Data
public class LineItem {

    @Id
    @Column(name = "sourced_id", length = 255)
    private String sourcedId;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 50)
    private StatusEnum status = StatusEnum.active;

    @Column(name = "date_last_modified", nullable = false)
    private ZonedDateTime dateLastModified = ZonedDateTime.now();

    @NotBlank
    @Column(nullable = false, length = 255)
    private String title;

    @Column(columnDefinition = "TEXT")
    private String description;

    @Column(name = "assign_date")
    private LocalDate assignDate;

    @Column(name = "due_date")
    private LocalDate dueDate;

    @NotBlank
    @Column(name = "class_sourced_id", nullable = false, length = 255)
    private String classSourcedId;

    @Column(name = "category_sourced_id", length = 255)
    private String categorySourcedId;

    @Column(name = "grading_period_sourced_id", length = 255)
    private String gradingPeriodSourcedId;

    @Column(name = "academic_session_sourced_id", length = 255)
    private String academicSessionSourcedId;

    @Column(name = "school_sourced_id", length = 255)
    private String schoolSourcedId;

    @Column(name = "score_scale_sourced_id", length = 255)
    private String scoreScaleSourcedId;

    @Column(name = "result_value_min", precision = 10, scale = 2)
    private BigDecimal resultValueMin;

    @Column(name = "result_value_max", precision = 10, scale = 2)
    private BigDecimal resultValueMax;

    @Type(type = "jsonb")
    @Column(name = "learning_objective_set", columnDefinition = "jsonb")
    private String learningObjectiveSet;

    @Column(name = "created_at", updatable = false)
    private ZonedDateTime createdAt = ZonedDateTime.now();

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "category_sourced_id", insertable = false, updatable = false)
    private Category category;

    @PreUpdate
    protected void onUpdate() {
        this.dateLastModified = ZonedDateTime.now();
    }

    public enum StatusEnum {
        active, tobedeleted
    }
}
```

**model/Result.java**

```java
package com.example.gradebook.model;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;
import org.hibernate.annotations.Type;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.ZonedDateTime;

@Entity
@Table(name = "results")
@Data
public class Result {

    @Id
    @Column(name = "sourced_id", length = 255)
    private String sourcedId;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 50)
    private StatusEnum status = StatusEnum.active;

    @Column(name = "date_last_modified", nullable = false)
    private ZonedDateTime dateLastModified = ZonedDateTime.now();

    @NotBlank
    @Column(name = "line_item_sourced_id", nullable = false, length = 255)
    private String lineItemSourcedId;

    @NotBlank
    @Column(name = "student_sourced_id", nullable = false, length = 255)
    private String studentSourcedId;

    @Column(name = "class_sourced_id", length = 255)
    private String classSourcedId;

    @Enumerated(EnumType.STRING)
    @Column(name = "score_status", nullable = true, length = 50)
    private ScoreStatusEnum scoreStatus;

    @Column(precision = 10, scale = 2)
    private BigDecimal score;

    @Column(name = "text_score", length = 255)
    private String textScore;

    @Column(name = "score_date")
    private LocalDate scoreDate;

    @Column(columnDefinition = "TEXT")
    private String comment;

    @Column(name = "score_scale_sourced_id", length = 255)
    private String scoreScaleSourcedId;

    @Type(type = "jsonb")
    @Column(name = "learning_objective_set", columnDefinition = "jsonb")
    private String learningObjectiveSet;

    @Column(name = "in_progress")
    private Boolean inProgress = false;

    @Column
    private Boolean incomplete = false;

    @Column
    private Boolean late = false;

    @Column
    private Boolean missing = false;

    @Column(name = "created_at", updatable = false)
    private ZonedDateTime createdAt = ZonedDateTime.now();

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "line_item_sourced_id", insertable = false, updatable = false)
    private LineItem lineItem;

    @PreUpdate
    protected void onUpdate() {
        this.dateLastModified = ZonedDateTime.now();
    }

    public enum StatusEnum {
        active, tobedeleted
    }

    public enum ScoreStatusEnum {
        earnedPartial, earnedFull, notEarned, notSubmitted, submitted,
        late, incomplete, missing, inProgress, withdrawn
    }
}
```

## 3.2 Rostering Serviceとの連携

Gradebook ServiceはRostering Serviceの以下のエンティティをsourcedIdで参照します。

### 必要なRosteringエンティティ

| エンティティ | 使用箇所 | 説明 |
|------------|---------|------|
| **Class** | LineItem, Result | 課題・成績が属するクラス |
| **User** | Result | 成績の対象となる学生 |
| **AcademicSession** | LineItem | 学期・成績期間 |
| **Organization** | LineItem | 学校レベルのLineItem |

### Rostering API呼び出し例

参照整合性を保つため、Gradebook ServiceはRostering APIを呼び出してエンティティの存在確認を行います。

**Node.js例：Class存在確認**

```javascript
const axios = require('axios');

async function validateClassExists(classSourcedId, accessToken) {
  try {
    const response = await axios.get(
      `${process.env.ROSTERING_BASE_URL}/classes/${classSourcedId}`,
      {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Accept': 'application/json'
        }
      }
    );
    return response.status === 200;
  } catch (error) {
    if (error.response && error.response.status === 404) {
      return false;
    }
    throw error;
  }
}
```

**Python例：User存在確認**

```python
import httpx
from app.core.config import settings

async def validate_user_exists(user_sourced_id: str, access_token: str) -> bool:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{settings.ROSTERING_BASE_URL}/users/{user_sourced_id}",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json"
                }
            )
            return response.status_code == 200
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return False
            raise
```

**Java例：AcademicSession存在確認**

```java
@Service
public class RosteringService {

    @Value("${rostering.base-url}")
    private String rosteringBaseUrl;

    @Autowired
    private RestTemplate restTemplate;

    public boolean validateAcademicSessionExists(String sessionSourcedId, String accessToken) {
        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setBearerAuth(accessToken);
            headers.setAccept(Collections.singletonList(MediaType.APPLICATION_JSON));

            HttpEntity<String> entity = new HttpEntity<>(headers);

            ResponseEntity<String> response = restTemplate.exchange(
                rosteringBaseUrl + "/academicSessions/" + sessionSourcedId,
                HttpMethod.GET,
                entity,
                String.class
            );

            return response.getStatusCode() == HttpStatus.OK;
        } catch (HttpClientErrorException.NotFound e) {
            return false;
        }
    }
}
```

---

# 第4章 OAuth 2.0認証・認可の実装

## 4.1 OneRosterのOAuth 2.0要件

OneRoster 1.2では、**OAuth 2.0 Client Credentials Grant**が唯一の認証方式です。

### 必要な情報

1. **Client ID**: アプリケーションの公開識別子
2. **Client Secret**: 共有秘密鍵
3. **Token Endpoint URL**: トークン取得用URL
4. **Scopes**: 要求するエンドポイント権限

### OneRoster Gradebookスコープ

| スコープ | URL | 権限 |
|---------|-----|------|
| **gradebook.readonly** | `https://purl.imsglobal.org/spec/or/v1p1/scope/gradebook.readonly` | GET操作（読み取り専用） |
| **gradebook.createput** | `https://purl.imsglobal.org/spec/or/v1p1/scope/gradebook.createput` | PUT操作（作成/更新） |
| **gradebook.delete** | `https://purl.imsglobal.org/spec/or/v1p1/scope/gradebook.delete` | DELETE操作（削除） |

## 4.2 Provider実装（認証サーバー側）

### 4.2.1 Node.js (oauth2-server)

**config/oauth.js**

```javascript
const OAuth2Server = require('oauth2-server');
const Request = OAuth2Server.Request;
const Response = OAuth2Server.Response;

// モデル実装
const model = {
  // クライアント認証情報の取得
  getClient: async (clientId, clientSecret) => {
    const clients = [
      {
        id: process.env.OAUTH_CLIENT_ID,
        clientSecret: process.env.OAUTH_CLIENT_SECRET,
        grants: ['client_credentials'],
        redirectUris: []
      }
    ];

    const client = clients.find(c => c.id === clientId);
    if (!client || client.clientSecret !== clientSecret) {
      return null;
    }
    return client;
  },

  // アクセストークンの保存
  saveToken: async (token, client, user) => {
    token.client = client;
    token.user = user;
    // データベースに保存（実装例）
    await db.tokens.create({
      accessToken: token.accessToken,
      accessTokenExpiresAt: token.accessTokenExpiresAt,
      clientId: client.id,
      scope: token.scope
    });
    return token;
  },

  // アクセストークンの取得
  getAccessToken: async (accessToken) => {
    const token = await db.tokens.findOne({
      where: { accessToken }
    });

    if (!token) return null;

    return {
      accessToken: token.accessToken,
      accessTokenExpiresAt: token.accessTokenExpiresAt,
      scope: token.scope,
      client: { id: token.clientId },
      user: {}
    };
  },

  // Client Credentials Grantの実装
  getUserFromClient: async (client) => {
    return {}; // Client Credentialsではユーザー不要
  },

  // スコープ検証
  verifyScope: async (token, scope) => {
    if (!token.scope) return false;
    const requestedScopes = scope.split(' ');
    const tokenScopes = token.scope.split(' ');
    return requestedScopes.every(s => tokenScopes.includes(s));
  }
};

const oauth = new OAuth2Server({
  model: model,
  accessTokenLifetime: 3600, // 1時間
  allowBearerTokensInQueryString: false
});

module.exports = oauth;
```

**middleware/auth.js**

```javascript
const oauth = require('../config/oauth');

// OAuth 2.0認証ミドルウェア
exports.authenticate = (requiredScope) => {
  return async (req, res, next) => {
    const request = new oauth.Request(req);
    const response = new oauth.Response(res);

    try {
      const token = await oauth.authenticate(request, response);

      // スコープチェック
      if (requiredScope) {
        const hasScope = await oauth.model.verifyScope(token, requiredScope);
        if (!hasScope) {
          return res.status(403).json({
            statusInfoSet: [{
              imsx_codeMajor: 'failure',
              imsx_severity: 'error',
              imsx_description: '権限が不足しています',
              imsx_codeMinor: 'forbidden'
            }]
          });
        }
      }

      req.oauth = { token };
      next();
    } catch (err) {
      return res.status(err.code || 401).json({
        statusInfoSet: [{
          imsx_codeMajor: 'failure',
          imsx_severity: 'error',
          imsx_description: err.message,
          imsx_codeMinor: 'unauthorized'
        }]
      });
    }
  };
};

// トークン発行エンドポイント
exports.token = async (req, res) => {
  const request = new oauth.Request(req);
  const response = new oauth.Response(res);

  try {
    const token = await oauth.token(request, response);
    res.json(token);
  } catch (err) {
    res.status(err.code || 500).json(err);
  }
};
```

### 4.2.2 Python (Authlib)

**core/security.py**

```python
from authlib.integrations.starlette_client import OAuth
from authlib.oauth2.rfc6749 import grants
from authlib.oauth2 import ResourceProtector, HttpRequest
from authlib.oauth2.rfc6750 import BearerTokenValidator
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import time

security = HTTPBearer()

# トークンストア（実際はデータベースを使用）
token_store = {}

class ClientCredentialsGrant(grants.ClientCredentialsGrant):
    TOKEN_ENDPOINT_AUTH_METHODS = ['client_secret_basic', 'client_secret_post']

    def save_token(self, token):
        # トークンをデータベースに保存
        token_store[token['access_token']] = {
            'access_token': token['access_token'],
            'token_type': 'Bearer',
            'expires_in': token['expires_in'],
            'scope': token['scope'],
            'created_at': time.time()
        }

class OneRosterBearerTokenValidator(BearerTokenValidator):
    def authenticate_token(self, token_string):
        token = token_store.get(token_string)
        if not token:
            return None

        # トークン有効期限チェック
        if time.time() > token['created_at'] + token['expires_in']:
            return None

        return token

    def request_invalid(self, request):
        return False

    def token_revoked(self, token):
        return False

# スコープ検証関数
def verify_scope(token: dict, required_scope: str) -> bool:
    if 'scope' not in token:
        return False
    token_scopes = token['scope'].split(' ')
    required_scopes = required_scope.split(' ')
    return all(scope in token_scopes for scope in required_scopes)

# 認証デコレータ
async def get_current_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
    required_scope: Optional[str] = None
):
    token_string = credentials.credentials
    validator = OneRosterBearerTokenValidator()
    token = validator.authenticate_token(token_string)

    if not token:
        raise HTTPException(
            status_code=401,
            detail={
                "statusInfoSet": [{
                    "imsx_codeMajor": "failure",
                    "imsx_severity": "error",
                    "imsx_description": "無効なアクセストークンです",
                    "imsx_codeMinor": "unauthorized"
                }]
            }
        )

    # スコープチェック
    if required_scope and not verify_scope(token, required_scope):
        raise HTTPException(
            status_code=403,
            detail={
                "statusInfoSet": [{
                    "imsx_codeMajor": "failure",
                    "imsx_severity": "error",
                    "imsx_description": "権限が不足しています",
                    "imsx_codeMinor": "forbidden"
                }]
            }
        )

    return token
```

**トークン発行エンドポイント**

```python
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from app.core.security import ClientCredentialsGrant
import secrets
import time

router = APIRouter()
security_basic = HTTPBasic()

@router.post("/oauth/token")
async def token(credentials: HTTPBasicCredentials = Depends(security_basic)):
    # クライアント認証
    correct_client_id = secrets.compare_digest(
        credentials.username,
        settings.OAUTH_CLIENT_ID
    )
    correct_client_secret = secrets.compare_digest(
        credentials.password,
        settings.OAUTH_CLIENT_SECRET
    )

    if not (correct_client_id and correct_client_secret):
        raise HTTPException(
            status_code=401,
            detail="Invalid client credentials"
        )

    # トークン生成
    access_token = secrets.token_urlsafe(32)
    expires_in = 3600
    scope = "https://purl.imsglobal.org/spec/or/v1p1/scope/gradebook.readonly"

    grant = ClientCredentialsGrant()
    grant.save_token({
        'access_token': access_token,
        'token_type': 'Bearer',
        'expires_in': expires_in,
        'scope': scope
    })

    return {
        "access_token": access_token,
        "token_type": "Bearer",
        "expires_in": expires_in,
        "scope": scope
    }
```

### 4.2.3 Java (Spring Security OAuth2)

**config/SecurityConfig.java**

```java
package com.example.gradebook.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationConverter;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(authorize -> authorize
                .requestMatchers("/oauth/token").permitAll()
                .requestMatchers("/categories/**").hasAuthority("SCOPE_gradebook.readonly")
                .requestMatchers("/lineItems/**").hasAuthority("SCOPE_gradebook.readonly")
                .requestMatchers("/results/**").hasAuthority("SCOPE_gradebook.readonly")
                .anyRequest().authenticated()
            )
            .oauth2ResourceServer(oauth2 -> oauth2
                .jwt(jwt -> jwt
                    .jwtAuthenticationConverter(jwtAuthenticationConverter())
                )
            )
            .csrf().disable();

        return http.build();
    }

    @Bean
    public JwtAuthenticationConverter jwtAuthenticationConverter() {
        JwtAuthenticationConverter converter = new JwtAuthenticationConverter();
        // スコープをGrantedAuthorityに変換
        converter.setJwtGrantedAuthoritiesConverter(new OneRosterScopeConverter());
        return converter;
    }
}
```

**config/OAuth2Config.java**

```java
package com.example.gradebook.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.oauth2.server.authorization.config.annotation.web.configuration.OAuth2AuthorizationServerConfiguration;
import org.springframework.security.oauth2.server.authorization.settings.AuthorizationServerSettings;

@Configuration
public class OAuth2Config {

    @Value("${oauth2.issuer-uri}")
    private String issuerUri;

    @Bean
    public AuthorizationServerSettings authorizationServerSettings() {
        return AuthorizationServerSettings.builder()
            .issuer(issuerUri)
            .tokenEndpoint("/oauth/token")
            .build();
    }
}
```

**OneRosterScopeConverter.java**

```java
package com.example.gradebook.config;

import org.springframework.core.convert.converter.Converter;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.oauth2.jwt.Jwt;

import java.util.Collection;
import java.util.Collections;
import java.util.stream.Collectors;

public class OneRosterScopeConverter implements Converter<Jwt, Collection<GrantedAuthority>> {

    @Override
    public Collection<GrantedAuthority> convert(Jwt jwt) {
        String scope = jwt.getClaimAsString("scope");
        if (scope == null) {
            return Collections.emptyList();
        }

        return Collections.singletonList(new SimpleGrantedAuthority("SCOPE_" + scope));
    }
}
```

## 4.3 Consumer実装（APIクライアント側）

### 4.3.1 Node.js トークン取得

**services/oauthClient.js**

```javascript
const axios = require('axios');

class OAuthClient {
  constructor() {
    this.clientId = process.env.OAUTH_CLIENT_ID;
    this.clientSecret = process.env.OAUTH_CLIENT_SECRET;
    this.tokenUrl = process.env.OAUTH_TOKEN_URL;
    this.token = null;
    this.tokenExpiry = null;
  }

  // アクセストークン取得
  async getAccessToken(scope) {
    // キャッシュされたトークンが有効かチェック
    if (this.token && this.tokenExpiry && Date.now() < this.tokenExpiry) {
      return this.token;
    }

    try {
      // Basic認証用のエンコード
      const credentials = Buffer.from(
        `${this.clientId}:${this.clientSecret}`
      ).toString('base64');

      const response = await axios.post(
        this.tokenUrl,
        'grant_type=client_credentials&scope=' + encodeURIComponent(scope),
        {
          headers: {
            'Authorization': `Basic ${credentials}`,
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        }
      );

      this.token = response.data.access_token;
      // 60秒前に期限切れとみなす（クロックスキュー対策）
      this.tokenExpiry = Date.now() + (response.data.expires_in - 60) * 1000;

      return this.token;
    } catch (error) {
      console.error('Token acquisition failed:', error.response?.data || error.message);
      throw new Error('Failed to obtain access token');
    }
  }

  // Provider APIリクエスト
  async request(method, endpoint, data = null, scope = null) {
    const token = await this.getAccessToken(
      scope || 'https://purl.imsglobal.org/spec/or/v1p1/scope/gradebook.readonly'
    );

    const config = {
      method,
      url: `${process.env.PROVIDER_BASE_URL}${endpoint}`,
      headers: {
        'Authorization': `Bearer ${token}`,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }
    };

    if (data) {
      config.data = data;
    }

    try {
      const response = await axios(config);
      return response.data;
    } catch (error) {
      // 401エラー時はトークンをクリアして再試行
      if (error.response?.status === 401) {
        this.token = null;
        this.tokenExpiry = null;
        return this.request(method, endpoint, data, scope);
      }
      throw error;
    }
  }
}

module.exports = new OAuthClient();
```

### 4.3.2 Python トークン取得

**services/oauth_client.py**

```python
import httpx
import time
from typing import Optional
from app.core.config import settings

class OAuthClient:
    def __init__(self):
        self.client_id = settings.OAUTH_CLIENT_ID
        self.client_secret = settings.OAUTH_CLIENT_SECRET
        self.token_url = settings.OAUTH_TOKEN_URL
        self.token = None
        self.token_expiry = None

    async def get_access_token(self, scope: str) -> str:
        """アクセストークン取得"""
        # キャッシュされたトークンが有効かチェック
        if self.token and self.token_expiry and time.time() < self.token_expiry:
            return self.token

        async with httpx.AsyncClient() as client:
            try:
                # Basic認証
                auth = (self.client_id, self.client_secret)

                response = await client.post(
                    self.token_url,
                    data={
                        'grant_type': 'client_credentials',
                        'scope': scope
                    },
                    auth=auth,
                    headers={'Content-Type': 'application/x-www-form-urlencoded'}
                )
                response.raise_for_status()

                token_data = response.json()
                self.token = token_data['access_token']
                # 60秒前に期限切れとみなす
                self.token_expiry = time.time() + token_data['expires_in'] - 60

                return self.token
            except httpx.HTTPError as e:
                raise Exception(f"Failed to obtain access token: {str(e)}")

    async def request(
        self,
        method: str,
        endpoint: str,
        data: Optional[dict] = None,
        scope: str = "https://purl.imsglobal.org/spec/or/v1p1/scope/gradebook.readonly"
    ) -> dict:
        """Provider APIリクエスト"""
        token = await self.get_access_token(scope)

        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method=method,
                    url=f"{settings.PROVIDER_BASE_URL}{endpoint}",
                    headers={
                        'Authorization': f'Bearer {token}',
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'
                    },
                    json=data if data else None
                )

                # 401エラー時はトークンをクリアして再試行
                if response.status_code == 401:
                    self.token = None
                    self.token_expiry = None
                    return await self.request(method, endpoint, data, scope)

                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                raise Exception(f"API request failed: {str(e)}")

oauth_client = OAuthClient()
```

### 4.3.3 Java トークン取得

**service/OAuth2ClientService.java**

```java
package com.example.gradebook.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.RestTemplate;

import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.Base64;

@Service
public class OAuth2ClientService {

    @Value("${oauth2.client.client-id}")
    private String clientId;

    @Value("${oauth2.client.client-secret}")
    private String clientSecret;

    @Value("${oauth2.client.token-uri}")
    private String tokenUri;

    @Value("${provider.base-url}")
    private String providerBaseUrl;

    private final RestTemplate restTemplate = new RestTemplate();
    private String accessToken;
    private Instant tokenExpiry;

    /**
     * アクセストークン取得
     */
    public String getAccessToken(String scope) {
        // キャッシュされたトークンが有効かチェック
        if (accessToken != null && tokenExpiry != null && Instant.now().isBefore(tokenExpiry)) {
            return accessToken;
        }

        // Basic認証ヘッダー
        String credentials = clientId + ":" + clientSecret;
        String encodedCredentials = Base64.getEncoder()
            .encodeToString(credentials.getBytes(StandardCharsets.UTF_8));

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_FORM_URLENCODED);
        headers.set("Authorization", "Basic " + encodedCredentials);

        // リクエストボディ
        MultiValueMap<String, String> body = new LinkedMultiValueMap<>();
        body.add("grant_type", "client_credentials");
        body.add("scope", scope);

        HttpEntity<MultiValueMap<String, String>> request = new HttpEntity<>(body, headers);

        try {
            ResponseEntity<TokenResponse> response = restTemplate.postForEntity(
                tokenUri,
                request,
                TokenResponse.class
            );

            TokenResponse tokenResponse = response.getBody();
            if (tokenResponse != null) {
                this.accessToken = tokenResponse.getAccessToken();
                // 60秒前に期限切れとみなす
                this.tokenExpiry = Instant.now().plusSeconds(tokenResponse.getExpiresIn() - 60);
                return this.accessToken;
            }
        } catch (Exception e) {
            throw new RuntimeException("Failed to obtain access token", e);
        }

        throw new RuntimeException("Token response was null");
    }

    /**
     * Provider APIリクエスト
     */
    public <T> T request(String method, String endpoint, Object data, Class<T> responseType, String scope) {
        String token = getAccessToken(scope != null ? scope :
            "https://purl.imsglobal.org/spec/or/v1p1/scope/gradebook.readonly");

        HttpHeaders headers = new HttpHeaders();
        headers.setBearerAuth(token);
        headers.setAccept(java.util.Collections.singletonList(MediaType.APPLICATION_JSON));
        headers.setContentType(MediaType.APPLICATION_JSON);

        HttpEntity<Object> request = new HttpEntity<>(data, headers);

        try {
            ResponseEntity<T> response = restTemplate.exchange(
                providerBaseUrl + endpoint,
                HttpMethod.valueOf(method.toUpperCase()),
                request,
                responseType
            );
            return response.getBody();
        } catch (HttpClientErrorException.Unauthorized e) {
            // 401エラー時はトークンをクリアして再試行
            this.accessToken = null;
            this.tokenExpiry = null;
            return request(method, endpoint, data, responseType, scope);
        }
    }

    // トークンレスポンスDTO
    private static class TokenResponse {
        private String access_token;
        private String token_type;
        private int expires_in;
        private String scope;

        // Getters and Setters
        public String getAccessToken() { return access_token; }
        public void setAccess_token(String access_token) { this.access_token = access_token; }
        public String getTokenType() { return token_type; }
        public void setToken_type(String token_type) { this.token_type = token_type; }
        public int getExpiresIn() { return expires_in; }
        public void setExpires_in(int expires_in) { this.expires_in = expires_in; }
        public String getScope() { return scope; }
        public void setScope(String scope) { this.scope = scope; }
    }
}
```

---

# 第5章 Provider実装（API提供側）

## 5.1 ページネーション、フィルタリング、ソートの実装

OneRoster APIでは、すべてのコレクションエンドポイントで以下の機能が必須です。

- **ページネーション**: `limit`、`offset`
- **フィルタリング**: `filter`パラメータ
- **ソート**: `sort`、`orderBy`
- **フィールド選択**: `fields`

### 5.1.1 Node.js ミドルウェア実装

**middleware/pagination.js**

```javascript
exports.pagination = (req, res, next) => {
  const limit = parseInt(req.query.limit) || 100;
  const offset = parseInt(req.query.offset) || 0;

  // limit上限チェック
  if (limit > 1000) {
    return res.status(400).json({
      statusInfoSet: [{
        imsx_codeMajor: 'failure',
        imsx_severity: 'error',
        imsx_description: 'Limit exceeds maximum value of 1000',
        imsx_codeMinor: 'invalid_data'
      }]
    });
  }

  req.pagination = { limit, offset };
  next();
};

exports.filtering = (req, res, next) => {
  const filter = req.query.filter;
  if (!filter) {
    req.filter = null;
    return next();
  }

  try {
    req.filter = parseFilter(filter);
    next();
  } catch (error) {
    return res.status(400).json({
      statusInfoSet: [{
        imsx_codeMajor: 'failure',
        imsx_severity: 'error',
        imsx_description: `Invalid filter syntax: ${error.message}`,
        imsx_codeMinor: 'invalid_data'
      }]
    });
  }
};

exports.sorting = (req, res, next) => {
  const sort = req.query.sort;
  const orderBy = req.query.orderBy || 'asc';

  if (sort) {
    req.sort = { field: sort, order: orderBy.toLowerCase() };
  } else {
    req.sort = null;
  }
  next();
};

// フィルター構文パーサー
function parseFilter(filterString) {
  const operators = {
    '=': 'eq',
    '!=': 'ne',
    '>': 'gt',
    '>=': 'gte',
    '<': 'lt',
    '<=': 'lte',
    '~': 'like'
  };

  // 単純な実装例
  const regex = /([a-zA-Z_]+)\s*(=|!=|>=|<=|>|<|~)\s*'([^']+)'/g;
  const conditions = [];
  let match;

  while ((match = regex.exec(filterString)) !== null) {
    const [, field, operator, value] = match;
    conditions.push({
      field,
      operator: operators[operator],
      value
    });
  }

  return conditions;
}
```

**middleware/fieldSelection.js**

```javascript
exports.fieldSelection = (req, res, next) => {
  const fields = req.query.fields;

  if (fields) {
    req.selectedFields = fields.split(',').map(f => f.trim());
  } else {
    req.selectedFields = null;
  }
  next();
};

// レスポンスフィルタリング関数
exports.filterFields = (obj, selectedFields) => {
  if (!selectedFields || selectedFields.length === 0) {
    return obj;
  }

  const filtered = {};
  selectedFields.forEach(field => {
    if (obj.hasOwnProperty(field)) {
      filtered[field] = obj[field];
    }
  });

  // sourcedIdは常に含める
  if (obj.sourcedId) {
    filtered.sourcedId = obj.sourcedId;
  }

  return filtered;
};
```

### 5.1.2 Python依存関係とユーティリティ

**api/v1p2/dependencies.py**

```python
from fastapi import Query, HTTPException
from typing import Optional, List
from sqlalchemy import and_, or_

class PaginationParams:
    def __init__(
        self,
        limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
        offset: int = Query(0, ge=0, description="Starting position")
    ):
        self.limit = limit
        self.offset = offset

class FilterParams:
    def __init__(
        self,
        filter: Optional[str] = Query(None, description="Filter expression")
    ):
        self.filter_expr = filter
        self.conditions = self.parse_filter() if filter else []

    def parse_filter(self) -> List[dict]:
        """フィルター構文をパース"""
        import re

        operators = {
            '=': 'eq',
            '!=': 'ne',
            '>': 'gt',
            '>=': 'gte',
            '<': 'lt',
            '<=': 'lte',
            '~': 'like'
        }

        pattern = r"([a-zA-Z_]+)\s*(=|!=|>=|<=|>|<|~)\s*'([^']+)'"
        matches = re.findall(pattern, self.filter_expr)

        conditions = []
        for field, operator, value in matches:
            conditions.append({
                'field': field,
                'operator': operators.get(operator, 'eq'),
                'value': value
            })

        return conditions

    def apply_to_query(self, query, model):
        """SQLAlchemyクエリにフィルターを適用"""
        for condition in self.conditions:
            field = getattr(model, condition['field'], None)
            if field is None:
                continue

            operator = condition['operator']
            value = condition['value']

            if operator == 'eq':
                query = query.filter(field == value)
            elif operator == 'ne':
                query = query.filter(field != value)
            elif operator == 'gt':
                query = query.filter(field > value)
            elif operator == 'gte':
                query = query.filter(field >= value)
            elif operator == 'lt':
                query = query.filter(field < value)
            elif operator == 'lte':
                query = query.filter(field <= value)
            elif operator == 'like':
                query = query.filter(field.ilike(f'%{value}%'))

        return query

class SortParams:
    def __init__(
        self,
        sort: Optional[str] = Query(None, description="Field to sort by"),
        orderBy: Optional[str] = Query("asc", regex="^(asc|desc)$", description="Sort order")
    ):
        self.sort_field = sort
        self.sort_order = orderBy.lower()

class FieldSelectionParams:
    def __init__(
        self,
        fields: Optional[str] = Query(None, description="Comma-separated list of fields")
    ):
        self.selected_fields = fields.split(',') if fields else None

    def filter_dict(self, data: dict) -> dict:
        """辞書からフィールドを選択"""
        if not self.selected_fields:
            return data

        filtered = {}
        for field in self.selected_fields:
            field = field.strip()
            if field in data:
                filtered[field] = data[field]

        # sourcedIdは常に含める
        if 'sourcedId' in data:
            filtered['sourcedId'] = data['sourcedId']

        return filtered
```

### 5.1.3 Java ユーティリティクラス

**util/QueryUtils.java**

```java
package com.example.gradebook.util;

import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.data.jpa.domain.Specification;

import jakarta.persistence.criteria.Predicate;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class QueryUtils {

    /**
     * ページネーションパラメータ作成
     */
    public static Pageable createPageable(Integer limit, Integer offset, String sort, String orderBy) {
        int pageSize = (limit != null && limit > 0) ? Math.min(limit, 1000) : 100;
        int page = (offset != null && offset >= 0) ? offset / pageSize : 0;

        if (sort != null && !sort.isEmpty()) {
            Sort.Direction direction = "desc".equalsIgnoreCase(orderBy) ?
                Sort.Direction.DESC : Sort.Direction.ASC;
            return PageRequest.of(page, pageSize, Sort.by(direction, sort));
        }

        return PageRequest.of(page, pageSize);
    }

    /**
     * フィルター文字列をSpecificationに変換
     */
    public static <T> Specification<T> parseFilter(String filterString) {
        if (filterString == null || filterString.isEmpty()) {
            return null;
        }

        return (root, query, criteriaBuilder) -> {
            List<Predicate> predicates = new ArrayList<>();

            Pattern pattern = Pattern.compile("([a-zA-Z_]+)\\s*(=|!=|>=|<=|>|<|~)\\s*'([^']+)'");
            Matcher matcher = pattern.matcher(filterString);

            while (matcher.find()) {
                String field = matcher.group(1);
                String operator = matcher.group(2);
                String value = matcher.group(3);

                try {
                    switch (operator) {
                        case "=":
                            predicates.add(criteriaBuilder.equal(root.get(field), value));
                            break;
                        case "!=":
                            predicates.add(criteriaBuilder.notEqual(root.get(field), value));
                            break;
                        case ">":
                            predicates.add(criteriaBuilder.greaterThan(root.get(field), value));
                            break;
                        case ">=":
                            predicates.add(criteriaBuilder.greaterThanOrEqualTo(root.get(field), value));
                            break;
                        case "<":
                            predicates.add(criteriaBuilder.lessThan(root.get(field), value));
                            break;
                        case "<=":
                            predicates.add(criteriaBuilder.lessThanOrEqualTo(root.get(field), value));
                            break;
                        case "~":
                            predicates.add(criteriaBuilder.like(root.get(field), "%" + value + "%"));
                            break;
                    }
                } catch (IllegalArgumentException e) {
                    // フィールドが存在しない場合は無視
                }
            }

            return criteriaBuilder.and(predicates.toArray(new Predicate[0]));
        };
    }

    /**
     * フィールド選択を適用
     */
    public static <T> T filterFields(T object, String fieldsParam) {
        // 実装は複雑になるため、DTOマッピングライブラリ（MapStruct等）の使用を推奨
        return object;
    }
}
```

## 5.2 Categories API実装

### 5.2.1 Node.js (Express) Controller

**controllers/categoryController.js**

```javascript
const { Category } = require('../models');
const { Op } = require('sequelize');
const { filterFields } = require('../middleware/fieldSelection');

// GET /categories - 全カテゴリー取得
exports.getAllCategories = async (req, res) => {
  try {
    const { limit, offset } = req.pagination;
    const whereClause = {};

    // フィルター適用
    if (req.filter) {
      req.filter.forEach(condition => {
        if (condition.operator === 'like') {
          whereClause[condition.field] = { [Op.iLike]: `%${condition.value}%` };
        } else {
          whereClause[condition.field] = condition.value;
        }
      });
    }

    // クエリ実行
    const { count, rows } = await Category.findAndCountAll({
      where: whereClause,
      limit,
      offset,
      order: req.sort ? [[req.sort.field, req.sort.order.toUpperCase()]] : undefined
    });

    // フィールド選択
    let categories = rows.map(cat => cat.toJSON());
    if (req.selectedFields) {
      categories = categories.map(cat => filterFields(cat, req.selectedFields));
    }

    // レスポンス
    res.set('X-Total-Count', count.toString());
    if (offset + limit < count) {
      const nextOffset = offset + limit;
      res.set('Link', `</categories?limit=${limit}&offset=${nextOffset}>; rel="next"`);
    }

    res.json({ categories });
  } catch (error) {
    console.error('Error fetching categories:', error);
    res.status(500).json({
      statusInfoSet: [{
        imsx_codeMajor: 'failure',
        imsx_severity: 'error',
        imsx_description: 'Internal server error',
        imsx_codeMinor: 'server_error'
      }]
    });
  }
};

// GET /categories/{id} - 単一カテゴリー取得
exports.getCategory = async (req, res) => {
  try {
    const category = await Category.findByPk(req.params.id);

    if (!category) {
      return res.status(404).json({
        statusInfoSet: [{
          imsx_codeMajor: 'failure',
          imsx_severity: 'error',
          imsx_description: 'Category not found',
          imsx_codeMinor: 'unknown_object'
        }]
      });
    }

    let categoryData = category.toJSON();
    if (req.selectedFields) {
      categoryData = filterFields(categoryData, req.selectedFields);
    }

    res.json({ category: categoryData });
  } catch (error) {
    console.error('Error fetching category:', error);
    res.status(500).json({
      statusInfoSet: [{
        imsx_codeMajor: 'failure',
        imsx_severity: 'error',
        imsx_description: 'Internal server error',
        imsx_codeMinor: 'server_error'
      }]
    });
  }
};

// PUT /categories/{id} - カテゴリー作成/更新
exports.putCategory = async (req, res) => {
  try {
    const { id } = req.params;
    const categoryData = req.body.category;

    // バリデーション
    if (!categoryData.title) {
      return res.status(400).json({
        statusInfoSet: [{
          imsx_codeMajor: 'failure',
          imsx_severity: 'error',
          imsx_description: 'Title is required',
          imsx_codeMinor: 'invalid_data'
        }]
      });
    }

    // 既存チェック
    const existingCategory = await Category.findByPk(id);

    if (existingCategory) {
      // 更新
      await existingCategory.update({
        status: categoryData.status || existingCategory.status,
        title: categoryData.title,
        weight: categoryData.weight
      });

      res.json({ category: existingCategory.toJSON() });
    } else {
      // 新規作成
      const newCategory = await Category.create({
        sourcedId: id,
        status: categoryData.status || 'active',
        title: categoryData.title,
        weight: categoryData.weight
      });

      res.status(201).json({ category: newCategory.toJSON() });
    }
  } catch (error) {
    console.error('Error putting category:', error);
    res.status(500).json({
      statusInfoSet: [{
        imsx_codeMajor: 'failure',
        imsx_severity: 'error',
        imsx_description: 'Internal server error',
        imsx_codeMinor: 'server_error'
      }]
    });
  }
};

// DELETE /categories/{id} - カテゴリー削除（論理削除）
exports.deleteCategory = async (req, res) => {
  try {
    const category = await Category.findByPk(req.params.id);

    if (!category) {
      return res.status(404).json({
        statusInfoSet: [{
          imsx_codeMajor: 'failure',
          imsx_severity: 'error',
          imsx_description: 'Category not found',
          imsx_codeMinor: 'unknown_object'
        }]
      });
    }

    // 論理削除
    await category.update({ status: 'tobedeleted' });

    res.status(204).send();
  } catch (error) {
    console.error('Error deleting category:', error);
    res.status(500).json({
      statusInfoSet: [{
        imsx_codeMajor: 'failure',
        imsx_severity: 'error',
        imsx_description: 'Internal server error',
        imsx_codeMinor: 'server_error'
      }]
    });
  }
};

// GET /classes/{class_id}/categories - クラス別カテゴリー取得（v1.2）
exports.getCategoriesForClass = async (req, res) => {
  try {
    const { class_id } = req.params;
    const { limit, offset } = req.pagination;

    // Rostering APIでクラス存在確認（省略可能）

    // 実装はシステム固有のロジックに依存
    // 例：クラスに紐づくカテゴリーを取得

    res.json({ categories: [] });
  } catch (error) {
    console.error('Error fetching categories for class:', error);
    res.status(500).json({
      statusInfoSet: [{
        imsx_codeMajor: 'failure',
        imsx_severity: 'error',
        imsx_description: 'Internal server error',
        imsx_codeMinor: 'server_error'
      }]
    });
  }
};
```

### 5.2.2 Python (FastAPI) Endpoint

**api/v1p2/endpoints/categories.py**

```python
from fastapi import APIRouter, Depends, HTTPException, Response, Header
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.database import get_db
from app.core.security import get_current_token
from app.models.category import Category
from app.api.v1p2.dependencies import (
    PaginationParams, FilterParams, SortParams, FieldSelectionParams
)

router = APIRouter()

@router.get("/categories")
async def get_all_categories(
    response: Response,
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(),
    filter_params: FilterParams = Depends(),
    sort_params: SortParams = Depends(),
    field_params: FieldSelectionParams = Depends(),
    token: dict = Depends(lambda: get_current_token(
        required_scope="https://purl.imsglobal.org/spec/or/v1p1/scope/gradebook.readonly"
    ))
):
    """全カテゴリー取得"""
    # ベースクエリ
    query = db.query(Category)

    # フィルター適用
    if filter_params.conditions:
        query = filter_params.apply_to_query(query, Category)

    # ソート適用
    if sort_params.sort_field:
        sort_column = getattr(Category, sort_params.sort_field, None)
        if sort_column:
            if sort_params.sort_order == 'desc':
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())

    # 総数取得
    total_count = query.count()

    # ページネーション適用
    categories = query.offset(pagination.offset).limit(pagination.limit).all()

    # レスポンスヘッダー
    response.headers["X-Total-Count"] = str(total_count)
    if pagination.offset + pagination.limit < total_count:
        next_offset = pagination.offset + pagination.limit
        response.headers["Link"] = (
            f'</categories?limit={pagination.limit}&offset={next_offset}>; rel="next"'
        )

    # データ変換
    categories_data = [cat.to_dict() for cat in categories]
    if field_params.selected_fields:
        categories_data = [field_params.filter_dict(cat) for cat in categories_data]

    return {"categories": categories_data}

@router.get("/categories/{sourced_id}")
async def get_category(
    sourced_id: str,
    db: Session = Depends(get_db),
    field_params: FieldSelectionParams = Depends(),
    token: dict = Depends(lambda: get_current_token(
        required_scope="https://purl.imsglobal.org/spec/or/v1p1/scope/gradebook.readonly"
    ))
):
    """単一カテゴリー取得"""
    category = db.query(Category).filter(Category.sourced_id == sourced_id).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail={
                "statusInfoSet": [{
                    "imsx_codeMajor": "failure",
                    "imsx_severity": "error",
                    "imsx_description": "Category not found",
                    "imsx_codeMinor": "unknown_object"
                }]
            }
        )

    category_data = category.to_dict()
    if field_params.selected_fields:
        category_data = field_params.filter_dict(category_data)

    return {"category": category_data}

@router.put("/categories/{sourced_id}", status_code=200)
async def put_category(
    sourced_id: str,
    category_input: dict,
    db: Session = Depends(get_db),
    token: dict = Depends(lambda: get_current_token(
        required_scope="https://purl.imsglobal.org/spec/or/v1p1/scope/gradebook.createput"
    ))
):
    """カテゴリー作成/更新"""
    category_data = category_input.get("category", {})

    # バリデーション
    if not category_data.get("title"):
        raise HTTPException(
            status_code=400,
            detail={
                "statusInfoSet": [{
                    "imsx_codeMajor": "failure",
                    "imsx_severity": "error",
                    "imsx_description": "Title is required",
                    "imsx_codeMinor": "invalid_data"
                }]
            }
        )

    # 既存チェック
    existing_category = db.query(Category).filter(
        Category.sourced_id == sourced_id
    ).first()

    if existing_category:
        # 更新
        existing_category.title = category_data["title"]
        existing_category.weight = category_data.get("weight")
        if "status" in category_data:
            existing_category.status = category_data["status"]

        db.commit()
        db.refresh(existing_category)

        return {"category": existing_category.to_dict()}
    else:
        # 新規作成
        new_category = Category(
            sourced_id=sourced_id,
            status=category_data.get("status", "active"),
            title=category_data["title"],
            weight=category_data.get("weight")
        )

        db.add(new_category)
        db.commit()
        db.refresh(new_category)

        return Response(
            content={"category": new_category.to_dict()},
            status_code=201
        )

@router.delete("/categories/{sourced_id}", status_code=204)
async def delete_category(
    sourced_id: str,
    db: Session = Depends(get_db),
    token: dict = Depends(lambda: get_current_token(
        required_scope="https://purl.imsglobal.org/spec/or/v1p1/scope/gradebook.delete"
    ))
):
    """カテゴリー削除（論理削除）"""
    category = db.query(Category).filter(Category.sourced_id == sourced_id).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail={
                "statusInfoSet": [{
                    "imsx_codeMajor": "failure",
                    "imsx_severity": "error",
                    "imsx_description": "Category not found",
                    "imsx_codeMinor": "unknown_object"
                }]
            }
        )

    # 論理削除
    category.status = "tobedeleted"
    db.commit()

    return Response(status_code=204)
```

### 5.2.3 Java (Spring Boot) Controller

**controller/CategoryController.java**

```java
package com.example.gradebook.controller;

import com.example.gradebook.model.Category;
import com.example.gradebook.repository.CategoryRepository;
import com.example.gradebook.util.QueryUtils;
import com.example.gradebook.dto.OneRosterResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.domain.Specification;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Optional;

@RestController
@RequestMapping("/categories")
public class CategoryController {

    @Autowired
    private CategoryRepository categoryRepository;

    @GetMapping
    public ResponseEntity<OneRosterResponse<Category>> getAllCategories(
            @RequestParam(required = false) Integer limit,
            @RequestParam(required = false) Integer offset,
            @RequestParam(required = false) String filter,
            @RequestParam(required = false) String sort,
            @RequestParam(required = false) String orderBy,
            @RequestParam(required = false) String fields
    ) {
        // ページネーション
        Pageable pageable = QueryUtils.createPageable(limit, offset, sort, orderBy);

        // フィルター適用
        Specification<Category> spec = QueryUtils.parseFilter(filter);

        // クエリ実行
        Page<Category> page = categoryRepository.findAll(spec, pageable);

        // レスポンスヘッダー
        HttpHeaders headers = new HttpHeaders();
        headers.add("X-Total-Count", String.valueOf(page.getTotalElements()));

        if (page.hasNext()) {
            int nextOffset = offset != null ? offset + limit : limit;
            headers.add("Link",
                String.format("</categories?limit=%d&offset=%d>; rel=\"next\"", limit, nextOffset));
        }

        return ResponseEntity.ok()
            .headers(headers)
            .body(new OneRosterResponse<>("categories", page.getContent()));
    }

    @GetMapping("/{id}")
    public ResponseEntity<?> getCategory(@PathVariable String id) {
        Optional<Category> category = categoryRepository.findById(id);

        if (category.isEmpty()) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND)
                .body(OneRosterResponse.error("Category not found", "unknown_object"));
        }

        return ResponseEntity.ok(new OneRosterResponse<>("category", category.get()));
    }

    @PutMapping("/{id}")
    public ResponseEntity<?> putCategory(
            @PathVariable String id,
            @RequestBody OneRosterResponse<Category> request
    ) {
        Category categoryData = request.getData();

        // バリデーション
        if (categoryData.getTitle() == null || categoryData.getTitle().isEmpty()) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                .body(OneRosterResponse.error("Title is required", "invalid_data"));
        }

        Optional<Category> existingCategory = categoryRepository.findById(id);

        if (existingCategory.isPresent()) {
            // 更新
            Category category = existingCategory.get();
            category.setTitle(categoryData.getTitle());
            category.setWeight(categoryData.getWeight());
            if (categoryData.getStatus() != null) {
                category.setStatus(categoryData.getStatus());
            }

            categoryRepository.save(category);
            return ResponseEntity.ok(new OneRosterResponse<>("category", category));
        } else {
            // 新規作成
            categoryData.setSourcedId(id);
            if (categoryData.getStatus() == null) {
                categoryData.setStatus(Category.StatusEnum.active);
            }

            Category savedCategory = categoryRepository.save(categoryData);
            return ResponseEntity.status(HttpStatus.CREATED)
                .body(new OneRosterResponse<>("category", savedCategory));
        }
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<?> deleteCategory(@PathVariable String id) {
        Optional<Category> category = categoryRepository.findById(id);

        if (category.isEmpty()) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND)
                .body(OneRosterResponse.error("Category not found", "unknown_object"));
        }

        // 論理削除
        Category cat = category.get();
        cat.setStatus(Category.StatusEnum.tobedeleted);
        categoryRepository.save(cat);

        return ResponseEntity.noContent().build();
    }
}
```

**dto/OneRosterResponse.java**

```java
package com.example.gradebook.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.Data;
import java.util.Collections;
import java.util.List;

@Data
@JsonInclude(JsonInclude.Include.NON_NULL)
public class OneRosterResponse<T> {
    private List<T> categories;
    private List<T> lineItems;
    private List<T> results;
    private T category;
    private T lineItem;
    private T result;
    private List<StatusInfo> statusInfoSet;

    public OneRosterResponse(String type, T data) {
        switch (type) {
            case "categories":
                this.categories = (List<T>) data;
                break;
            case "category":
                this.category = data;
                break;
            case "lineItems":
                this.lineItems = (List<T>) data;
                break;
            case "lineItem":
                this.lineItem = data;
                break;
            case "results":
                this.results = (List<T>) data;
                break;
            case "result":
                this.result = data;
                break;
        }
    }

    public static OneRosterResponse<?> error(String description, String codeMinor) {
        OneRosterResponse<?> response = new OneRosterResponse<>(null, null);
        response.statusInfoSet = Collections.singletonList(
            new StatusInfo("failure", "error", description, codeMinor)
        );
        return response;
    }

    @Data
    public static class StatusInfo {
        private String imsx_codeMajor;
        private String imsx_severity;
        private String imsx_description;
        private String imsx_codeMinor;

        public StatusInfo(String codeMajor, String severity, String description, String codeMinor) {
            this.imsx_codeMajor = codeMajor;
            this.imsx_severity = severity;
            this.imsx_description = description;
            this.imsx_codeMinor = codeMinor;
        }
    }
}
```

---

# 第6章 Consumer実装（API利用側）

## 6.1 Consumer実装の概要

Consumer実装では、他システムが提供するOneRoster Gradebook APIを呼び出してデータを取得・操作します。

### 主要ユースケース

| システム | Consumerとしての役割 | 取得データ |
|---------|-------------------|---------|
| **LMS** | SISからカテゴリー取得 | Categories |
| **SIS** | LMSから成績受信 | LineItems, Results |
| **分析システム** | 成績データ統合 | 全データ |

## 6.2 Consumer実装パターン

### 6.2.1 Node.js Consumer例

**services/gradebookConsumer.js**

```javascript
const oauthClient = require('./oauthClient');

class GradebookConsumer {
  constructor(baseUrl) {
    this.baseUrl = baseUrl;
  }

  // Categories取得
  async getCategories(limit = 100, offset = 0, filter = null) {
    let endpoint = `/categories?limit=${limit}&offset=${offset}`;
    if (filter) {
      endpoint += `&filter=${encodeURIComponent(filter)}`;
    }

    const data = await oauthClient.request(
      'GET',
      endpoint,
      null,
      'https://purl.imsglobal.org/spec/or/v1p1/scope/gradebook.readonly'
    );

    return data.categories;
  }

  // 単一Category取得
  async getCategory(sourcedId) {
    const data = await oauthClient.request(
      'GET',
      `/categories/${sourcedId}`,
      null,
      'https://purl.imsglobal.org/spec/or/v1p1/scope/gradebook.readonly'
    );

    return data.category;
  }

  // LineItems取得
  async getLineItems(limit = 100, offset = 0) {
    const data = await oauthClient.request(
      'GET',
      `/lineItems?limit=${limit}&offset=${offset}`,
      null,
      'https://purl.imsglobal.org/spec/or/v1p1/scope/gradebook.readonly'
    );

    return data.lineItems;
  }

  // クラス別LineItems取得
  async getLineItemsForClass(classSourcedId, limit = 100, offset = 0) {
    const data = await oauthClient.request(
      'GET',
      `/classes/${classSourcedId}/lineItems?limit=${limit}&offset=${offset}`,
      null,
      'https://purl.imsglobal.org/spec/or/v1p1/scope/gradebook.readonly'
    );

    return data.lineItems;
  }

  // Results取得
  async getResultsForClass(classSourcedId, limit = 100, offset = 0) {
    const data = await oauthClient.request(
      'GET',
      `/classes/${classSourcedId}/results?limit=${limit}&offset=${offset}`,
      null,
      'https://purl.imsglobal.org/spec/or/v1p1/scope/gradebook.readonly'
    );

    return data.results;
  }

  // 学生別Results取得
  async getResultsForStudent(classSourcedId, studentSourcedId, limit = 100) {
    const data = await oauthClient.request(
      'GET',
      `/classes/${classSourcedId}/students/${studentSourcedId}/results?limit=${limit}`,
      null,
      'https://purl.imsglobal.org/spec/or/v1p1/scope/gradebook.readonly'
    );

    return data.results;
  }

  // LineItem作成/更新
  async putLineItem(sourcedId, lineItemData) {
    const data = await oauthClient.request(
      'PUT',
      `/lineItems/${sourcedId}`,
      { lineItem: lineItemData },
      'https://purl.imsglobal.org/spec/or/v1p1/scope/gradebook.createput'
    );

    return data.lineItem;
  }

  // Result作成/更新
  async putResult(sourcedId, resultData) {
    const data = await oauthClient.request(
      'PUT',
      `/results/${sourcedId}`,
      { result: resultData },
      'https://purl.imsglobal.org/spec/or/v1p1/scope/gradebook.createput'
    );

    return data.result;
  }

  // ページネーション対応の全件取得
  async getAllCategories() {
    let allCategories = [];
    let offset = 0;
    const limit = 100;
    let hasMore = true;

    while (hasMore) {
      const categories = await this.getCategories(limit, offset);
      allCategories = allCategories.concat(categories);

      if (categories.length < limit) {
        hasMore = false;
      } else {
        offset += limit;
      }
    }

    return allCategories;
  }
}

module.exports = GradebookConsumer;
```

**使用例**

```javascript
const GradebookConsumer = require('./services/gradebookConsumer');

const consumer = new GradebookConsumer('https://sis.example.com/ims/oneroster/gradebook/v1p2');

// カテゴリー同期
async function syncCategories() {
  try {
    const categories = await consumer.getAllCategories();

    for (const category of categories) {
      if (category.status === 'active') {
        // ローカルデータベースに保存
        await db.categories.upsert({
          sourcedId: category.sourcedId,
          title: category.title,
          weight: category.weight
        });
      }
    }

    console.log(`Synced ${categories.length} categories`);
  } catch (error) {
    console.error('Category sync failed:', error);
  }
}
```

### 6.2.2 Python Consumer例

**services/gradebook_consumer.py**

```python
from typing import List, Optional, Dict
from app.services.oauth_client import oauth_client

class GradebookConsumer:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def get_categories(
        self,
        limit: int = 100,
        offset: int = 0,
        filter_expr: Optional[str] = None
    ) -> List[Dict]:
        """Categories取得"""
        endpoint = f"/categories?limit={limit}&offset={offset}"
        if filter_expr:
            endpoint += f"&filter={filter_expr}"

        data = await oauth_client.request(
            "GET",
            endpoint,
            scope="https://purl.imsglobal.org/spec/or/v1p1/scope/gradebook.readonly"
        )

        return data.get("categories", [])

    async def get_category(self, sourced_id: str) -> Dict:
        """単一Category取得"""
        data = await oauth_client.request(
            "GET",
            f"/categories/{sourced_id}",
            scope="https://purl.imsglobal.org/spec/or/v1p1/scope/gradebook.readonly"
        )

        return data.get("category", {})

    async def get_line_items_for_class(
        self,
        class_sourced_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict]:
        """クラス別LineItems取得"""
        endpoint = f"/classes/{class_sourced_id}/lineItems?limit={limit}&offset={offset}"

        data = await oauth_client.request(
            "GET",
            endpoint,
            scope="https://purl.imsglobal.org/spec/or/v1p1/scope/gradebook.readonly"
        )

        return data.get("lineItems", [])

    async def get_results_for_class(
        self,
        class_sourced_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict]:
        """クラス別Results取得"""
        endpoint = f"/classes/{class_sourced_id}/results?limit={limit}&offset={offset}"

        data = await oauth_client.request(
            "GET",
            endpoint,
            scope="https://purl.imsglobal.org/spec/or/v1p1/scope/gradebook.readonly"
        )

        return data.get("results", [])

    async def put_line_item(self, sourced_id: str, line_item_data: Dict) -> Dict:
        """LineItem作成/更新"""
        data = await oauth_client.request(
            "PUT",
            f"/lineItems/{sourced_id}",
            data={"lineItem": line_item_data},
            scope="https://purl.imsglobal.org/spec/or/v1p1/scope/gradebook.createput"
        )

        return data.get("lineItem", {})

    async def put_result(self, sourced_id: str, result_data: Dict) -> Dict:
        """Result作成/更新"""
        data = await oauth_client.request(
            "PUT",
            f"/results/{sourced_id}",
            data={"result": result_data},
            scope="https://purl.imsglobal.org/spec/or/v1p1/scope/gradebook.createput"
        )

        return data.get("result", {})

    async def get_all_categories(self) -> List[Dict]:
        """全Categories取得（ページネーション対応）"""
        all_categories = []
        offset = 0
        limit = 100
        has_more = True

        while has_more:
            categories = await self.get_categories(limit=limit, offset=offset)
            all_categories.extend(categories)

            if len(categories) < limit:
                has_more = False
            else:
                offset += limit

        return all_categories

# 使用例
async def sync_categories():
    consumer = GradebookConsumer("https://sis.example.com/ims/oneroster/gradebook/v1p2")

    try:
        categories = await consumer.get_all_categories()

        for category in categories:
            if category["status"] == "active":
                # ローカルデータベースに保存
                await db.categories.upsert({
                    "sourced_id": category["sourcedId"],
                    "title": category["title"],
                    "weight": category.get("weight")
                })

        print(f"Synced {len(categories)} categories")
    except Exception as e:
        print(f"Category sync failed: {e}")
```

### 6.2.3 Java Consumer例

**service/GradebookConsumer.java**

```java
package com.example.gradebook.service;

import com.example.gradebook.dto.CategoryDTO;
import com.example.gradebook.dto.LineItemDTO;
import com.example.gradebook.dto.ResultDTO;
import com.example.gradebook.dto.OneRosterCollectionResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

@Service
public class GradebookConsumer {

    @Autowired
    private OAuth2ClientService oauth2ClientService;

    private static final String READONLY_SCOPE =
        "https://purl.imsglobal.org/spec/or/v1p1/scope/gradebook.readonly";
    private static final String CREATEPUT_SCOPE =
        "https://purl.imsglobal.org/spec/or/v1p1/scope/gradebook.createput";

    /**
     * Categories取得
     */
    public List<CategoryDTO> getCategories(int limit, int offset, String filter) {
        String endpoint = String.format("/categories?limit=%d&offset=%d", limit, offset);
        if (filter != null && !filter.isEmpty()) {
            endpoint += "&filter=" + filter;
        }

        OneRosterCollectionResponse<CategoryDTO> response = oauth2ClientService.request(
            "GET",
            endpoint,
            null,
            new ParameterizedTypeReference<OneRosterCollectionResponse<CategoryDTO>>() {},
            READONLY_SCOPE
        );

        return response.getCategories();
    }

    /**
     * 単一Category取得
     */
    public CategoryDTO getCategory(String sourcedId) {
        OneRosterCollectionResponse<CategoryDTO> response = oauth2ClientService.request(
            "GET",
            "/categories/" + sourcedId,
            null,
            new ParameterizedTypeReference<OneRosterCollectionResponse<CategoryDTO>>() {},
            READONLY_SCOPE
        );

        return response.getCategory();
    }

    /**
     * クラス別LineItems取得
     */
    public List<LineItemDTO> getLineItemsForClass(String classSourcedId, int limit, int offset) {
        String endpoint = String.format(
            "/classes/%s/lineItems?limit=%d&offset=%d",
            classSourcedId, limit, offset
        );

        OneRosterCollectionResponse<LineItemDTO> response = oauth2ClientService.request(
            "GET",
            endpoint,
            null,
            new ParameterizedTypeReference<OneRosterCollectionResponse<LineItemDTO>>() {},
            READONLY_SCOPE
        );

        return response.getLineItems();
    }

    /**
     * クラス別Results取得
     */
    public List<ResultDTO> getResultsForClass(String classSourcedId, int limit, int offset) {
        String endpoint = String.format(
            "/classes/%s/results?limit=%d&offset=%d",
            classSourcedId, limit, offset
        );

        OneRosterCollectionResponse<ResultDTO> response = oauth2ClientService.request(
            "GET",
            endpoint,
            null,
            new ParameterizedTypeReference<OneRosterCollectionResponse<ResultDTO>>() {},
            READONLY_SCOPE
        );

        return response.getResults();
    }

    /**
     * LineItem作成/更新
     */
    public LineItemDTO putLineItem(String sourcedId, LineItemDTO lineItemData) {
        OneRosterCollectionResponse<LineItemDTO> request =
            new OneRosterCollectionResponse<>("lineItem", lineItemData);

        OneRosterCollectionResponse<LineItemDTO> response = oauth2ClientService.request(
            "PUT",
            "/lineItems/" + sourcedId,
            request,
            new ParameterizedTypeReference<OneRosterCollectionResponse<LineItemDTO>>() {},
            CREATEPUT_SCOPE
        );

        return response.getLineItem();
    }

    /**
     * Result作成/更新
     */
    public ResultDTO putResult(String sourcedId, ResultDTO resultData) {
        OneRosterCollectionResponse<ResultDTO> request =
            new OneRosterCollectionResponse<>("result", resultData);

        OneRosterCollectionResponse<ResultDTO> response = oauth2ClientService.request(
            "PUT",
            "/results/" + sourcedId,
            request,
            new ParameterizedTypeReference<OneRosterCollectionResponse<ResultDTO>>() {},
            CREATEPUT_SCOPE
        );

        return response.getResult();
    }

    /**
     * 全Categories取得（ページネーション対応）
     */
    public List<CategoryDTO> getAllCategories() {
        List<CategoryDTO> allCategories = new ArrayList<>();
        int offset = 0;
        int limit = 100;
        boolean hasMore = true;

        while (hasMore) {
            List<CategoryDTO> categories = getCategories(limit, offset, null);
            allCategories.addAll(categories);

            if (categories.size() < limit) {
                hasMore = false;
            } else {
                offset += limit;
            }
        }

        return allCategories;
    }
}
```

---

# 第7章 OneRoster v1.2新機能の実装

## 7.1 ScoreScales実装

ScoreScalesは、システム間で統一された採点基準を交換するためのv1.2新機能です。

### 7.1.1 ScoreScaleモデル実装

**Node.js (Sequelize)**

```javascript
// models/scoreScale.js
const { DataTypes } = require('sequelize');

module.exports = (sequelize) => {
  const ScoreScale = sequelize.define('ScoreScale', {
    sourcedId: {
      type: DataTypes.STRING(255),
      primaryKey: true,
      field: 'sourced_id'
    },
    status: {
      type: DataTypes.ENUM('active', 'tobedeleted'),
      allowNull: false,
      defaultValue: 'active'
    },
    dateLastModified: {
      type: DataTypes.DATE,
      allowNull: false,
      defaultValue: DataTypes.NOW,
      field: 'date_last_modified'
    },
    title: {
      type: DataTypes.STRING(255),
      allowNull: false
    },
    type: {
      type: DataTypes.STRING(100),
      allowNull: true
    },
    courseSourcedId: {
      type: DataTypes.STRING(255),
      allowNull: true,
      field: 'course_sourced_id'
    },
    classSourcedId: {
      type: DataTypes.STRING(255),
      allowNull: true,
      field: 'class_sourced_id'
    },
    scoreScaleValue: {
      type: DataTypes.JSONB,
      allowNull: false,
      field: 'score_scale_value'
    }
  }, {
    tableName: 'score_scales',
    timestamps: true,
    createdAt: 'created_at',
    updatedAt: false
  });

  return ScoreScale;
};
```

**Python (SQLAlchemy)**

```python
# models/score_scale.py
from sqlalchemy import Column, String, Enum, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from app.core.database import Base

class ScoreScale(Base):
    __tablename__ = "score_scales"

    sourced_id = Column(String(255), primary_key=True)
    status = Column(Enum("active", "tobedeleted", name="status_enum"),
                   nullable=False, default="active")
    date_last_modified = Column(DateTime(timezone=True), nullable=False,
                                server_default=func.now(), onupdate=func.now())
    title = Column(String(255), nullable=False)
    type = Column(String(100), nullable=True)
    course_sourced_id = Column(String(255), nullable=True)
    class_sourced_id = Column(String(255), nullable=True)
    score_scale_value = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def to_dict(self):
        result = {
            "sourcedId": self.sourced_id,
            "status": self.status,
            "dateLastModified": self.date_last_modified.isoformat(),
            "title": self.title
        }

        if self.type:
            result["type"] = self.type
        if self.class_sourced_id:
            result["class"] = {
                "sourcedId": self.class_sourced_id,
                "type": "class"
            }
        if self.score_scale_value:
            result["scoreScaleValue"] = self.score_scale_value

        return result
```

### 7.1.2 ScoreScale使用例

**レター評価スケール（A-F）**

```json
{
  "scoreScale": {
    "sourcedId": "scale-letter-grade",
    "status": "active",
    "dateLastModified": "2024-01-15T10:00:00.000Z",
    "title": "Standard Letter Grade Scale",
    "type": "letterGrade",
    "scoreScaleValue": [
      {"itemValueLHS": "A+", "itemValueRHS": "100"},
      {"itemValueLHS": "A", "itemValueRHS": "94"},
      {"itemValueLHS": "A-", "itemValueRHS": "90"},
      {"itemValueLHS": "B+", "itemValueRHS": "87"},
      {"itemValueLHS": "B", "itemValueRHS": "84"},
      {"itemValueLHS": "B-", "itemValueRHS": "80"},
      {"itemValueLHS": "C+", "itemValueRHS": "77"},
      {"itemValueLHS": "C", "itemValueRHS": "74"},
      {"itemValueLHS": "C-", "itemValueRHS": "70"},
      {"itemValueLHS": "D", "itemValueRHS": "65"},
      {"itemValueLHS": "F", "itemValueRHS": "0"}
    ]
  }
}
```

**ルーブリックスケール**

```json
{
  "scoreScale": {
    "sourcedId": "scale-rubric-essay",
    "status": "active",
    "title": "Essay Rubric Scale",
    "type": "rubric",
    "scoreScaleValue": [
      {"itemValueLHS": "Excellent", "itemValueRHS": "4"},
      {"itemValueLHS": "Proficient", "itemValueRHS": "3"},
      {"itemValueLHS": "Developing", "itemValueRHS": "2"},
      {"itemValueLHS": "Beginning", "itemValueRHS": "1"}
    ]
  }
}
```

### 7.1.3 ScoreScale変換ロジック

**Node.js例**

```javascript
class ScoreScaleConverter {
  constructor(scoreScale) {
    this.scoreScale = scoreScale;
    this.mappings = this.buildMappings();
  }

  buildMappings() {
    const mappings = {
      textToNumeric: {},
      numericToText: {}
    };

    if (this.scoreScale.scoreScaleValue) {
      this.scoreScale.scoreScaleValue.forEach(mapping => {
        mappings.textToNumeric[mapping.itemValueLHS] = parseFloat(mapping.itemValueRHS);
        mappings.numericToText[mapping.itemValueRHS] = mapping.itemValueLHS;
      });
    }

    return mappings;
  }

  textToNumeric(textScore) {
    return this.mappings.textToNumeric[textScore] || null;
  }

  numericToText(numericScore) {
    // 最も近い値を検索
    const numericValues = Object.keys(this.mappings.numericToText)
      .map(v => parseFloat(v))
      .sort((a, b) => b - a);

    for (const value of numericValues) {
      if (numericScore >= value) {
        return this.mappings.numericToText[value.toString()];
      }
    }

    return this.mappings.numericToText[numericValues[numericValues.length - 1].toString()];
  }
}

// 使用例
const letterGradeScale = await ScoreScale.findByPk('scale-letter-grade');
const converter = new ScoreScaleConverter(letterGradeScale);

const numericScore = converter.textToNumeric('B+'); // 87
const letterGrade = converter.numericToText(92);    // 'A'
```

## 7.2 一括操作（Bulk Operations）実装

v1.2では、POSTエンドポイントによる一括作成が可能です。

### 7.2.1 一括LineItems作成

**Node.js Controller**

```javascript
// POST /classes/{class_id}/lineItems
exports.postLineItemsForClass = async (req, res) => {
  try {
    const { class_id } = req.params;
    const lineItemsData = req.body.lineItems;

    if (!Array.isArray(lineItemsData)) {
      return res.status(400).json({
        statusInfoSet: [{
          imsx_codeMajor: 'failure',
          imsx_severity: 'error',
          imsx_description: 'lineItems must be an array',
          imsx_codeMinor: 'invalid_data'
        }]
      });
    }

    const sourcedIdPairs = [];

    for (const lineItemData of lineItemsData) {
      const suppliedSourcedId = lineItemData.sourcedId;

      // サーバー側でGUID生成
      const allocatedSourcedId = require('uuid').v4();

      // LineItem作成
      const lineItem = await LineItem.create({
        sourcedId: allocatedSourcedId,
        status: lineItemData.status || 'active',
        title: lineItemData.title,
        description: lineItemData.description,
        assignDate: lineItemData.assignDate,
        dueDate: lineItemData.dueDate,
        classSourcedId: class_id,
        categorySourcedId: lineItemData.category?.sourcedId,
        resultValueMin: lineItemData.resultValueMin,
        resultValueMax: lineItemData.resultValueMax
      });

      sourcedIdPairs.push({
        suppliedSourcedId,
        allocatedSourcedId
      });
    }

    res.status(201).json({ sourcedIdPairs });
  } catch (error) {
    console.error('Error creating bulk line items:', error);
    res.status(500).json({
      statusInfoSet: [{
        imsx_codeMajor: 'failure',
        imsx_severity: 'error',
        imsx_description: 'Internal server error',
        imsx_codeMinor: 'server_error'
      }]
    });
  }
};
```

**Python Endpoint**

```python
@router.post("/classes/{class_id}/lineItems", status_code=201)
async def post_line_items_for_class(
    class_id: str,
    line_items_input: dict,
    db: Session = Depends(get_db),
    token: dict = Depends(lambda: get_current_token(
        required_scope="https://purl.imsglobal.org/spec/or/v1p1/scope/gradebook.createput"
    ))
):
    """一括LineItems作成"""
    line_items_data = line_items_input.get("lineItems", [])

    if not isinstance(line_items_data, list):
        raise HTTPException(
            status_code=400,
            detail={
                "statusInfoSet": [{
                    "imsx_codeMajor": "failure",
                    "imsx_severity": "error",
                    "imsx_description": "lineItems must be an array",
                    "imsx_codeMinor": "invalid_data"
                }]
            }
        )

    sourced_id_pairs = []

    for line_item_data in line_items_data:
        supplied_sourced_id = line_item_data.get("sourcedId")

        # サーバー側でGUID生成
        import uuid
        allocated_sourced_id = str(uuid.uuid4())

        # LineItem作成
        new_line_item = LineItem(
            sourced_id=allocated_sourced_id,
            status=line_item_data.get("status", "active"),
            title=line_item_data["title"],
            description=line_item_data.get("description"),
            assign_date=line_item_data.get("assignDate"),
            due_date=line_item_data.get("dueDate"),
            class_sourced_id=class_id,
            category_sourced_id=line_item_data.get("category", {}).get("sourcedId"),
            result_value_min=line_item_data.get("resultValueMin"),
            result_value_max=line_item_data.get("resultValueMax")
        )

        db.add(new_line_item)

        sourced_id_pairs.append({
            "suppliedSourcedId": supplied_sourced_id,
            "allocatedSourcedId": allocated_sourced_id
        })

    db.commit()

    return {"sourcedIdPairs": sourced_id_pairs}
```

### 7.2.2 一括Results作成

**POST /lineItems/{li_id}/results**

```javascript
// Node.js
exports.postResultsForLineItem = async (req, res) => {
  try {
    const { li_id } = req.params;
    const resultsData = req.body.results;

    const sourcedIdPairs = [];

    for (const resultData of resultsData) {
      const suppliedSourcedId = resultData.sourcedId;
      const allocatedSourcedId = require('uuid').v4();

      const result = await Result.create({
        sourcedId: allocatedSourcedId,
        status: resultData.status || 'active',
        lineItemSourcedId: li_id,
        studentSourcedId: resultData.student.sourcedId,
        scoreStatus: resultData.scoreStatus,
        score: resultData.score,
        textScore: resultData.textScore,
        scoreDate: resultData.scoreDate,
        comment: resultData.comment,
        late: resultData.late,
        missing: resultData.missing
      });

      sourcedIdPairs.push({
        suppliedSourcedId,
        allocatedSourcedId
      });
    }

    res.status(201).json({ sourcedIdPairs });
  } catch (error) {
    console.error('Error creating bulk results:', error);
    res.status(500).json({
      statusInfoSet: [{
        imsx_codeMajor: 'failure',
        imsx_severity: 'error',
        imsx_description: 'Internal server error',
        imsx_codeMinor: 'server_error'
      }]
    });
  }
};
```

## 7.3 LearningObjectiveSet（標準準拠型評価）実装

CASE仕様との連携により、学習目標と成績を紐付けます。

### 7.3.1 データ構造

```json
{
  "lineItem": {
    "sourcedId": "li-math-quadratic",
    "title": "Quadratic Equations Assessment",
    "learningObjectiveSet": {
      "source": "CASE",
      "learningObjectiveIds": [
        "550e8400-e29b-41d4-a716-446655440000",
        "6fa459ea-ee8a-3ca4-894e-db77e160355e"
      ]
    }
  }
}
```

```json
{
  "result": {
    "sourcedId": "result-12345",
    "lineItem": {"sourcedId": "li-math-quadratic", "type": "lineItem"},
    "student": {"sourcedId": "student-456", "type": "user"},
    "scoreStatus": "earnedFull",
    "learningObjectiveSet": {
      "learningObjectiveScores": [
        {
          "learningObjectiveId": "550e8400-e29b-41d4-a716-446655440000",
          "score": 85.0,
          "scoreStatus": "earnedFull"
        },
        {
          "learningObjectiveId": "6fa459ea-ee8a-3ca4-894e-db77e160355e",
          "score": 92.0,
          "scoreStatus": "earnedFull"
        }
      ]
    }
  }
}
```

### 7.3.2 標準準拠評価レポート生成

**Node.js例**

```javascript
class StandardsBasedReporting {
  async getStudentMasteryReport(studentSourcedId, academicSessionSourcedId) {
    // 学生の全Results取得
    const results = await Result.findAll({
      where: { studentSourcedId },
      include: [{
        model: LineItem,
        where: { academicSessionSourcedId }
      }]
    });

    const masteryByObjective = {};

    for (const result of results) {
      if (result.learningObjectiveSet && result.learningObjectiveSet.learningObjectiveScores) {
        for (const objectiveScore of result.learningObjectiveSet.learningObjectiveScores) {
          const objId = objectiveScore.learningObjectiveId;

          if (!masteryByObjective[objId]) {
            masteryByObjective[objId] = {
              learningObjectiveId: objId,
              scores: [],
              averageScore: 0,
              masteryLevel: ''
            };
          }

          masteryByObjective[objId].scores.push(objectiveScore.score);
        }
      }
    }

    // 平均スコアと習熟度レベルを計算
    for (const objId in masteryByObjective) {
      const scores = masteryByObjective[objId].scores;
      const average = scores.reduce((a, b) => a + b, 0) / scores.length;

      masteryByObjective[objId].averageScore = average;
      masteryByObjective[objId].masteryLevel = this.getMasteryLevel(average);
    }

    return masteryByObjective;
  }

  getMasteryLevel(score) {
    if (score >= 90) return 'Mastered';
    if (score >= 75) return 'Proficient';
    if (score >= 60) return 'Developing';
    return 'Beginning';
  }
}
```

## 7.4 AssessmentLineItems/Results（階層型評価）

クラスに紐付かない階層型評価をサポートします。

### 7.4.1 階層構造の実装

**テーブル追加**

```sql
CREATE TABLE assessment_line_items (
    sourced_id VARCHAR(255) PRIMARY KEY,
    status VARCHAR(50) NOT NULL,
    date_last_modified TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    title VARCHAR(255),
    description TEXT,
    assign_date DATE,
    due_date DATE,
    parent_assessment_line_item_sourced_id VARCHAR(255),
    class_sourced_id VARCHAR(255),  -- 任意
    result_value_min DECIMAL(10,2),
    result_value_max DECIMAL(10,2),
    FOREIGN KEY (parent_assessment_line_item_sourced_id)
        REFERENCES assessment_line_items(sourced_id)
);

CREATE TABLE assessment_results (
    sourced_id VARCHAR(255) PRIMARY KEY,
    status VARCHAR(50) NOT NULL,
    date_last_modified TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    assessment_line_item_sourced_id VARCHAR(255) NOT NULL,
    student_sourced_id VARCHAR(255) NOT NULL,
    score_status VARCHAR(50),
    score DECIMAL(10,2),
    score_percentile DECIMAL(5,2),  -- v1.2新機能
    FOREIGN KEY (assessment_line_item_sourced_id)
        REFERENCES assessment_line_items(sourced_id)
);
```

**階層構造の例**

```json
{
  "assessmentLineItem": {
    "sourcedId": "state-test-math",
    "title": "State Mathematics Test 2024",
    "description": "Statewide standardized math assessment"
  }
}
```

```json
{
  "assessmentLineItem": {
    "sourcedId": "state-test-math-algebra",
    "title": "Algebra Section",
    "parentAssessmentLineItem": {
      "sourcedId": "state-test-math",
      "type": "assessmentLineItem"
    }
  }
}
```

```json
{
  "assessmentLineItem": {
    "sourcedId": "state-test-math-algebra-q1",
    "title": "Question 1: Solve for x",
    "parentAssessmentLineItem": {
      "sourcedId": "state-test-math-algebra",
      "type": "assessmentLineItem"
    },
    "resultValueMin": 0,
    "resultValueMax": 1
  }
}
```

---

# 第8章 テストとデバッグ

## 8.1 単体テスト

### 8.1.1 Node.js (Jest) テスト

**tests/category.test.js**

```javascript
const request = require('supertest');
const app = require('../src/app');
const { Category } = require('../src/models');

describe('Category API Tests', () => {
  let accessToken;

  beforeAll(async () => {
    // テストトークン取得
    const tokenResponse = await request(app)
      .post('/oauth/token')
      .auth(process.env.TEST_CLIENT_ID, process.env.TEST_CLIENT_SECRET)
      .send('grant_type=client_credentials&scope=https://purl.imsglobal.org/spec/or/v1p1/scope/gradebook.readonly');

    accessToken = tokenResponse.body.access_token;
  });

  describe('GET /categories', () => {
    it('should return all categories with pagination', async () => {
      const response = await request(app)
        .get('/categories?limit=10&offset=0')
        .set('Authorization', `Bearer ${accessToken}`)
        .expect(200);

      expect(response.body).toHaveProperty('categories');
      expect(Array.isArray(response.body.categories)).toBe(true);
      expect(response.headers).toHaveProperty('x-total-count');
    });

    it('should apply filter correctly', async () => {
      const response = await request(app)
        .get("/categories?filter=status='active'")
        .set('Authorization', `Bearer ${accessToken}`)
        .expect(200);

      response.body.categories.forEach(cat => {
        expect(cat.status).toBe('active');
      });
    });

    it('should return 401 without token', async () => {
      await request(app)
        .get('/categories')
        .expect(401);
    });
  });

  describe('POST /categories/{id}', () => {
    it('should create a new category', async () => {
      const newCategory = {
        category: {
          title: 'Test Category',
          weight: 0.3
        }
      };

      const response = await request(app)
        .put('/categories/test-cat-123')
        .set('Authorization', `Bearer ${accessToken}`)
        .send(newCategory)
        .expect(201);

      expect(response.body.category).toHaveProperty('sourcedId', 'test-cat-123');
      expect(response.body.category).toHaveProperty('title', 'Test Category');
    });
  });
});
```

### 8.1.2 Python (pytest) テスト

**tests/test_categories.py**

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def access_token():
    """テストトークン取得"""
    response = client.post(
        "/oauth/token",
        auth=(TEST_CLIENT_ID, TEST_CLIENT_SECRET),
        data={
            "grant_type": "client_credentials",
            "scope": "https://purl.imsglobal.org/spec/or/v1p1/scope/gradebook.readonly"
        }
    )
    return response.json()["access_token"]

def test_get_categories(access_token):
    """全Categories取得テスト"""
    response = client.get(
        "/categories?limit=10&offset=0",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200
    assert "categories" in response.json()
    assert isinstance(response.json()["categories"], list)
    assert "X-Total-Count" in response.headers

def test_get_categories_with_filter(access_token):
    """フィルター付き取得テスト"""
    response = client.get(
        "/categories?filter=status='active'",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200
    for category in response.json()["categories"]:
        assert category["status"] == "active"

def test_get_categories_unauthorized():
    """認証なしアクセステスト"""
    response = client.get("/categories")
    assert response.status_code == 401

def test_create_category(access_token):
    """Category作成テスト"""
    new_category = {
        "category": {
            "title": "Test Category",
            "weight": 0.3
        }
    }

    response = client.put(
        "/categories/test-cat-123",
        json=new_category,
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 201
    assert response.json()["category"]["sourcedId"] == "test-cat-123"
    assert response.json()["category"]["title"] == "Test Category"
```

### 8.1.3 Java (JUnit) テスト

**src/test/java/com/example/gradebook/CategoryControllerTest.java**

```java
package com.example.gradebook;

import com.example.gradebook.controller.CategoryController;
import com.example.gradebook.model.Category;
import com.example.gradebook.repository.CategoryRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
public class CategoryControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private CategoryRepository categoryRepository;

    @BeforeEach
    public void setup() {
        categoryRepository.deleteAll();
    }

    @Test
    @WithMockUser(authorities = {"SCOPE_gradebook.readonly"})
    public void testGetAllCategories() throws Exception {
        mockMvc.perform(get("/categories?limit=10&offset=0"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.categories").isArray())
            .andExpect(header().exists("X-Total-Count"));
    }

    @Test
    public void testGetCategoriesUnauthorized() throws Exception {
        mockMvc.perform(get("/categories"))
            .andExpect(status().isUnauthorized());
    }

    @Test
    @WithMockUser(authorities = {"SCOPE_gradebook.createput"})
    public void testCreateCategory() throws Exception {
        String categoryJson = """
            {
              "category": {
                "title": "Test Category",
                "weight": 0.3
              }
            }
            """;

        mockMvc.perform(put("/categories/test-cat-123")
                .contentType(MediaType.APPLICATION_JSON)
                .content(categoryJson))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.category.sourcedId").value("test-cat-123"))
            .andExpect(jsonPath("$.category.title").value("Test Category"));
    }
}
```

## 8.2 統合テスト

### 8.2.1 エンドツーエンドシナリオテスト

**Node.js E2Eテスト**

```javascript
// tests/e2e/gradebook-workflow.test.js
const request = require('supertest');
const app = require('../../src/app');

describe('Gradebook Workflow E2E Tests', () => {
  let accessToken;
  let categoryId;
  let lineItemId;
  let resultId;

  beforeAll(async () => {
    // OAuth token取得
    const tokenResponse = await request(app)
      .post('/oauth/token')
      .auth(process.env.TEST_CLIENT_ID, process.env.TEST_CLIENT_SECRET)
      .send('grant_type=client_credentials&scope=https://purl.imsglobal.org/spec/or/v1p1/scope/gradebook.createput');

    accessToken = tokenResponse.body.access_token;
  });

  it('Complete gradebook workflow', async () => {
    // 1. Category作成
    categoryId = 'e2e-cat-' + Date.now();
    const categoryResponse = await request(app)
      .put(`/categories/${categoryId}`)
      .set('Authorization', `Bearer ${accessToken}`)
      .send({
        category: {
          title: 'E2E Test Category',
          weight: 0.4
        }
      })
      .expect(201);

    expect(categoryResponse.body.category.sourcedId).toBe(categoryId);

    // 2. LineItem作成
    lineItemId = 'e2e-li-' + Date.now();
    const lineItemResponse = await request(app)
      .put(`/lineItems/${lineItemId}`)
      .set('Authorization', `Bearer ${accessToken}`)
      .send({
        lineItem: {
          title: 'E2E Test Assignment',
          class: { sourcedId: 'class-123', type: 'class' },
          category: { sourcedId: categoryId, type: 'category' },
          resultValueMin: 0,
          resultValueMax: 100
        }
      })
      .expect(201);

    expect(lineItemResponse.body.lineItem.sourcedId).toBe(lineItemId);

    // 3. Result作成
    resultId = 'e2e-result-' + Date.now();
    const resultResponse = await request(app)
      .put(`/results/${resultId}`)
      .set('Authorization', `Bearer ${accessToken}`)
      .send({
        result: {
          lineItem: { sourcedId: lineItemId, type: 'lineItem' },
          student: { sourcedId: 'student-456', type: 'user' },
          scoreStatus: 'earnedFull',
          score: 85.5
        }
      })
      .expect(201);

    expect(resultResponse.body.result.sourcedId).toBe(resultId);
    expect(resultResponse.body.result.score).toBe(85.5);

    // 4. クラス別Results取得
    const resultsResponse = await request(app)
      .get(`/classes/class-123/results?limit=100`)
      .set('Authorization', `Bearer ${accessToken}`)
      .expect(200);

    const createdResult = resultsResponse.body.results.find(r => r.sourcedId === resultId);
    expect(createdResult).toBeDefined();

    // 5. クリーンアップ（論理削除）
    await request(app)
      .delete(`/results/${resultId}`)
      .set('Authorization', `Bearer ${accessToken}`)
      .expect(204);

    await request(app)
      .delete(`/lineItems/${lineItemId}`)
      .set('Authorization', `Bearer ${accessToken}`)
      .expect(204);

    await request(app)
      .delete(`/categories/${categoryId}`)
      .set('Authorization', `Bearer ${accessToken}`)
      .expect(204);
  });
});
```

## 8.3 APIテストツール

### 8.3.1 Postmanコレクション

**OneRoster_Gradebook.postman_collection.json**

```json
{
  "info": {
    "name": "OneRoster Gradebook API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "auth": {
    "type": "oauth2",
    "oauth2": [
      {
        "key": "tokenName",
        "value": "OneRoster Token",
        "type": "string"
      },
      {
        "key": "grant_type",
        "value": "client_credentials",
        "type": "string"
      },
      {
        "key": "accessTokenUrl",
        "value": "{{base_url}}/oauth/token",
        "type": "string"
      }
    ]
  },
  "item": [
    {
      "name": "Categories",
      "item": [
        {
          "name": "Get All Categories",
          "request": {
            "method": "GET",
            "header": [],
            "url": {
              "raw": "{{base_url}}/categories?limit=100&offset=0",
              "host": ["{{base_url}}"],
              "path": ["categories"],
              "query": [
                {"key": "limit", "value": "100"},
                {"key": "offset", "value": "0"}
              ]
            }
          }
        },
        {
          "name": "Get Category by ID",
          "request": {
            "method": "GET",
            "url": "{{base_url}}/categories/{{category_id}}"
          }
        },
        {
          "name": "Create/Update Category",
          "request": {
            "method": "PUT",
            "header": [{"key": "Content-Type", "value": "application/json"}],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"category\": {\n    \"title\": \"Homework\",\n    \"weight\": 0.3\n  }\n}"
            },
            "url": "{{base_url}}/categories/{{category_id}}"
          }
        }
      ]
    }
  ]
}
```

### 8.3.2 curlコマンド例

**トークン取得**

```bash
curl -X POST https://api.example.com/oauth/token \
  -u "client_id:client_secret" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&scope=https://purl.imsglobal.org/spec/or/v1p1/scope/gradebook.readonly"
```

**Categories取得**

```bash
TOKEN="your_access_token"

curl -X GET "https://api.example.com/ims/oneroster/gradebook/v1p2/categories?limit=100&offset=0" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/json"
```

**LineItem作成**

```bash
curl -X PUT "https://api.example.com/ims/oneroster/gradebook/v1p2/lineItems/li-12345" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "lineItem": {
      "title": "Math Quiz 1",
      "class": {"sourcedId": "class-456", "type": "class"},
      "resultValueMin": 0,
      "resultValueMax": 100
    }
  }'
```

---

# 第9章 IMS認定準備

## 9.1 IMS認定の概要

### 認定のメリット

- **相互運用性の保証**: 認定製品間でシームレスなデータ交換
- **市場優位性**: IMS Product Directoryへの掲載
- **統合コスト削減**: カスタム統合が不要
- **ベンダーロックイン回避**: 標準準拠による柔軟性

### 認定タイプ

| 認定タイプ | 説明 | 対象 |
|----------|------|------|
| **Provider (Pull)** | GETエンドポイント提供 | SIS、LMS（データ提供側） |
| **Provider (Push)** | PUT/POST/DELETEを受信 | SIS（データ受信側） |
| **Consumer (Pull)** | 他システムのGETエンドポイント呼び出し | LMS、分析システム |
| **Consumer (Push)** | 他システムにPUT/POST/DELETE送信 | LMS（データ送信側） |

## 9.2 必須エンドポイント

### Gradebook Service Provider認定

**最小必須エンドポイント（Pull）:**

```
GET  /categories
GET  /categories/{id}
GET  /lineItems
GET  /lineItems/{id}
GET  /classes/{class_id}/lineItems
GET  /results
GET  /results/{id}
GET  /classes/{class_id}/results
GET  /classes/{class_id}/lineItems/{li_id}/results
GET  /classes/{class_id}/students/{student_id}/results
```

**Push対応の場合（追加）:**

```
PUT    /categories/{id}
DELETE /categories/{id}
PUT    /lineItems/{id}
DELETE /lineItems/{id}
PUT    /results/{id}
DELETE /results/{id}
```

**v1.2一括操作（オプション）:**

```
POST /classes/{class_id}/lineItems
POST /lineItems/{li_id}/results
```

### ScoreScales対応（オプション）

```
GET    /scoreScales
GET    /scoreScales/{id}
GET    /classes/{class_id}/scoreScales
PUT    /scoreScales/{id}
DELETE /scoreScales/{id}
```

## 9.3 適合性テスト

### OneRoster参照実装の活用

IMS Globalは参照実装ツールを提供しています。
https://or-ri.imsglobal.org/

**テスト手順:**

1. **アカウント登録**: IMS Global Webサイトでアカウント作成
2. **エンドポイント登録**: 実装したAPIのベースURLを登録
3. **認証情報設定**: OAuth 2.0のClient ID/Secretを設定
4. **テスト実行**: 自動テストスイートを実行
5. **レポート確認**: 適合性レポートをダウンロード

### 手動テストチェックリスト

**基本機能:**

- [ ] OAuth 2.0 Client Credentials Grantが正しく機能
- [ ] Bearer Token認証が正常に動作
- [ ] TLS 1.2以上で通信
- [ ] すべてのレスポンスが正しいJSON形式
- [ ] HTTPステータスコードが仕様通り

**ページネーション:**

- [ ] `limit`パラメータが正しく機能（最大1000）
- [ ] `offset`パラメータが正しく機能
- [ ] `X-Total-Count`ヘッダーが返却される
- [ ] `Link`ヘッダー（next）が正しく生成される

**フィルタリング:**

- [ ] `filter`パラメータが正しく解析される
- [ ] 演算子（=、!=、>、<、~）が正しく動作
- [ ] 論理演算子（AND、OR）が正しく動作
- [ ] 無効なフィルター構文で400エラー

**ソート:**

- [ ] `sort`パラメータが正しく機能
- [ ] `orderBy`（asc/desc）が正しく機能

**エラーハンドリング:**

- [ ] 401: 無効なトークンで認証エラー
- [ ] 403: 権限不足でアクセス拒否
- [ ] 404: 存在しないリソースで未検出
- [ ] 422: 無効なデータでバリデーションエラー
- [ ] すべてのエラーが`statusInfoSet`形式

**データ整合性:**

- [ ] `sourcedId`はグローバル一意
- [ ] `status`は`active`または`tobedeleted`のみ
- [ ] `dateLastModified`は更新時に自動更新
- [ ] 外部キー（class、category等）の参照整合性
- [ ] 削除は論理削除（status='tobedeleted'）

**v1.2新機能（実装した場合）:**

- [ ] ScoreScalesが正しく動作
- [ ] 一括操作（POST）がGUIDペアを返却
- [ ] LearningObjectiveSetが正しく保存・返却
- [ ] AssessmentLineItems/Resultsが正しく動作
- [ ] textScoreが正しく保存・返却

## 9.4 認定申請プロセス

### ステップ1: 自己評価

適合性チェックリストを使用して自己評価を実施します。

### ステップ2: 参照実装テスト

IMS参照実装ツールで自動テストを実行し、レポートを取得します。

### ステップ3: 認定申請

IMS Global Webサイトから認定申請フォームを提出：
https://www.imsglobal.org/cc/statuscert.cfm

**必要情報:**

- 製品名とバージョン
- 会社情報
- 実装したエンドポイントリスト
- サポートするスコープ
- 参照実装テストレポート

### ステップ4: レビューと修正

IMS認定チームがレビューし、必要に応じて修正を依頼します。

### ステップ5: 認定取得

審査合格後、IMS Product Directoryに掲載されます。
https://www.imscert.org/

---

# 第10章 運用とベストプラクティス

## 10.1 パフォーマンス最適化

### 10.1.1 データベースインデックス

**推奨インデックス:**

```sql
-- 頻繁に検索されるフィールド
CREATE INDEX idx_line_items_class ON line_items(class_sourced_id);
CREATE INDEX idx_line_items_category ON line_items(category_sourced_id);
CREATE INDEX idx_line_items_status ON line_items(status);

CREATE INDEX idx_results_line_item ON results(line_item_sourced_id);
CREATE INDEX idx_results_student ON results(student_sourced_id);
CREATE INDEX idx_results_class ON results(class_sourced_id);
CREATE INDEX idx_results_status ON results(status);
CREATE INDEX idx_results_score_status ON results(score_status);

-- 複合インデックス
CREATE INDEX idx_results_class_student ON results(class_sourced_id, student_sourced_id);
CREATE INDEX idx_results_class_lineitem ON results(class_sourced_id, line_item_sourced_id);

-- 日付範囲検索用
CREATE INDEX idx_line_items_due_date ON line_items(due_date);
CREATE INDEX idx_results_score_date ON results(score_date);
```

### 10.1.2 キャッシング戦略

**Node.js (Redis) キャッシング**

```javascript
const redis = require('redis');
const client = redis.createClient();

class CachedGradebookService {
  async getCategories(limit, offset, filter) {
    const cacheKey = `categories:${limit}:${offset}:${filter || 'none'}`;

    // キャッシュチェック
    const cached = await client.get(cacheKey);
    if (cached) {
      return JSON.parse(cached);
    }

    // DBクエリ
    const categories = await Category.findAndCountAll({
      limit,
      offset,
      where: filter ? this.buildWhereClause(filter) : {}
    });

    // キャッシュに保存（5分間）
    await client.setex(cacheKey, 300, JSON.stringify(categories));

    return categories;
  }

  async invalidateCategoryCache(categoryId) {
    const keys = await client.keys('categories:*');
    if (keys.length > 0) {
      await client.del(...keys);
    }
  }
}
```

### 10.1.3 データベース接続プーリング

**Node.js (Sequelize)**

```javascript
const { Sequelize } = require('sequelize');

const sequelize = new Sequelize(process.env.DATABASE_URL, {
  dialect: 'postgres',
  pool: {
    max: 20,
    min: 5,
    acquire: 30000,
    idle: 10000
  },
  logging: false
});
```

**Python (SQLAlchemy)**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

## 10.2 監視とロギング

### 10.2.1 ロギング実装

**Node.js (Winston)**

```javascript
const winston = require('winston');

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' })
  ]
});

// OAuth認証ログ
logger.info('OAuth token requested', {
  clientId: clientId,
  scope: scope,
  timestamp: new Date()
});

// APIリクエストログ
logger.info('API request', {
  method: req.method,
  endpoint: req.path,
  clientId: req.oauth.token.clientId,
  duration: responseTime
});
```

**Python (structlog)**

```python
import structlog

logger = structlog.get_logger()

# OAuth認証ログ
logger.info("oauth_token_requested",
    client_id=client_id,
    scope=scope,
    timestamp=datetime.now()
)

# APIリクエストログ
logger.info("api_request",
    method=request.method,
    endpoint=request.url.path,
    client_id=token.get("client_id"),
    duration=response_time
)
```

### 10.2.2 メトリクス収集

**Prometheusメトリクス (Node.js)**

```javascript
const promClient = require('prom-client');

// カスタムメトリクス
const httpRequestDuration = new promClient.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'endpoint', 'status']
});

const oauthTokens = new promClient.Counter({
  name: 'oauth_tokens_issued_total',
  help: 'Total number of OAuth tokens issued',
  labelNames: ['client_id', 'scope']
});

// ミドルウェア
app.use((req, res, next) => {
  const start = Date.now();

  res.on('finish', () => {
    const duration = (Date.now() - start) / 1000;
    httpRequestDuration.labels(req.method, req.path, res.statusCode).observe(duration);
  });

  next();
});

// メトリクスエンドポイント
app.get('/metrics', async (req, res) => {
  res.set('Content-Type', promClient.register.contentType);
  res.end(await promClient.register.metrics());
});
```

## 10.3 セキュリティベストプラクティス

### 10.3.1 認証情報管理

**環境変数 vs シークレット管理**

```bash
# .env ファイル（開発環境）
OAUTH_CLIENT_ID=dev_client_id
OAUTH_CLIENT_SECRET=dev_secret
DATABASE_URL=postgresql://localhost:5432/gradebook_dev

# 本番環境: AWS Secrets Manager、HashiCorp Vault等を使用
```

**Node.js (AWS Secrets Manager)**

```javascript
const AWS = require('aws-sdk');
const secretsManager = new AWS.SecretsManager();

async function getSecret(secretName) {
  const data = await secretsManager.getSecretValue({ SecretId: secretName }).promise();
  return JSON.parse(data.SecretString);
}

// 使用例
const credentials = await getSecret('oneroster/oauth/credentials');
const clientId = credentials.client_id;
const clientSecret = credentials.client_secret;
```

### 10.3.2 レート制限

**Node.js (express-rate-limit)**

```javascript
const rateLimit = require('express-rate-limit');

const apiLimiter = rateLimit({
  windowMs: 1 * 60 * 1000, // 1分
  max: 100, // 100リクエスト/分
  message: {
    statusInfoSet: [{
      imsx_codeMajor: 'failure',
      imsx_severity: 'error',
      imsx_description: 'Too many requests',
      imsx_codeMinor: 'server_busy'
    }]
  },
  standardHeaders: true,
  legacyHeaders: false
});

app.use('/ims/oneroster/gradebook/v1p2', apiLimiter);
```

**Python (slowapi)**

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/categories")
@limiter.limit("100/minute")
async def get_categories(request: Request):
    # ...
```

### 10.3.3 入力バリデーション

**Node.js (express-validator)**

```javascript
const { body, validationResult } = require('express-validator');

app.put('/lineItems/:id',
  authenticate('gradebook.createput'),
  [
    body('lineItem.title').isString().notEmpty().trim(),
    body('lineItem.class.sourcedId').isString().notEmpty(),
    body('lineItem.resultValueMin').optional().isFloat({ min: 0 }),
    body('lineItem.resultValueMax').optional().isFloat({ min: 0 })
  ],
  (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        statusInfoSet: [{
          imsx_codeMajor: 'failure',
          imsx_severity: 'error',
          imsx_description: 'Validation failed: ' + errors.array().map(e => e.msg).join(', '),
          imsx_codeMinor: 'invalid_data'
        }]
      });
    }

    // 処理続行...
  }
);
```

## 10.4 データバックアップと災害復旧

### 10.4.1 定期バックアップ

**PostgreSQL自動バックアップスクリプト**

```bash
#!/bin/bash
# backup-gradebook.sh

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="/backups/gradebook"
DB_NAME="gradebook"

# フルバックアップ
pg_dump -U postgres -d $DB_NAME -F c -f "$BACKUP_DIR/gradebook_$TIMESTAMP.backup"

# 古いバックアップ削除（30日以上前）
find $BACKUP_DIR -name "gradebook_*.backup" -mtime +30 -delete

echo "Backup completed: gradebook_$TIMESTAMP.backup"
```

**cron設定（毎日午前2時）**

```bash
0 2 * * * /path/to/backup-gradebook.sh
```

### 10.4.2 災害復旧計画

**RTO/RPO目標:**

- **RTO (Recovery Time Objective)**: 4時間以内
- **RPO (Recovery Point Objective)**: 1時間以内

**リストア手順:**

```bash
# 最新バックアップからリストア
pg_restore -U postgres -d gradebook_restored -c /backups/gradebook/gradebook_20240115_020000.backup

# データ整合性確認
psql -U postgres -d gradebook_restored -c "SELECT COUNT(*) FROM categories;"
psql -U postgres -d gradebook_restored -c "SELECT COUNT(*) FROM line_items;"
psql -U postgres -d gradebook_restored -c "SELECT COUNT(*) FROM results;"
```

## 10.5 ドキュメンテーション

### 10.5.1 OpenAPI仕様書生成

**Node.js (swagger-jsdoc)**

```javascript
const swaggerJsdoc = require('swagger-jsdoc');
const swaggerUi = require('swagger-ui-express');

const swaggerOptions = {
  definition: {
    openapi: '3.0.0',
    info: {
      title: 'OneRoster Gradebook API',
      version: '1.2.0',
      description: 'OneRoster 1.2 Gradebook Service Implementation'
    },
    servers: [
      { url: 'https://api.example.com/ims/oneroster/gradebook/v1p2' }
    ],
    components: {
      securitySchemes: {
        oauth2: {
          type: 'oauth2',
          flows: {
            clientCredentials: {
              tokenUrl: 'https://api.example.com/oauth/token',
              scopes: {
                'https://purl.imsglobal.org/spec/or/v1p1/scope/gradebook.readonly': 'Read access',
                'https://purl.imsglobal.org/spec/or/v1p1/scope/gradebook.createput': 'Write access',
                'https://purl.imsglobal.org/spec/or/v1p1/scope/gradebook.delete': 'Delete access'
              }
            }
          }
        }
      }
    },
    security: [{ oauth2: [] }]
  },
  apis: ['./src/routes/*.js']
};

const swaggerSpec = swaggerJsdoc(swaggerOptions);

app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec));
```

**ルートにJSDocアノテーション追加**

```javascript
/**
 * @swagger
 * /categories:
 *   get:
 *     summary: Get all categories
 *     tags: [Categories]
 *     parameters:
 *       - in: query
 *         name: limit
 *         schema:
 *           type: integer
 *           minimum: 1
 *           maximum: 1000
 *           default: 100
 *       - in: query
 *         name: offset
 *         schema:
 *           type: integer
 *           minimum: 0
 *           default: 0
 *     responses:
 *       200:
 *         description: List of categories
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 categories:
 *                   type: array
 *                   items:
 *                     $ref: '#/components/schemas/Category'
 */
router.get('/categories', categoryController.getAllCategories);
```

---

# 付録A: 完全実装チェックリスト

## Provider実装

### 基盤機能
- [ ] PostgreSQLデータベース設定完了
- [ ] OAuth 2.0認証サーバー実装完了
- [ ] Bearer Token検証実装完了
- [ ] TLS 1.2以上設定完了
- [ ] エラーハンドリングミドルウェア実装完了

### Categories API
- [ ] GET /categories 実装完了
- [ ] GET /categories/{id} 実装完了
- [ ] PUT /categories/{id} 実装完了
- [ ] DELETE /categories/{id} 実装完了
- [ ] GET /classes/{class_id}/categories 実装完了（v1.2）

### LineItems API
- [ ] GET /lineItems 実装完了
- [ ] GET /lineItems/{id} 実装完了
- [ ] PUT /lineItems/{id} 実装完了
- [ ] DELETE /lineItems/{id} 実装完了
- [ ] GET /classes/{class_id}/lineItems 実装完了
- [ ] POST /classes/{class_id}/lineItems 実装完了（v1.2一括操作）

### Results API
- [ ] GET /results 実装完了
- [ ] GET /results/{id} 実装完了
- [ ] PUT /results/{id} 実装完了
- [ ] DELETE /results/{id} 実装完了
- [ ] GET /classes/{class_id}/results 実装完了
- [ ] GET /classes/{class_id}/lineItems/{li_id}/results 実装完了
- [ ] GET /classes/{class_id}/students/{student_id}/results 実装完了
- [ ] POST /lineItems/{li_id}/results 実装完了（v1.2一括操作）

### v1.2新機能
- [ ] ScoreScales API実装完了
- [ ] AssessmentLineItems API実装完了
- [ ] AssessmentResults API実装完了
- [ ] LearningObjectiveSet対応完了
- [ ] textScore対応完了
- [ ] 一括操作GUIDペア機構実装完了

### 共通機能
- [ ] ページネーション（limit、offset）実装完了
- [ ] フィルタリング（filter構文）実装完了
- [ ] ソート（sort、orderBy）実装完了
- [ ] フィールド選択（fields）実装完了
- [ ] X-Total-Countヘッダー実装完了
- [ ] Linkヘッダー（next）実装完了

## Consumer実装

- [ ] OAuth 2.0クライアント実装完了
- [ ] トークンキャッシング実装完了
- [ ] APIクライアントラッパー実装完了
- [ ] ページネーション対応全件取得実装完了
- [ ] エラーハンドリング実装完了
- [ ] 401エラー時の自動リトライ実装完了

## テスト

- [ ] 単体テスト実装完了（カバレッジ80%以上）
- [ ] 統合テスト実装完了
- [ ] E2Eテスト実装完了
- [ ] Postmanコレクション作成完了
- [ ] IMS参照実装テスト合格

## 運用

- [ ] ロギング実装完了
- [ ] メトリクス収集実装完了
- [ ] レート制限実装完了
- [ ] データベースインデックス最適化完了
- [ ] バックアップスクリプト設定完了
- [ ] 災害復旧計画文書化完了
- [ ] OpenAPI仕様書生成完了

---

# 付録B: トラブルシューティング

## 認証関連

**問題**: 401 Unauthorizedエラーが頻発

**原因と解決策**:
- トークン有効期限切れ → トークンキャッシングとリフレッシュロジック実装
- クロックスキュー → サーバー時刻同期（NTP設定）
- スコープ不足 → 正しいスコープでトークン取得

**問題**: OAuth 2.0トークン取得失敗

**原因と解決策**:
- Client ID/Secret不正 → 認証情報確認
- Basic認証エンコード誤り → Base64エンコード確認
- Content-Type誤り → application/x-www-form-urlencodedを使用

## パフォーマンス関連

**問題**: API応答が遅い

**原因と解決策**:
- インデックス不足 → 頻繁に検索されるカラムにインデックス追加
- N+1クエリ → ORMのeager loading使用
- 大量データ取得 → ページネーション適切に実装、limit上限設定

**問題**: データベース接続プール枯渇

**原因と解決策**:
- 接続リーク → 必ず接続をクローズ、try-finally使用
- プールサイズ不足 → max_connectionsを増やす

## データ整合性関連

**問題**: 外部キー制約違反

**原因と解決策**:
- 存在しないclassSourcedId参照 → Rostering APIで存在確認
- 削除済みリソース参照 → status='active'のみ参照

**問題**: dateLastModified更新されない

**原因と解決策**:
- トリガー未設定 → データベーストリガー設定
- ORMフック未実装 → beforeUpdateフック実装

---

# 付録C: 参考資料

## 公式仕様書

1. **OneRoster 1.2 Gradebook Service Information Model**
   https://www.imsglobal.org/spec/oneroster/v1p2/gradebook/info

2. **OneRoster 1.2 Gradebook Service REST Binding**
   https://www.imsglobal.org/spec/oneroster/v1p2/gradebook/bind/rest

3. **IMS Security Framework 1.0**
   https://www.imsglobal.org/spec/security/v1p0/

4. **RFC 6749 - OAuth 2.0 Authorization Framework**
   https://tools.ietf.org/html/rfc6749

## ツールとライブラリ

### Node.js
- Express.js: https://expressjs.com/
- Sequelize ORM: https://sequelize.org/
- oauth2-server: https://github.com/oauthjs/node-oauth2-server
- Jest: https://jestjs.io/

### Python
- FastAPI: https://fastapi.tiangolo.com/
- SQLAlchemy: https://www.sqlalchemy.org/
- Authlib: https://docs.authlib.org/
- pytest: https://docs.pytest.org/

### Java
- Spring Boot: https://spring.io/projects/spring-boot
- Spring Security OAuth2: https://spring.io/projects/spring-security-oauth
- Spring Data JPA: https://spring.io/projects/spring-data-jpa
- JUnit: https://junit.org/

## コミュニティとサポート

- **IMS Global公式フォーラム**: https://www.imsglobal.org/forums
- **OneRoster開発者FAQ**: https://support.imsglobal.org/
- **IMS認定製品ディレクトリ**: https://imscert.org/
- **OneRoster参照実装**: https://or-ri.imsglobal.org/

---

# まとめ

本ガイドでは、OneRoster Gradebook Service v1.2の完全な実装方法を、Node.js、Python、Javaの3言語で解説しました。

## 主要ポイント

1. **アーキテクチャ理解**: Gradebook ServiceはRostering Serviceに依存し、独立したサービスとして機能
2. **OAuth 2.0必須**: Client Credentials Grantが唯一の認証方式
3. **v1.2新機能**: ScoreScales、一括操作、標準準拠型評価、階層型評価
4. **Provider/Consumer両対応**: データ提供側と利用側の両方の実装パターン
5. **IMS認定**: 相互運用性保証のための認定取得プロセス

## 次のステップ

1. **環境構築**: 第2章を参考に開発環境をセットアップ
2. **最小実装**: Categories、LineItems、Resultsの基本APIを実装
3. **テスト**: 単体テスト、統合テストを実装
4. **拡張機能**: v1.2新機能を段階的に実装
5. **IMS認定**: 参照実装ツールでテストし、認定申請

本ガイドを活用して、堅牢で標準準拠のOneRoster Gradebook Serviceを構築してください。

---

**【使用ガイド】**

本技術資料は、以下の用途で活用できます。

- **新規実装**: ゼロからGradebook Serviceを構築
- **既存システム統合**: LMS/SISへのOneRoster対応追加
- **技術評価**: OneRoster導入可否の判断材料
- **開発者教育**: チーム内でのOneRoster知識共有

**【レビューポイント】**

1. 使用する技術スタック（Node.js/Python/Java）の選択は適切か
2. Provider/Consumerどちらを実装するか明確か
3. v1.2新機能のうち、必要な機能を特定できたか
4. IMS認定取得が必要かどうか判断できたか

何か修正や追加のご要望はありますか？
