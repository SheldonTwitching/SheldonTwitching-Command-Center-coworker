"""GitHub device sign-in and private Projects V2 draft-card synchronization.

Credentials are session-only. Never logs or exports OAuth responses. Network work
runs off the HTTP/render thread. Persisted base snapshots support three-way checks.
"""
from copy import deepcopy
import json
import re
import threading
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from kanban import FIELDS, STATUSES, card_values

SECTIONS = {'description':'Description','acceptance':'Acceptance criteria','evidence':'Evidence',
            'build':'Build / scene / source','area':'Area','priority':'Priority','kind':'Type',
            'blockedReason':'Blocking reason'}


def encode_card(c):
    parts = [f"<!-- command-center:{c['id']} -->"]
    for key, title in SECTIONS.items():
        parts.append('## ' + title + '\n<!-- cc-field:' + key + ' -->\n' + c[key] + '\n<!-- /cc-field:' + key + ' -->')
    parts.append('## Checks\n' + '\n'.join(f"- [{'x' if c[k] else ' '}] {k}" for k in ('blocked','implemented','verified','accepted','archived')))
    return '\n\n'.join(parts)


def decode_card(title, body, status, areas):
    c = dict(title=title, status=status or 'Inbox')
    marker = re.search(r'<!-- command-center:([a-zA-Z0-9-]+) -->', body)
    if marker:
        for key, heading in SECTIONS.items():
            match = re.search(r'<!-- cc-field:' + key + r' -->\n(.*?)\n<!-- /cc-field:' + key + r' -->',body,re.S)
            if match:
                c[key] = match.group(1)
        checks_body=body.rsplit('\n\n## Checks\n',1)[-1] if '\n\n## Checks\n' in body else ''
        for key in ('blocked','implemented','verified','accepted','archived'):
            c[key] = bool(re.search(r'^- \[x\] ' + key + '$',checks_body,re.M))
    else:
        c['description'] = body
    return card_values(c, areas), marker.group(1) if marker else None


