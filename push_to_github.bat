@echo off
echo ============================================================
echo Pushing CodeIntent to https://github.com/arshsri0513/why-the-code-is-like-this
echo ============================================================
cd /d "C:\Users\Arsh\.gemini\antigravity\scratch\why-the-code-is-like-this"
git push -u origin main
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================================
    echo SUCCESS! Repository uploaded to GitHub:
    echo https://github.com/arshsri0513/why-the-code-is-like-this
    echo ============================================================
) else (
    echo.
    echo ============================================================
    echo FAILED: Make sure you created the empty repo on GitHub first:
    echo https://github.com/new (Name: why-the-code-is-like-this)
    echo ============================================================
)
pause
