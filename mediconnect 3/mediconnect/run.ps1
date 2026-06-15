# ============================================================
# RUN SCRIPT - Blockchain Clinical Trial Framework
# ============================================================
# Usage: .\run.ps1
# ============================================================

$ErrorActionPreference = "Stop"
$ParentDir = $PSScriptRoot
$BlockchainDir = Join-Path $ParentDir "blockchain_api\blockchain_api"
$PhdDir = Join-Path $ParentDir "PHD_Project-fresh_code\PHD_Project-fresh_code"
$DeployDir = Join-Path $BlockchainDir "deploy"
$BlockchainVenv = Join-Path $BlockchainDir "venv"
$PhdVenv = Join-Path $PhdDir "venv"
$EnvFile = Join-Path $BlockchainDir ".env"

function Write-Status($msg, $color = "White") {
    Write-Host ""
    Write-Host "[INFO] $msg" -ForegroundColor $color
}

function Write-ErrorMsg($msg) {
    Write-Host ""
    Write-Host "[ERROR] $msg" -ForegroundColor "Red"
}

function Write-Success($msg) {
    Write-Host ""
    Write-Host "[SUCCESS] $msg" -ForegroundColor "Green"
}

function Write-Sep {
    Write-Host "============================================================" -ForegroundColor "Cyan"
}

Write-Sep
Write-Host "  BLOCKCHAIN CLINICAL TRIAL FRAMEWORK - RUN" -ForegroundColor "Cyan"
Write-Sep

# ============================================================
# STEP 1: Wallet Configuration
# ============================================================
Write-Host ""
Write-Sep
Write-Host "  WALLET CONFIGURATION" -ForegroundColor "Cyan"
Write-Sep

# Read credentials from .env
$CurrentWallet = ""
$CurrentKey = ""

if (Test-Path $EnvFile) {
    $EnvLines = Get-Content $EnvFile
    foreach ($line in $EnvLines) {
        if ($line -match "^WALLET_ADDRESS=(.+)$") {
            $CurrentWallet = $Matches[1].Trim()
        }
        if ($line -match "^PRIVATE_KEY=(.+)$") {
            $CurrentKey = $Matches[1].Trim()
        }
    }
}

if (-not $CurrentWallet -or -not $CurrentKey) {
    Write-Status "No existing credentials found in .env - you must enter them below." "Yellow"
    $CurrentWallet = "N/A"
    $CurrentKey = "N/A"
}

$WalletChanged = $false

Write-Host ""
Write-Host "Current wallet address: $CurrentWallet" -ForegroundColor "Yellow"

$changeWallet = Read-Host "Do you want to change wallet address and private key? (y/n)"

if ($changeWallet -eq "y" -or $changeWallet -eq "Y") {
    Write-Host ""
    Write-Host "Enter new wallet address:" -ForegroundColor "Cyan"
    $NewWallet = Read-Host "Wallet Address"

    Write-Host ""
    Write-Host "Enter new private key:" -ForegroundColor "Cyan"
    $NewKey = Read-Host "Private Key"

    if ($NewWallet -and $NewKey) {
        $CurrentWallet = $NewWallet
        $CurrentKey = $NewKey
        $WalletChanged = $true
        Write-Success "Wallet credentials updated"
    } else {
        Write-Status "No input provided, keeping existing credentials." "Yellow"
    }
} else {
    Write-Status "Keeping existing wallet credentials. Skipping deployment." "Yellow"
}

# ============================================================
# STEP 2: Deploy + Update ABI (only if wallet changed)
# ============================================================
$ContractAddress = "unchanged"

