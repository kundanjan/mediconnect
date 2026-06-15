# ============================================================
# SETUP & RUN SCRIPT - Blockchain Clinical Trial Framework
# ============================================================
# Run this script from the parent folder containing both projects
# Usage: .\setup_and_run.ps1
# ============================================================

$ErrorActionPreference = "Stop"
$ParentDir = $PSScriptRoot
$BlockchainDir = Join-Path $ParentDir "blockchain_api\blockchain_api"
$PhdDir = Join-Path $ParentDir "PHD_Project-fresh_code\PHD_Project-fresh_code"
$DeployDir = Join-Path $BlockchainDir "deploy"

# Helper to run external commands safely (ignores stderr noise)
function Invoke-SafeCommand($cmd, $args) {
    $oldPref = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $cmd
    $psi.Arguments = ($args -join " ")
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.UseShellExecute = $false
    $psi.CreateNoWindow = $true
    $proc = [System.Diagnostics.Process]::Start($psi)
    $proc.WaitForExit()
    $ErrorActionPreference = $oldPref
    return $proc.ExitCode
}

# Colors
$Green = "Green"
$Yellow = "Yellow"
$Red = "Red"
$Cyan = "Cyan"
$White = "White"

function Write-Status($msg, $color = $White) {
    Write-Host "`n[INFO] $msg" -ForegroundColor $color
}

function Write-ErrorMsg($msg) {
    Write-Host "`n[ERROR] $msg" -ForegroundColor $Red
}

function Write-Success($msg) {
    Write-Host "`n[SUCCESS] $msg" -ForegroundColor $Green
}

# ============================================================
Write-Host "============================================================" -ForegroundColor $Cyan
Write-Host "  BLOCKCHAIN CLINICAL TRIAL FRAMEWORK - SETUP & RUN" -ForegroundColor $Cyan
Write-Host "============================================================" -ForegroundColor $Cyan

# ============================================================
# STEP 1: Check Python Installation
# ============================================================
Write-Status "Checking Python installation..."

# FIX: Store exe path and args separately to avoid & operator splitting issue
$PythonExe = $null

# Try py launcher first (py -3.11)
try {
    $result = & py -3.11 --version 2>&1
    if ($result -match "Python 3\.11") {
        $PythonExe = "py"
        $PythonArgs = @("-3.11")
        Write-Status "Found Python: $result" $Green
    }
} catch {}

# Fallback to python.exe
if (-not $PythonExe) {
    try {
        $result = & python --version 2>&1
        if ($result -match "3\.1[01]") {
            $PythonExe = "python"
            $PythonArgs = @()
            Write-Status "Found Python: $result" $Green
        }
    } catch {}
}

# Fallback to direct paths
if (-not $PythonExe) {
    $PythonPaths = @(
        "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
        "$env:ProgramFiles\Python311\python.exe",
        "C:\Python311\python.exe"
    )
    foreach ($path in $PythonPaths) {
        if (Test-Path $path) {
            $PythonExe = $path
            $PythonArgs = @()
            $result = & $path --version 2>&1
            Write-Status "Found Python: $result" $Green
            break
        }
    }
}

if (-not $PythonExe) {
    Write-ErrorMsg "Python 3.11 or 3.10 not found. Please install Python 3.11 first."
    Write-Host "Download: https://www.python.org/downloads/release/python-3119/" -ForegroundColor $Yellow
    exit 1
}

# Helper to invoke python correctly regardless of how it was found
function Invoke-Python($extraArgs) {
    & $PythonExe @PythonArgs @extraArgs
}

# ============================================================
# STEP 2: Setup Virtual Environments
# ============================================================
Write-Status "Setting up virtual environments..."

# Blockchain API venv
$BlockchainVenv = Join-Path $BlockchainDir "venv"
$RecreateBlockchainVenv = $false
if (Test-Path (Join-Path $BlockchainVenv "Scripts\python.exe")) {
    $TestPip = & "$BlockchainVenv\Scripts\python.exe" -m pip --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Status "Blockchain API venv is broken, recreating..." $Yellow
        Remove-Item -Recurse -Force $BlockchainVenv -ErrorAction SilentlyContinue
        $RecreateBlockchainVenv = $true
    } else {
        Write-Status "Blockchain API venv already exists" $Green
    }
} else {
    $RecreateBlockchainVenv = $true
}

