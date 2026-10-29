param(
    [string]$GameDir = (Split-Path $PSScriptRoot -Parent),
    [string]$TtsHome = (Join-Path $HOME "VoiceTTS"),
    [string]$Python = (Join-Path $TtsHome "venv_f5\Scripts\python.exe"),
    [int]$MaxRestarts = 50,
    [int]$Attempts = 4,
    [switch]$Loop
)

$build = $PSScriptRoot
$work = Join-Path $build "work"
$pidFile = Join-Path $work "voice.pid"
New-Item -ItemType Directory -Force -Path $work | Out-Null

if (-not $Loop) {
    if (Test-Path $pidFile) {
        $running = Get-Process -Id (Get-Content $pidFile) -ErrorAction SilentlyContinue |
            Where-Object { $_.ProcessName -in @("powershell", "python") }
        if ($running) {
            Write-Host "Already running (PID $($running.Id))"
            exit
        }
    }
    $supervisor = Start-Process -FilePath "powershell.exe" `
        -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "`"$PSCommandPath`"", "-Loop", "-Attempts", $Attempts) `
        -WindowStyle Hidden -PassThru
    Set-Content -Path $pidFile -Value $supervisor.Id
    Write-Host "Started (PID $($supervisor.Id)). Progress: $work\voice.log"
    exit
}

$questLists = @("quests.json", "quests_horde.json") |
    ForEach-Object { Join-Path $work $_ } |
    Where-Object { Test-Path $_ } |
    ForEach-Object { "`"$_`"" }
$optionalArgs = @("--ru-voices", "`"$work\ru_voices.json`"", "--redo", "`"$TtsHome\progress\redo_f5.json`"", "--attempts", $Attempts)
$gossipList = Join-Path $work "gossip.json"
if (Test-Path $gossipList) { $optionalArgs += @("--gossip", "`"$gossipList`"") }
$catquest = Join-Path $GameDir "Interface\AddOns\AI_VoiceOverData_CatQuest"
if (Test-Path $catquest) { $optionalArgs += @("--catquest", "`"$catquest`"") }

$env:HF_HOME = Join-Path $TtsHome "hf"
$log = Join-Path $work "voice.log"
for ($attempt = 0; $attempt -le $MaxRestarts; $attempt++) {
    if (Test-Path $log) { Get-Content $log -Encoding UTF8 | Add-Content (Join-Path $work "voice_history.log") -Encoding UTF8 }
    $process = Start-Process -FilePath $Python `
        -ArgumentList (@(
            "-I", "`"$build\tools\voice_quests.py`""
        ) + $questLists + @(
            "`"$GameDir\Interface\AddOns\AI_VoiceOverData_Russian`"",
            "`"$TtsHome\progress`""
        ) + $optionalArgs) `
        -WorkingDirectory $build `
        -RedirectStandardOutput $log `
        -RedirectStandardError (Join-Path $work "voice.err.log") `
        -WindowStyle Hidden -PassThru
    $null = $process.Handle
    $process.PriorityClass = "BelowNormal"
    $process.WaitForExit()
    if ($process.ExitCode -eq 0) { break }
    Add-Content -Path (Join-Path $work "restarts.log") -Value "$(Get-Date -Format s) exit $($process.ExitCode), restart $($attempt + 1)"
    Start-Sleep -Seconds 60
}
