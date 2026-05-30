# Package Distribution

## Why

利用者へ `html 1 枚` を直接配る方式は軽いが、以下で詰まりやすい。

- 配布済みパッケージが複数ある
- 会社配布版とローカル作成版が同居する
- 利用者が手元の版が古いことに気づけない

そのため、配布単位を `package` として識別し、Exe ランチャーまたは将来の配布マネージャから扱える前提を置く。

## Core Concepts

### `package_id`

各 RAG パッケージの一意識別子。

例:

- `hils-procedure-rag`
- `bench-troubleshooting-rag`
- `local-sandbox-rag`

### `channel`

同じ用途でも由来を分ける。

- `company`
- `team-beta`
- `local`
- `archive`

### `storage_root`

ローカル保存先は `package_id` ごとに分ける。

例:

```text
%LOCALAPPDATA%/RAGEngine/packages/hils-procedure-rag/
%LOCALAPPDATA%/RAGEngine/packages/local-sandbox-rag/
```

### `manifest`

`package` の身分証。version だけでなく hash, entrypoint, engine modes を持つ。

## Launcher Model

Exe 配布を前提にする場合、最も運用しやすいのは `1 Exe = 複数 package ランチャー` 方式。

最低限ほしい表示:

- package 一覧
- `display_name`
- `channel`
- `version`
- 更新有無
- `開く`

利用者向けには `company` と `local` を同列表示しない方が安全。

## Update Check

利用者側は `installed manifest` と `latest manifest` の比較で更新通知を出す。

優先順位:

1. `package_hash`
2. `data_hash`
3. `version`

判定文言例:

- `アプリ更新があります`
- `文書データ更新があります`

## Files Added Here

- [distribution/package-manifest.example.json](/C:/Users/Kaoru/Documents/RAG_Engine/distribution/package-manifest.example.json)
- [distribution/launcher-registry.example.json](/C:/Users/Kaoru/Documents/RAG_Engine/distribution/launcher-registry.example.json)
- [src/rag_engine/package_manifest.py](/C:/Users/Kaoru/Documents/RAG_Engine/src/rag_engine/package_manifest.py)
- [src/rag_engine/build_release_manifest.py](/C:/Users/Kaoru/Documents/RAG_Engine/src/rag_engine/build_release_manifest.py)

## Next Natural Step

`build_release_manifest.py` を release zip 生成とつなぎ、`latest-manifest.json` を自動生成する。
