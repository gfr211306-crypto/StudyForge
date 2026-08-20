# Security Policy

## Supported version

StudyForge 目前仍在早期開發階段，安全修正會套用至 `main` 分支的最新版本。

## 回報安全問題

請不要用公開 Issue 回報尚未修正的漏洞，也不要附上真實的機密 PDF、API key、
密碼、個資或可識別使用者的日誌。

若 GitHub 儲存庫的 **Security** 頁面提供 **Report a vulnerability**，
請使用該私人通報管道。若尚未啟用私人通報，請先透過不含漏洞細節的普通 Issue
請維護者開啟聯絡管道。

回報時建議包含：

- 受影響版本或 commit
- 可安全分享的重現步驟
- 可能影響
- 建議修正方式

## 部署者注意事項

- StudyForge 不需要 API key 或 Streamlit secrets。
- 公開部署時，PDF 會傳送至部署該服務的伺服器處理。
- 請勿宣稱公開部署適合處理機密、醫療、法律或其他敏感文件。
- 請保持 Python 與套件在支援版本，並定期檢視 Dependabot 更新。
