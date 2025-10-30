# Contributing to OneRoster Gradebook Reference Implementation

このプロジェクトへの貢献に興味を持っていただき、ありがとうございます！

## 貢献の方法

### バグ報告

バグを見つけた場合は、[GitHub Issues](https://github.com/nahisaho/oneroster-gradebook-reference/issues)で報告してください。

報告には以下の情報を含めてください：
- 問題の詳細な説明
- 再現手順
- 期待される動作
- 実際の動作
- 実行環境（OS、言語バージョンなど）
- エラーメッセージやスクリーンショット

### 機能リクエスト

新機能の提案も歓迎します。[GitHub Issues](https://github.com/nahisaho/oneroster-gradebook-reference/issues)で提案してください。

以下の情報を含めてください：
- 機能の詳細な説明
- ユースケース
- なぜこの機能が必要か

### プルリクエスト

コードの改善を提案する場合：

1. **リポジトリをフォーク**
   ```bash
   git clone https://github.com/nahisaho/oneroster-gradebook-reference.git
   cd oneroster-gradebook-reference
   ```

2. **機能ブランチを作成**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **変更を実装**
   - コーディング規約に従う
   - テストを追加
   - ドキュメントを更新

4. **テストを実行**
   ```bash
   # Node.js
   cd implementations/nodejs && npm test
   
   # Python
   cd implementations/python && pytest
   
   # Java
   cd implementations/java && mvn test
   ```

5. **変更をコミット**
   ```bash
   git add .
   git commit -m 'Add: 素晴らしい機能の追加'
   ```
   
   コミットメッセージの規約：
   - `Add:` - 新機能追加
   - `Fix:` - バグ修正
   - `Update:` - 既存機能の更新
   - `Docs:` - ドキュメントのみの変更
   - `Test:` - テストの追加・修正
   - `Refactor:` - リファクタリング

6. **ブランチにプッシュ**
   ```bash
   git push origin feature/amazing-feature
   ```

7. **プルリクエストを作成**
   - 変更内容の詳細な説明を記載
   - 関連するIssue番号を記載（あれば）

## コーディング規約

### Node.js
- [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)に準拠
- ESLintでチェック: `npm run lint`

### Python
- [PEP 8](https://pep8.org/)に準拠
- Black + Flake8でフォーマット: `black . && flake8`

### Java
- [Google Java Style Guide](https://google.github.io/styleguide/javaguide.html)に準拠
- Checkstyleでチェック: `mvn checkstyle:check`

## テスト

すべてのコード変更には適切なテストが必要です：

- **単体テスト**: 新しい関数・メソッドには単体テストを追加
- **統合テスト**: APIエンドポイントには統合テストを追加
- **カバレッジ**: 80%以上のコードカバレッジを維持

## ドキュメント

コードと同様にドキュメントも重要です：

- 新機能にはREADMEを更新
- APIの変更には実装ガイドを更新
- コメントは日本語または英語で記載

## 行動規範

このプロジェクトでは、以下の行動を期待します：

- 敬意を持った丁寧なコミュニケーション
- 建設的なフィードバック
- 多様性の尊重
- 教育技術コミュニティへの貢献

不適切な行動を発見した場合は、プロジェクトメンテナーに報告してください。

## ライセンス

貢献されたコードは、プロジェクトと同じ[MITライセンス](LICENSE)の下でライセンスされます。

## 質問

質問がある場合は、[GitHub Issues](https://github.com/nahisaho/oneroster-gradebook-reference/issues)で質問してください。

---

**あなたの貢献に感謝します！ 🙏**
