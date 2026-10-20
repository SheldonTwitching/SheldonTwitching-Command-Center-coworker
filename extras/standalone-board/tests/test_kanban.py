from copy import deepcopy
import io
import json
import base64
import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from kanban import Kanban, BoardConflict, FIELDS
from github_board import GitHubBoard, encode_card, decode_card

FEATURES=[dict(id='cabinet',title='Cabinet',next=['Count nine buttons'],roadmap='docs/cabinet.md')]


def update(board,card,**changes):
    return board.action(dict(action='update',revision=board.data['revision'],id=card['id'],card={**{k:card[k] for k in FIELDS},**changes}))


def test_board_restart_migration_and_conflict(tmp_path):
    board=Kanban(tmp_path,FEATURES)
    roadmap={'cabinet':{'ideas':[dict(id='idea-1',text='Bigger paint shoulders',pinned=True)]}}
    board.migrate(roadmap);board.migrate(roadmap)
    assert len(board.data['cards'])==2
    old=board.snapshot()
    update(board,board.data['cards'][0],status='In progress',blocked=True,blockedReason='Need reference')
    with pytest.raises(BoardConflict):board.action(dict(action='create',revision=old['revision'],card={'title':'stale'}))
    restarted=Kanban(tmp_path,FEATURES)
    assert restarted.data==board.data
    assert restarted.data['cards'][1]['priority']=='P1'
    assert (tmp_path/'kanban.json.bak').exists()


def test_done_requires_evidence_and_owner_acceptance(tmp_path):
    board=Kanban(tmp_path,FEATURES);c=board.data['cards'][0]
    with pytest.raises(ValueError):update(board,c,status='Done')
    update(board,c,status='Done',implemented=True,verified=True,accepted=True,evidence='Owner checked nine buttons in OBS')
    assert board.data['cards'][0]['status']=='Done'


def test_backup_import_is_atomic_and_non_destructive(tmp_path):
    board=Kanban(tmp_path,FEATURES);board.migrate({})
    backup=deepcopy(board.data)
    board.action(dict(action='import',revision=board.data['revision'],board=backup))
    assert len(board.data['cards'])==1
    backup['cards'][0]['title']='Different version'
    before=deepcopy(board.data)
    with pytest.raises(BoardConflict):board.action(dict(action='import',revision=before['revision'],board=backup))
    assert board.data==before
    (tmp_path/'kanban.json').write_text('damaged')
    broken=Kanban(tmp_path,FEATURES)
    assert broken.problem
    with pytest.raises(ValueError):broken.migrate({}) if not broken.problem else broken.action(dict(action='create',revision=0,card={'title':'Do not overwrite'}))
    assert (tmp_path/'kanban.json').read_text()=='damaged'


def test_screenshots_validated_and_retained(tmp_path):
    from PIL import Image
    board=Kanban(tmp_path,FEATURES);board.migrate({});c=board.data['cards'][0]
    with pytest.raises(ValueError):board.attach(dict(revision=board.data['revision'],id=c['id'],image=base64.b64encode(b'<script>bad</script>').decode()))
    out=io.BytesIO();Image.new('RGB',(5,5),'blue').save(out,'PNG')
    board.attach(dict(revision=board.data['revision'],id=c['id'],image=base64.b64encode(out.getvalue()).decode()))
    c=board.data['cards'][0];assert len(c['attachments'])==1
    assert (tmp_path/'board-attachments'/c['attachments'][0]).exists()
    update(board,c,archived=True);update(board,board.data['cards'][0],archived=False)
    assert board.data['cards'][0]['attachments']==c['attachments']


class FakeGitHub(GitHubBoard):
    def __init__(self,board):
        super().__init__(board);self.project_id='P1';self.project_url='https://github.com/users/test/projects/1';self.remote={};self.fail=False
    def remote_cards(self):
        if self.fail:raise ValueError('Offline')
        return deepcopy(self.remote)
    def push(self,c,mapping):
        m=mapping or dict(itemId='R'+c['id'],contentId='D'+c['id'])
        values={k:c[k] for k in FIELDS}
        self.remote[m['itemId']]=dict(values=values,contentId=m['contentId'],localId=c['id'])
        return dict(m,base=values)