class GitHubBoard:
    def __init__(self, board):
        self.board = board
        self.lock = threading.RLock()
        self.token = None
        self.client_id = ''
        self.project_url = 'https://github.com/users/SheldonTwitching/projects/1'
        self.project_id = None
        self.message = 'Not connected. Local board is available.'
        self.user_code = None
        self.generation = 0
        self.busy = False
        self.next_sync = 0
        self.interval = 60
        self.enabled = False
        self.fields = None
        self.config = board.home / 'github-project.json'
        try:
            c = json.loads(self.config.read_text(encoding='utf-8'))
            self.client_id = c['clientId']; self.project_url = c['projectUrl']
        except (OSError,ValueError,KeyError,TypeError):
            pass

    def status(self):
        with self.lock, self.board.lock:
            return dict(connected=bool(self.token),clientId=self.client_id,projectUrl=self.project_url,
                        userCode=self.user_code,message=self.message,busy=self.busy,
                        conflicts=deepcopy(self.board.data['sync'].get('conflicts',[])))

    def _request(self, url, data, token=None):
        headers={'Accept':'application/json','User-Agent':'SheldonTwitching-Command-Center'}
        if token:
            headers['Authorization']='Bearer '+token
            raw=json.dumps(data).encode();headers['Content-Type']='application/json'
        else:
            raw=urlencode(data).encode();headers['Content-Type']='application/x-www-form-urlencoded'
        try:
            with urlopen(Request(url,raw,headers),timeout=12) as r:
                value=json.loads(r.read(3000000))
        except Exception:
            raise ValueError('GitHub request failed. Check connectivity, sign-in and Projects permission; queued local edits are retained.') from None
        return value

    def gql(self, query, **variables):
        with self.lock:
            token=self.token
        if not token:
            raise ValueError('Connect with GitHub first')
        value=self._request('https://api.github.com/graphql',dict(query=query,variables=variables),token)
        if value.get('errors'):
            raise ValueError('GitHub rejected the project operation. Check project access, field setup and sign-in; local edits are retained.')
        return value['data']

    def _save_config(self):
        self.board.home.mkdir(parents=True,exist_ok=True)
        tmp=self.config.with_suffix('.tmp')
        tmp.write_text(json.dumps(dict(clientId=self.client_id,projectUrl=self.project_url)),encoding='utf-8')
        tmp.replace(self.config)

    def dispatch(self, action, data):
        if not isinstance(data,dict):
            raise ValueError('Invalid GitHub operation')
        if action == 'disconnect':
            with self.lock:
                self.generation+=1;self.token=None;self.user_code=None;self.message='Disconnected. Sign-in has been cleared from this app session.'
            return self.status()
        if action == 'resolve':
            return self.resolve(data)
        if action not in ('connect','link','create','sync'):
            raise ValueError('Unknown GitHub operation')
        with self.lock:
            if self.busy:
                raise ValueError('A GitHub operation is already running')
            if action=='connect' and not re.fullmatch(r'[A-Za-z0-9_.-]{5,100}',data.get('clientId','')):
                raise ValueError('Enter the public Client ID from your GitHub OAuth application settings')
            if action=='sync':self.enabled=True
            if action=='connect':self.token=None;self.user_code=None;self.enabled=False
            self.busy=True;self.message='Working with GitHub…'
            generation=self.generation
        threading.Thread(target=self._work,args=(action,deepcopy(data),generation),daemon=True).start()
        return self.status()

    def _work(self, action, data, generation):
        try:
            if action=='connect':
                self.connect(data['clientId'],generation)
            elif action=='create':
                self.create()
            elif action=='link':
                self.link(data.get('url',''))
            else:
                self.sync()
            self.interval=60
        except Exception as e:
            with self.lock:
                if action=='connect':self.user_code=None
                self.message=str(e) if isinstance(e,ValueError) else 'Synchronization failed. Local edits are retained; try again.'
            self.interval=min(900,self.interval*2)
        finally:
            with self.lock:
                self.busy=False;self.next_sync=time.monotonic()+self.interval if self.enabled else float('inf')

    def connect(self, client_id, generation):
        value=self._request('https://github.com/login/device/code',dict(client_id=client_id,scope='project'))
        if not value.get('device_code'):
            raise ValueError('Device sign-in is unavailable. Enable Device Flow in your GitHub OAuth app settings.')
        with self.lock:
            if self.generation!=generation:return
            self.client_id=client_id;self.user_code=value['user_code'];self.message='Enter the displayed code on GitHub, then approve Projects access.'
            self._save_config()
        expires=time.monotonic()+min(900,int(value.get('expires_in',900)))
        interval=max(5,int(value.get('interval',5)))
        while time.monotonic()<expires:
            # Cancellable wait, does not hold HTTP/render threads or board locks.
            for _ in range(interval):
                time.sleep(1)
                if self.generation!=generation:return
            result=self._request('https://github.com/login/oauth/access_token',dict(client_id=client_id,device_code=value['device_code'],grant_type='urn:ietf:params:oauth:grant-type:device_code'))
            if result.get('access_token'):
                with self.lock:
                    if self.generation!=generation:return
                    self.token=result['access_token'];self.user_code=None
                who=self.gql('query { viewer { login } }')['viewer']['login']
                with self.lock:self.message='Connected as '+who+'. Link or create a private project.'
                return
            if result.get('error')=='slow_down':interval+=5
            elif result.get('error')!='authorization_pending':
                raise ValueError('GitHub sign-in was declined or expired. Start Connect again.')
        self.user_code=None
        raise ValueError('GitHub sign-in expired. Start Connect again.')

    def tick(self):
        # Called by a single background loop, not by OBS polling.
        with self.lock:
            due=self.enabled and self.token and self.project_url and not self.busy and time.monotonic()>=self.next_sync
        if due:
            try:self.dispatch('sync',{})
            except ValueError:pass  # Another window may have started an operation meanwhile.

    def start(self):
        def loop():
            while True:
                time.sleep(5)
                self.tick()
        threading.Thread(target=loop,daemon=True).start()

    def create(self):
        owner=self.gql('query { viewer { id } }')['viewer']['id']
        project=self.gql('mutation($owner:ID!){createProjectV2(input:{ownerId:$owner,title:"SheldonTwitching - Command Center"}){projectV2{id url public}}}',owner=owner)['createProjectV2']['projectV2']
        self.gql('mutation($id:ID!){updateProjectV2(input:{projectId:$id,public:false}){projectV2{id}}}',id=project['id'])
        self.link(project['url'])

    def link(self, url):
        if not isinstance(url,str):raise ValueError('Choose a GitHub Project URL')
        m=re.fullmatch(r'https://github.com/(users|orgs)/([A-Za-z0-9-]+)/projects/([1-9][0-9]*)/?',url)
        if not m:raise ValueError('Use the full GitHub user or organization Project URL')
        typ='user' if m[1]=='users' else 'organization'
        project=self.gql('query($login:String!,$number:Int!){'+typ+'(login:$login){projectV2(number:$number){id url public}}}',login=m[2],number=int(m[3]))[typ]['projectV2']
        if not project or project['public']:raise ValueError('Select a private project before sharing any board cards')
        with self.board.lock:
            previous=self.board.data['sync'].get('projectId')
            if previous and previous!=project['id']:
                raise ValueError('This board is linked to another project. Use the existing project to preserve synchronization history.')
        self.project_id=project['id'];self.project_url=project['url'];self.fields=None;self.enabled=False;self._save_config()
        self._fields()
        self.message='Private project linked. Sync now will share this board with that project.'
        # First upload is explicit; later polling begins after Sync now.
        self.next_sync=float('inf')

    def _fields(self):
        p=self.gql('query($id:ID!){node(id:$id){... on ProjectV2{public fields(first:100){nodes{... on ProjectV2SingleSelectField{id name options{id name}}}}}}}',id=self.project_id)['node']
        if not p or p['public']:raise ValueError('Project is no longer private. Synchronization stopped.')
        field=next((f for f in p['fields']['nodes'] if f.get('name')=='Command Center Status'),None)
        if not field:
            opts=[dict(name=s,color='GRAY',description=s) for s in STATUSES]
            field=self.gql('mutation($id:ID!,$opts:[ProjectV2SingleSelectFieldOptionInput!]!){createProjectV2Field(input:{projectId:$id,dataType:SINGLE_SELECT,name:"Command Center Status",singleSelectOptions:$opts}){projectV2Field{... on ProjectV2SingleSelectField{id name options{id name}}}}}',id=self.project_id,opts=opts)['createProjectV2Field']['projectV2Field']
        if set(STATUSES)-{o['name'] for o in field['options']}:raise ValueError('Command Center Status must contain all six board columns')
        self.fields=field

    def remote_cards(self):
        self._fields()  # Privacy checked before every upload cycle, including after reconnect.
        items=[];cursor=None
        while True:
            p=self.gql('query($id:ID!,$after:String){node(id:$id){... on ProjectV2{items(first:100,after:$after){pageInfo{hasNextPage endCursor} nodes{id fieldValues(first:100){nodes{... on ProjectV2ItemFieldSingleSelectValue{name field{... on ProjectV2SingleSelectField{name}}}}} content{... on DraftIssue{id title body}}}}}}}',id=self.project_id,after=cursor)['node']['items']
            items+=p['nodes']
            if len(items)>1000:raise ValueError('Project exceeds the 1,000-card synchronization limit')
            if not p['pageInfo']['hasNextPage']:break
            cursor=p['pageInfo']['endCursor']
        result={}
        for item in items:
            content=item.get('content') or {}
            if not content.get('title'):continue  # Issues and PRs are outside this draft-card adapter.
            status=next((f['name'] for f in item['fieldValues']['nodes'] if f.get('field',{}).get('name')=='Command Center Status'),'Inbox')
            values,local_id=decode_card(content['title'],content.get('body',''),status,self.board.areas)
            result[item['id']]=dict(values=values,contentId=content['id'],localId=local_id)
        return result

    def push(self, c, mapping):
        if not mapping:
            item=self.gql('mutation($id:ID!,$title:String!,$body:String!){addProjectV2DraftIssue(input:{projectId:$id,title:$title,body:$body}){projectItem{id content{... on DraftIssue{id}}}}}',id=self.project_id,title=c['title'],body=encode_card(c))['addProjectV2DraftIssue']['projectItem']
            mapping=dict(itemId=item['id'],contentId=item['content']['id'])
            # Record identity before the next network step, so retry cannot duplicate it.
            with self.board.lock:
                value=deepcopy(self.board.data);value['sync'].setdefault('items',{})[c['id']]=mapping
                value['sync']['projectId']=self.project_id;self.board._persist(value)
        else:
            self.gql('mutation($id:ID!,$title:String!,$body:String!){updateProjectV2DraftIssue(input:{draftIssueId:$id,title:$title,body:$body}){draftIssue{id}}}',id=mapping['contentId'],title=c['title'],body=encode_card(c))
        option=next(o['id'] for o in self.fields['options'] if o['name']==c['status'])
        self.gql('mutation($project:ID!,$item:ID!,$field:ID!,$option:String!){updateProjectV2ItemFieldValue(input:{projectId:$project,itemId:$item,fieldId:$field,value:{singleSelectOptionId:$option}}){projectV2Item{id}}}',project=self.project_id,item=mapping['itemId'],field=self.fields['id'],option=option)
        return dict(mapping,base={k:c[k] for k in FIELDS})

    def sync(self):
        if not self.project_id:
            enabled=self.enabled
            self.link(self.project_url)
            self.enabled=enabled
        remote=self.remote_cards()
        snap=self.board.snapshot();mappings=snap['sync'].get('items',{});conflicts=[]
        known={m['itemId'] for m in mappings.values()}
        for item_id,r in remote.items():
            if item_id not in known:
                # Reconcile a successful upload whose response was lost, or import a GitHub draft.
                c=next((c for c in snap['cards'] if c['id']==r['localId']),None)
                with self.board.lock:
                    value=deepcopy(self.board.data)
                    if c is None:
                        c=self.board._new(r['values']);value['cards'].append(c)
                    mapping=dict(itemId=item_id,contentId=r['contentId'],base=r['values'])
                    value['sync'].setdefault('items',{})[c['id']]=mapping;value['sync']['projectId']=self.project_id
                    value['revision']+=1;self.board._persist(value)
        snap=self.board.snapshot()
        for c in snap['cards']:
            mapping=snap['sync'].get('items',{}).get(c['id']);local={k:c[k] for k in FIELDS}
            r=remote.get(mapping['itemId']) if mapping else None
            base=mapping.get('base') if mapping else None
            if mapping and r is None:
                conflicts.append(dict(id=c['id'],title=c['title'],local=local,remote=None,reason='GitHub item missing or archived; no deletion was applied locally.'));continue
            changed_remote=r and r['values']!=base
            changed_local=local!=base
            if changed_remote and changed_local and local!=r['values']:
                conflicts.append(dict(id=c['id'],title=c['title'],local=local,remote=r['values']));continue
            if changed_remote and not changed_local:
                with self.board.lock:
                    value=deepcopy(self.board.data);current=next(v for v in value['cards'] if v['id']==c['id'])
                    if current['version']!=c['version']:continue
                    current.update(r['values']);current['version']+=1;current['updatedAt']=time.time()
                    value['sync']['items'][c['id']]['base']=r['values'];value['revision']+=1;self.board._persist(value)
            elif changed_local or not mapping:
                new_mapping=self.push(c,mapping)
                with self.board.lock:
                    value=deepcopy(self.board.data);value['sync'].setdefault('items',{})[c['id']]=new_mapping
                    value['sync']['projectId']=self.project_id;self.board._persist(value)
        with self.board.lock:
            value=deepcopy(self.board.data);value['sync']['conflicts']=conflicts;value['sync']['lastSync']=time.time();self.board._persist(value)
        self.message='Last sync '+time.strftime('%H:%M:%S')+f' · {len(conflicts)} conflicts · next check in about a minute.'

    def resolve(self, data):
        with self.board.lock:
            value=deepcopy(self.board.data)
            conflict=next((c for c in value['sync'].get('conflicts',[]) if c['id']==data.get('id')),None)
            c=next((c for c in value['cards'] if c['id']==data.get('id')),None)
            if not conflict or not c or data.get('choice') not in ('local','remote'):
                raise ValueError('Select an existing conflict and resolution')
            if conflict['remote'] is None:raise ValueError('Restore the missing/archived item in GitHub, then synchronize again. Local copy is retained.')
            if {k:c[k] for k in FIELDS}!=conflict['local']:
                raise ValueError('Card changed after this conflict was reported. Synchronize again before choosing.')
            if data['choice']=='remote':c.update(card_values(conflict['remote'],self.board.areas));c['version']+=1;c['updatedAt']=time.time()
            value['sync']['items'][c['id']]['base']=conflict['remote']
            value['sync']['conflicts']=[v for v in value['sync']['conflicts'] if v['id']!=c['id']]
            value['revision']+=1;self.board._persist(value)
        self.message='Conflict choice saved. Sync now to apply it to GitHub.'
        return self.status()