if ($RecreateBlockchainVenv) {
    Write-Status "Creating venv for blockchain_api..."
    Invoke-Python @("-m", "venv", $BlockchainVenv)
    Write-Success "Blockchain API venv created"
}

# PHD Project venv
$PhdVenv = Join-Path $PhdDir "venv"
$RecreatePhdVenv = $false
if (Test-Path (Join-Path $PhdVenv "Scripts\python.exe")) {
    $TestPip = & "$PhdVenv\Scripts\python.exe" -m pip --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Status "PHD Project venv is broken, recreating..." $Yellow
        Remove-Item -Recurse -Force $PhdVenv -ErrorAction SilentlyContinue
        $RecreatePhdVenv = $true
    } else {
        Write-Status "PHD Project venv already exists" $Green
    }
} else {
    $RecreatePhdVenv = $true
}

if ($RecreatePhdVenv) {
    Write-Status "Creating venv for PHD_Project..."
    Invoke-Python @("-m", "venv", $PhdVenv)
    Write-Success "PHD Project venv created"
}

# ============================================================
# STEP 3: Check & Install Dependencies
# ============================================================
Write-Status "Checking dependencies..."

# Blockchain API dependencies
Write-Status "Checking blockchain_api dependencies..."
$BlockchainReq = Join-Path $BlockchainDir "requirements.txt"
if (Test-Path $BlockchainReq) {
    $ExitCode = Invoke-SafeCommand "$BlockchainVenv\Scripts\python.exe" @("-m", "pip", "install", "-r", $BlockchainReq, "--quiet", "--disable-pip-version-check")
    if ($ExitCode -eq 0) {
        Write-Success "Blockchain API dependencies installed"
    } else {
        Write-ErrorMsg "Failed to install blockchain_api dependencies"
        exit 1
    }
}

# Install py-solc-x if not present
Invoke-SafeCommand "$BlockchainVenv\Scripts\python.exe" @("-m", "pip", "install", "py-solc-x", "python-dotenv", "--quiet", "--disable-pip-version-check") | Out-Null

# PHD Project dependencies
Write-Status "Checking PHD_Project dependencies..."
$PhdReq = Join-Path $PhdDir "requirements.txt"
if (Test-Path $PhdReq) {
    Write-Status "Installing PHD_Project dependencies (compatible versions)..."

    # First install setuptools < 70 to avoid build issues
    Invoke-SafeCommand "$PhdVenv\Scripts\python.exe" @("-m", "pip", "install", "setuptools<70", "--quiet", "--disable-pip-version-check") | Out-Null

    # Install packages one by one to handle failures gracefully
    $PhdPackages = @(
        "beautifulsoup4==4.12.2",
        "chardet==5.2.0",
        "defusedxml==0.7.1",
        "dj-database-url==2.1.0",
        "Django==3.2.25",
        "django-allauth==0.63.6",
        "django-appconf==1.0.6",
        "django-braces==1.15.0",
        "django-crispy-forms==1.14.0",
        "django-filter==23.5",
        "django-nose==1.4.7",
        "django-storages==1.14.2",
        "django-tagulous==1.3.3",
        "djangorestframework==3.14.0",
        "docutils==0.20.1",
        "idna==3.6",
        "jmespath==1.0.1",
        "nose==1.3.7",
        "oauthlib==3.2.2",
        "pilkit==3.0",
        "Pillow==10.2.0",
        "pandas==2.1.4",
        "psycopg2-binary==2.9.9",
        "python-dateutil==2.8.2",
        "python3-openid==3.2.0",
        "pytz==2023.3",
        "requests==2.31.0",
        "requests-oauthlib==1.3.1",
        "s3transfer==0.10.0",
        "six==1.16.0",
        "sqlparse==0.4.4",
        "tmdbsimple==2.9.1",
        "urllib3==2.1.0",
        "wheel==0.42.0",
        "whitenoise==6.6.0",
        "pytesseract==0.3.10",
        "django-import-export==3.3.7"
    )

    foreach ($pkg in $PhdPackages) {
        Write-Host "  Installing $pkg..." -NoNewline
        $ExitCode = Invoke-SafeCommand "$PhdVenv\Scripts\python.exe" @("-m", "pip", "install", $pkg, "--quiet", "--disable-pip-version-check")
        if ($ExitCode -eq 0) {
            Write-Host " OK" -ForegroundColor $Green
        } else {
            Write-Host " FAILED (skipping)" -ForegroundColor $Yellow
        }
    }

    Write-Success "PHD Project dependencies installed"
}

