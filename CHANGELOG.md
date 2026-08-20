# Changelog

本專案的重要變更會記錄於此。

## [0.2.0] - 2026-08-20

### Added

- GitHub Actions CI，測試 Python 3.11 與 3.12
- Bug Report、Feature Request、PR templates
- Dependabot、CONTRIBUTING、SECURITY 與 Code of Conduct
- Streamlit Community Cloud 部署設定與部署文件
- Repository secret／forbidden-file audit
- PDF 大小、頁數與擷取文字量限制
- HTML 預覽 escaping、CSV formula mitigation 與相關測試

### Changed

- 將執行依賴與開發依賴分離
- 將 PDF 分析結果改為每個 Streamlit session 獨立保存
- 公開錯誤畫面不再顯示伺服器 stack trace
- 更新公開部署隱私說明與完整 README

## [0.1.0] - 2026-08-19

### Added

- 初始 Streamlit 網站
- PyMuPDF PDF 文字擷取
- 離線英中詞典、單字排序與 Anki CSV 匯出
- Windows 安裝／啟動腳本與基礎測試
