; Smart SVN Commit 安装程序
; 编译命令: makensis installer.nsi

!define APPNAME "Smart SVN Commit"
!define COMPANYNAME "Smart SVN Commit"
!define DESCRIPTION "AI 驱动的 SVN 提交助手"
!define VERSIONMAJOR 3
!define VERSIONMINOR 0
!define VERSIONBUILD 4
!define HELPURL "https://github.com/hi-fangj/smart-svn-commit" ; 请修改为实际的仓库 URL
!define UPDATEURL "https://github.com/hi-fangj/smart-svn-commit"
!define ABOUTURL "https://github.com/hi-fangj/smart-svn-commit"
!define INSTALLSIZE 50000 ; 估算大小（KB）

!define DISPLAYNAME "${APPNAME} ${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}"

; 包含现代 UI
!include "MUI2.nsh"
!include "WinMessages.nsh"

; StrReplace 宏实现
!define StrReplace "!insertmacro StrReplace"
!macro StrReplace Result String Substring Replacement
  Push `${String}`
  Push `${Substring}`
  Push `${Replacement}`
  Call StrReplace
  Pop `${Result}`
!macroend

; 卸载版本的 StrReplace 宏
!define un.StrReplace "!insertmacro un.StrReplace"
!macro un.StrReplace Result String Substring Replacement
  Push `${String}`
  Push `${Substring}`
  Push `${Replacement}`
  Call un.StrReplace
  Pop `${Result}`
!macroend

Function StrReplace
  Exch $R2 ; replacement
  Exch
  Exch $R1 ; substring
  Exch 2
  Exch $R0 ; string
  Push $R3
  Push $R4
  Push $R5
  Push $R6
  StrLen $R3 $R1
  StrCpy $R4 0
  loop:
    StrCpy $R5 $R0 $R3 $R4
    StrCmp $R5 $R1 replace
    StrCmp $R5 "" done
    IntOp $R4 $R4 + 1
    Goto loop
  replace:
    StrCpy $R5 $R0 $R4
    IntOp $R6 $R4 + $R3
    StrCpy $R6 $R0 "" $R6
    StrCpy $R0 "$R5$R2$R6"
    IntOp $R4 $R4 + $R3
    StrCmp $R5 "" done
    Goto loop
  done:
  StrCpy $R0 $R0
  Pop $R6
  Pop $R5
  Pop $R4
  Pop $R3
  Exch $R0
FunctionEnd

; 卸载版本的 StrReplace 函数
Function un.StrReplace
  Exch $R2 ; replacement
  Exch
  Exch $R1 ; substring
  Exch 2
  Exch $R0 ; string
  Push $R3
  Push $R4
  Push $R5
  Push $R6
  StrLen $R3 $R1
  StrCpy $R4 0
  loop:
    StrCpy $R5 $R0 $R3 $R4
    StrCmp $R5 $R1 replace
    StrCmp $R5 "" done
    IntOp $R4 $R4 + 1
    Goto loop
  replace:
    StrCpy $R5 $R0 $R4
    IntOp $R6 $R4 + $R3
    StrCpy $R6 $R0 "" $R6
    StrCpy $R0 "$R5$R2$R6"
    IntOp $R4 $R4 + $R3
    StrCmp $R5 "" done
    Goto loop
  done:
    StrCpy $R0 $R0
    Pop $R6
    Pop $R5
    Pop $R4
    Pop $R3
    Exch $R0
FunctionEnd

; StrContains 宏实现
!define StrContains "!insertmacro StrContains"
!macro StrContains Result String Substring
  Push `${String}`
  Push `${Substring}`
  Call StrContains
  Pop `${Result}`
!macroend

Function StrContains
  Exch $R2 ; substring
  Exch
  Exch $R1 ; string
  Push $R0
  Push $R3
  Push $R4
  Push $R5
  StrLen $R3 $R2
  StrCpy $R4 0
  loop:
    StrCpy $R5 $R1 $R3 $R4
    StrCmp $R5 $R2 done
    StrCmp $R5 "" done
    IntOp $R4 $R4 + 1
    Goto loop
  done:
  StrCpy $R0 $R1 "" $R4
  StrCmp $R0 "" "" +2
  StrCpy $R0 0
  StrCmp $R0 0 +2
  StrCpy $R0 1
  Pop $R5
  Pop $R4
  Pop $R3
  Pop $R1
  Exch $R0
FunctionEnd

; 通用设置
Name "${DISPLAYNAME}"
OutFile "smart-svn-commit-setup-${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}.exe"
Unicode True
RequestExecutionLevel admin ; 需要管理员权限（用于注册表写入）
InstallDir "$PROGRAMFILES\${APPNAME}"
InstallDirRegKey HKCU "Software\${APPNAME}" ""

; 安装程序设置
ShowInstDetails show
ShowUnInstDetails show
SetCompressor lzma

; 界面设置
!define MUI_ABORTWARNING
!define MUI_ICON "..\icon.ico"
!define MUI_UNICON "..\icon.ico"

; 安装程序页面
!insertmacro MUI_PAGE_WELCOME
;!insertmacro MUI_PAGE_LICENSE "LICENSE" ; 如果有许可证文件
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; 卸载程序页面
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; 语言
!insertmacro MUI_LANGUAGE "SimpChinese"
!insertmacro MUI_LANGUAGE "English"

