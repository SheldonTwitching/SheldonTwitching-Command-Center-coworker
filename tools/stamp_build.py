"""Stamp a local/CI Windows build without including any user configuration."""
import json, re, subprocess, sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
version=sys.argv[1] if len(sys.argv)>1 else '2.0.0'
if not re.fullmatch(r'\d+\.\d+\.\d+',version):raise SystemExit('Use a three-number version')
parts=tuple(map(int,version.split('.')))+(0,)
if any(x>65535 for x in parts):raise SystemExit('Version component too large')
name='SheldonTwitching - Command Center'
text=f"""VSVersionInfo(
 ffi=FixedFileInfo(filevers={parts!r},prodvers={parts!r},mask=0x3f,flags=0x0,OS=0x40004,fileType=0x1,subtype=0x0,date=(0,0)),
 kids=[StringFileInfo([StringTable('040904B0',[
 StringStruct('CompanyName','SheldonTwitching'),StringStruct('FileDescription','{name}'),
 StringStruct('FileVersion','{version}'),StringStruct('ProductVersion','{version}'),
 StringStruct('ProductName','{name}'),StringStruct('OriginalFilename','{name}.exe')])]),
 VarFileInfo([VarStruct('Translation',[1033,1200])])])
"""
(root/'installer/version_info.txt').write_text(text,encoding='utf-8')
commit=subprocess.run(['git','rev-parse','HEAD'],cwd=root,capture_output=True,text=True).stdout.strip()
(root/'arcade/build-info.json').write_text(json.dumps({'name':name,'version':version,'commit':commit,'updates':'https://github.com/SheldonTwitching/SheldonTwitching-Command-Center/actions'},indent=2))
print(name+' '+version)
