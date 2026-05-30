# Next Steps

## Current State

- `Inline BM25` / `Local Vector` / `Hybrid Server` を共通 UI で切替可能
- UI: [web/index.html](/C:/Users/Kaoru/Documents/RAG_Engine/web/index.html)
- main app: [src/rag_engine/main.py](/C:/Users/Kaoru/Documents/RAG_Engine/src/rag_engine/main.py)
- service: [src/rag_engine/service.py](/C:/Users/Kaoru/Documents/RAG_Engine/src/rag_engine/service.py)

## Confirmed Behavior

- fresh start で 3 系統とも起動と疎通は確認済み
- query: `inverter boot sequence のチェックリストは？`
  - `Inline BM25` Top1: `html\inverter_boot_sequence_checklist.html`
  - `Local Vector` Top1: `md\hils_power_mode_transition_notes.md`
  - `Hybrid Server` Top1: `md\hils_power_mode_transition_notes.md`

## Open Tasks

- CLI 側で `Hybrid backend` を本番相当 API 契約に合わせる
- `hils_rag_sample_docs/evaluation_cases.json` に表記ゆれ比較ケースを追加
- vector 側で以下を比較
  - 本文のみ埋め込み
  - `title + source_label + text` 埋め込み
  - chunk size 縮小

## Useful Files

- [hils_rag_sample_docs/evaluation_cases.json](/C:/Users/Kaoru/Documents/RAG_Engine/hils_rag_sample_docs/evaluation_cases.json)
- [README.md](/C:/Users/Kaoru/Documents/RAG_Engine/README.md)
- [docs/runtime_ui.md](/C:/Users/Kaoru/Documents/RAG_Engine/docs/runtime_ui.md)

## Snapshot

- [archive/rag_engine_snapshot_2026-05-30_212025.zip](/C:/Users/Kaoru/Documents/RAG_Engine/archive/rag_engine_snapshot_2026-05-30_212025.zip)
