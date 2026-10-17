param(
    [string]$GameDir = (Split-Path $PSScriptRoot -Parent),
    [string]$TtsHome = (Join-Path $HOME "VoiceTTS"),
    [string]$Python = (Join-Path $TtsHome "venv_xtts\Scripts\python.exe")
)

$build = $PSScriptRoot
$work = Join-Path $build "work"
$pidFile = Join-Path $work "voice.pid"
New-Item -ItemType Directory -Force -Path $work | Out-Null

if (Test-Path $pidFile) {
    $running = Get-Process -Id (Get-Content $pidFile) -ErrorAction SilentlyContinue | Where-Object { $_.Path -eq $Python }
    if ($running) {
        Write-Host "Already running (PID $($running.Id))"
        exit
    }
}

$questLists = @("quests.json", "quests_horde.json") |
    ForEach-Object { Join-Path $work $_ } |
    Where-Object { Test-Path $_ } |
    ForEach-Object { "`"$_`"" }

$env:TTS_HOME = Join-Path $TtsHome "tts"
$process = Start-Process -FilePath $Python `
    -ArgumentList (@(
        "-I", "`"$build\tools\voice_quests.py`""
    ) + $questLists + @(
        "`"$GameDir\Interface\AddOns\AI_VoiceOverData_Wrath\generated\sounds\quests`"",
        "`"$GameDir\Interface\AddOns\AI_VoiceOverData_Russian`"",
        "`"$TtsHome\progress`""
    )) `
    -WorkingDirectory $build `
    -RedirectStandardOutput (Join-Path $work "voice.log") `
    -RedirectStandardError (Join-Path $work "voice.err.log") `
    -WindowStyle Hidden -PassThru
$process.PriorityClass = "BelowNormal"
Set-Content -Path $pidFile -Value $process.Id
Write-Host "Started (PID $($process.Id)). Progress: $work\voice.log"
