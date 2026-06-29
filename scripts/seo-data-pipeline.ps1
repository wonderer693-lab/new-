<#
.SYNOPSIS
  SEO Data Pipeline for Hyper-Vertical API Integrations Hub
.DESCRIPTION
  Validates JSON files and rebuilds the master index.
  Usage: .\scripts\seo-data-pipeline.ps1 -Action All
#>

param(
  [ValidateSet("All", "IndexOnly", "Validate")]
  [string]$Action = "All"
)

$ProjectRoot = Resolve-Path "$PSScriptRoot\.."
$DataDir = "$ProjectRoot\data"
$ProcessedDir = "$DataDir\processed"
$IntegrationsDir = "$ProcessedDir\integrations"
$MasterIndexFile = "$ProcessedDir\master-integration-hub-index.json"

Write-Host "=== SEO Data Pipeline ===" -ForegroundColor Cyan
Write-Host "Project: $ProjectRoot"
Write-Host "Action: $Action"
Write-Host ""

function Test-JsonFile {
  param([string]$Path)
  try {
    $content = Get-Content $Path -Raw -ErrorAction Stop
    $null = $content | ConvertFrom-Json
    return $true
  } catch {
    Write-Host "  FAILED: $Path" -ForegroundColor Red
    Write-Host "  Error: $_" -ForegroundColor Red
    return $false
  }
}

function Invoke-ValidateAll {
  Write-Host "[Validate] Scanning all JSON files..." -ForegroundColor Yellow
  $files = Get-ChildItem $ProcessedDir -Recurse -Filter "*.json"
  $valid = 0; $invalid = 0
  foreach ($file in $files) {
    if (Test-JsonFile $file.FullName) {
      Write-Host "  OK: $($file.Name)" -ForegroundColor Green
      $valid++
    } else {
      $invalid++
    }
  }
  Write-Host "[Validate] $valid valid, $invalid invalid" -ForegroundColor Green
  return ($invalid -eq 0)
}

function Build-MasterIndex {
  Write-Host "[Index] Building master index..." -ForegroundColor Yellow
  $tools = @()
  $integrations = @()
  $totalErrors = 0
  $totalCommunity = 0

  $toolFiles = Get-ChildItem $ProcessedDir -Filter "*-api-data.json" | Where-Object { $_.Name -ne "master-integration-hub-index.json" }
  foreach ($tf in $toolFiles) {
    try {
      $data = Get-Content $tf.FullName -Raw | ConvertFrom-Json
      $eCount = ($data.error_dictionary | Measure-Object).Count
      $cCount = ($data.community_constraints | Measure-Object).Count
      $tools += @{
        id = $data.tool_id
        name = $data.tool_name
        category = $data.category
        data_file = $tf.Name
        api_version = if ($data.api_version) { $data.api_version } else { "N/A" }
        auth_type = if ($data.authentication.mechanisms) { $data.authentication.mechanisms[0].type } else { "See file" }
        rate_limits = if ($data.rate_limits.error_on_exceed) { $data.rate_limits.error_on_exceed } else { "See file" }
        errors = $eCount
        community_issues = $cCount
      }
      $totalErrors += $eCount
      $totalCommunity += $cCount
    } catch {
      Write-Host "  SKIP: $($tf.Name) - parse error" -ForegroundColor Yellow
    }
  }

  if (Test-Path $IntegrationsDir) {
    $intFiles = Get-ChildItem $IntegrationsDir -Filter "*.json"
    foreach ($intf in $intFiles) {
      try {
        $data = Get-Content $intf.FullName -Raw | ConvertFrom-Json
        $eCount = ($data.edge_cases_and_errors | Measure-Object).Count
        $keywords = if ($data.search_volume_keywords) { $data.search_volume_keywords[0..2] } else { @() }
        $integrations += @{
          id = $data.integration_id
          name = $data.integration_name
          data_file = "integrations/$($intf.Name)"
          sync_type = $data.sync_type
          errors = $eCount
          top_keywords = $keywords
        }
        $totalErrors += $eCount
      } catch {
        Write-Host "  SKIP: $($intf.Name) - parse error" -ForegroundColor Yellow
      }
    }
  }

  # Write master index
  $index = @{
    project = "Hyper-Vertical API Integrations Hub"
    niche = "CRM & Sales Automation"
    schema_version = "1.0.0"
    generated = (Get-Date -Format "yyyy-MM-dd")
    total_tools = $tools.Count
    total_integration_pairs = $integrations.Count
    total_error_solutions = $totalErrors
    total_community_mining = $totalCommunity
    tools = $tools
    integration_pairs = $integrations
  }

  $index | ConvertTo-Json -Depth 10 | Set-Content $MasterIndexFile -Encoding UTF8
  Write-Host "[Index] Done. $($tools.Count) tools, $($integrations.Count) pairs, $totalErrors solutions" -ForegroundColor Green
}

# Execute
if ($Action -in @("All","Validate")) {
  $ok = Invoke-ValidateAll
  if (-not $ok -and $Action -eq "Validate") { exit 1 }
}
if ($Action -in @("All","IndexOnly")) {
  Build-MasterIndex
}

Write-Host "=== Done ===" -ForegroundColor Cyan