def test_bidirectional_sync_and_conflict_resolution(tmp_path):
    board=Kanban(tmp_path,FEATURES);board.migrate({});sync=FakeGitHub(board);sync.sync()
    c=board.data['cards'][0];key='R'+c['id']
    sync.remote[key]['values']['status']='In progress';sync.sync()
    assert board.data['cards'][0]['status']=='In progress'
    update(board,board.data['cards'][0],priority='P1');sync.sync()
    assert sync.remote[key]['values']['priority']=='P1'
    sync.remote[key]['values']['description']='Edited remotely'
    update(board,board.data['cards'][0],description='Edited locally')
    sync.sync();assert len(sync.status()['conflicts'])==1
    assert board.data['cards'][0]['description']=='Edited locally'
    sync.resolve(dict(id=c['id'],choice='remote'))
    assert board.data['cards'][0]['description']=='Edited remotely'
    assert not sync.status()['conflicts']
    # A lost create response is matched by the stable marker, avoiding duplicate cards.
    board.data['sync']['items']={};sync.sync();assert len(sync.remote)==1


def test_offline_queue_and_missing_remote_keep_local_copy(tmp_path):
    board=Kanban(tmp_path,FEATURES);board.migrate({});sync=FakeGitHub(board);sync.sync()
    update(board,board.data['cards'][0],description='Saved offline')
    sync.fail=True
    with pytest.raises(ValueError):sync.sync()
    assert Kanban(tmp_path,FEATURES).data['cards'][0]['description']=='Saved offline'
    sync.fail=False;sync.sync();assert next(iter(sync.remote.values()))['values']['description']=='Saved offline'
    sync.remote={};sync.sync();assert len(board.data['cards'])==1
    assert sync.status()['conflicts'][0]['remote'] is None


def test_markdown_payload_roundtrip_and_public_project_refusal(tmp_path):
    board=Kanban(tmp_path,FEATURES);c=board.data['cards'][0]
    c.update(description='Check materials\n\n## Evidence\nOriginal detail\n- [x] accepted\n\n',blocked=True,blockedReason='Waiting for masks')
    values,identity=decode_card(c['title'],encode_card(c),c['status'],board.areas)
    assert values=={k:c[k] for k in FIELDS};assert identity==c['id']
    sync=GitHubBoard(board)
    sync.gql=lambda *a,**k:{'user':{'projectV2':dict(id='P',url='https://github.com/users/test/projects/1',public=True)}}
    with pytest.raises(ValueError,match='private'):sync.link('https://github.com/users/test/projects/1')
    assert not sync.project_id
    sync.token='sensitive-test-value'
    assert 'sensitive-test-value' not in json.dumps(sync.status())
    sync.dispatch('disconnect',{});assert sync.token is None


def test_device_flow_slow_down_and_session_only_credentials(tmp_path,monkeypatch):
    import github_board
    board=Kanban(tmp_path,FEATURES);sync=GitHubBoard(board)
    responses=iter([dict(device_code='private-device-code',user_code='ABCD-EFGH',expires_in=900,interval=5),
                    dict(error='authorization_pending'),dict(error='slow_down'),dict(access_token='test-session-token')])
    requests=[];waits=[]
    def request(url,data,token=None):
        requests.append((url,data));return next(responses)
    sync._request=request
    sync.gql=lambda *a,**kw:{'viewer':{'login':'test-owner'}}
    monkeypatch.setattr(github_board.time,'sleep',lambda seconds:waits.append(seconds))
    sync.connect('public-client-id',0)
    assert sync.token=='test-session-token' and sync.user_code is None
    assert requests[0][1]['scope']=='project'
    assert len(waits)==20  # 5 + 5 + 10: respects GitHub slow_down.
    saved=(tmp_path/'github-project.json').read_text()
    assert 'test-session-token' not in saved and 'private-device-code' not in saved
    assert 'test-session-token' not in json.dumps(sync.status())
    assert GitHubBoard(board).token is None


def test_conflict_choice_cannot_erase_a_newer_local_edit(tmp_path):
    board=Kanban(tmp_path,FEATURES);board.migrate({});sync=FakeGitHub(board);sync.sync()
    c=board.data['cards'][0];key='R'+c['id']
    sync.remote[key]['values']['description']='Remote'
    update(board,c,description='Local');sync.sync()
    update(board,board.data['cards'][0],description='Newer local draft')
    with pytest.raises(ValueError,match='changed after'):sync.resolve(dict(id=c['id'],choice='remote'))
    assert board.data['cards'][0]['description']=='Newer local draft'
