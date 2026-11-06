param(
    [Parameter(Mandatory=$true)][string]$Video,
    [Parameter(Mandatory=$true)][string]$Rig,
    [Parameter(Mandatory=$true)][string]$OutputDir,
    [string]$Skeleton,
    [switch]$DetectHands,
    [switch]$NoPreview,
    [string]$ToolRoot,
    [string]$Python
)
$ErrorActionPreference='Stop'
$settings = $null
if (-not $ToolRoot -or -not $Python) {
    $settings = & python -B -X utf8 -c 'from lightstory.config import Config; import json; c=Config.load(); print(json.dumps({"root":str(c.path("motion2mixamorig_root") or ""),"python":c.executable("motion_python")}))' | ConvertFrom-Json
    if ($LASTEXITCODE -ne 0) { throw 'Cannot read LightStory configuration; pass -ToolRoot and -Python explicitly' }
}
$motionRoot = if ($ToolRoot) { (Resolve-Path -LiteralPath $ToolRoot).Path } elseif ($settings.root) { (Resolve-Path -LiteralPath $settings.root).Path } else { throw 'Configure motion2mixamorig_root or pass -ToolRoot' }
if (-not (Test-Path -LiteralPath (Join-Path $motionRoot 'motion2mixamorig') -PathType Container)) { throw 'Pass -ToolRoot with the installed Motion2MixamoRig repository; this adapter is not the backend.' }
$externalPython = if ($Python) { (Resolve-Path -LiteralPath $Python).Path } elseif ($settings.python) { (Resolve-Path -LiteralPath $settings.python).Path } else { Join-Path $motionRoot '.venv\Scripts\python.exe' }
$videoPath=(Resolve-Path -LiteralPath $Video).Path
$rigPath=(Resolve-Path -LiteralPath $Rig).Path
$outputPath=[System.IO.Path]::GetFullPath($OutputDir)
if(-not(Test-Path -LiteralPath $outputPath)){New-Item -ItemType Directory -Path $outputPath | Out-Null}
$runtimePath=Join-Path $outputPath 'runtime'
foreach($name in @('temp','matplotlib','yolo')){
    $folder=Join-Path $runtimePath $name
    if(-not(Test-Path -LiteralPath $folder)){New-Item -ItemType Directory -Path $folder | Out-Null}
}
$env:TEMP=Join-Path $runtimePath 'temp'
$env:TMP=$env:TEMP
$env:TMPDIR=$env:TEMP
$env:MPLCONFIGDIR=Join-Path $runtimePath 'matplotlib'
$env:YOLO_CONFIG_DIR=Join-Path $runtimePath 'yolo'
$env:TORCH_HOME=Join-Path $motionRoot 'weights\rtmpose'
$env:GVHMR_CHECKPOINTS=Join-Path $motionRoot 'weights'
$env:GVHMR_BODY_MODELS=Join-Path $motionRoot 'assets\body_models'
if (-not $env:HF_HOME) { $env:HF_HOME=Join-Path $motionRoot '.cache\huggingface' }
$env:HF_HUB_DISABLE_XET='1'
$env:PYTHONUTF8='1'
$env:PYTHONDONTWRITEBYTECODE='1'
$env:OPENBLAS_NUM_THREADS='1'
$env:OMP_NUM_THREADS='4'
$arguments=@('-B','-X','utf8','-m','motion2mixamorig.cli','run','--video',$videoPath,'--rig',$rigPath,'--device','cuda','--output-dir',$outputPath,'--progress-jsonl',(Join-Path $outputPath 'progress.jsonl'))
if($Skeleton){$arguments+=@('--skeleton',(Resolve-Path -LiteralPath $Skeleton).Path)}
if($DetectHands){$arguments+=@('--detect-hands','--hand-smooth','0.08')}
if($NoPreview){$arguments+='--no-preview'}
& $externalPython @arguments
exit $LASTEXITCODE
