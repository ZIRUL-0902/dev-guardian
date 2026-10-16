# 在 SSH 主機安裝 dev-guardian

儲存庫：<https://github.com/ZIRUL-0902/dev-guardian>（私人）。SSH 主機需有 Git、Python 3.9+、已可使用的 Codex CLI，以及可存取此儲存庫的 GitHub SSH key。不要把本機密鑰複製進 repo。

## 一次安裝

先 SSH 登入你平常執行 Codex 的主機，再執行以下命令。使用執行 Codex 的同一個帳號，不要加 sudo。

```sh
mkdir -p "$HOME/.local/share" "$HOME/.agents/skills"
git clone git@github.com:ZIRUL-0902/dev-guardian.git "$HOME/.local/share/dev-guardian"
ln -s "$HOME/.local/share/dev-guardian/outputs/dev-guardian" "$HOME/.agents/skills/dev-guardian"
python3 "$HOME/.agents/skills/dev-guardian/tests/test_guardian.py"
```

`clone` 與 `ln -s` 遇到同名目錄會停止，不會覆蓋原有安裝。若已存在，先檢查其 Git remote 與連結目標，再選擇沿用或更新；不要直接刪除或強制連結。

如果 SSH key 尚未設定，先依 GitHub 的方式完成驗證，或使用該主機既有的 HTTPS Git 驗證方式 clone。不要把 token 放進 URL、命令列或交接文件。

## 啟動與呼叫

在實際開發專案內啟動 Codex：

```sh
cd /path/to/your-project
codex
```

在 **Codex 對話內**輸入：

```text
$dev-guardian
讀取此專案的規則、Git 狀態與持久化紀錄，核實後接續開發。
```

`$dev-guardian` 是對話內的 Skill 名稱，不是 shell 命令。可用 `/skills` 查看技能；若未顯示，重新啟動 Codex。現行 Codex 會探索使用者的 `~/.agents/skills`，並支援連結的技能目錄。[OpenAI 官方文件](https://learn.chatgpt.com/docs/build-skills)

## 為開發專案建立治理紀錄

先確認位於目標 Git repository 根目錄，再執行：

```sh
python3 "$HOME/.agents/skills/dev-guardian/scripts/guardian.py" --root . init
```

這會保留既有紀錄，將規則加入 `AGENTS.md`，並建立 `.dev-guardian/` 範本。請讓 Agent 檢查專案真正的測試與 CI，再設定 `config.json` 的 `tests` 與 `required_ids`；空白設定不會產生假的通過結果。

若需讓其他設備與其他 LLM 不依賴全域安裝，可把技能來源複製進目標專案的 `.agents/skills/dev-guardian`（遇到既有目錄先比較），並將技能、AGENTS、簡短開發紀錄及經審查的證據納入該專案 Git。不同設備不共用對話；接手依據是專案內的紀錄與實際程式碼。

## 更新

```sh
git -C "$HOME/.local/share/dev-guardian" status --short
git -C "$HOME/.local/share/dev-guardian" pull --ff-only
python3 "$HOME/.agents/skills/dev-guardian/tests/test_guardian.py"
```

若有本機修改或無法 fast-forward，先處理差異；不要 reset/clean。重新啟動 Codex 後使用更新版本。

## 驗證界線

本機套件測試與新 clone 檢查可確認來源／腳本可用；你實際 SSH 主機上的 Codex 自動探索、權限、Python/Git 環境與執行結果仍需在該主機確認。這份儲存庫不會自動安裝 Ponytail 或 Taste；兩者是先前在本機另外安裝的工具。
