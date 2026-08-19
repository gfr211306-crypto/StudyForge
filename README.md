# StudyForge

StudyForge 是一個給學生使用的本機學習網站：

**上傳 PDF → 讀取文字 → 自動挑選重要英文單字 → 顯示中文意思、詞性與原文例句 → 匯出 Anki CSV**

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB)
![Streamlit](https://img.shields.io/badge/Streamlit-1.41%2B-FF4B4B)
![License](https://img.shields.io/badge/License-MIT-green)

## 主要功能

- 使用 **PyMuPDF** 讀取 PDF 文字
- 依出現頻率、跨頁分布、單字難度與學術標籤計算推薦分數
- 使用本機離線英中詞典，並將釋義轉成繁體中文
- 不把 PDF 送到翻譯網站或外部 AI 服務
- 自動合併常見詞形變化，例如 `analyzed` → `analyze`
- 從 PDF 原文挑選適合的例句
- 在網頁表格內編輯單字、詞性、中文意思與例句
- 匯出帶有 UTF-8 BOM 的 Anki 相容 CSV，中文不會亂碼
- 對密碼 PDF、空白 PDF、掃描型 PDF 提供清楚的中文錯誤訊息

## Windows 最簡單的啟動方式

### 第一次使用

1. 安裝 [Python 3.11 或更新版本](https://www.python.org/downloads/)。
2. 安裝時勾選 **Add python.exe to PATH**。
3. 雙擊 `setup.bat`，等待套件安裝完成。

### 每次開啟網站

雙擊 `run.bat`。瀏覽器通常會自動開啟：

```text
http://localhost:8501
```

若沒有自動開啟，請自行在瀏覽器輸入上面的網址。

你也可以先上傳 `samples/StudyForge_demo.pdf`，立即查看範例整理結果。

## 使用終端機安裝

PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
streamlit run app.py
```

macOS / Linux：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
streamlit run app.py
```

## 如何匯入 Anki

1. 在 StudyForge 下載 CSV。
2. 開啟 Anki，選擇「檔案」→「匯入」。
3. 選擇剛下載的 CSV。
4. 第一欄對應 `Front`、第二欄對應 `Back`、第三欄對應 `Tags`。
5. 勾選「允許欄位使用 HTML」。
6. 確認分隔符號為逗號後匯入。

## PDF 限制

StudyForge 適合「文字可以反白選取」的 PDF。若 PDF 是掃描照片，PyMuPDF
無法直接辨識圖片內的文字，請先用 OCR 工具轉成可搜尋 PDF。

- 一般文字型 PDF：支援
- 密碼保護 PDF：請先解除密碼
- 掃描圖片 PDF：需先 OCR
- 單次上傳大小上限：200 MB

## 專案結構

```text
StudyForge/
├─ app.py                         # Streamlit 網站入口
├─ studyforge/
│  ├─ dictionary.py              # 離線詞典查詢
│  ├─ exporter.py                # Anki CSV 匯出
│  ├─ fallback_dictionary.py     # 詞典遺失時的精簡備援
│  ├─ models.py                  # 資料模型
│  ├─ pdf_reader.py              # PyMuPDF 文字擷取
│  └─ vocabulary.py              # 單字分析與排序
├─ data/
│  ├─ studyforge_dictionary.db   # 離線英中詞典
│  ├─ NOTICE.md
│  └─ LICENSE_ECDICT.txt
├─ scripts/
│  └─ build_dictionary.py        # 從 ECDICT 重建詞典
├─ samples/
│  ├─ StudyForge_demo.pdf         # 可直接上傳測試的示範教材
│  └─ StudyForge_demo.txt         # 示範教材原文
├─ tests/                         # 自動化測試
├─ requirements.txt
├─ setup.bat
└─ run.bat
```

## 執行測試

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

也可以檢查所有 Python 檔案是否可編譯：

```powershell
.\.venv\Scripts\python.exe -m compileall app.py studyforge scripts tests
```

## 重建離線詞典

一般使用者不需要執行此步驟。若要從最新版 ECDICT 重建：

```powershell
python scripts/build_dictionary.py data/stardict.csv
```

原始詞典為 [ECDICT](https://github.com/skywind3000/ECDICT)，採 MIT License。
轉換後資料的授權說明位於 `data/NOTICE.md`。

## 隱私

- PDF 由目前執行 Streamlit 的電腦處理。
- 本專案不會主動把 PDF 內容傳到第三方翻譯或 AI API。
- 關閉網站後，上傳內容不會由本專案另存為檔案。

## 授權

本專案程式碼採 [MIT License](LICENSE)。
