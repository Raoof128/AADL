<#
.SYNOPSIS
    Generates example variables for the ADCS lab in a safe, offline manner.
#>

param(
    [string]$OutputPath = "../terraform/terraform.tfvars"
)

$content = @"
lab_name = \"adcs-lab\"
vm_count = 2
"@

Set-Content -Path $OutputPath -Value $content -Encoding UTF8
Write-Host "Wrote example Terraform variables to $OutputPath"
