from rag_engine.models import RetrievalHit


def compose_answer(question: str, hits: list[RetrievalHit]) -> str:
    if not hits:
        return (
            f"質問: {question}\n"
            "関連資料は見つからなかった。語彙の揺れ、文書未登録、抽出失敗の可能性がある。"
        )

    top_hit = hits[0]
    evidence = top_hit.text[:240]
    return (
        f"最上位候補は `{top_hit.title}` だ。\n"
        f"該当箇所要約: {evidence}\n"
        "これは自動判断ではなく、検索結果上位チャンクの提示である。原文確認を前提に使うこと。"
    )
