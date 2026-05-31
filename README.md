# HILS RAG Portfolio Rebuild

HILS 運用向けに実務で構築した手順書 RAG を、機密情報を含まない形で再構築するポートフォリオ用リポジトリ。

## 目的

- 分散した手順書を横断検索できる状態を再現する
- 「AI を使うべき部分」と「AI を使わない部分」の設計境界を示す
- HILS の運用課題に対して、検索品質・更新管理・説明性を優先した実装を提示する

## この MVP で扱う範囲

- ローカルフォルダを SharePoint 同期先の代替として取り込む
- `PDF` `Word` `Excel` `HTML` `Markdown` `Text` をテキスト抽出する
- 文字数ベースのチャンク化を行う
- SQLite FTS5 を使った軽量全文検索を行う
- 同じチャンクを別トラックで vector-style SQLite DB に積める
- FastAPI 経由で検索 API を提供する
- Retrieval 評価の雛形を用意する

## あえて入れていないもの

- 会社固有の SharePoint 接続情報
- 社外秘・個人情報を含む実データ
- 複雑な Agent 構成
- 先に VectorDB を前提にした過剰設計

この構成にしている理由は、実運用で効いたのが高度な RAG テクニックよりも、文書整備・命名・更新管理・検索可能状態の確立だったため。

## ディレクトリ

```text
.
├─ docs/                 設計・評価ドキュメント
├─ sample_data/          ポートフォリオ用のダミー手順書
├─ src/rag_engine/       アプリ本体
├─ tests/                最小テスト
└─ pyproject.toml
```

## セットアップ

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .[dev]
```

## 起動

```powershell
python -m uvicorn rag_engine.main:app --app-dir src --reload
```

または、`src/` レイアウトを使うため以下でもよい。

```powershell
python -m uvicorn rag_engine.main:app --app-dir src --reload
```

## 静的 HTML BM25 デモ

文書本体を別工程で用意し、こちらでは検索 UI を単体 HTML として見せたい場合のために、
`web/index.html` を用意してある。BM25 は HTML 内の JavaScript で計算し、文書抽出とチャンク化は Python で前処理する。
公開物にはプレースホルダ化済みチャンクだけを載せ、原文チャンクはドライランでのみ扱う。
既定の取り込み元は `hils_rag_sample_docs/`。

### 検索データ生成

```powershell
$env:PYTHONPATH="src"
python -m rag_engine.export_static --forms-url https://example.com/forms/procedure-request
```

これで以下が再生成される。

- `web/chunk-dry-run.json`
- `web/search-data.js`

`chunk-dry-run.json` には原文のハッシュと件数だけを残す。生チャンク本文は保存しない。
`search-data.js` には `source_url` を含めるため、HTML から元ドキュメントをすぐ開ける。
`--forms-url` を付けると、`Admin` タブの既定値と manifest プレビューにも埋め込まれる。

## ローカル ベクトルDB

BM25 とは別に、同じ文書群からベクトル型チャンク DB を `data/rag_vector.sqlite3` へ作れる。

```powershell
$env:PYTHONPATH="src"
python -m rag_engine.build_vector_index
```

実装方針:

- まず Ollama `http://127.0.0.1:11434/api/embed` を試す
- 現在のモデルが embeddings 非対応なら、自動でローカル hash vectorizer にフォールバックする
- そのため DB 構築は止まりにくいが、意味検索の質は使用モデルに依存する

API から使う場合は、ベクトル索引を先に再構築して `engine=vector` を指定する。

```powershell
curl -X POST http://127.0.0.1:8000/index/rebuild-vector

curl -X POST http://127.0.0.1:8000/query `
  -H "Content-Type: application/json" `
  -d "{\"question\":\"PRECHARGE stall の確認項目は？\",\"top_k\":3,\"engine\":\"vector\"}"
```

### プレースホルダ管理

`placeholder_rules.example.json` を複製して、実データ向けの置換ルール JSON を用意する。

```json
{
  "rules": [
    {
      "key": "ecu_name",
      "placeholder": "{{ECU_NAME}}",
      "values": ["実際のECU名"]
    }
  ]
}
```

生成時に `values` が `placeholder` へ置換され、その凡例も HTML に埋め込まれる。

### 検索演算子

- `+term` : 必須語
- `-term` : 除外語
- `"phrase"` : フレーズ一致
- `source:value` : 出典ラベル絞り込み
- `title:value` : タイトル絞り込み

日本語の助詞はトークナイザで無視する。

### 表示

