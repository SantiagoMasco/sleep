$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

function Get-SettingsWindow {
    $desktop = [System.Windows.Automation.AutomationElement]::RootElement
    $windows = $desktop.FindAll(
        [System.Windows.Automation.TreeScope]::Children,
        [System.Windows.Automation.Condition]::TrueCondition
    )
    foreach ($window in $windows) {
        if ($window.Current.Name -match 'Configuraci.n|Settings') {
            return $window
        }
    }
    return $null
}

function Get-ActionButton([System.Windows.Automation.AutomationElement]$window, [string]$pattern) {
    $elements = $window.FindAll(
        [System.Windows.Automation.TreeScope]::Descendants,
        [System.Windows.Automation.Condition]::TrueCondition
    )
    foreach ($element in $elements) {
        if ($element.Current.Name -match $pattern) {
            try {
                [System.Windows.Automation.InvokePattern]$invoke = $element.GetCurrentPattern(
                    [System.Windows.Automation.InvokePattern]::Pattern
                )
                return $invoke
            }
            catch {
                continue
            }
        }
    }
    return $null
}

function Invoke-Action([System.Windows.Automation.AutomationElement]$window, [string]$pattern) {
    $button = Get-ActionButton $window $pattern
    if ($null -eq $button) {
        return $false
    }
    $button.Invoke()
    Start-Sleep -Milliseconds 500
    return $true
}

Start-Process 'ms-settings:nightlight'
$window = $null
for ($attempt = 0; $attempt -lt 20 -and $null -eq $window; $attempt++) {
    Start-Sleep -Milliseconds 150
    $window = Get-SettingsWindow
}
if ($null -eq $window) {
    throw 'No se pudo abrir Configuracion de Luz nocturna.'
}

$turnOff = '^Desactivar ahora$|^Turn off now$'
if (-not (Invoke-Action $window $turnOff)) {
    # No off button means the official UI already reports Night Light off.
    Write-Output 'Luz nocturna ya estaba apagada.'
    exit 0
}

Write-Output 'Luz nocturna apagada.'
