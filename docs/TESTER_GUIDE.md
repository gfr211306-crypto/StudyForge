# StudyForge 5-minute Tester Guide

感謝你協助測試 StudyForge。我們正在找第一批 **3 位真人測試者**。
最短流程約 5 分鐘。**No Star or Follow is required.** 也不需要提供個人資料。

> 回報問題需要登入 GitHub。請勿上傳私人、機密或未獲授權的 PDF。

## 準備

- 一份 1–10 頁、文字可以反白的英文 PDF
- PDF 不含姓名、學校帳號、病歷、公司資料或私人筆記
- 桌面或手機瀏覽器

## 最短操作流程

### 1. PDF — 約 1 分鐘

1. 開啟 [StudyForge Demo](https://studyforge-kpamprbzckvvgx4sz6fxvz.streamlit.app/)。
2. 上傳 PDF。
3. 確認頁數、英文詞數與單字表有顯示。

### 2. IELTS / CEFR — 約 2 分鐘

1. 將單字難度切換成 **IELTS 單字**。
2. 查看至少 3 個推薦單字與 PDF 原文例句。
3. 查看 CEFR 欄位：
   - A1、A2、B1、B2、C1、C2 都是有效結果。
   - `unknown` 代表資料不足或詞義有歧義，不一定是錯誤。

### 3. Export — 約 1 分鐘

選擇你最常用的一種格式並下載：

- Anki CSV
- 普通 CSV
- JSON

確認檔案能開啟，而且包含單字、中文意思與 CEFR。

### 4. Feedback — 約 1 分鐘

使用
[External User Feedback form](https://github.com/gfr211306-crypto/StudyForge/issues/new?template=external_feedback.yml)
回報：

- 哪些功能正常
- 哪一步不清楚或失敗
- 使用的裝置／瀏覽器
- PDF 大約頁數與大小

若沒有遇到問題，也可以選擇 **Positive feedback**，告訴我們完整流程是否順利。

## 如果遇到問題

請提供最短重現步驟、預期結果、實際結果與錯誤訊息。截圖必須先移除個資，
不要將原始敏感 PDF 附在公開 Issue。

## 匿名 Tester ID

目前沒有真人測試紀錄，也沒有任何 Tester ID。

第一、第二、第三位實際完成流程並提交回饋、且同意匿名追蹤者，才會依序取得：

```text
Tester-001 → Tester-002 → Tester-003
```

同一位測試者後續沿用原 ID。自動化測試、AI 模擬或沒有實際完成流程的回覆，
永遠不會取得 Tester ID。

## Optional extended check

若你願意多花幾分鐘，可再下載另外兩種匯出格式，或用另一份 PDF 重試。
這不是取得 Tester ID 的必要條件。

## Maintainer follow-up

收到真人回饋後，維護者會：

1. 使用 `external-user-feedback` label 整理 GitHub Issue。
2. 用去識別化資訊重現。
3. 為可重現問題新增 regression test。
4. 修復並執行完整測試。
5. 準備需要的 patch release。
