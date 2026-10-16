# dev-guardian 交付與驗證紀錄

這個目錄原本是空白工作區，沒有應用程式、AGENTS、測試或 CI。已在目前專案建立可直接執行的治理系統，並初始化本地 Git；沒有設定遠端、推送或部署。

## 使用方式

Codex 下一個回合可使用 `$dev-guardian`。專案的 `AGENTS.md` 已要求開發任務遵循此流程。其他 Agent 可直接閱讀 `AGENTS.md`、`outputs/dev-guardian/SKILL.md` 與 `.dev-guardian/STATE.md`，執行相同 Python 命令；不需要 Codex 私有工具。

```sh
python3 outputs/dev-guardian/scripts/guardian.py --root . snapshot
python3 outputs/dev-guardian/scripts/guardian.py --root . verify
python3 outputs/dev-guardian/scripts/guardian.py --root . check
```

新專案：將 `dev-guardian` 整個資料夾複製到 `.agents/skills/dev-guardian`，執行該資料夾的 `scripts/guardian.py --root <專案> init`。它會保留既有紀錄、合併規則。先檢查實際測試與 CI，再填 `.dev-guardian/config.json`；範本刻意沒有假測試。`required_ids` 必須對應當次必要驗收項目，包含尚無命令的硬體／外部整合；缺失或 BLOCKED 均不能使完整 gate 通過。`check --ids ...` 僅驗證指定子集合。

本機安裝：`~/.codex/skills/dev-guardian` 連至本專案技能來源。換設備後須重新建立連結或複製；Git 內的來源、規則與 Markdown 記憶不依賴此絕對路徑。

## 實際驗證

| 項目 | 結果與範圍 |
| --- | --- |
| 官方技能檢查器 | PASSED：frontmatter、命名、未完成 scaffold 檢查。開發用隔離 venv 安裝 PyYAML 6.0.3；技能執行本身無第三方 Python 依賴 |
| CLI／Git 回歸套件 | PASSED：21 個測試，真實子程序與臨時 Git 儲存庫，未用 process/filesystem mocks |
| 初始化／持久化 | PASSED：重跑不覆蓋使用者記憶，既有 AGENTS 內容保留，規則不重複加入 |
| 證據 | PASSED：成功、失敗、逾時、命令不存在、未執行、BLOCKED、內容變更失效、日誌竄改拒絕、測試中修改來源拒絕 |
| 回歸選擇 | PASSED：明確路徑、未知影響擴大全部、staged/unstaged 抵消、重新命名前後路徑；獨立 probe 也驗證 base 到 HEAD 的重新命名 |
| 必要驗收門檻 | PASSED：unit 通過仍不能掩蓋 required external 項目的 NOT TESTED／BLOCKED |
| Git 復原 | PASSED：保留 index／工作內容，保存 staged、unstaged、指定 untracked 檔案，在隔離 worktree 套用 patch 復原。拒絕 traversal、symlink、明顯密鑰檔名；未操作使用者資料作破壞性復原 |
| 穩定性 | PASSED：併行證據目錄不衝突、日誌容量上限、常見憑證遮罩、長行捨棄、POSIX 逾時子程序清理、搬移技能副本仍可執行 |
| 接手情境 | PASSED：獨立 Agent 明確載入 Skill，核對實際原始碼，拒絕舊的 fixture/build 完成聲明，執行真實檢查並保存 49 行交接；外部整合／讀卡機標 BLOCKED |
| 獨立審查 | 已重現並修復遮罩、staged 指紋、變更範圍與重新命名問題；修正後由審查 Agent 重新執行對應 probes |

測試命令：`python3 outputs/dev-guardian/tests/test_guardian.py`。目前專案的正式證據位於 `.dev-guardian/evidence/`，JSON 保存實際 HEAD、工作樹/index SHA256、環境指紋、命令、退出碼與 log hash。讀取最新紀錄並重新執行，才可評估目前版本；新 commit 或環境改變會使舊證據失效。

`validation/forward/` 是隔離情境的歷史交接與原始證據副本，指向當時的 fixture，不是本專案目前版本的通過證明。其中提到的預設 gate 缺口已於後續以 `required_ids` 修復。無 Skill 的基線 Agent 本來就沒有誇大完成，因此不主張比較實驗已證明模型行為改善。

## 已安裝的上游工具

- **Ponytail 5.3.1**：以官方 `codex plugin marketplace add DietrichGebert/ponytail` 與 `codex plugin add ponytail@ponytail` 安裝。CLI 查詢確認 installed、enabled；以隔離 PLUGIN_DATA 與明確 Node 執行 activation hook 成功。真實客戶端 lifecycle hook 尚 NOT TESTED；依上游需在 `/hooks` 檢查／信任後啟動新聊天或重新啟動 App。
- **Taste Skill**：安裝預設 `design-taste-frontend`，含 scripts、references、library、assets；29 個檔案與固定 commit `f624f37a8c650b9cc550253104925efe4c8de246` 相符。方向產生器與真正 Chrome inspector 的隔離頁面冒煙測試 PASSED，inspector 有一個「頁面沒有動作按鈕」WARN。沒有安裝該 repo 的所有選配風格技能，也未聲稱完成任何產品 UI。
- 系統預設 PATH 沒有 `node`；已確認 App 隨附 Node v24.19.0 可執行這些腳本。路徑詳見 `installations.json`。需要一般 `node` 命令或自動 hook 時，須讓其執行環境的 PATH 包含該 Node 目錄；未擅自修改 shell 設定或繞過 hook 信任。

## 未驗證與保障界線

- **NOT TESTED**：下一回合的 Codex 自動技能選擇、真正 Claude/Gemini 執行、第二台設備 Git 接續、遠端 CI matrix、Windows 與 Linux 實際執行。CI 已建立，但尚無遠端可觸發。
- **BLOCKED**：實體硬體與外部產品服務驗收，因沒有提供相關應用程式、設備或環境。建置、模擬器、E2E 與硬體結果不能互相替代。
- 指令退出零僅表示該命令成功；Agent 仍須核對斷言、skip 數、真實依賴與驗收結果。此系統不是簽章認證、防偽存證、完整依賴分析或任意密鑰偵測器，也不能強迫其他模型服從規則。
- Checkpoint 只保護明確選取的安全檔案；未選、ignored、外部資源不在備份範圍。壓縮檔與 logs 預設留本機，摘要可 Git 同步。交付包內包含本次經檢查的安全日誌；日後同步其他 logs 前仍須審查，或在接收端重新驗證。

交付包包含技能、AGENTS、記憶範本與目前紀錄、測試、CI、安裝紀錄及本次安全證據；解壓後先讀 AGENTS，再依實際新 Git 狀態重新驗證。

## 後續 GitHub 發布（2026-10-16）

已建立私人儲存庫 [ZIRUL-0902/dev-guardian](https://github.com/ZIRUL-0902/dev-guardian)，後續狀態以 GitHub 與專案 STATE 為準。前文的「未設定遠端／未推送」描述第一階段交付狀態。SSH 安裝與更新請見 [SSH-INSTALL.md](SSH-INSTALL.md)；目前 Codex 官方使用者技能路徑為 `~/.agents/skills`。原始 zip 是第一階段快照，GitHub 包含後續文件更新。
