#define AppName "Gestão de Carreira Assistente"
#define AppVersion "1.0.3"
#define AppPublisher "Gestão de Carreira"
#define AppExeName "GestaoDeCarreira-Assistente.exe"

[Setup]
AppId={{B8B8B1F3-1A55-4B94-8FB2-1A7B9B20F7F4}}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL=https://www.portaldoservidor.mg.gov.br/
AppSupportURL=https://www.portaldoservidor.mg.gov.br/
AppUpdatesURL=https://www.portaldoservidor.mg.gov.br/
DefaultDirName={localappdata}\GestaoDeCarreira\Assistente
DefaultGroupName={#AppName}
DisableDirPage=yes
DisableProgramGroupPage=yes
OutputBaseFilename=GestaoDeCarreira-Setup-1.0.3
OutputDir=..\..\backend\static\downloads
SetupIconFile=..\assets\installer-icon.ico
UninstallDisplayIcon={app}\{#AppExeName}
Compression=lzma2
SolidCompression=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
WizardStyle=modern
VersionInfoVersion=1.0.3.0
VersionInfoTextVersion={#AppVersion}
VersionInfoProductName={#AppName}
VersionInfoProductVersion={#AppVersion}
VersionInfoCompany={#AppPublisher}
VersionInfoDescription=Instalador do assistente Windows de importação de contracheques.
VersionInfoCopyright=Copyright (C) 2026 Gestão de Carreira

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "Criar ícone na área de trabalho"; GroupDescription: "Ícones adicionais:"; Flags: unchecked

[Files]
Source: "..\dist\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"; WorkingDir: "{app}"
Name: "{userdesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Abrir {#AppName} agora"; Flags: postinstall nowait skipifsilent

[Registry]
Root: HKCU; Subkey: "Software\Classes\gestaodecarreira"; ValueType: string; ValueName: ""; ValueData: "URL:Gestão de Carreira"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\gestaodecarreira"; ValueType: string; ValueName: "URL Protocol"; ValueData: ""; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\gestaodecarreira\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#AppExeName}"" ""%1"""; Flags: uninsdeletekey
