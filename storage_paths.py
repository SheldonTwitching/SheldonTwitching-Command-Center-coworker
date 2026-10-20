"""Resolve persistent local app data independently of the installation directory."""
import json,os,shutil,hashlib
from pathlib import Path

def legacy_home():
    return Path(os.environ.get('APPDATA',Path.home()))/'SheldonTwitchingLabels'

def data_home():
    if os.environ.get('ST_LABELS_HOME'):return Path(os.environ['ST_LABELS_HOME'])
    pointer=legacy_home()/'storage-location.json'
    if not pointer.exists():return legacy_home()
    value=json.loads(pointer.read_text(encoding='utf-8'))
    target=Path(value.get('directory',''))
    if value.get('schema')!=1 or not target.is_absolute():raise ValueError('Invalid saved Command Center data directory')
    return target

def migrate_data(destination,source=None):
    source=Path(source) if source is not None else data_home()
    destination=Path(destination)
    if not destination.is_absolute():raise ValueError('Choose an absolute data directory')
    destination=destination.resolve()
    if source.resolve()!=destination:
        if destination.is_relative_to(source.resolve()):raise ValueError('Destination cannot be inside the old profile')
        files=[p for p in source.rglob('*') if p.is_file() and not p.is_symlink() and p.name!='storage-location.json']
        # Refuse to overwrite a different profile. Original data is never removed.
        for item in files:
            target=destination/item.relative_to(source)
            if target.exists() and target.read_bytes()!=item.read_bytes():raise ValueError('Destination contains different saved data: '+str(item.relative_to(source)))
        destination.mkdir(parents=True,exist_ok=True)
        for item in files:
            target=destination/item.relative_to(source);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(item,target)
            if hashlib.sha256(item.read_bytes()).digest()!=hashlib.sha256(target.read_bytes()).digest():raise OSError('Copied data verification failed')
    else:files=[]
    pointer=legacy_home()/'storage-location.json';pointer.parent.mkdir(parents=True,exist_ok=True)
    temporary=pointer.with_suffix('.tmp');temporary.write_text(json.dumps({'schema':1,'directory':str(destination)},indent=2),encoding='utf-8');os.replace(temporary,pointer)
    return {'directory':str(destination),'copiedFiles':len(files),'originalsRetained':True}
