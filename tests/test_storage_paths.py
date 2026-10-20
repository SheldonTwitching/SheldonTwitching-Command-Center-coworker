import json
import pytest
import storage_paths as storage

def test_copy_verify_and_persist_new_data_home(tmp_path,monkeypatch):
    monkeypatch.setenv('APPDATA',str(tmp_path/'appdata'));monkeypatch.delenv('ST_LABELS_HOME',raising=False)
    old=storage.legacy_home();old.mkdir(parents=True);(old/'studio.json').write_text('{"ideas":["keep me"]}');(old/'nested').mkdir();(old/'nested'/'art.png').write_bytes(b'original')
    new=tmp_path/'Command Center'/'User Data';result=storage.migrate_data(new)
    assert result['copiedFiles']==2 and result['originalsRetained']
    assert storage.data_home()==new and (old/'studio.json').exists()
    assert (new/'nested'/'art.png').read_bytes()==b'original'
    assert storage.migrate_data(new)['copiedFiles']==0
    monkeypatch.setenv('ST_LABELS_HOME',str(tmp_path/'isolated'))
    assert storage.data_home()==tmp_path/'isolated'

def test_migration_does_not_overwrite_existing_profile(tmp_path,monkeypatch):
    monkeypatch.setenv('APPDATA',str(tmp_path/'appdata'));monkeypatch.delenv('ST_LABELS_HOME',raising=False)
    old=storage.legacy_home();old.mkdir(parents=True);(old/'studio.json').write_text('old')
    new=tmp_path/'new';new.mkdir();(new/'studio.json').write_text('different')
    with pytest.raises(ValueError):storage.migrate_data(new)
    assert not (old/'storage-location.json').exists()
    assert (new/'studio.json').read_text()=='different'

def test_invalid_pointer_is_not_silently_ignored(tmp_path,monkeypatch):
    monkeypatch.setenv('APPDATA',str(tmp_path));monkeypatch.delenv('ST_LABELS_HOME',raising=False)
    old=storage.legacy_home();old.mkdir();(old/'storage-location.json').write_text(json.dumps({'schema':1,'directory':'relative'}))
    with pytest.raises(ValueError):storage.data_home()
