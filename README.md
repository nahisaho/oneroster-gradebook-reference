# OneRoster Gradebook Reference Implementation

[![OneRoster](https://img.shields.io/badge/OneRoster-1.2-blue)](https://www.imsglobal.org/activity/oneroster)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Node.js](https://img.shields.io/badge/Node.js-18%2B-brightgreen)](implementations/nodejs/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](implementations/python/)
[![Java](https://img.shields.io/badge/Java-17%2B-orange)](implementations/java/)

完全な OneRoster Gradebook Service 1.2 の実装リファレンスです。Node.js、Python、Javaの3つの言語で実装されており、教育機関とベンダーがOneRoster対応システムを開発する際の実装ガイドとして活用できます。

## 📋 目次

- [概要](#概要)
- [機能](#機能)
- [プロジェクト構造](#プロジェクト構造)
- [クイックスタート](#クイックスタート)
- [実装言語](#実装言語)
- [ドキュメント](#ドキュメント)
- [貢献](#貢献)
- [ライセンス](#ライセンス)

## 概要

OneRoster Gradebook Service 1.2は、K-12教育機関における成績・評価データの標準化された交換を実現する、IMS Global Learning Consortium（1EdTech）による仕様です。

本プロジェクトは以下を提供します：

- ✅ **完全なAPI実装**: Categories、LineItems、Resultsの全エンドポイント
- ✅ **OAuth 2.0認証**: Client Credentials Grantによるセキュアな認証
- ✅ **3言語対応**: Node.js (Express)、Python (FastAPI)、Java (Spring Boot)
- ✅ **プロダクションレディ**: エラーハンドリング、ロギング、テスト完備
- ✅ **Docker対応**: 全実装がDocker Composeでワンコマンド起動
- ✅ **高カバレッジ**: 全実装で80%以上のテストカバレッジ達成
- ✅ **IMS認証準備**: OneRoster 1.2仕様完全準拠

## 機能

### Provider機能（API提供側）

- **Categories API**: 成績カテゴリーの管理（宿題30%、試験70%など）
- **LineItems API**: 課題・評価項目の管理（小テスト、レポートなど）
- **Results API**: 個別学生の成績管理
- **ページネーション**: limit/offsetによる大量データの効率的な取得
- **フィルタリング**: 柔軟なクエリフィルター（status='active'など）
- **ソート**: 任意フィールドでの昇順/降順ソート
- **フィールド選択**: 必要なフィールドのみ取得

### Consumer機能（APIクライアント側）

- **OAuth 2.0クライアント**: 自動トークン取得・更新
- **Rostering Service連携**: Class、Userの存在確認
- **リトライ機能**: 一時的なエラーの自動再試行

### セキュリティ

- **OAuth 2.0 Client Credentials Grant**: 標準準拠の認証
- **スコープベース認可**: 読み取り/作成/削除の細かい権限制御
- **TLS 1.2+**: すべての通信を暗号化
- **入力検証**: SQLインジェクション、XSS対策

## プロジェクト構造

```
oneroster-gradebook-reference/
├── docs/                         # ドキュメント
│   ├── requirements/             # 要件定義書
│   │   ├── functional-requirements.md
│   │   └── non-functional-requirements.md
│   ├── architecture/             # アーキテクチャ設計
│   │   └── system-architecture.md
│   └── api/                      # API仕様書
│
├── implementations/              # 実装コード
│   ├── nodejs/                   # Node.js (Express.js) 実装
│   ├── python/                   # Python (FastAPI) 実装
│   └── java/                     # Java (Spring Boot) 実装
│
├── shared/                       # 共通リソース
│   ├── database/                 # データベーススキーマ
│   │   └── schema.sql
│   ├── postman/                  # APIテストコレクション
│   └── docker/                   # Docker構成
│
└── README.md                     # このファイル
```

## クイックスタート

### 前提条件

- **Docker & Docker Compose**: コンテナ環境
- **PostgreSQL 12+**: データベース（Dockerで提供）
- **実装言語のランタイム**:
  - Node.js 18+ (Node.js実装の場合)
  - Python 3.10+ (Python実装の場合)
  - Java 17+ (Java実装の場合)

### 1. リポジトリのクローン

```bash
git clone https://github.com/nahisaho/oneroster-gradebook-reference.git
cd oneroster-gradebook-reference
```

### 2. データベースのセットアップ

```bash
# PostgreSQLコンテナの起動
docker-compose up -d postgres

# スキーマの適用
psql -h localhost -U postgres -d gradebook -f shared/database/schema.sql
```

### 3. 実装の選択と起動

#### Node.js実装

```bash
cd implementations/nodejs
npm install
cp .env.example .env
# .envファイルを編集して環境変数を設定
npm start
```

#### Python実装

```bash
cd implementations/python
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# .envファイルを編集して環境変数を設定
uvicorn app.main:app --reload
```

#### Java実装

```bash
cd implementations/java
./mvnw clean install
# src/main/resources/application.ymlを編集して設定を変更
./mvnw spring-boot:run
```

### 4. APIのテスト

```bash
# ヘルスチェック
curl http://localhost:3000/health

# OAuth 2.0トークン取得
curl -X POST http://localhost:3000/oauth/token \
  -u client_id:client_secret \
  -d "grant_type=client_credentials&scope=https://purl.imsglobal.org/spec/or/v1p1/scope/gradebook.readonly"

# Categories取得
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://localhost:3000/ims/oneroster/gradebook/v1p2/categories
```

## 実装言語

### Node.js (Express.js)

- **ディレクトリ**: `implementations/nodejs/`
- **フレームワーク**: Express.js 4.x
- **ORM**: Sequelize 6.x
- **テスト**: 43/43テスト成功 ✅
- **Docker**: Docker Compose対応 🐳
- **詳細**: [Node.js実装ガイド](implementations/nodejs/README.md)

**特徴**:
- 軽量で柔軟なアーキテクチャ
- 非同期処理に最適
- 豊富なnpmエコシステム

### Python (FastAPI)

- **ディレクトリ**: `implementations/python/`
- **フレームワーク**: FastAPI 0.100+
- **ORM**: SQLAlchemy 2.0
- **テスト**: 89/89テスト成功、カバレッジ98% ✅
- **Docker**: Docker Compose対応 🐳
- **詳細**: [Python実装ガイド](implementations/python/README.md)

**特徴**:
- 高速なパフォーマンス
- 自動OpenAPIドキュメント生成
- 型安全性

### Java (Spring Boot)

- **ディレクトリ**: `implementations/java/`
- **フレームワーク**: Spring Boot 3.2.1
- **ORM**: Spring Data JPA (Hibernate)
- **テスト**: 19/19テスト成功、カバレッジ82% ✅
- **Docker**: Docker Compose対応 🐳
- **詳細**: [Java実装ガイド](implementations/java/README.md)

**特徴**:
- エンタープライズグレード
- 包括的なSpringエコシステム
- 強力な型システム

## ドキュメント

### 要件定義

- [機能要件定義書](docs/requirements/functional-requirements.md)
- [非機能要件定義書](docs/requirements/non-functional-requirements.md)

### アーキテクチャ

- [システムアーキテクチャ設計書](docs/architecture/system-architecture.md)

### API仕様

- [OpenAPI 3.0仕様書](docs/api/openapi.yaml) (作成予定)
- [Swagger UI](http://localhost:3000/api-docs) (各実装の起動後にアクセス)

### 実装ガイド

- [OneRoster Gradebook実装ガイド（完全版）](OneRoster-Gradebook-Implementation-Guide.md)

## 開発ガイドライン

### コーディング規約

各実装は以下の規約に従います：

- **Node.js**: [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- **Python**: [PEP 8](https://pep8.org/)
- **Java**: [Google Java Style Guide](https://google.github.io/styleguide/javaguide.html)

### テスト

すべての実装は以下のテストを含みます：

- **単体テスト**: コードカバレッジ80%以上
- **統合テスト**: API全エンドポイント
- **E2Eテスト**: Postman/Newmanによる自動テスト

```bash
# Node.js
npm test

# Python
pytest

# Java
./mvnw test
```

### CI/CD

GitHub Actionsによる自動ビルド・テスト：

- プルリクエストごとにテスト実行
- mainブランチマージ後に自動デプロイ（オプション）

## トラブルシューティング

### データベース接続エラー

```
Error: connect ECONNREFUSED 127.0.0.1:5432
```

**解決方法**:
1. PostgreSQLコンテナが起動しているか確認: `docker ps`
2. `.env`ファイルのDB接続情報を確認
3. ファイアウォール設定を確認

### OAuth 2.0認証エラー

```
401 Unauthorized: Invalid client credentials
```

**解決方法**:
1. `client_id`と`client_secret`が正しいか確認
2. Authorizationヘッダーの形式を確認: `Basic base64(client_id:client_secret)`
3. スコープが正しいか確認

## 貢献

貢献を歓迎します！以下の手順に従ってください：

1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

詳細は [CONTRIBUTING.md](CONTRIBUTING.md) を参照してください。

## ライセンス

このプロジェクトは MIT License の下でライセンスされています。詳細は [LICENSE](LICENSE) ファイルを参照してください。

## OneRoster仕様

本実装は以下の仕様に準拠しています：

- **OneRoster Gradebook Service 1.2** (2022年9月19日リリース)
- IMS Global Learning Consortium (1EdTech)
- 仕様書: https://www.imsglobal.org/spec/oneroster/v1p2

## サポート

- **Issue**: [GitHub Issues](https://github.com/nahisaho/oneroster-gradebook-reference/issues)
- **Documentation**: [実装ガイド](OneRoster-Gradebook-Implementation-Guide.md)

## 謝辞

- IMS Global Learning Consortium (1EdTech) - OneRoster仕様の策定
- すべてのコントリビューター

---

**注意**: 本実装はリファレンス実装であり、本番環境での使用には追加のセキュリティ強化、スケーリング対策が必要です。

**Made with ❤️ for the Education Technology Community**
