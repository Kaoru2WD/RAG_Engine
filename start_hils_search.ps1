$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$python = "python"
$url = "http://127.0.0.1:8000/ui"

Start-Process -FilePath $python -ArgumentList @("-m", "uvicorn", "rag_engine.main:app", "--app-dir", "src", "--host", "127.0.0.1", "--port", "8000") -WorkingDirectory $root -WindowStyle Hidden
Start-Sleep -Seconds 2
Start-Process $url
