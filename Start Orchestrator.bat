@echo off
rem Opens Claude Code in this project. The main thread runs as the orchestrator (.claude/settings.json).
rem Then type "go" to work the next task in tasks\, or give it a new request.
cd /d "%~dp0"
claude
