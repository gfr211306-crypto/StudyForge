# Changelog

本專案的重要變更會記錄於此。

## [Unreleased]

### Added

- Five-minute recruitment workflow for the first three real external testers
- External User Feedback GitHub Issue form
- Separate Human testers and Automated tests tracking policy

### Fixed

- Streamlit Cloud import failure when the checkout directory shadows the
  bundled `studyforge` package

### Changed

- Replaced non-reproducible fixed E2E and pytest counts in public documentation
  with links to the tracked tests, public CI workflow, and reproducible commands
- Kept tester documentation regression checks focused on workflow structure,
  public links, privacy, and separation of human and automated testing

## [0.2.0] - 2026-08-20

### Added

- Reusable `StudyForge` Python API shared by Web and CLI
- Published to the official PyPI index as `studyforge-vocab==0.2.0`
- `studyforge extract` CLI with Anki CSV, ordinary CSV, and JSON output
- IELTS vocabulary mode using explicit dictionary IELTS tags
- CEFR A1-C2 labels from CEFR-J and Octanove vocabulary profiles
- Explicit `unknown` CEFR result for absent or ambiguous headwords
- `pyproject.toml`, console-script metadata, package data, wheel and sdist build
- PyPI Trusted Publishing workflow using GitHub OIDC and the `pypi` environment
- GitHub Actions CI，測試 Python 3.11 與 3.12
- Bug Report、Feature Request、PR templates
- Dependabot、CONTRIBUTING、SECURITY 與 Code of Conduct
- Streamlit Community Cloud 部署設定與部署文件
- Repository secret／forbidden-file audit
- PDF 大小、頁數與擷取文字量限制
- HTML 預覽 escaping、CSV formula mitigation 與相關測試

### Changed

- Streamlit Web App now consumes the same public core API as the CLI
- Offline dictionary and CEFR mapping are bundled as Python package data
- Anki cards now include CEFR and IELTS tags
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
