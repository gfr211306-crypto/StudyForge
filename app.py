from __future__ import annotations

import hashlib
import logging
import re
import uuid
from pathlib import Path

import pandas as pd
import streamlit as st

from studyforge.dictionary import DictionaryStore
from studyforge.exporter import build_anki_csv
from studyforge.pdf_reader import (
    MAX_PDF_BYTES,
    MAX_PDF_PAGES,
    PdfReadError,
    extract_pdf_text,
)
from studyforge.presentation import build_word_card_html
from studyforge.vocabulary import LEVEL_LABELS, analyze_vocabulary


APP_ROOT = Path(__file__).resolve().parent
DICTIONARY_PATH = APP_ROOT / "data" / "studyforge_dictionary.db"
LOGGER = logging.getLogger("studyforge")


def apply_theme() -> None:
    st.markdown(
        """
        <style>
        :root {
            --ink: #17212b;
            --muted: #607080;
            --brand: #4f46e5;
            --brand-soft: #eef2ff;
            --mint: #0f9f7f;
            --paper: #fbfcff;
        }
        .stApp {
            background:
                radial-gradient(circle at 8% 0%, rgba(79, 70, 229, .10), transparent 24rem),
                radial-gradient(circle at 95% 10%, rgba(15, 159, 127, .10), transparent 22rem),
                var(--paper);
        }
        .block-container {
            max-width: 1120px;
            padding-top: 2.2rem;
            padding-bottom: 4rem;
        }
        .hero {
            padding: 1.2rem 0 1.4rem;
        }
        .eyebrow {
            display: inline-flex;
            align-items: center;
            gap: .45rem;
            color: var(--brand);
            background: var(--brand-soft);
            border: 1px solid #dfe3ff;
            border-radius: 999px;
            padding: .36rem .72rem;
            font-weight: 700;
            font-size: .82rem;
            letter-spacing: .02em;
        }
        .hero h1 {
            color: var(--ink);
            font-size: clamp(2.35rem, 5vw, 4.5rem);
            line-height: .98;
            letter-spacing: -.055em;
            margin: 1rem 0 .85rem;
        }
        .hero p {
            color: var(--muted);
            font-size: 1.08rem;
            max-width: 720px;
            line-height: 1.7;
        }
        .step-card {
            height: 100%;
            border: 1px solid rgba(96, 112, 128, .17);
            border-radius: 18px;
            padding: 1rem 1.05rem;
            background: rgba(255, 255, 255, .78);
            box-shadow: 0 12px 34px rgba(23, 33, 43, .05);
        }
        .step-number {
            color: var(--brand);
            font-weight: 800;
            font-size: .78rem;
            text-transform: uppercase;
            letter-spacing: .08em;
        }
        .step-title {
            color: var(--ink);
            font-weight: 750;
            margin-top: .3rem;
        }
        div[data-testid="stMetric"] {
            background: rgba(255,255,255,.78);
            border: 1px solid rgba(96,112,128,.16);
            padding: .9rem 1rem;
            border-radius: 16px;
        }
        div[data-testid="stFileUploader"] section {
            border: 1.5px dashed rgba(79,70,229,.42);
            background: rgba(238,242,255,.55);
            border-radius: 18px;
            padding: 1rem;
        }
        .word-card {
            border: 1px solid rgba(96,112,128,.17);
            border-left: 4px solid var(--brand);
            border-radius: 14px;
            padding: .9rem 1rem;
            margin: .55rem 0;
            background: rgba(255,255,255,.82);
        }
        .word-card strong {
            color: var(--ink);
            font-size: 1.08rem;
        }
        .word-meta {
            color: var(--mint);
            font-size: .88rem;
            font-weight: 650;
        }
        .word-example {
            color: var(--muted);
            margin-top: .35rem;
            line-height: 1.55;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_resource(show_spinner=False)
def get_dictionary(path: str) -> DictionaryStore:
    return DictionaryStore(Path(path))


def process_pdf(
    file_bytes: bytes,
    max_words: int,
    level: str,
    min_occurrences: int,
    dictionary_path: str,
):
    document = extract_pdf_text(file_bytes)
    dictionary = get_dictionary(dictionary_path)
    words = analyze_vocabulary(
        document,
        dictionary,
        limit=max_words,
        level=level,
        min_occurrences=min_occurrences,
    )
    return document, words


def safe_download_name(original_name: str) -> str:
    stem = Path(original_name).stem[:80]
    safe_stem = re.sub(r"[^\w.-]+", "_", stem, flags=re.UNICODE).strip("._")
    return f"{safe_stem or 'studyforge'}_anki.csv"


def result_dataframe(words) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "加入 Anki": True,
                "英文單字": item.word,
                "音標": item.phonetic,
                "詞性": item.part_of_speech,
                "中文意思": item.translation,
                "PDF 例句": item.example,
                "出現次數": item.count,
                "頁碼": item.page_label,
            }
            for item in words
        ]
    )


def main() -> None:
    st.set_page_config(
        page_title="StudyForge｜PDF 英文單字整理器",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    apply_theme()

    st.markdown(
        """
        <div class="hero">
          <span class="eyebrow">✦ PDF → VOCABULARY → ANKI</span>
          <h1>把教材，鍛造成<br>真正記得住的單字卡。</h1>
          <p>
            上傳英文 PDF，StudyForge 會讀取內文、找出值得學習的單字，
            補上中文意思與詞性，並從原文擷取例句。確認後即可匯出成 Anki 相容 CSV。
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    steps = [
        ("STEP 01", "上傳 PDF", "支援一般文字型 PDF"),
        ("STEP 02", "自動整理", "依出現頻率與難度排序"),
        ("STEP 03", "檢查編輯", "所有欄位都能自行調整"),
        ("STEP 04", "匯入 Anki", "下載 UTF-8 CSV 單字卡"),
    ]
    columns = st.columns(4)
    for column, (number, title, detail) in zip(columns, steps):
        with column:
            st.markdown(
                f"""
                <div class="step-card">
                  <div class="step-number">{number}</div>
                  <div class="step-title">{title}</div>
                  <div style="color:#607080;font-size:.88rem;margin-top:.25rem">{detail}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("")
    with st.sidebar:
        st.header("整理設定")
        max_words = st.slider("單字數量", min_value=10, max_value=80, value=30, step=5)
        level_label = st.selectbox(
            "單字難度",
            options=list(LEVEL_LABELS.values()),
            index=0,
            help="「綜合推薦」最適合第一次使用。",
        )
        level = next(key for key, value in LEVEL_LABELS.items() if value == level_label)
        min_occurrences = st.select_slider(
            "最低出現次數",
            options=[1, 2, 3, 4, 5],
            value=1,
            help="短篇 PDF 建議設為 1；長篇教材可提高到 2 或 3。",
        )
        st.divider()
        st.caption(
            "🔒 PDF 只會傳送到目前執行 StudyForge 的伺服器處理，"
            "不會送往翻譯或 AI API。若使用公開部署，請勿上傳機密文件。"
        )
        dictionary = get_dictionary(str(DICTIONARY_PATH))
        if dictionary.using_fallback:
            st.warning("目前使用精簡內建詞典。重新執行安裝腳本可建立完整版離線詞典。")
        else:
            st.success(f"離線詞典已就緒：{dictionary.entry_count:,} 個詞條")

    st.subheader("上傳教材")
    uploaded_file = st.file_uploader(
        "拖曳 PDF 到這裡，或點擊選擇檔案",
        type=["pdf"],
        accept_multiple_files=False,
        help=(
            f"上限 {MAX_PDF_BYTES // (1024 * 1024)} MB、{MAX_PDF_PAGES} 頁。"
            "目前僅處理內含可選取文字的 PDF；掃描圖片型 PDF 需要先做 OCR。"
        ),
    )

    if uploaded_file is None:
        st.session_state.pop("analysis_key", None)
        st.session_state.pop("analysis_result", None)
        st.info("請先上傳一份英文 PDF。你的整理結果會顯示在這裡。", icon="👆")
        with st.expander("哪些 PDF 最適合？"):
            st.markdown(
                """
                - 英文講義、課本章節、研究文章、閱讀測驗
                - 文字可以用滑鼠反白選取的 PDF
                - 若是掃描圖片，請先使用 OCR 工具轉成可搜尋文字
                """
            )
        return

    file_bytes = uploaded_file.getvalue()
    file_hash = hashlib.sha256(file_bytes).hexdigest()
    analysis_key = (file_hash, max_words, level, min_occurrences)

    try:
        if (
            st.session_state.get("analysis_key") != analysis_key
            or "analysis_result" not in st.session_state
        ):
            st.session_state.pop("analysis_key", None)
            st.session_state.pop("analysis_result", None)
            with st.spinner("正在閱讀 PDF 並整理重要單字…"):
                result = process_pdf(
                    file_bytes,
                    max_words,
                    level,
                    min_occurrences,
                    str(DICTIONARY_PATH),
                )
            st.session_state["analysis_key"] = analysis_key
            st.session_state["analysis_result"] = result
        document, words = st.session_state["analysis_result"]
    except PdfReadError as exc:
        st.error(str(exc), icon="⚠️")
        return
    except Exception:
        error_id = uuid.uuid4().hex[:8]
        LOGGER.exception("Unhandled PDF processing error [%s]", error_id)
        st.error(
            "處理 PDF 時發生未預期錯誤。請換一份 PDF 再試一次。"
            f"若問題持續發生，請在回報時附上錯誤代碼：{error_id}",
            icon="⚠️",
        )
        return

    if not words:
        st.warning(
            "讀到了 PDF 文字，但找不到符合目前條件的英文單字。"
            "請把「最低出現次數」調成 1，或改用「綜合推薦」。"
        )
        return

    st.success(f"完成！已整理出 {len(words)} 個學習單字。")
    metric_columns = st.columns(4)
    metric_columns[0].metric("PDF 頁數", document.page_count)
    metric_columns[1].metric("英文詞數", f"{document.english_word_count:,}")
    metric_columns[2].metric("擷取字元", f"{len(document.full_text):,}")
    metric_columns[3].metric("推薦單字", len(words))

    st.subheader("檢查與編輯")
    st.caption("你可以直接修改中文意思、詞性或例句，也可以取消不想匯出的單字。")
    edited_df = st.data_editor(
        result_dataframe(words),
        hide_index=True,
        use_container_width=True,
        height=min(650, 90 + len(words) * 35),
        column_config={
            "加入 Anki": st.column_config.CheckboxColumn(width="small"),
            "英文單字": st.column_config.TextColumn(required=True, width="medium"),
            "音標": st.column_config.TextColumn(width="small"),
            "詞性": st.column_config.TextColumn(width="small"),
            "中文意思": st.column_config.TextColumn(required=True, width="large"),
            "PDF 例句": st.column_config.TextColumn(width="large"),
            "出現次數": st.column_config.NumberColumn(disabled=True, width="small"),
            "頁碼": st.column_config.TextColumn(disabled=True, width="small"),
        },
        disabled=["出現次數", "頁碼"],
        key=f"vocabulary_editor_{file_hash}_{level}_{max_words}_{min_occurrences}",
    )

    selected_df = edited_df[edited_df["加入 Anki"] == True].copy()  # noqa: E712
    csv_data = build_anki_csv(selected_df.to_dict(orient="records"))
    download_name = safe_download_name(uploaded_file.name)

    action_left, action_right = st.columns([1, 2])
    with action_left:
        st.download_button(
            "⬇️ 下載 Anki CSV",
            data=csv_data,
            file_name=download_name,
            mime="text/csv",
            use_container_width=True,
            disabled=selected_df.empty,
        )
    with action_right:
        st.info(
            f"目前會匯出 **{len(selected_df)}** 張卡片。"
            "匯入 Anki 時，欄位依序選擇 Front、Back、Tags，並勾選允許 HTML。",
            icon="💡",
        )

    with st.expander("預覽單字卡"):
        for row in selected_df.head(10).to_dict(orient="records"):
            st.markdown(
                build_word_card_html(row),
                unsafe_allow_html=True,
            )
        if len(selected_df) > 10:
            st.caption(f"此處只預覽前 10 張；CSV 會包含全部 {len(selected_df)} 張。")

    with st.expander("查看擷取出的 PDF 文字"):
        st.text_area(
            "文字預覽",
            value=document.full_text[:12000],
            height=280,
            disabled=True,
            label_visibility="collapsed",
        )


if __name__ == "__main__":
    main()
