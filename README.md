# StudyForge

[![CI](https://github.com/gfr211306-crypto/StudyForge/actions/workflows/ci.yml/badge.svg)](https://github.com/gfr211306-crypto/StudyForge/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/studyforge-vocab.svg)](https://pypi.org/project/studyforge-vocab/)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.61.1-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

StudyForge v0.2.0 是一個可重用的開源 PDF vocabulary toolkit。它提供
Streamlit Web App、CLI 與 Python API，可將英文 PDF 自動整理成可複習、
可編輯並能匯入 Anki 的單字資料：

**PDF → 文字擷取 → 重要英文單字 → 繁體中文釋義／詞性／原文例句 → Anki CSV**

全程不需要 API key，也不會把文件內容送往翻譯或 AI API。

## Quick Start

從正式 PyPI 安裝：

```bash
pip install studyforge-vocab
```

使用 CLI 從 PDF 產生 Anki CSV：

```bash
studyforge extract file.pdf --limit 30 --format anki
```

或在 Python 中使用：

```python
from studyforge import analyze_pdf

result = analyze_pdf("file.pdf", limit=30, mode="ielts")
print(result.items)
```

## Feedback

遇到錯誤或有功能建議時，歡迎使用 GitHub Issues：

- [🐛 Report a bug](https://github.com/gfr211306-crypto/StudyForge/issues/new?template=bug_report.yml)
- [💡 Request a feature](https://github.com/gfr211306-crypto/StudyForge/issues/new?template=feature_request.yml)

提交前請先搜尋是否已有相同 Issue，並避免公開上傳含個資、機密內容或未獲授權的
PDF。

## Live Demo

### 🚀 [立即開啟 StudyForge 公開版](https://studyforge-kpamprbzckvvgx4sz6fxvz.streamlit.app/)

- 公開網址：<https://studyforge-kpamprbzckvvgx4sz6fxvz.streamlit.app/>
- 本機示範：執行 `streamlit run app.py` 後開啟 `http://localhost:8501`
- 示範教材：`samples/StudyForge_demo.pdf`
- Community Cloud 入口檔：`app.py`
- 建議部署 Python：`3.12`

## Features

- 使用 **PyMuPDF** 擷取文字型 PDF 的逐頁內容
- 依出現頻率、跨頁分布、字頻與學術標籤推薦重要單字
- 使用超過 50,000 個詞條的本機離線英中詞典
- 將簡體詞典釋義轉成繁體中文
- 合併常見詞形，例如 `analyzed` → `analyze`
- IELTS vocabulary mode 優先排列詞典中明確標記為 IELTS 的單字
- CEFR A1–C2 分級；來源無法可靠判定時明確標示 `unknown`
- 從 PDF 原文自動挑選例句
- 顯示音標、詞性、中文意思、出現次數與頁碼
- 可在匯出前直接編輯或取消單字
- 支援 Anki CSV、普通 CSV 與 JSON
- 提供 `studyforge extract` CLI
- 提供可供其他 Python 專案 import 的 public API
- 對空白、損壞、密碼保護與掃描型 PDF 提供中文錯誤訊息
- 防護公開部署資源：25 MB、400 頁、2,000,000 個擷取字元上限
- 對 PDF 與使用者輸入進行 HTML escaping
- 使用每個 Streamlit session 獨立的分析結果，不共用使用者 PDF 快取

## Architecture

```mermaid
flowchart LR
    Web[Streamlit Web App] --> API[StudyForge public API]
    CLI[studyforge CLI] --> API
    Python[Other Python projects] --> API
    API --> PDF[PyMuPDF reader]
    API --> Dictionary[Offline ECDICT database]
    API --> CEFR[Reliable partial CEFR profile]
    API --> Ranker[Vocabulary ranking / IELTS mode]
    Ranker --> Exporters[Anki CSV / CSV / JSON exporters]
```

Web、CLI 與 Python API 共用同一套 reader、dictionary、CEFR、ranking 與
exporter，沒有複製三份邏輯。

StudyForge 不使用生成式 AI。中文意思、詞性、音標與詞形資料來自專案內的
離線詞典；例句取自使用者上傳的 PDF。

## Installation

### 系統需求

- Python 3.11 或 3.12（公開部署建議 3.12）
- pip
- Git（只有 clone 或貢獻程式時需要）

### Windows 快速安裝

1. 安裝 [Python](https://www.python.org/downloads/)，並勾選
   **Add python.exe to PATH**。
2. 下載或 clone 此儲存庫。
3. 雙擊 `setup.bat`。
4. 安裝完成後雙擊 `run.bat`。

`run.bat` 會啟動網站並開啟 `http://localhost:8501`。

### 安裝 CLI 與 Python package

從正式 PyPI 安裝：

```bash
python -m pip install studyforge-vocab
```

如果要參與開發，再從原始碼安裝 editable package：

```bash
git clone https://github.com/gfr211306-crypto/StudyForge.git
cd StudyForge
python -m pip install -e .
```

若也要執行 Web App：

```bash
python -m pip install -e ".[web]"
```

### Windows PowerShell

```powershell
git clone https://github.com/gfr211306-crypto/StudyForge.git
cd StudyForge
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
streamlit run app.py
```

### macOS / Linux

```bash
git clone https://github.com/gfr211306-crypto/StudyForge.git
cd StudyForge
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
streamlit run app.py
```

## Usage

### Web App

1. 啟動 StudyForge。
2. 上傳文字可以被反白選取的英文 PDF。
3. 在側邊欄選擇單字數量、難度與最低出現次數。
4. 等待 StudyForge 擷取文字並整理單字。
5. 在表格中修正中文意思、詞性或例句，取消不需要的項目。
6. 選擇 Anki CSV、普通 CSV 或 JSON 後下載。

### CLI

最基本的 Anki 匯出：

```bash
studyforge extract file.pdf --limit 30 --format anki
```

IELTS mode 與 JSON：

```bash
studyforge extract file.pdf \
  --mode ielts \
  --limit 50 \
  --format json \
  --output ielts-vocabulary.json
```

支援的選項：

```text
--mode balanced|basic|intermediate|advanced|ielts
--format anki|csv|json
--limit 1-500
--min-occurrences 1-100
--output FILE
```

未指定 `--output` 時，CLI 會在目前目錄建立
`<pdf-name>_<format>.csv` 或 `.json`。使用 `--output -` 可輸出至 stdout。

也可以不安裝 console script：

```bash
python -m studyforge extract file.pdf --format csv
```

### Python API

```python
from studyforge import StudyForge, analyze_pdf, export_vocabulary

# Convenience function
result = analyze_pdf(
    "file.pdf",
    limit=30,
    mode="ielts",
)

for item in result.items:
    print(item.word, item.cefr_level, item.is_ielts)

anki_bytes = export_vocabulary(result.items, "anki")
json_bytes = export_vocabulary(result.items, "json")

# Reuse one service instance for multiple PDFs
engine = StudyForge()
another_result = engine.analyze_file("another.pdf", mode="balanced")
```

主要 public API：

```text
StudyForge
analyze_pdf
analyze_pdf_bytes
AnalysisResult
VocabularyItem
CEFRProfile
export_vocabulary
export_rows
```

### 匯入 Anki

1. 在 Anki 選擇 **檔案 → 匯入**。
2. 選擇 StudyForge 下載的 CSV。
3. 對應欄位：`Front`、`Back`、`Tags`。
4. 勾選允許欄位使用 HTML。
5. 確認分隔符號為逗號後匯入。

### PDF 限制

| 類型 | 支援狀態 |
| --- | --- |
| 一般文字型 PDF | 支援 |
| 密碼保護 PDF | 請先解除密碼 |
| 掃描圖片 PDF | 請先使用 OCR |
| 超過 25 MB | 請先壓縮或分割 |
| 超過 400 頁 | 請先分割 |

## Streamlit Community Cloud deployment

本儲存庫已符合 Community Cloud 的基本檔案配置：

```text
app.py
requirements.txt
.streamlit/config.toml
studyforge/data/studyforge_dictionary.db
studyforge/data/cefr_levels.json
```

部署時使用：

| 設定 | 值 |
| --- | --- |
| Repository | `gfr211306-crypto/StudyForge` |
| Branch | `main` |
| Main file path | `app.py` |
| Python version | `3.12` |
| Secrets | 不需要 |

`requirements.txt` 只包含網站執行依賴；pytest 位於
`requirements-dev.txt`，不會增加 Community Cloud 的部署負擔。

## Testing

先安裝開發依賴：

```bash
python -m pip install -r requirements-dev.txt
```

執行完整檢查：

```bash
python -m pip check
python scripts/audit_repository.py
python -m pytest -q
python -m compileall -q app.py studyforge scripts tests
```

GitHub Actions 會在每次 push、pull request 與手動觸發時，於 Python 3.11
及 3.12 執行相同的依賴檢查、儲存庫掃描、pytest、編譯檢查、package
build 與 CLI smoke test。

建立 wheel 與 source distribution：

```bash
python -m build
```

## Project structure

```text
StudyForge/
├─ .github/
│  ├─ ISSUE_TEMPLATE/             # Bug 與功能建議表單
│  ├─ workflows/ci.yml            # GitHub Actions CI
│  └─ dependabot.yml
├─ .streamlit/config.toml         # Streamlit 公開部署設定
├─ app.py                         # Streamlit 入口檔
├─ data/
│  ├─ NOTICE.md
│  ├─ NOTICE_CEFR.md
│  └─ LICENSE_ECDICT.txt
├─ samples/                       # 可直接上傳測試的教材
├─ scripts/
│  ├─ audit_repository.py         # 敏感檔案與秘密掃描
│  ├─ build_cefr_data.py           # 重建可靠 CEFR mapping
│  └─ build_dictionary.py         # 從 ECDICT 重建詞典
├─ studyforge/
│  ├─ api.py                       # Web／CLI 共用 public API
│  ├─ cli.py                       # studyforge extract
│  ├─ cefr.py                      # CEFR 查詢與 unknown policy
│  ├─ exporter.py                  # Anki CSV／CSV／JSON
│  ├─ vocabulary.py                # 排序與 IELTS mode
│  └─ data/                        # wheel 內含詞典與 CEFR mapping
├─ tests/                         # pytest 測試
├─ pyproject.toml                 # PyPI package metadata
├─ CONTRIBUTING.md
├─ SECURITY.md
├─ requirements.txt              # 公開部署執行依賴
└─ requirements-dev.txt          # 開發與測試依賴
```

## Privacy and security

- **本機執行：** PDF 只在你的電腦處理。
- **公開部署：** PDF 會傳送至執行 StudyForge 的 Streamlit 伺服器。
- PDF 不會被送往外部翻譯服務或 AI API。
- 專案不會主動把 PDF 或擷取文字寫入永久檔案。
- 分析結果只保留於目前使用者的 Streamlit session。
- 公開部署不適合機密、醫療、法律或含大量個資的文件。
- 回報問題時，請勿把真實敏感 PDF 上傳到公開 GitHub Issue。

安全問題請參閱 [SECURITY.md](SECURITY.md)。

## Contributing

歡迎 Bug 修正、測試、文件與功能改善。開始前請閱讀
[CONTRIBUTING.md](CONTRIBUTING.md)，並使用專案提供的 Issue templates。

基本流程：

1. Fork 儲存庫並建立功能分支。
2. 安裝 `requirements-dev.txt`。
3. 修改程式並補充測試。
4. 通過完整測試與 repository audit。
5. 建立內容聚焦的 Pull Request。

參與者請遵守 [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)。

## Roadmap

- [x] PDF 文字擷取
- [x] 離線英中詞典與繁體中文轉換
- [x] 原文例句與 Anki CSV
- [x] GitHub Actions、Issue forms 與公開部署設定
- [x] IELTS vocabulary mode
- [x] CEFR A1–C2 可靠部分映射與 `unknown`
- [x] CLI、Python API、普通 CSV 與 JSON
- [x] 可建立 wheel 與 source distribution 的 `pyproject.toml`
- [ ] OCR 掃描型 PDF 支援
- [ ] 使用者自訂停用詞
- [ ] 單字清單去重與手動新增功能
- [ ] 更多 Anki 卡片模板
- [ ] 無障礙與手機版操作改善
- [ ] 多語言介面

## Vocabulary data and CEFR policy

離線詞典由 [ECDICT](https://github.com/skywind3000/ECDICT) 資料篩選轉換而成。
詞典來源與授權說明請見 [data/NOTICE.md](data/NOTICE.md) 與
[data/LICENSE_ECDICT.txt](data/LICENSE_ECDICT.txt)。

CEFR mapping 由 CEFR-J 1.5 與 Octanove C1/C2 1.0 建置。StudyForge 只保留
同一 normalized headword 在來源中一致的級別；若不同詞性或語義對應不同級別，
就不做猜測並輸出 `unknown`。目前 bundled mapping 有約 7,900 個無歧義詞條。
來源、授權與處理規則請見 [data/NOTICE_CEFR.md](data/NOTICE_CEFR.md)。

## License

StudyForge 程式碼採 [MIT License](LICENSE)。

第三方詞典資料保留其原始 MIT 授權與版權聲明。
