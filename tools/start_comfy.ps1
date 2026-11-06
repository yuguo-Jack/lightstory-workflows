param(
    [ValidateSet('Default','Balanced','Conservative','PixalStable')][string]$Profile='Balanced',
    [string]$Config,
    [switch]$PlanOnly
)
$ErrorActionPreference='Stop'
$arguments=@('-B','-X','utf8',(Join-Path $PSScriptRoot 'lightstory.py'))
if ($Config) { $arguments+=@('--config',$Config) }
$arguments+=@('runtime','start','--profile',$Profile)
if (-not $PlanOnly) { $arguments+='--apply' }
& python @arguments
exit $LASTEXITCODE
