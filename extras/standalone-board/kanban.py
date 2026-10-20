"""Local owner board. Atomic saves, optimistic revisions and non-destructive imports."""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import base64
import hashlib
import io
import json
import math
import re
import threading
import time
import uuid

STATUSES = ('Inbox', 'Ready', 'In progress', 'Review', 'Owner testing', 'Done')
TYPES = ('feature', 'bug', 'art', 'research', 'maintenance', 'review')
PRIORITIES = ('P0', 'P1', 'P2', 'P3')
FIELDS = {'title', 'description', 'area', 'priority', 'kind', 'status', 'acceptance',
          'evidence', 'build', 'blocked', 'blockedReason', 'implemented', 'verified', 'accepted', 'archived'}


class BoardConflict(ValueError):
    pass


def card_values(value, areas):
    if not isinstance(value, dict) or set(value) - FIELDS:
        raise ValueError('Unsupported card fields')
    c = dict(title='', description='', area='planning', priority='P2', kind='feature',
             status='Inbox', acceptance='', evidence='', build='', blocked=False,
             blockedReason='', implemented=False, verified=False, accepted=False, archived=False)
    c.update(deepcopy(value))
    for key in FIELDS - {'blocked', 'implemented', 'verified', 'accepted', 'archived'}:
        if not isinstance(c[key], str) or len(c[key]) > (180 if key == 'title' else 12000):
            raise ValueError('Invalid card ' + key)
    c['title'] = c['title'].strip()
    if not c['title'] or c['area'] not in areas | {'planning'} or c['priority'] not in PRIORITIES or c['kind'] not in TYPES or c['status'] not in STATUSES:
        raise ValueError('Choose a title, area, priority, type and status')
    for key in ('blocked', 'implemented', 'verified', 'accepted', 'archived'):
        if not isinstance(c[key], bool):
            raise ValueError('Invalid card switch')
    if c['blocked'] and not c['blockedReason'].strip():
        raise ValueError('Explain what is blocking this card')
    if c['accepted'] and not (c['implemented'] and c['verified']):
        raise ValueError('Owner acceptance requires implementation and verification checks')
    if c['status'] == 'Done' and not (c['acceptance'].strip() and c['evidence'].strip() and c['implemented'] and c['verified'] and c['accepted']) :
        raise ValueError('Done requires acceptance criteria, evidence and all three completion checks')
    return c