共通 UI はサーバ配信前提なので、`http://127.0.0.1:8000/ui` から開く。
検索結果は画面下部のプロンプト欄から Copilot / Gemini サイドバーに貼り付けて、自然言語の回答整形へ回せる。
`Sources` タブにはチャンク化したソース一覧を保持し、各文書を `開く` ボタンから直接参照できる。
`Admin` タブでは、カテゴリ推定の確認、手順書作成依頼フォーム URL の入力、manifest プレビューとダウンロードができる。

## 検索 UI

共通 UI のまま、次を切り替えられる。

- `Inline BM25`
- `Local Vector`
- `Hybrid Server`

`Local Vector` は `data/rag_vector.sqlite3` を使うローカル vector 検索。
`Hybrid Server` はローカル FastAPI を経由して、外部のベクトル検索バックエンドへ問い合わせる。

### 起動

```powershell
.\start_hils_search.ps1
```

または

```powershell
python -m uvicorn rag_engine.main:app --app-dir src --host 127.0.0.1 --port 8000
```

その後 [http://127.0.0.1:8000/ui](http://127.0.0.1:8000/ui) を開く。

### Local Vector index build

```powershell
$env:PYTHONPATH="src"
python -m rag_engine.build_vector_index --documents-dir hils_rag_sample_docs --database-path data/rag_vector.sqlite3
```

### Hybrid backend contract

CLI 側のベクトルチャンク化・埋め込み索引は別実装でよい。こちらが期待するのは HTTP API 契約だけだ。

リクエスト:

```json
{
  "question": "CAN通信異常時の確認項目は？",
  "top_k": 8
}
```

レスポンス例:

```json
{
  "answer": "",
  "backend_status": "connected",
  "hits": [
    {
      "document_ref": "DOC-001",
      "source_path": "C:/path/to/doc.md",
      "source_url": "file:///C:/path/to/doc.md",
      "source_label": "md/doc.md",
      "title": "doc",
      "file_type": "md",
      "chunk_index": 0,
      "score": 0.91,
      "text": "検索ヒット本文",
      "placeholder_keys": []
    }
  ]
}
```

`source_path` か `source_url` のどちらかは返す方がよい。ローカル文書と一致すれば、こちらで `document_ref` や `source_url` を補完する。

## 代表 API

### インデックス再構築

```powershell
curl -X POST http://127.0.0.1:8000/index/rebuild
```

### 検索

```powershell
curl -X POST http://127.0.0.1:8000/query `
  -H "Content-Type: application/json" `
  -d "{\"question\":\"CAN通信異常時の確認項目は？\",\"top_k\":3}"
```

## 評価

```powershell
$env:PYTHONPATH="src"
python -m rag_engine.evaluate
```

## ドキュメント

- [docs/index.md](/C:/Users/Kaoru/Documents/RAG_Engine/docs/index.md)
- [docs/architecture.md](/C:/Users/Kaoru/Documents/RAG_Engine/docs/architecture.md)
- [docs/evaluation.md](/C:/Users/Kaoru/Documents/RAG_Engine/docs/evaluation.md)
- [docs/runtime_ui.md](/C:/Users/Kaoru/Documents/RAG_Engine/docs/runtime_ui.md)
- [docs/package_distribution.md](/C:/Users/Kaoru/Documents/RAG_Engine/docs/package_distribution.md)

## アーキテクチャ要点

- `同期` と `検索` を分離し、機密依存を repo 外へ追い出す
- `検索` はまず SQLite FTS5 を主軸にし、軽量・高速・説明性を優先する
- `回答生成` は retrieval の上に乗る後段として扱い、検索根拠を常に返す
- Embedding/VectorDB は差し替え可能だが、最初から主役にはしない

詳細は [docs/architecture.md](/C:/Users/Kaoru/Documents/RAG_Engine/docs/architecture.md) を参照。

## Exe 配布

ローカルサーバを同梱起動する Windows 用ランチャー exe を作れる。今回は `onedir` を既定にしている。
理由は、`source_url` から元文書を開く導線を壊しにくく、複数 RAG package 同居時の実体確認もしやすいため。

### Build

```powershell
pip install -e .[build]
$env:PYTHONPATH="src"
python -m rag_engine.build_exe
```

生成先:

- `dist/HILSRAGLauncher/HILSRAGLauncher.exe`

### Launch

```powershell
dist\HILSRAGLauncher\HILSRAGLauncher.exe
```

初回起動では、ローカル `%LOCALAPPDATA%\RAGEngine\packages\hils-procedure-rag\data\` に
BM25 / vector の索引が無ければ自動再構築する。

保存先を固定したい場合は `RAG_ENGINE_STORAGE_ROOT` で上書きできる。

### Smoke Test

```powershell
dist\HILSRAGLauncher\HILSRAGLauncher.exe --smoke-test --no-browser --port 8012
```

`/health` 到達まで確認して正常終了すれば、同梱サーバの初動は通っている。
