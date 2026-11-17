#Requires -Version 5.1
<#
.SYNOPSIS
Read-only WSL installation plan; use -Apply from administrator PowerShell to install.
.EXAMPLE
.\scripts\setup_wsl.ps1 -Apply -Distribution Ubuntu -WebDownload
#>
[CmdletBinding()]
param([switch]$Apply, [string]$Distribution = 'Ubuntu', [switch]$WebDownload)

function Resolve-WslExecutable {
    param([string]$WindowsDirectory, [bool]$Is64BitOS, [bool]$Is64BitProcess)
    $folder = if ($Is64BitOS -and -not $Is64BitProcess) { 'Sysnative' } else { 'System32' }
    $candidate = Join-Path (Join-Path $WindowsDirectory $folder) 'wsl.exe'
    if (Test-Path -LiteralPath $candidate -PathType Leaf) { return $candidate }
    return $null
}

function Get-WslHost {
    $windows = [Environment]::OSVersion.Platform -eq [PlatformID]::Win32NT
    $admin = $false
    $executable = $null
    if ($windows) {
        $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
        try {
            $principal = [Security.Principal.WindowsPrincipal]::new($identity)
            $admin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
        } finally { $identity.Dispose() }
        $executable = Resolve-WslExecutable ([Environment]::GetFolderPath('Windows')) `
            ([Environment]::Is64BitOperatingSystem) ([Environment]::Is64BitProcess)
    }
    return @{ IsWindows = $windows; Build = [Environment]::OSVersion.Version.Build;
              IsAdmin = $admin; WslPath = $executable }
}

function ConvertTo-WslArgument {
    param([string]$Value)
    if ($Value -match '\A[^\s"]+\z') { return $Value }
    $escaped = [regex]::Replace($Value, '(\\*)"', '$1$1\"')
    $escaped = [regex]::Replace($escaped, '(\\+)$', '$1$1')
    return '"' + $escaped + '"'
}

function ConvertFrom-WslBytes {
    param([byte[]]$Bytes)
    $encoding = [Text.UnicodeEncoding]::new($false, $false, $true)
    $text = $encoding.GetString($Bytes)
    return $text.TrimStart([char]0xFEFF)
}

function Invoke-WslCommand {
    param([string]$Executable, [string[]]$Arguments)
    $info = [Diagnostics.ProcessStartInfo]::new()
    $info.FileName = $Executable
    $info.Arguments = (($Arguments | ForEach-Object { ConvertTo-WslArgument $_ }) -join ' ')
    $info.UseShellExecute = $false
    $info.CreateNoWindow = $true
    $info.RedirectStandardOutput = $true
    $info.RedirectStandardError = $true
    $info.EnvironmentVariables.Remove('WSL_UTF8')
    $process = [Diagnostics.Process]::new()
    $process.StartInfo = $info
    $stdout = [IO.MemoryStream]::new()
    $stderr = [IO.MemoryStream]::new()
    try {
        [void]$process.Start()
        $outTask = $process.StandardOutput.BaseStream.CopyToAsync($stdout)
        $errTask = $process.StandardError.BaseStream.CopyToAsync($stderr)
        $process.WaitForExit()
        [void]$outTask.GetAwaiter().GetResult()
        [void]$errTask.GetAwaiter().GetResult()
        $nativeCode = $process.ExitCode
        $errors = @()
        $outText = ''
        $errText = ''
        $outRaw = $null
        $errRaw = $null
        try { $outText = ConvertFrom-WslBytes $stdout.ToArray() }
        catch {
            $outRaw = [Convert]::ToBase64String($stdout.ToArray())
            $errors += 'decoding-failed stdout: expected Microsoft WSL UTF-16LE; ' + $_.Exception.Message
        }
        try { $errText = ConvertFrom-WslBytes $stderr.ToArray() }
        catch {
            $errRaw = [Convert]::ToBase64String($stderr.ToArray())
            $errors += 'decoding-failed stderr: expected Microsoft WSL UTF-16LE; ' + $_.Exception.Message
        }
        $code = if ($errors.Count -gt 0 -and $nativeCode -eq 0) { 1 } else { $nativeCode }
        return @{ ExitCode = $code; NativeExitCode = $nativeCode; Stdout = $outText; Stderr = $errText;
                  StdoutBytesBase64 = $outRaw; StderrBytesBase64 = $errRaw;
                  Output = (@($outText, $errText) + $errors) -join "`n" }
    } finally {
        $process.Dispose()
        $stdout.Dispose()
        $stderr.Dispose()
    }
}

