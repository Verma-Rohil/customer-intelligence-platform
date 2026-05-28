$ErrorActionPreference = 'Stop'
$NewPassword = 'MySQL_Root_2026!'
$InitFile = "$env:TEMP\mysql-init.txt"
$MysqldPath = 'C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqld.exe'
$MyIni = 'C:\ProgramData\MySQL\MySQL Server 8.0\my.ini'

Write-Host '=== MySQL Root Password Reset ===' -ForegroundColor Cyan

# Step 1: Create init file
"ALTER USER 'root'@'localhost' IDENTIFIED BY '$NewPassword';" | Out-File $InitFile -Encoding ascii
Write-Host '[1/5] Init file created.' -ForegroundColor Green

# Step 2: Stop service
Write-Host '[2/5] Stopping MySQL80 service...' -ForegroundColor Green
net stop MySQL80 2>$null
Start-Sleep -Seconds 2

# Step 3: Start mysqld with init-file
Write-Host '[3/5] Applying new password...' -ForegroundColor Green
$proc = Start-Process -FilePath $MysqldPath -ArgumentList "--defaults-file=`"$MyIni`"","--init-file=`"$InitFile`"","--console" -PassThru -WindowStyle Hidden
Start-Sleep -Seconds 12

# Step 4: Kill temp mysqld and cleanup
Write-Host '[4/5] Stopping temp process and cleaning up...' -ForegroundColor Green
Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 3
Remove-Item $InitFile -Force -ErrorAction SilentlyContinue

# Step 5: Restart service
Write-Host '[5/5] Restarting MySQL80 service...' -ForegroundColor Green
net start MySQL80

Write-Host ''
Write-Host '=== DONE! ===' -ForegroundColor Green
Write-Host "New root password: $NewPassword" -ForegroundColor Yellow
Write-Host 'Test with:  mysql -u root -p' -ForegroundColor Gray
