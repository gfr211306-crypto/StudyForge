# StudyForge Tester Guide

感謝你協助測試 StudyForge。這份指南的目標是讓每位測試者完成相同的最小流程，
方便維護者比較不同環境的結果。

## 測試前注意事項

- 請使用英文講義、公開文章、自己的練習文件或可公開分享的 PDF。
- 不要上傳姓名、學校帳號、病歷、公司資料、私人筆記或其他機密內容。
- 不要在公開 Issue 附上真實敏感 PDF。
- 測試者不需要提供姓名、Email、GitHub 帳號以外的個人資料。

## 測試環境

請記下但不要提供敏感資訊：

- 作業系統
- 瀏覽器與版本
- 使用公開 Demo 或本機安裝
- PDF 大小與大約頁數
- PDF 是文字型還是掃描型

## 必做流程

### 1. 開啟網站

前往 [StudyForge 公開 Demo](https://studyforge-kpamprbzckvvgx4sz6fxvz.streamlit.app/)。

### 2. 上傳 PDF

1. 上傳一份可以用滑鼠反白英文文字的 PDF。
2. 先使用「綜合推薦」。
3. 確認畫面能顯示 PDF 頁數、英文詞數與推薦單字。

### 3. 測試 IELTS mode

1. 將單字難度切換成 **IELTS 單字**。
2. 重新分析或重新上傳同一份 PDF。
3. 觀察結果是否合理：
   - 是否優先出現適合學習的單字？
   - 是否有明顯不相關、專有名詞或亂碼？
   - 是否仍有 PDF 原文例句？

### 4. 檢查 CEFR

請查看單字表的 CEFR 欄位：

- A1、A2、B1、B2、C1、C2 都是有效結果。
- `unknown` 也是預期結果，代表目前資料不足或詞義有歧義。
- 請不要把 `unknown` 當成程式錯誤。

### 5. 測試三種匯出

依序選擇並下載：

1. **Anki CSV**
   - 確認檔案可以開啟。
   - 確認 Front、Back、Tags 存在。
2. **普通 CSV**
   - 確認中文沒有亂碼。
   - 確認單字、詞性、CEFR、例句存在。
3. **JSON**
   - 確認檔案是合法 JSON。
   - 確認每筆資料包含 `word`、`cefr`、`is_ielts`。

### 6. 回報結果

請使用 [External User Feedback Issue form](https://github.com/gfr211306-crypto/StudyForge/issues/new?template=external_feedback.yml)。

若你希望匿名追蹤後續回覆，可以在表單中表示「希望取得匿名 Tester ID」；
維護者只有在確認你實際完成測試後，才會分配 `Tester-001`、`Tester-002` 等編號。

## 如何描述問題

請提供：

- 發生問題的步驟
- 預期結果
- 實際結果
- 使用的 mode 與匯出格式
- PDF 大小、頁數與文字型／掃描型狀態
- 錯誤訊息或畫面截圖（請先移除個資）

不要猜測原因，也不要公開貼出敏感文件。只要描述你看到的行為即可。

## 匿名 Tester ID 規則

目前尚未有真人測試紀錄，因此尚未建立任何 Tester ID。

未來規則：

1. 第一位完成測試並提供回饋、且同意匿名追蹤者，才會得到 `Tester-001`。
2. 同一位測試者的後續回饋沿用同一 ID。
3. ID 不包含姓名、Email 或 GitHub 使用者名稱。
4. 維護者只記錄測試範圍、環境類型、問題與結果，不記錄原始 PDF。
5. 自動化測試永遠不會產生 Tester ID。

## Maintainer follow-up

收到真人回饋後，維護者會：

1. 使用 `external-user-feedback` label 建立或整理 GitHub Issue。
2. 嘗試用去識別化資訊重現。
3. 為可重現問題新增 regression test。
4. 修復後重新執行完整測試。
5. 在 Issue 中回報修復版本與驗證結果。
6. 若需要，準備下一個 patch release。
