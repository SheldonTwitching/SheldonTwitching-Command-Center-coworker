"""Original-art regression tests, independent of a physical controller or OBS."""
import base64
import json
import sys
from pathlib import Path
import pytest
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from arcade_studio import ArcadeStudio, DEFAULT, INPUT_FLAGS, validated
ASSETS=ROOT/'arcade/assets'

def test_source_pixels_and_alpha_are_preserved():
    geometry=json.loads((ASSETS/'geometry.json').read_text())
    assert geometry['missing']==[]
    assert Image.open(ASSETS/'CABINET.png').size==(1942,1220)
    assert Image.open(ASSETS/'FX.png').size==(2030,1220)
    assert Image.open(ASSETS/'BUTTON_NEUTRAL.png').size==(78,66)
    assert Image.open(ASSETS/'BUTTON_PRESSED.png').size==(78,60)
    # The exported safe rectangle must actually be transparent in BOTH supplied layers.
    for name,x in [('CABINET.png',59),('FX.png',15)]:
        alpha=Image.open(ASSETS/name).getchannel('A')
        assert alpha.crop((443-x,374,1617-x,952)).getextrema()==(0,0)
    # The reference contains these sprites at exact, unscaled pixel coordinates.
    reference=Image.open(ASSETS/'ArcadeCabinet_FINAL.png')
    for name,x,y in [('BUTTON_AREA.png',1113,1049),('NEUTRAL.png',842,942)]:
        sprite=Image.open(ASSETS/name)
        for sy in range(sprite.height):
            for sx in range(sprite.width):
                pixel=sprite.getpixel((sx,sy))
                if pixel[3]==255:assert reference.getpixel((x+sx,y+sy))[:3]==pixel[:3]

def test_eight_neutral_buttons_reconstruct_the_reference_sheet():
    sheet=Image.open(ASSETS/'BUTTON_AREA.png');neutral=Image.open(ASSETS/'BUTTON_NEUTRAL.png')
    composite=Image.new('RGBA',sheet.size)
    for position in [(26,4),(106,0),(186,0),(266,4),(0,44),(80,40),(160,40),(240,44),(362,34)]:
        composite.alpha_composite(neutral,position)
    for y in range(sheet.height):
        for x in range(sheet.width):
            source=sheet.getpixel((x,y))
            if source[3]==255:assert composite.getpixel((x,y))[:3]==source[:3]

def test_original_configuration_and_variations_remain_independent(tmp_path):
    studio=ArcadeStudio(tmp_path);c=studio.get()
    assert (c['canvasWidth'],c['canvasHeight'])==(2060,1220)
    assert (c['gameLeft'],c['gameTop'],c['gameWidth'],c['gameHeight'])==(403,340,1254,646)
    assert c['gameAspect']=='original' and not c['artworkEffects']
    positions=c['originalPositions'];c.update(artworkMode='variation',gameWidth=1280,gameTop=138)
    studio.save(c);assert studio.get()['canvasWidth']==1920
    c=studio.get();c['artworkMode']='original';studio.save(c)
    assert studio.get()['originalPositions']==positions

@pytest.mark.parametrize('point',[[float('nan'),10],[-1,0],[100,1200],[True,20],'bad'])
def test_invalid_sprite_positions(point):
    c=validated({});c['originalPositions']['buttons'][0]=point
    with pytest.raises(ValueError):validated(c)

def test_sprites_events_migrate_and_save(tmp_path):
    c=validated({});image='data:image/png;base64,'+base64.b64encode((ASSETS/'BUTTON_PRESSED.png').read_bytes()).decode()
    c['spriteOverrides'][0]=image;c['eventSettings']['donation']['sprite']=image
    studio=ArcadeStudio(tmp_path);studio.save(c)
    assert ArcadeStudio(tmp_path).get()['spriteOverrides'][0]==image
    studio.trigger_event('donation','Test');assert studio.live()['event']['sprite']==image
    for bad in ['https://example.com/button.png','data:image/png;base64,aGVsbG8=']:
        c['spriteOverrides'][0]=bad
        with pytest.raises(ValueError):validated(c)
    legacy={**DEFAULT};legacy['eventSettings']={k:{key:v for key,v in value.items() if key!='sprite'} for k,value in DEFAULT['eventSettings'].items()}
    assert validated(legacy)['eventSettings']['donation']['sprite']==''

def test_face_buttons_and_dpad_are_separate(tmp_path):
    studio=ArcadeStudio(tmp_path);studio._controller_bits=lambda:INPUT_FLAGS['X']|INPUT_FLAGS['DPAD_UP']|INPUT_FLAGS['DPAD_RIGHT']
    state=studio.live();assert state['pressed']==[0]
    assert state['dpad']==['DPAD_UP','DPAD_RIGHT']