class Kanban:
    def __init__(self, home, features):
        self.home = Path(home)
        self.path = self.home / 'kanban.json'
        self.features = features
        self.areas = {f['id'] for f in features}
        self.lock = threading.RLock()
        self.problem = ''
        self.data = dict(schema=1, revision=0, cards=[], migratedIdeas=[], sync={})
        if self.path.exists():
            try:
                value = json.loads(self.path.read_text(encoding='utf-8'))
                self._validate_store(value)
                self.data = value
            except (ValueError, TypeError, KeyError, OSError):
                self.problem = 'Board file could not be read. Original retained; restore a valid backup before saving.'
        else:
            for f in features:
                for i, step in enumerate(f['next']):
                    self.data['cards'].append(self._new(dict(title=step[:180], description=step,
                        area=f['id'], status='Ready' if i == 0 else 'Inbox',
                        kind='art' if f['id'] in ('cabinet', 'sourceArt', 'cabinetShapes', 'scenes', 'social', 'stingers') else 'feature',
                        acceptance='Record the expected result and verify it against the feature roadmap before owner acceptance.',
                        evidence=f['roadmap']), 'seed-' + f['id'] + '-' + str(i)))

    def _new(self, values, identity=None):
        return dict(card_values(values, self.areas), id=identity or str(uuid.uuid4()),
                    version=1, updatedAt=time.time(), attachments=[])

    def _validate_store(self, value):
        if not isinstance(value, dict) or value.get('schema') != 1 or not isinstance(value.get('revision'), int) or value['revision'] < 0:
            raise ValueError('Unsupported board backup')
        if not isinstance(value.get('cards'), list) or len(value['cards']) > 1000:
            raise ValueError('Board has too many cards')
        ids = set()
        for c in value['cards']:
            card_values({k: c[k] for k in FIELDS}, self.areas)
            if not isinstance(c['id'], str) or not c['id'] or len(c['id']) > 160 or c['id'] in ids:
                raise ValueError('Duplicate or invalid card ID')
            ids.add(c['id'])
            if not isinstance(c.get('version'), int) or c['version'] < 1 or not isinstance(c.get('attachments'), list):
                raise ValueError('Invalid card version')
            if len(c['attachments'])>10 or any(not isinstance(a,str) or not re.fullmatch(r'[a-f0-9]{64}\.png',a) for a in c['attachments']):
                raise ValueError('Invalid screenshots')
            if not isinstance(c.get('updatedAt'),(int,float)) or not math.isfinite(c['updatedAt']):
                raise ValueError('Invalid update time')
        if not isinstance(value.get('migratedIdeas'), list) or not isinstance(value.get('sync'), dict):
            raise ValueError('Invalid board metadata')

    def _persist(self, value):
        if self.problem:
            raise ValueError(self.problem)
        self._validate_store(value)
        self.home.mkdir(parents=True, exist_ok=True)
        temp = self.path.with_suffix('.tmp')
        temp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
        if self.path.exists():
            # Copy backup, then replace: no period where the main file is missing.
            self.path.with_suffix('.json.bak').write_bytes(self.path.read_bytes())
        temp.replace(self.path)
        self.data = value

    def snapshot(self):
        with self.lock:
            return dict(deepcopy(self.data), statuses=STATUSES, types=TYPES, priorities=PRIORITIES,
                        features=deepcopy(self.features), error=self.problem)

    def migrate(self, roadmaps):
        with self.lock:
            if self.problem:
                return
            value = deepcopy(self.data)
            for area, r in roadmaps.items():
                for idea in r.get('ideas', []):
                    key = area + ':' + idea['id']
                    if key not in value['migratedIdeas'] and idea['text'].strip():
                        c = self._new(dict(title=idea['text'][:180], description=idea['text'], area=area,
                                           priority='P1' if idea['pinned'] else 'P2'))
                        value['cards'].append(c)
                        value['migratedIdeas'].append(key)
            if value != self.data or not self.path.exists():
                value['revision'] += 1
                self._persist(value)

    def action(self, request):
        with self.lock:
            if not isinstance(request, dict) or request.get('revision') != self.data['revision']:
                raise BoardConflict('The board changed in another window. Reload before saving; your draft is still open.')
            value = deepcopy(self.data)
            action = request.get('action')
            if action == 'create':
                value['cards'].append(self._new(request.get('card')))
            elif action == 'update':
                c = next((c for c in value['cards'] if c['id'] == request.get('id')), None)
                if not c:
                    raise ValueError('Card not found')
                c.update(card_values(request.get('card'), self.areas))
                c['version'] += 1
                c['updatedAt'] = time.time()
            elif action == 'import':
                backup = request.get('board')
                self._validate_store(backup)
                existing = {c['id']: c for c in value['cards']}
                for c in backup['cards']:
                    if c['id'] not in existing:
                        # Attachments belong to the exporting machine unless copied separately.
                        imported = deepcopy(c)
                        imported['attachments'] = []
                        value['cards'].append(imported)
                    elif {k: c[k] for k in FIELDS} != {k: existing[c['id']][k] for k in FIELDS}:
                        raise BoardConflict('Import contains a different version of an existing card. No cards were changed.')
                value['migratedIdeas'] = list(set(value['migratedIdeas'] + backup['migratedIdeas']))
            else:
                raise ValueError('Unknown board action')
            value['revision'] += 1
            self._persist(value)
            return self.snapshot()

    def attach(self, request):
        from PIL import Image
        with self.lock:
            if not isinstance(request, dict) or request.get('revision') != self.data['revision']:
                raise BoardConflict('Reload the board before attaching a screenshot')
            value = deepcopy(self.data)
            c = next((c for c in value['cards'] if c['id'] == request.get('id')), None)
            if not c or len(c['attachments']) >= 10:
                raise ValueError('Choose a card with fewer than ten screenshots')
            try:
                raw = base64.b64decode(request.get('image', ''), validate=True)
                if not 0 < len(raw) <= 1500000:
                    raise ValueError()
                im = Image.open(io.BytesIO(raw))
                if im.format not in ('PNG', 'JPEG', 'WEBP') or im.width * im.height > 16000000:
                    raise ValueError()
                im.load()
                # Re-encode to strip metadata and never serve user-supplied executable content.
                out = io.BytesIO()
                im.convert('RGB').save(out, 'PNG')
                raw = out.getvalue()
            except Exception:
                raise ValueError('Choose a PNG, JPEG or WebP screenshot under 1.5 MB and 16 megapixels') from None
            name = hashlib.sha256(raw).hexdigest() + '.png'
            folder = self.home / 'board-attachments'
            folder.mkdir(parents=True, exist_ok=True)
            (folder / name).write_bytes(raw)
            if name not in c['attachments']:
                c['attachments'].append(name)
            c['version'] += 1
            c['updatedAt'] = time.time()
            value['revision'] += 1
            self._persist(value)
            return self.snapshot()
