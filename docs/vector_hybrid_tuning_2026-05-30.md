# Vector / Hybrid Tuning Notes

## 実行コマンド

```powershell
$env:PYTHONPATH="src"
pytest -q -p no:cacheprovider --basetemp .pytest_tmp
python -m rag_engine.evaluate_vector
python -m rag_engine.build_vector_index --documents-dir hils_rag_sample_docs --database-path data/rag_vector.sqlite3 --document-text-mode title_source_text --chunk-size 800 --chunk-overlap 100
python -m uvicorn rag_engine.main:app --app-dir src --host 127.0.0.1 --port 8000
```

疎通確認:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/backend/query -Method Post -ContentType "application/json" -Body '{"question":"inverter boot sequence のチェックリストは？","top_k":3}'
Invoke-RestMethod http://127.0.0.1:8000/query/hybrid -Method Post -ContentType "application/json" -Body '{"question":"inverter boot sequence のチェックリストは？","top_k":3}'
```

## 変更ファイル

- `.env.example`
- `hils_rag_sample_docs/evaluation_cases.json`
- `src/rag_engine/config.py`
- `src/rag_engine/build_vector_index.py`
- `src/rag_engine/evaluate_vector.py`
- `src/rag_engine/main.py`
- `src/rag_engine/service.py`
- `src/rag_engine/vector_indexer.py`
- `src/rag_engine/vector_storage.py`
- `src/rag_engine/vector_text.py`
- `tests/test_hybrid_backend_contract.py`
- `tests/test_vector_retriever.py`
- `tests/test_vector_text.py`

## 比較結果の要約

- BM25: Top1 1.000 / Top3 1.000
- Vector `text_800`: Top1 0.727 / Top3 0.818
- Vector `title_source_text_800`: Top1 0.909 / Top3 1.000
- Vector `title_source_text_500`: Top1 0.909 / Top3 0.909

結論:

- `title + source_label + text` を連結して埋め込む条件が有効
- 特に `inverter boot sequence のチェックリストは？` と `inverter startup checklist を見たい` のズレを修正
- chunk size を 500 に下げても Top1 は伸びず、Top3 は悪化
- 本番既定値は `title_source_text` / `800` / `100` に設定

## まだ残るズレ

- `インバータの起動手順はどこ？` は metadata 連結条件で Top1 が `html/inverter_boot_sequence_checklist.html` から外れるケースがある
- 500 chunk 条件では同ケースが Top3 からも外れた
- つまり英日混在クエリには metadata 連結が効く一方、純日本語寄りでは `power mode` / `recovery` 系の意味近傍へ吸われる余地が残る
- 次に効きそうなのは、固定長より `見出し単位 + 固定長補助` の chunking
