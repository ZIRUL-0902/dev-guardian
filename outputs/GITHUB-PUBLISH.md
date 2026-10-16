# GitHub 發布完成

- 私人儲存庫：[ZIRUL-0902/dev-guardian](https://github.com/ZIRUL-0902/dev-guardian)
- SSH 安裝：[SSH-INSTALL.md](SSH-INSTALL.md)
- 已驗證來源：`0d09675016f7c389a4cb183f591d092831e01aa0`；本機、遠端 main、GitHub 全新 clone HEAD 相符。
- 從 GitHub clone 後建立技能 symlink 並執行測試：21 tests，OK。
- [遠端 CI](https://github.com/ZIRUL-0902/dev-guardian/actions/runs/38921244577)：Ubuntu/macOS × Python 3.9/3.13，四組皆 success。
- 後續發布狀態／紀錄 commit 僅更新文件；實際 SSH 主機、使用者的 GitHub key 與 Codex 探索尚 NOT TESTED。

SSH 主機需先有私人儲存庫存取權，再執行：

```sh
mkdir -p "$HOME/.local/share" "$HOME/.agents/skills"
git clone git@github.com:ZIRUL-0902/dev-guardian.git "$HOME/.local/share/dev-guardian"
ln -s "$HOME/.local/share/dev-guardian/outputs/dev-guardian" "$HOME/.agents/skills/dev-guardian"
python3 "$HOME/.agents/skills/dev-guardian/tests/test_guardian.py"
```

重新啟動 Codex，在對話內使用 `$dev-guardian`；可用 `/skills` 確認。既有安裝請先比較，命令不使用強制覆蓋。[Codex 技能路徑與呼叫方式官方文件](https://learn.chatgpt.com/docs/build-skills)