function Get-WslRegistrations {
    param([string]$Executable)
    try {
        $probe = Invoke-WslCommand $Executable @('--list', '--quiet')
        $nativeCode = if ($probe.ContainsKey('NativeExitCode')) { $probe.NativeExitCode } else { $probe.ExitCode }
        if ($probe.ExitCode -ne 0) {
            return @{ state = 'unknown'; names = @(); exit_code = $probe.ExitCode;
                      native_exit_code = $nativeCode; diagnostic = $probe.Output;
                      raw_stdout_base64 = $probe.StdoutBytesBase64; raw_stderr_base64 = $probe.StderrBytesBase64 }
        }
        $names = @(([string]$probe.Stdout).Replace([string][char]0, '') -split '[\r\n]+' |
                   ForEach-Object { $_.Trim() } | Where-Object { $_ })
        return @{ state = 'listed'; names = $names; exit_code = 0;
                  native_exit_code = $nativeCode; diagnostic = $probe.Stderr }
    } catch {
        return @{ state = 'unknown'; names = @(); exit_code = 1;
                  native_exit_code = $null; diagnostic = $_.Exception.Message }
    }
}

function Invoke-WslSetup {
    param([switch]$Apply, [string]$Distribution = 'Ubuntu', [switch]$WebDownload)
    if ($Distribution -cnotmatch '\A[A-Za-z0-9][A-Za-z0-9_.-]{0,79}\z') {
        throw 'Distribution must be an online WSL name, e.g. Ubuntu or Ubuntu-24.04 (ASCII letters, digits, dot, dash, underscore).'
    }
    $hostState = Get-WslHost
    if (-not $hostState.IsWindows) { throw 'Windows is required; run this script in Windows PowerShell.' }
    if ($hostState.Build -lt 19041) { throw 'Windows build 19041 or newer is required; see Microsoft WSL manual installation.' }
    if (-not $hostState.WslPath) { throw 'System wsl.exe is missing; see Microsoft WSL manual installation or repair Windows.' }
    $before = Get-WslRegistrations $hostState.WslPath
    $command = @('--install', '--distribution', $Distribution, '--no-launch')
    if ($WebDownload) { $command += '--web-download' }
    $result = [ordered]@{
        status = 'planned'; exit_code = 0; distribution = $Distribution;
        executable = $hostState.WslPath; command = $command; before = $before;
        next_step = "Use -Apply in administrator PowerShell to install. After any required restart, first launch: wsl -d $Distribution ; create your Linux user, then verify with wsl --list --verbose."
    }
    if ($before.state -eq 'listed' -and $before.names -icontains $Distribution) {
        $result.status = 'already-registered'
        $result.next_step = "Installation skipped. Registration does not prove WSL2 or user initialization; first launch: wsl -d $Distribution ; verify with wsl --list --verbose."
        return [pscustomobject]$result
    }
    if (-not $Apply) { return [pscustomobject]$result }
    if (-not $hostState.IsAdmin) { throw 'Run -Apply in an administrator PowerShell for the same Windows user.' }
    $help = Invoke-WslCommand $hostState.WslPath @('--help')
    if ($help.ExitCode -ne 0) { throw ('WSL help failed: ' + $help.Output) }
    $required = @('--install', '--distribution', '--no-launch')
    if ($WebDownload) { $required += '--web-download' }
    foreach ($flag in $required) {
        if ($help.Output -notmatch ([regex]::Escape($flag) + '(?![a-zA-Z0-9-])')) {
            throw "This system WSL does not advertise $flag. Update WSL manually using Microsoft guidance, then retry."
        }
    }
    $install = Invoke-WslCommand $hostState.WslPath $command
    $result.install = $install
    $result.exit_code = $install.ExitCode
    if ($install.ExitCode -eq 3010) {
        $result.status = 'restart-required'
        $result.next_step = 'Restart Windows manually, rerun this script, then complete first launch and user initialization.'
    } elseif ($install.ExitCode -ne 0) {
        $result.status = 'install-failed'
        $result.next_step = 'Read install diagnostics; resolve the reported Windows/WSL issue before retrying.'
    } else {
        $result.status = 'install-command-completed'
        $result.after = Get-WslRegistrations $hostState.WslPath
        $result.next_step = "Command completed; readiness is unverified. If Windows requests a restart, restart manually and rerun. Then first launch: wsl -d $Distribution ; create a Linux user and verify WSL2 with wsl --list --verbose."
    }
    return [pscustomobject]$result
}

if ($MyInvocation.InvocationName -ne '.') {
    [Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)
    try {
        $result = Invoke-WslSetup -Apply:$Apply -Distribution $Distribution -WebDownload:$WebDownload
    } catch {
        $result = [pscustomobject]@{ status = 'error'; exit_code = 1; diagnostic = $_.Exception.Message }
    }
    $result | ConvertTo-Json -Depth 12
    exit $result.exit_code
}
