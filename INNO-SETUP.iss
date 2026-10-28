#define AppName "SmartStitch"
#define AppVersion "3.1.0"
[Setup]
AppId={{83E4C16B-464E-4FE7-9FAF-83952EEB7804}
AppName={#AppName}
AppVersion={#AppVersion}
DefaultDirName={localappdata}\Programs\SmartStitch
DefaultGroupName={#AppName}
OutputDir=installer
OutputBaseFilename=SmartStitch
Compression=lzma
SolidCompression=yes
PrivilegesRequired=lowest
[Files]
Source: "dist\SmartStitch\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion
[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\SmartStitch.exe"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\SmartStitch.exe"; Tasks: desktopicon
[Tasks]
Name: "desktopicon"; Description: "Criar atalho na area de trabalho"; Flags: unchecked
