param([string]$Config,[switch]$Cancel,[switch]$PlanOnly)
$ErrorActionPreference='Stop'
$arguments=@('-B','-X','utf8',(Join-Path $PSScriptRoot 'lightstory.py'))
if ($Config) { $arguments+=@('--config',$Config) }
$arguments+=@('runtime','stop')
if ($Cancel) { $arguments+='--cancel' }
if (-not $PlanOnly) { $arguments+='--apply' }
& python @arguments
exit $LASTEXITCODE
