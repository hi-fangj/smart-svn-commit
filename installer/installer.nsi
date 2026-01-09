; Smart SVN Commit 安装程序
; 编译命令: makensis installer.nsi

!define APPNAME "Smart SVN Commit"
!define COMPANYNAME "Smart SVN Commit"
!define DESCRIPTION "AI 驱动的 SVN 提交助手"
!define VERSIONMAJOR 2
!define VERSIONMINOR 1
!define VERSIONBUILD 0
!define HELPURL "https://github.com/hi-fangj/smart-svn-commit" ; 请修改为实际的仓库 URL
!define UPDATEURL "https://github.com/hi-fangj/smart-svn-commit"
!define ABOUTURL "https://github.com/hi-fangj/smart-svn-commit"
!define INSTALLSIZE 50000 ; 估算大小（KB）

!define DISPLAYNAME "${APPNAME} ${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}"

; 包含现代 UI
!include "MUI2.nsh"

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
;!define MUI_ICON "icon.ico" ; 如果有图标文件
;!define MUI_UNICON "icon.ico" ; 如果有图标文件

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

; 安装程序节
Section "主程序" SecMain

    ; 设置输出路径
    SetOutPath $INSTDIR

    ; 安装主程序文件
    ; 假设使用 PyInstaller 打包的单文件
    File /oname=smart-svn-commit.exe "..\dist\smart-svn-commit.exe"

    ; 创建桌面快捷方式（可选）
    CreateShortCut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\smart-svn-commit.exe" "" "$INSTDIR\smart-svn-commit.exe" 0

    ; 创建开始菜单快捷方式
    CreateDirectory "$SMPROGRAMS\${APPNAME}"
    CreateShortCut "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk" "$INSTDIR\smart-svn-commit.exe" "" "$INSTDIR\smart-svn-commit.exe" 0
    CreateShortCut "$SMPROGRAMS\${APPNAME}\卸载.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\uninstall.exe" 0

    ; 注册到 PATH（可选）
    ; Environ::Set "PATH" "$INSTDIR;$%PATH%"

    ; 注册右键菜单
    DetailPrint "正在注册右键菜单..."
    nsExec::ExecToLog '"$INSTDIR\smart-svn-commit.exe" --context-menu install'
    Pop $0
    ${If} $0 != "0"
        MessageBox MB_OK "右键菜单注册失败，请稍后手动运行: smart-svn-commit.exe --context-menu install"
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

    ; 卸载右键菜单
    DetailPrint "正在卸载右键菜单..."
    nsExec::ExecToLog '"$INSTDIR\smart-svn-commit.exe" --context-menu uninstall'
    Pop $0

    ; 删除文件
    Delete $INSTDIR\smart-svn-commit.exe
    Delete $INSTDIR\uninstall.exe

    ; 删除快捷方式
    Delete "$DESKTOP\${APPNAME}.lnk"
    Delete "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk"
    Delete "$SMPROGRAMS\${APPNAME}\卸载.lnk"
    RMDir "$SMPROGRAMS\${APPNAME}"

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

