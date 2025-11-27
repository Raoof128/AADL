<#
.SYNOPSIS
    Simulated ADCS template scanner to highlight ESC conditions.
.NOTES
    Operates on exported template metadata in JSON/YAML; does not contact AD.
#>

param(
    [string]$ConfigPath = "../data/sample_templates.yaml"
)

if (!(Test-Path -Path $ConfigPath)) {
    Write-Error "Config path $ConfigPath not found"
    exit 1
}

# Simple YAML->PSObject conversion using ConvertFrom-Yaml available in modern PowerShell
$templates = (Get-Content -Raw -Path $ConfigPath | ConvertFrom-Yaml).certificate_templates

$findings = @()
foreach ($template in $templates) {
    if ($template.subject_name_editable -and -not $template.manager_approval_required) {
        $findings += [pscustomobject]@{
            Template       = $template.name
            Severity       = 'High'
            Description    = 'Subject name editable without approval (ESC1 risk)'
            Recommendation = 'Disable subject editing or require manager approval'
        }
    }
}

if ($findings.Count -eq 0) {
    Write-Host "No misconfigurations found" -ForegroundColor Green
} else {
    $findings | Format-Table -AutoSize
}
