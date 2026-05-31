# Next Steps

## Current State

- `Inline BM25` / `Local Vector` / `Hybrid Server` を共通 UI で切替可能
- UI: [web/index.html](/C:/Users/Kaoru/Documents/RAG_Engine/web/index.html)
- main app: [src/rag_engine/main.py](/C:/Users/Kaoru/Documents/RAG_Engine/src/rag_engine/main.py)
- service: [src/rag_engine/service.py](/C:/Users/Kaoru/Documents/RAG_Engine/src/rag_engine/service.py)
- hybrid backend の既定値は `http://127.0.0.1:8000/backend/query`
- vector 既定値は `title_source_text` / `800` / `100`

## Confirmed Behavior

- fresh start で 3 系統とも起動と疎通は確認済み
- query: `inverter boot sequence のチェックリストは？`
  - `Inline BM25` Top1: `html\inverter_boot_sequence_checklist.html`
  - `Local Vector` は tuning 後に改善済み
  - `Hybrid Server` は `/backend/query` 既定 backend で疎通済み
- vector 評価ケースは 11 件
- summary:
  - BM25: Top1 `1.000` / Top3 `1.000`
  - Vector `text_800`: Top1 `0.727` / Top3 `0.818`
  - Vector `title_source_text_800`: Top1 `0.909` / Top3 `1.000`
  - Vector `title_source_text_500`: Top1 `0.909` / Top3 `0.909`
  - Vector `title_source_text_heading`: Top1 `0.909` / Top3 `0.909`

## Open Tasks

- 見出し単位 chunking の一次比較は実施済み
- `title_source_text_heading` は `title_source_text_800` を上回らなかった
- `インバータの起動手順はどこ？` のような純日本語寄り query での vector 残差を詰める
- 次候補は見出し分割より、query-side expansion / 同義語辞書 / 日本語寄りメタデータ付与
- Benchmark タブ上で BM25 / Local Vector / Hybrid を継続比較する
- カテゴリ機能を実装する
  - 文書に `カテゴリ` `装置系統` `工程` などのメタデータを持たせる
  - UI でカテゴリ絞り込みとカテゴリ表示を追加する
  - 将来の package / launcher 側でもカテゴリ単位で配布物を切り分けられるようにする
- エンドユーザー向けに `手順書作成依頼フォーム` へのリンクを実装する
  - UI 上から不足文書の依頼導線へ飛べるようにする
  - 将来は `検索ヒットなし` や `期待手順なし` の時に自然に誘導できる位置へ置く
  - URL は設定値または manifest から差し替え可能にする

## Useful Files

- [hils_rag_sample_docs/evaluation_cases.json](/C:/Users/Kaoru/Documents/RAG_Engine/hils_rag_sample_docs/evaluation_cases.json)
- [README.md](/C:/Users/Kaoru/Documents/RAG_Engine/README.md)
- [docs/runtime_ui.md](/C:/Users/Kaoru/Documents/RAG_Engine/docs/runtime_ui.md)
- [docs/vector_hybrid_tuning_2026-05-30.md](/C:/Users/Kaoru/Documents/RAG_Engine/docs/vector_hybrid_tuning_2026-05-30.md)
- [data/vector_eval_report.json](/C:/Users/Kaoru/Documents/RAG_Engine/data/vector_eval_report.json)

## Snapshot

- [archive/rag_engine_snapshot_2026-05-30_212025.zip](/C:/Users/Kaoru/Documents/RAG_Engine/archive/rag_engine_snapshot_2026-05-30_212025.zip)
