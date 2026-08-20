# Contributing to StudyForge

感謝你願意改善 StudyForge。無論是修正錯誤、補充測試、改善文件或提出學習功能，
都歡迎透過 Issue 與 Pull Request 參與。

## 開始之前

1. 先搜尋現有 Issues 與 Pull Requests。
2. Bug 請使用 Bug Report；功能建議請使用 Feature Request。
3. 大型功能建議先開 Issue 討論，避免投入大量時間後方向不一致。
4. 不要上傳含個資、機密內容或未獲授權的 PDF。

## 建立開發環境

```bash
git clone https://github.com/gfr211306-crypto/StudyForge.git
cd StudyForge
python -m venv .venv
```

Windows PowerShell：

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

macOS / Linux：

```bash
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

## 開發流程

1. 從最新的 `main` 建立簡短且具描述性的分支。
2. 修改程式並補上可重現問題或驗證功能的測試。
3. 執行完整檢查：

```bash
python -m pip check
python scripts/audit_repository.py
python -m pytest -q
python -m compileall -q app.py studyforge scripts tests
python -m build
```

4. 執行 `streamlit run app.py`，手動檢查受影響的操作流程。
5. 建立內容聚焦、訊息清楚的 commit 與 Pull Request。

## 程式原則

- 優先使用清楚、可測試的小函式。
- 所有 PDF 或使用者可編輯內容，在插入 HTML 前必須 escaping。
- 不新增不必要的網路服務或 API；若功能需要外部服務，請先開 Issue 討論。
- 執行依賴放在 `requirements.txt`，測試工具放在 `requirements-dev.txt`。
- 新功能應包含合理測試，錯誤訊息應讓非技術使用者也能理解。

## Commit 與 Pull Request

- 一個 commit 應代表一組真正有意義且可說明的變更。
- 不要為增加 commit 數量而拆分微小修改。
- PR 描述應說明「為什麼修改」、「如何修改」與「如何驗證」。

提交貢獻即表示你同意你的貢獻依本專案的 MIT License 發布。
