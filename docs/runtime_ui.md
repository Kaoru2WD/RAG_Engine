# Runtime UI Notes

## 目的

共通 UI で次を切り替える。

- `Inline BM25`
- `Local Vector`
- `Hybrid Server`
- `Admin`

## 表示項目

- 検索結果の Top1 候補
- 想定ソースを選んだ場合の `Top1 PASS / FAIL`
- 応答時間 `elapsed sec`
- `Benchmark` タブでの評価ケース一括確認
- `Admin` タブでのカテゴリ確認
- `Admin` タブでの `forms URL` 入力と manifest プレビュー

## Hybrid 前提

- UI は `http://127.0.0.1:8000/ui`
- ベクトル検索本体は別実装
- こちらは HTTP 契約だけ固定する

## 評価ケース

`hils_rag_sample_docs/evaluation_cases.json` を静的エクスポート時に `search-data.js` へ埋め込む。

## 機密境界

- 公開 UI にはプレースホルダ化済み本文だけを載せる
- 原文チャンクは `chunk-dry-run.json` でハッシュ確認に留める