; ============================================================================
; 函数
; ============================================================================

; 检查并关闭正在运行的应用
Function CheckAndCloseApp
    DetailPrint "检查是否有正在运行的应用实例..."

    ; 使用 taskkill 关闭所有 smart-svn-commit.exe 进程
    ; /F: 强制终止
    ; /IM: 指定映像名称
    nsExec::ExecToLog 'taskkill /F /IM smart-svn-commit.exe'
    Pop $0

    ; 等待一下确保进程完全关闭
    Sleep 1000
FunctionEnd

; 安装初始化函数
Function .onInit
    Call CheckAndCloseApp
FunctionEnd

; 安装程序节
Section "主程序" SecMain

    ; 设置输出路径
    SetOutPath $INSTDIR

    ; 安装主程序文件
    ; 假设使用 PyInstaller 打包的单文件
    File /oname=smart-svn-commit.exe "..\dist\smart-svn-commit.exe"

    ; 创建开始菜单快捷方式（不创建桌面快捷方式）
    CreateDirectory "$SMPROGRAMS\${APPNAME}"
    CreateShortCut "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk" "$INSTDIR\smart-svn-commit.exe" "" "$INSTDIR\smart-svn-commit.exe" 0
    CreateShortCut "$SMPROGRAMS\${APPNAME}\卸载.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\uninstall.exe" 0

    ; 注册到用户 PATH 环境变量
    ReadRegStr $0 HKCU "Environment" "PATH"
    ${If} $0 == ""
        WriteRegStr HKCU "Environment" "PATH" "$INSTDIR"
    ${Else}
        ; 检查 PATH 中是否已包含 $INSTDIR
        ${StrContains} $2 "$INSTDIR" $0
        ${If} $2 == "0"
            WriteRegStr HKCU "Environment" "PATH" "$INSTDIR;$0"
        ${EndIf}
    ${EndIf}

    ; 注意：PATH 更改需要重新打开命令行窗口才能生效

    ; 注册 COM Shell Extension 右键菜单（仅在 SVN 工作副本中显示）
    DetailPrint "正在注册右键菜单（仅在 SVN 工作副本中显示）..."
    nsExec::ExecToLog '"$INSTDIR\smart-svn-commit.exe" --context-menu install-com'
    Pop $0
    ${If} $0 != "0"
        MessageBox MB_OK "右键菜单注册失败，请稍后手动运行: smart-svn-commit.exe --context-menu install-com"
    ${EndIf}

    ; 写入卸载信息
    WriteRegStr HKCU "Software\${APPNAME}" "" $INSTDIR
    WriteRegStr HKCU "Software\${APPNAME}" "Version" "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayName" "${DISPLAYNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString" "$\"$INSTDIR\uninstall.exe$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "QuietUninstallString" "$\"$INSTDIR\uninstall.exe$\" /S"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "Publisher" "${COMPANYNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "HelpLink" "${HELPURL}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "URLUpdateInfo" "${UPDATEURL}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "URLInfoAbout" "${ABOUTURL}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayVersion" "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "VersionMajor" ${VERSIONMAJOR}
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "VersionMinor" ${VERSIONMINOR}
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "NoRepair" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "EstimatedSize" ${INSTALLSIZE}

    ; 创建卸载程序
    WriteUninstaller "$INSTDIR\uninstall.exe"

SectionEnd

; 卸载程序节
Section "Uninstall"

    ; 卸载 COM Shell Extension 右键菜单
    DetailPrint "正在卸载右键菜单..."
    nsExec::ExecToLog '"$INSTDIR\smart-svn-commit.exe" --context-menu uninstall-com'
    Pop $0

    ; 删除文件
    Delete $INSTDIR\smart-svn-commit.exe
    Delete $INSTDIR\uninstall.exe

    ; 删除开始菜单快捷方式（无桌面快捷方式）
    Delete "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk"
    Delete "$SMPROGRAMS\${APPNAME}\卸载.lnk"
    RMDir "$SMPROGRAMS\${APPNAME}"

    ; 从用户 PATH 中移除安装目录
    ReadRegStr $0 HKCU "Environment" "PATH"
    ${If} $0 != ""
        ; 移除 $INSTDIR;$INSTDIR; 等变体
        ; 方法: 使用 StrReplace 替换为空字符串
        !insertmacro un.StrReplace $1 "$INSTDIR;" "" $0
        !insertmacro un.StrReplace $2 ";$INSTDIR" "" $1
        !insertmacro un.StrReplace $3 "$INSTDIR" "" $2
        WriteRegStr HKCU "Environment" "PATH" $3
    ${EndIf}

    ; 注意：PATH 更改需要重新打开命令行窗口才能生效

    ; 删除注册表项
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
    DeleteRegKey HKCU "Software\${APPNAME}"

    ; 删除安装目录
    RMDir $INSTDIR

SectionEnd

; 描述
LangString DESC_SecMain ${LANG_SIMPCHINESE} "安装 Smart SVN Commit 主程序"
LangString DESC_SecMain ${LANG_ENGLISH} "Install Smart SVN Commit main program"

!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecMain} $(DESC_SecMain)
!insertmacro MUI_FUNCTION_DESCRIPTION_END
