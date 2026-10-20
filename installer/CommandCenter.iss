#ifndef AppBuildVersion
  #define AppBuildVersion "2.0.0"
#endif
#define ProductName "SheldonTwitching - Command Center"
[Setup]
AppId={{B6122707-28A9-47A8-B986-E4EC487FE81D}
AppName={#ProductName}
AppVersion={#AppBuildVersion}
AppPublisher=SheldonTwitching
AppPublisherURL=https://www.twitch.tv/SheldonTwitching
DefaultDirName={localappdata}\Programs\SheldonTwitchingCommandCenter
DefaultGroupName={#ProductName}
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir=..\dist
OutputBaseFilename=SheldonTwitching-Command-Center-Setup-{#AppBuildVersion}
SetupIconFile=..\assets\ST-Command-Center.ico
UninstallDisplayIcon={app}\{#ProductName}.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
CloseApplications=yes
RestartApplications=no
DisableProgramGroupPage=yes
[Tasks]
Name: desktopicon; Description: "Create a desktop shortcut"; Flags: unchecked
[Files]
Source: "..\dist\{#ProductName}.exe"; DestDir: "{app}"; Flags: ignoreversion
[Icons]
Name: "{group}\{#ProductName}"; Filename: "{app}\{#ProductName}.exe"
Name: "{autodesktop}\{#ProductName}"; Filename: "{app}\{#ProductName}.exe"; Tasks: desktopicon
[Run]
Filename: "{app}\{#ProductName}.exe"; Description: "Open Command Center"; Flags: nowait postinstall skipifsilent
; No AppData/profile files are installed or removed. Stable AppId upgrades in place.
