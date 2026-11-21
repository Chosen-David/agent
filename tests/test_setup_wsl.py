"""Exercise WSL setup decisions without installing, launching or rebooting WSL."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from tests.central_acceptance import acceptance_path

ROOT = Path(__file__).resolve().parents[1]
SHELL = shutil.which('powershell') or shutil.which('pwsh')
SCRIPT = Path(os.environ.get('WSL_SETUP_TEST_SCRIPT', ROOT / 'scripts/setup_wsl.ps1'))


@unittest.skipUnless(SHELL, 'PowerShell is required for native script contracts')
class WslSetupTests(unittest.TestCase):
    def test_mandatory_acceptance_blocks_missing_powershell(self):
        import sys
        entry = acceptance_path('WSL-SETUP-01/acceptance.py')
        env = {**os.environ, 'AGENT_TEST_PROJECT_ROOT': str(ROOT), 'PATH': ''}
        proc = subprocess.run([sys.executable, '-B', str(entry)], env=env,
                              capture_output=True, text=True, timeout=10)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn('PowerShell', proc.stderr)

    def run_case(self, scenario='fresh', args='', expected_error=None):
        fixture = r'''
$ErrorActionPreference = 'Stop'
$script:Calls = @()
$script:Lists = 0
function Get-WslHost {
    @{ IsWindows = ($scenario -ne 'linux'); Build = $(if ($scenario -eq 'old') { 18362 } else { 26100 });
       IsAdmin = ($scenario -notin @('nonadmin', 'existing')); WslPath = $(if ($scenario -eq 'missing') { $null } else { 'system-wsl.exe' }) }
}
function Invoke-WslCommand {
    param([string]$Executable, [string[]]$Arguments)
    $script:Calls += ,@($Arguments)
    if ($Arguments[0] -eq '--help') {
        if ($scenario -eq 'helpfail') { return @{ ExitCode = 5; Output = 'help failed' } }
        return @{ ExitCode = 0; Output = $(if ($scenario -eq 'oldflags') { '--install --distribution' } else { '--install --distribution --no-launch --web-download' }) }
    }
    if ($Arguments[0] -eq '--list') {
        $script:Lists++
        if ($scenario -eq 'unknown' -or ($scenario -eq 'postfail' -and $script:Lists -gt 1)) {
            return @{ ExitCode = 5; Stdout = ''; Stderr = 'probe failed'; Output = 'probe failed' }
        }
        $names = if ($scenario -in @('existing','existing-stderr')) { "u`0B`0u`0n`0t`0u`0`r`n" } elseif ($scenario -in @('other','target-stderr')) { 'Debian' } else { '' }
        $diagnostic = if ($scenario -eq 'target-stderr') { 'Ubuntu' } elseif ($scenario -eq 'existing-stderr') { 'warning' } else { '' }
        return @{ ExitCode = 0; Stdout = $names; Stderr = $diagnostic; Output = ($names + $diagnostic) }
    }
    if ($Arguments[0] -ne '--install') { throw 'Unexpected modifying command' }
    if ($scenario -eq 'fail') { return @{ ExitCode = 17; Output = 'install failed' } }
    if ($scenario -eq 'reboot') { return @{ ExitCode = 3010; Output = 'restart needed' } }
    return @{ ExitCode = 0; Output = 'accepted' }
}
'''
        harness = r'''
. '__SCRIPT__'
__FIXTURE__
try { $result = Invoke-WslSetup __ARGS__; $caught = $null }
catch { $result = $null; $caught = $_.Exception.Message }
@{ result = $result; error = $caught; calls = @($script:Calls) } | ConvertTo-Json -Depth 12 -Compress
'''
        script = SCRIPT
        self.assertTrue(script.is_file(), 'WSL installer entry point missing')
        harness = "$scenario = '" + scenario + "'\n" + harness.replace(
            '__SCRIPT__', str(script).replace("'", "''")).replace('__ARGS__', args).replace('__FIXTURE__', fixture)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'case.ps1'
            path.write_text(harness, encoding='utf-8-sig')
            proc = subprocess.run([SHELL, '-NoProfile', '-NonInteractive', '-ExecutionPolicy',
                                   'Bypass', '-File', str(path)], capture_output=True,
                                  encoding='utf-8', errors='replace', timeout=25)
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
        result = json.loads(proc.stdout)
        if expected_error:
            self.assertIn(expected_error, result['error'])
        else:
            self.assertIsNone(result['error'], result)
        return result

    def entry_case(self, scenario, arguments, expected_exit):
        text = SCRIPT.read_text(encoding='utf-8-sig')
        fixture = r'''
function Get-WslHost { @{ IsWindows=$true; Build=26100; IsAdmin=__ADMIN__; WslPath='fixture' } }
function Invoke-WslCommand {
    param($Executable, $Arguments)
    if ($Arguments[0] -eq '--install') {
        if (-not $Apply) { throw 'MUTATION: modifying call without Apply' }
        return @{ ExitCode=__CODE__; Output='fixture install' }
    }
    if ($Arguments[0] -eq '--help') { return @{ ExitCode=0; Output='--install --distribution --no-launch --web-download' } }
    return @{ ExitCode=0; Stdout=''; Stderr=''; Output='' }
}
'''.replace('__ADMIN__', '$false' if scenario == 'nonadmin' else '$true').replace('__CODE__', str(expected_exit))
        guard = "if ($MyInvocation.InvocationName -ne '.') {"
        self.assertIn(guard, text)
        text = text.replace(guard, fixture + '\n' + guard)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'entry.ps1'
            path.write_text(text, encoding='utf-8-sig')
            proc = subprocess.run([SHELL, '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass',
                                   '-File', str(path), *arguments], capture_output=True,
                                  encoding='utf8', errors='replace', timeout=25)
        self.assertEqual(proc.returncode, expected_exit if os.name == 'nt' else expected_exit % 256,
                         proc.stderr + proc.stdout)
        return json.loads(proc.stdout)

    def test_process_entry_json_and_exit_codes(self):
        self.assertEqual(self.entry_case('fresh', [], 0)['status'], 'planned')
        row = self.entry_case('fresh', ['-Apply'], 0)
        self.assertEqual(row['status'], 'install-command-completed')
        self.assertIn('first launch', row['next_step'])
        self.assertEqual(self.entry_case('nonadmin', ['-Apply'], 1)['status'], 'error')
        self.assertEqual(self.entry_case('fresh', ['-Apply'], 17)['status'], 'install-failed')
        self.assertEqual(self.entry_case('fresh', ['-Apply'], 3010)['status'], 'restart-required')

    def ps(self, body):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'native.ps1'
            path.write_text("$ErrorActionPreference='Stop'\n. '" + str(SCRIPT).replace("'", "''") + "'\n" + body,
                            encoding='utf-8-sig')
            proc = subprocess.run([SHELL, '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass',
                                   '-File', str(path)], capture_output=True, encoding='utf8', errors='replace', timeout=25)
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
        return json.loads(proc.stdout)

    def test_system32_sysnative_and_missing_executable(self):
        with tempfile.TemporaryDirectory() as tmp:
            for folder in ['System32', 'Sysnative']:
                target = Path(tmp) / folder / 'wsl.exe'
                target.parent.mkdir()
                target.touch()
            quoted = tmp.replace("'", "''")
            row = self.ps("@{ native=Resolve-WslExecutable '" + quoted + "' $true $true; "
                          "redirected=Resolve-WslExecutable '" + quoted + "' $true $false; "
                          "missing=Resolve-WslExecutable '" + quoted + "/missing' $true $true } | ConvertTo-Json")
            self.assertEqual(Path(row['native']), Path(tmp) / 'System32/wsl.exe')
            self.assertEqual(Path(row['redirected']), Path(tmp) / 'Sysnative/wsl.exe')
            self.assertIsNone(row['missing'])

    def test_native_bytes_arguments_stderr_and_exit(self):
        with tempfile.TemporaryDirectory(prefix='wsl fixture ') as tmp:
            child = Path(tmp) / 'emit.ps1'
            child.write_text(r'''param([string]$Value)
$out=[Console]::OpenStandardOutput()
$inherited = if ($env:WSL_UTF8) { 'inherited' } else { 'absent' }
$bytes=[Text.Encoding]::Unicode.GetBytes($Value + "`r`n" + $inherited)
$out.Write($bytes,0,$bytes.Length)
$err=[Console]::OpenStandardError()
$bytes=[Text.Encoding]::Unicode.GetBytes('stderr diagnostic')
$err.Write($bytes,0,$bytes.Length)
exit 17
''', encoding='utf-8-sig')
            args = [SHELL, str(child)]
            shell, path = [a.replace("'", "''") for a in args]
            row = self.ps("$env:WSL_UTF8='1'\n$r=Invoke-WslCommand '" + shell + "' @('-NoProfile','-NonInteractive',"
                          "'-ExecutionPolicy','Bypass','-File','" + path + "','Ubuntu spaced 测试')\n"
                          "@{ native=$r; parent=$env:WSL_UTF8 } | ConvertTo-Json -Depth 8")
            self.assertEqual(row['native']['ExitCode'], 17)
            self.assertEqual(row['native']['Stdout'], 'Ubuntu spaced 测试\r\nabsent')
            self.assertEqual(row['native']['Stderr'], 'stderr diagnostic')
            self.assertEqual(row['parent'], '1')

    def test_output_decoder_rejects_corruption(self):
        row = self.ps(r'''$utf16=[Text.Encoding]::Unicode.GetBytes("Ubuntu`r`n")
$failed=$false
try { ConvertFrom-WslBytes ([byte[]]@(255,255,255)) } catch { $failed=$true }
@{ utf16=ConvertFrom-WslBytes $utf16; failed=$failed } | ConvertTo-Json''')
        self.assertEqual(row['utf16'], 'Ubuntu\r\n')
        self.assertTrue(row['failed'])

    def test_native_utf16_contract_with_and_without_nul(self):
        with tempfile.TemporaryDirectory() as tmp:
            for data, names in [('65,66', ['\u4241']), ('65,0,66,0,10,0', ['AB']), ('65,66,10', None)]:
                child = Path(tmp) / 'ambiguous.ps1'
                child.write_text('$s=[Console]::OpenStandardOutput()\n$b=[byte[]]@(' + data + ')\n$s.Write($b,0,$b.Length)\nexit 0', encoding='utf-8-sig')
                shell, path = [p.replace("'", "''") for p in [SHELL, str(child)]]
                row = self.ps("Set-Item function:Invoke-Saved ${function:Invoke-WslCommand}\n"
                              "function Invoke-WslCommand { param($Executable,$Arguments) "
                              "Invoke-Saved '" + shell + "' @('-NoProfile','-NonInteractive','-ExecutionPolicy','Bypass','-File','" + path + "') }\n"
                              "Get-WslRegistrations 'fixture' | ConvertTo-Json -Depth 8")
                if names is None:
                    self.assertEqual(row['state'], 'unknown')
                    self.assertEqual(row['names'], [])
                    self.assertIn('decoding-failed', row['diagnostic'])
                else:
                    self.assertEqual(row['state'], 'listed')
                    self.assertEqual(row['names'], names)

    def test_native_corruption_makes_probe_unknown_preserving_native_exit(self):
        with tempfile.TemporaryDirectory() as tmp:
            for stream in ['Output', 'Error']:
                for code in [0, 17]:
                    with self.subTest(stream=stream, code=code):
                        child = Path(tmp) / 'corrupt.ps1'
                        child.write_text('$s=[Console]::OpenStandard' + stream + '()\n'
                                         '$b=[byte[]]@(255,255,255)\n$s.Write($b,0,$b.Length)\n'
                                         '$other=[Console]::OpenStandard' + ('Error' if stream == 'Output' else 'Output') + '()\n'
                                         "$valid=[Text.Encoding]::Unicode.GetBytes('valid native diagnostic')\n"
                                         '$other.Write($valid,0,$valid.Length)\nexit ' + str(code), encoding='utf-8-sig')
                        shell, path = [p.replace("'", "''") for p in [SHELL, str(child)]]
                        row = self.ps("Set-Item function:Invoke-Saved ${function:Invoke-WslCommand}\n"
                                      "function Invoke-WslCommand { param($Executable,$Arguments) "
                                      "Invoke-Saved '" + shell + "' @('-NoProfile','-NonInteractive','-ExecutionPolicy','Bypass','-File','" + path + "') }\n"
                                      "Get-WslRegistrations 'fixture' | ConvertTo-Json -Depth 8")
                        self.assertEqual(row['state'], 'unknown')
                        self.assertEqual(row['native_exit_code'], code)
                        self.assertIn('decoding-failed', row['diagnostic'])
                        self.assertIn('valid native diagnostic', row['diagnostic'])
                        field = 'raw_stdout_base64' if stream == 'Output' else 'raw_stderr_base64'
                        self.assertEqual(row[field], '////')
                        self.assertEqual(row['exit_code'], 1 if code == 0 else code)
                        self.assertEqual(row['names'], [])

    def test_default_plan_never_installs(self):
        row = self.run_case()
        self.assertEqual(row['result']['status'], 'planned')
        self.assertFalse(any(c[0] == '--install' for c in row['calls']))

    def test_existing_case_insensitive_nul_names_skip_even_without_admin(self):
        row = self.run_case('existing', '-Apply')
        self.assertEqual(row['result']['status'], 'already-registered')
        self.assertFalse(any(c[0] == '--install' for c in row['calls']))

    def test_stderr_never_becomes_distribution_name(self):
        row = self.run_case('target-stderr', '-Apply')
        self.assertEqual(row['result']['before']['names'], ['Debian'])
        self.assertEqual(row['result']['before']['diagnostic'], 'Ubuntu')
        self.assertTrue(any(c[0] == '--install' for c in row['calls']))
        row = self.run_case('existing-stderr', '-Apply')
        self.assertEqual(row['result']['status'], 'already-registered')
        self.assertEqual(row['result']['before']['diagnostic'], 'warning')
        self.assertFalse(any(c[0] == '--install' for c in row['calls']))

    def test_explicit_target_web_download_and_other_distribution(self):
        row = self.run_case('other', "-Apply -Distribution 'Ubuntu-24.04' -WebDownload")
        self.assertEqual([c for c in row['calls'] if c[0] == '--install'],
                         [['--install', '--distribution', 'Ubuntu-24.04', '--no-launch', '--web-download']])
        self.assertEqual(row['result']['status'], 'install-command-completed')

    def test_unknown_probe_is_never_absence_or_readiness(self):
        row = self.run_case('unknown', '-Apply')
        self.assertEqual(row['result']['before']['state'], 'unknown')
        self.assertEqual(row['result']['after']['state'], 'unknown')
        self.assertEqual(row['result']['before']['exit_code'], 5)
        self.assertEqual(row['result']['status'], 'install-command-completed')

    def test_preflight_blocks_modification(self):
        for scenario, error in [('linux', 'Windows'), ('old', '19041'),
                                ('missing', 'wsl.exe'), ('nonadmin', 'administrator'),
                                ('oldflags', '--no-launch'), ('helpfail', 'help failed')]:
            with self.subTest(scenario=scenario):
                row = self.run_case(scenario, '-Apply', error)
                self.assertFalse(any(c[0] == '--install' for c in row['calls']))

    def test_nonadmin_can_read_plan(self):
        self.assertEqual(self.run_case('nonadmin')['result']['status'], 'planned')

    def test_install_failure_preserves_native_code_and_diagnostics(self):
        row = self.run_case('fail', '-Apply')
        self.assertEqual(row['result']['status'], 'install-failed')
        self.assertEqual(row['result']['exit_code'], 17)
        self.assertEqual(row['result']['install']['Output'], 'install failed')

    def test_reboot_is_pending_without_post_probe_or_restart(self):
        row = self.run_case('reboot', '-Apply')
        self.assertEqual(row['result']['status'], 'restart-required')
        self.assertEqual(row['result']['exit_code'], 3010)
        self.assertEqual(sum(c[0] == '--list' for c in row['calls']), 1)

    def test_success_and_failed_post_probe_never_claim_ready(self):
        row = self.run_case('postfail', '-Apply')
        self.assertEqual(row['result']['after']['state'], 'unknown')
        self.assertEqual(row['result']['status'], 'install-command-completed')
        self.assertIn('first launch', row['result']['next_step'])

    def test_distribution_rejects_commands_and_option_injection(self):
        for name in ['--unregister', 'Ubuntu;whoami', 'Ubuntu&whoami', 'Ubuntu Test', '../Ubuntu']:
            with self.subTest(name=name):
                row = self.run_case(args="-Apply -Distribution '" + name + "'", expected_error='Distribution')
                self.assertFalse(row['calls'])


if __name__ == '__main__':
    unittest.main()
