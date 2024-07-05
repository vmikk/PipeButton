# Get the current user's name
$username = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name.Split('\')[-1]

# Construct the path to the .lnk file
$linkPath = "C:\Users\$username\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\pipecraft.lnk"

# Execute the .lnk file
Start-Process $linkPath
