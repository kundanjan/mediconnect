param(
    [string]$BaseUrl = "http://127.0.0.1:8000"
)

$ErrorActionPreference = "Stop"

$projectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $projectRoot

$env:DISABLE_EXTERNAL_APIS = "1"
$env:E2E_BASE_URL = $BaseUrl

.\venv\Scripts\Activate.ps1

python -m pip install pytest pytest-django pytest-playwright playwright
python -m playwright install

python manage.py migrate
python manage.py flush --noinput
python scripts\seed_test_data.py

$server = Start-Process -FilePath "python" -ArgumentList "manage.py","runserver","127.0.0.1:8000","--noreload" -PassThru

try {
    $ready = $false
    for ($i = 0; $i -lt 30; $i++) {
        try {
            Invoke-WebRequest -Uri "$BaseUrl/" -UseBasicParsing -TimeoutSec 2 | Out-Null
            $ready = $true
            break
        } catch {
            Start-Sleep -Seconds 1
        }
    }

    if (-not $ready) {
        throw "Server did not start on $BaseUrl"
    }

    pytest -m "not e2e"
    pytest -m "e2e"
} finally {
    if ($server -and -not $server.HasExited) {
        Stop-Process -Id $server.Id
    }
}
