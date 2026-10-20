"""Versioned evidence from the actual owner PSD, without a Photoshop runtime dependency."""
import json
from pathlib import Path
from arcade_studio import CABINET_STRUCTURE,validated
from copy import deepcopy
import pytest
ROOT=Path(__file__).resolve().parents[1]

def test_psd_evidence_keeps_source_limits_and_recovered_frames():
    r=json.loads((ROOT/'docs/psd-reference/inventory.json').read_text(encoding='utf-8'))
    assert r['sourceUnchanged'] and r['source']['sha256']==CABINET_STRUCTURE['sourcePsd']['sha256']
    assert len(r['documents'])==4 and sum(len(d['layers']) for d in r['documents'])==47
    assert sum(v['sameRGBA'] for v in r['assetComparisons'])==16
    assert r['decodedAnimation']['selectedFrameMatchesSavedVisibility']
    assert [f['ball'][0] for f in r['decodedAnimation']['frames']]==['FRONT','FRONT_LEFT','LEFT','BACK_LEFT','BACK','BACK_RIGHT','RIGHT','FRONT_RIGHT']
    assert CABINET_STRUCTURE['controlGeometry']['arrowSizes']['DOWN']==[44,46]
    assert CABINET_STRUCTURE['controlGeometry']['button']['pressedTravel']==6

def test_material_settings_are_bounded_and_source_masks_stay_explicit():
    c=validated({});assert c['buttonSkin']['roles'][8]=='accent'
    for key,value in [('ballLighting',{'lightX':float('nan')}),('surfaceFinish',{'edgeGap':99}),('leverIndicators',{'shape':'unknown'})]:
        bad=deepcopy(c);bad[key].update(value)
        with pytest.raises(ValueError):validated(bad)
    bad=deepcopy(c);bad['buttonSkin']['roles']=bad['buttonSkin']['roles'][:8]
    with pytest.raises(ValueError):validated(bad)
