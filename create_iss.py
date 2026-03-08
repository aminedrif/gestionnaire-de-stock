"""Generate a clean Inno Setup script file"""

content = r"""[Setup]
AppName=DamDev POS
AppVersion=1.0
AppPublisher=DamDev
DefaultDirName={autopf}\DamDevPOS
DefaultGroupName=DamDev POS
OutputDir=dist
OutputBaseFilename=DamDevPOS_Setup
SetupIconFile=resources\images\logo.ico
Compression=lzma
SolidCompression=yes
PrivilegesRequired=lowest
DisableProgramGroupPage=yes
UninstallDisplayIcon={app}\DamDevPOS.exe

[Files]
Source: "dist\DamDevPOS.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\DamDev POS"; Filename: "{app}\DamDevPOS.exe"
Name: "{userdesktop}\DamDev POS"; Filename: "{app}\DamDevPOS.exe"

[Run]
Filename: "{app}\DamDevPOS.exe"; Description: "Launch DamDev POS"; Flags: nowait postinstall skipifsilent
"""

with open('installer.iss', 'w', encoding='utf-8-sig', newline='\r\n') as f:
    f.write(content.strip() + '\r\n')

print("installer.iss created successfully!")