# ============================================================
# STEP 4: Wallet Configuration
# ============================================================
Write-Host "`n============================================================" -ForegroundColor $Cyan
Write-Host "  WALLET CONFIGURATION" -ForegroundColor $Cyan
Write-Host "============================================================" -ForegroundColor $Cyan

$CurrentWallet = "0x4Dd06BE68483cF90156521d43430D036f6986B7a"
$CurrentKey = "0xf5300dd7716a74d559e2ba27ffdccc689aaa36783eb64df4307224c97717a9cf"

Write-Host "`nCurrent wallet address: $CurrentWallet" -ForegroundColor $Yellow

$changeWallet = Read-Host "`nDo you want to change wallet address and private key? (y/n)"

if ($changeWallet -eq "y" -or $changeWallet -eq "Y") {
    Write-Host "`nEnter new wallet address:" -ForegroundColor $Cyan
    $NewWallet = Read-Host "Wallet Address"

    Write-Host "`nEnter new private key:" -ForegroundColor $Cyan
    $NewKey = Read-Host "Private Key"

    if ($NewWallet -and $NewKey) {
        $CurrentWallet = $NewWallet
        $CurrentKey = $NewKey
        Write-Success "Wallet credentials updated"
    }
}

# ============================================================
# STEP 5: Deploy Smart Contract
# ============================================================
Write-Host "`n============================================================" -ForegroundColor $Cyan
Write-Host "  SMART CONTRACT DEPLOYMENT" -ForegroundColor $Cyan
Write-Host "============================================================" -ForegroundColor $Cyan

$deployContract = Read-Host "`nDo you want to deploy the smart contract? (y/n)"

if ($deployContract -eq "y" -or $deployContract -eq "Y") {
    # Update deploy.py with wallet credentials
    $DeployScript = Join-Path $DeployDir "deploy.py"
    $DeployContent = Get-Content $DeployScript -Raw

    # Replace private key
    $DeployContent = $DeployContent -replace 'account_private_key = "0x[a-fA-F0-9]{64}"', "account_private_key = `"$CurrentKey`""

    # Replace account address
    $DeployContent = $DeployContent -replace 'account_address = "0x[a-fA-F0-9]{40}"', "account_address = `"$CurrentWallet`""

    Set-Content $DeployScript $DeployContent -NoNewline
    Write-Status "Updated deploy.py with wallet credentials" $Green

    # Run deployment
    Write-Status "Deploying smart contract..."
    Set-Location $DeployDir
    $DeployOutput = & "$BlockchainVenv\Scripts\python.exe" deploy.py 2>&1
    $DeployExitCode = $LASTEXITCODE

    if ($DeployExitCode -eq 0) {
        Write-Success "Contract deployed successfully!"
        Write-Host $DeployOutput -ForegroundColor $Green

        # Extract contract address
        $ContractAddress = ($DeployOutput | Select-String "Contract deployed at address: (.*)" | ForEach-Object { $_.Matches.Groups[1].Value }).Trim()

        if ($ContractAddress) {
            Write-Status "Contract Address: $ContractAddress" $Cyan

            # Update contract_address.txt
            $ContractFile = Join-Path $BlockchainDir "contract_address.txt"
            Set-Content $ContractFile "Contract deployed at address: $ContractAddress" -NoNewline

            # Update api/views.py
            $ViewsFile = Join-Path $BlockchainDir "api\views.py"
            $ViewsContent = Get-Content $ViewsFile -Raw
            $ViewsContent = $ViewsContent -replace "contract_address = '0x[a-fA-F0-9]{40}'", "contract_address = '$ContractAddress'"
            Set-Content $ViewsFile $ViewsContent -NoNewline

            # Update .env with ABI and credentials
            $AbiFile = Join-Path $DeployDir "abi.json"
            $AbiContent = Get-Content $AbiFile -Raw
            $EnvFile = Join-Path $BlockchainDir ".env"
            Set-Content $EnvFile "ABI=$AbiContent`nWALLET_ADDRESS=$CurrentWallet`nPRIVATE_KEY=$CurrentKey`nGANACHE_URL=HTTP://127.0.0.1:7545" -NoNewline

            Write-Success "All configuration files updated"
        }
    } else {
        Write-ErrorMsg "Contract deployment failed!"
        Write-Host $DeployOutput -ForegroundColor $Red
        Write-Host "`nMake sure Ganache is running on port 7545" -ForegroundColor $Yellow
        exit 1
    }
}