if ($WalletChanged) {
    Write-Host ""
    Write-Sep
    Write-Host "  SMART CONTRACT DEPLOYMENT" -ForegroundColor "Cyan"
    Write-Sep

    $DeployScript = Join-Path $DeployDir "deploy.py"
    $DeployContent = Get-Content $DeployScript -Raw

    $DeployContent = $DeployContent -replace 'account_private_key = "0x[a-fA-F0-9]{64}"', "account_private_key = `"$CurrentKey`""
    $DeployContent = $DeployContent -replace 'account_address = "0x[a-fA-F0-9]{40}"', "account_address = `"$CurrentWallet`""
    Set-Content $DeployScript $DeployContent -NoNewline
    Write-Status "Injected wallet credentials into deploy.py" "Green"

    Write-Status "Deploying smart contract - make sure Ganache is running on port 7545..."
    Set-Location $DeployDir

    $oldPref = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $DeployOutput = & "$BlockchainVenv\Scripts\python.exe" deploy.py 2>&1
    $DeployExitCode = $LASTEXITCODE
    $ErrorActionPreference = $oldPref

    if ($DeployExitCode -ne 0) {
        Write-ErrorMsg "Contract deployment failed!"
        Write-Host $DeployOutput -ForegroundColor "Red"
        Write-Host "Make sure Ganache is running on HTTP://127.0.0.1:7545" -ForegroundColor "Yellow"
        exit 1
    }

    Write-Success "Contract deployed successfully!"
    Write-Host $DeployOutput -ForegroundColor "Green"

    $ContractAddress = ($DeployOutput | Select-String "Contract deployed at address: (.*)" | ForEach-Object { $_.Matches.Groups[1].Value } | Select-Object -First 1).Trim()

    if (-not $ContractAddress) {
        Write-ErrorMsg "Could not extract contract address from deployment output."
        exit 1
    }

    Write-Status "Contract Address: $ContractAddress" "Cyan"

    # Update config files
    Write-Host ""
    Write-Sep
    Write-Host "  UPDATING ABI AND CONFIG FILES" -ForegroundColor "Cyan"
    Write-Sep

    $ContractFile = Join-Path $BlockchainDir "contract_address.txt"
    Set-Content $ContractFile "Contract deployed at address: $ContractAddress" -NoNewline
    Write-Status "Updated contract_address.txt" "Green"

    $ViewsFile = Join-Path $BlockchainDir "api\views.py"
    $ViewsContent = Get-Content $ViewsFile -Raw
    $ViewsContent = $ViewsContent -replace "contract_address = '0x[a-fA-F0-9]{40}'", "contract_address = '$ContractAddress'"
    Set-Content $ViewsFile $ViewsContent -NoNewline
    Write-Status "Updated api/views.py" "Green"

    $AbiFile = Join-Path $DeployDir "abi.json"
    $AbiContent = Get-Content $AbiFile -Raw
    Set-Content $EnvFile "ABI=$AbiContent`nWALLET_ADDRESS=$CurrentWallet`nPRIVATE_KEY=$CurrentKey`nGANACHE_URL=HTTP://127.0.0.1:7545" -NoNewline
    Write-Status "Updated .env with ABI and credentials" "Green"

    Write-Success "All config files updated"
    Set-Location $ParentDir
}

# ============================================================
# STEP 3: Start Both Projects
# ============================================================
Write-Host ""
Write-Sep
Write-Host "  STARTING PROJECTS" -ForegroundColor "Cyan"
Write-Sep

Write-Status "Checking for existing processes on ports 8000 and 8003..."

$Port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
$Port8003 = Get-NetTCPConnection -LocalPort 8003 -ErrorAction SilentlyContinue

if ($Port8000) {
    Write-Status "Killing existing process on port 8000..." "Yellow"
    Stop-Process -Id $Port8000.OwningProcess -Force -ErrorAction SilentlyContinue
}
if ($Port8003) {
    Write-Status "Killing existing process on port 8003..." "Yellow"
    Stop-Process -Id $Port8003.OwningProcess -Force -ErrorAction SilentlyContinue
}

Start-Sleep -Seconds 2

Write-Status "Starting PHD_Project on port 8000..."
$PhdProcess = Start-Process -FilePath "$PhdVenv\Scripts\python.exe" `
    -ArgumentList "manage.py", "runserver", "127.0.0.1:8000" `
    -WorkingDirectory $PhdDir `
    -PassThru `
    -WindowStyle Normal

Start-Sleep -Seconds 3

Write-Status "Starting Blockchain API on port 8003..."
$BlockchainProcess = Start-Process -FilePath "$BlockchainVenv\Scripts\python.exe" `
    -ArgumentList "manage.py", "runserver", "127.0.0.1:8003" `
    -WorkingDirectory $BlockchainDir `
    -PassThru `
    -WindowStyle Normal

Start-Sleep -Seconds 3
Write-Success "Both projects started"

# ============================================================
# STEP 4: Display Status
# ============================================================
Write-Host ""
Write-Sep
Write-Host "  ALL DONE - PROJECTS ARE RUNNING" -ForegroundColor "Green"
Write-Sep
Write-Host ""
Write-Host "  PHD PROJECT" -ForegroundColor "White"
Write-Host "  URL : http://127.0.0.1:8000" -ForegroundColor "White"
Write-Host "  PID : $($PhdProcess.Id)" -ForegroundColor "White"
Write-Host ""
Write-Host "  BLOCKCHAIN API" -ForegroundColor "White"
Write-Host "  URL : http://127.0.0.1:8003" -ForegroundColor "White"
Write-Host "  PID : $($BlockchainProcess.Id)" -ForegroundColor "White"
Write-Host ""
Write-Host "  GANACHE" -ForegroundColor "White"
Write-Host "  URL      : HTTP://127.0.0.1:7545" -ForegroundColor "White"
Write-Host "  Contract : $ContractAddress" -ForegroundColor "White"
Write-Host ""
Write-Sep
Write-Host "  To stop the servers, close the terminal windows or press Ctrl+C" -ForegroundColor "Yellow"
Write-Sep