param(
    [string]$GameDir = (Split-Path $PSScriptRoot -Parent),
    [string]$TtsHome = (Join-Path $HOME "VoiceTTS"),
    [string]$Python = (Join-Path $TtsHome "venv_f5\Scripts\python.exe")
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
$optionalArgs = @("--ru-voices", "`"$work\ru_voices.json`"", "--redo", "`"$TtsHome\progress\redo_f5.json`"")
$gossipList = Join-Path $work "gossip.json"
if (Test-Path $gossipList) { $optionalArgs += @("--gossip", "`"$gossipList`"") }
$catquest = Join-Path $GameDir "Interface\AddOns\AI_VoiceOverData_CatQuest"
if (Test-Path $catquest) { $optionalArgs += @("--catquest", "`"$catquest`"") }

$env:HF_HOME = Join-Path $TtsHome "hf"
$process = Start-Process -FilePath $Python `
    -ArgumentList (@(
        "-I", "`"$build\tools\voice_quests.py`""
    ) + $questLists + @(
        "`"$GameDir\Interface\AddOns\AI_VoiceOverData_Russian`"",
        "`"$TtsHome\progress`""
    ) + $optionalArgs) `
    -WorkingDirectory $build `
    -RedirectStandardOutput (Join-Path $work "voice.log") `
    -RedirectStandardError (Join-Path $work "voice.err.log") `
    -WindowStyle Hidden -PassThru
$process.PriorityClass = "BelowNormal"
Set-Content -Path $pidFile -Value $process.Id
Write-Host "Started (PID $($process.Id)). Progress: $work\voice.log"