Set-Location $ParentDir

# ============================================================
# STEP 6: Run Test Suite
# ============================================================
Write-Host "`n============================================================" -ForegroundColor $Cyan
Write-Host "  RUNNING TEST SUITE" -ForegroundColor $Cyan
Write-Host "============================================================" -ForegroundColor $Cyan

$runTests = Read-Host "`nDo you want to run initial tests? (y/n)"

if ($runTests -eq "y" -or $runTests -eq "Y") {
    Write-Status "Running blockchain_api tests..."
    Set-Location $BlockchainDir
    $oldPref = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    & "$BlockchainVenv\Scripts\python.exe" manage.py test 2>&1
    $ErrorActionPreference = $oldPref

    Write-Status "Running PHD_Project tests..."
    Set-Location $PhdDir
    $ErrorActionPreference = "Continue"
    & "$PhdVenv\Scripts\python.exe" manage.py test 2>&1
    $ErrorActionPreference = $oldPref

    Set-Location $ParentDir
    Write-Success "Tests completed"
}

# ============================================================
# STEP 7: Run Both Projects
# ============================================================
Write-Host "`n============================================================" -ForegroundColor $Cyan
Write-Host "  STARTING PROJECTS" -ForegroundColor $Cyan
Write-Host "============================================================" -ForegroundColor $Cyan

# Kill any existing processes on ports 8000 and 8003
Write-Status "Checking for existing processes..."
$Port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
$Port8003 = Get-NetTCPConnection -LocalPort 8003 -ErrorAction SilentlyContinue

if ($Port8000) {
    Write-Status "Killing process on port 8000..." $Yellow
    Stop-Process -Id $Port8000.OwningProcess -Force -ErrorAction SilentlyContinue
}

if ($Port8003) {
    Write-Status "Killing process on port 8003..." $Yellow
    Stop-Process -Id $Port8003.OwningProcess -Force -ErrorAction SilentlyContinue
}

Start-Sleep -Seconds 2

# Start PHD Project on port 8000
Write-Status "Starting PHD_Project on port 8000..."
$PhdProcess = Start-Process -FilePath "$PhdVenv\Scripts\python.exe" `
    -ArgumentList "manage.py", "runserver", "127.0.0.1:8000" `
    -WorkingDirectory $PhdDir `
    -PassThru `
    -WindowStyle Normal

Start-Sleep -Seconds 3

# Start Blockchain API on port 8003
Write-Status "Starting Blockchain API on port 8003..."
$BlockchainProcess = Start-Process -FilePath "$BlockchainVenv\Scripts\python.exe" `
    -ArgumentList "manage.py", "runserver", "127.0.0.1:8003" `
    -WorkingDirectory $BlockchainDir `
    -PassThru `
    -WindowStyle Normal

Start-Sleep -Seconds 3

# ============================================================
# STEP 8: Display Results
# ============================================================
Write-Host "`n============================================================" -ForegroundColor $Cyan
Write-Host "  PROJECTS ARE RUNNING" -ForegroundColor $Green
Write-Host "============================================================" -ForegroundColor $Cyan

Write-Host @"

  +-----------------------------------------------------------+
  |  PHD PROJECT (Main Application)                           |
  |  URL: http://127.0.0.1:8000                               |
  |  PID: $($PhdProcess.Id)                                    |
  +-----------------------------------------------------------+

  +-----------------------------------------------------------+
  |  BLOCKCHAIN API                                           |
  |  URL: http://127.0.0.1:8003                               |
  |  PID: $($BlockchainProcess.Id)                             |
  +-----------------------------------------------------------+

  +-----------------------------------------------------------+
  |  GANACHE (Local Blockchain)                               |
  |  URL: HTTP://127.0.0.1:7545                               |
  +-----------------------------------------------------------+

"@ -ForegroundColor $White

Write-Host "  To stop the servers, close the terminal windows or press Ctrl+C" -ForegroundColor $Yellow
Write-Host "`n============================================================`n" -ForegroundColor $Cyan