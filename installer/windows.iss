#define AppName "PDV SAT Pro"
#define AppVersion "1.0.0"
#ifndef Arch
  #define Arch "x64"
#endif

[Setup]
AppId={{8D8D75E5-34B6-49B2-9865-3C934CE227D0}
AppName={#AppName}
AppVersion={#AppVersion}
DefaultDirName={autopf}\PDV SAT Pro
DefaultGroupName=PDV SAT Pro
OutputDir=..\dist
OutputBaseFilename=PDV-SAT-Pro-Windows-{#Arch}-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
#if Arch == "x64"
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
#endif

[Files]
Source: "..\dist\PDV-SAT-Pro.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\PDV SAT Pro"; Filename: "{app}\PDV-SAT-Pro.exe"
Name: "{autodesktop}\PDV SAT Pro"; Filename: "{app}\PDV-SAT-Pro.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na área de trabalho"; GroupDescription: "Atalhos:"

[Run]
Filename: "{app}\PDV-SAT-Pro.exe"; Description: "Abrir PDV SAT Pro"; Flags: nowait postinstall skipifsilent

