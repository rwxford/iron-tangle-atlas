"""Optional local browser regressions. Requires Playwright and Chromium."""
import json, pathlib, re
from playwright.sync_api import sync_playwright
ROOT=pathlib.Path(__file__).resolve().parents[1]
# In-memory DOM integration test: this environment blocks browser navigation.
# Data fetch, localStorage and history are explicit fixtures, not live-host checks.
def prepare(page, fragment=''):
    html=(ROOT/'web/reader.html').read_text()
    html=re.sub(r'<script[^>]*src=[^>]*></script>', '', html)
    html=re.sub(r'<link[^>]*stylesheet[^>]*>', '', html)
    page.set_content(html)
    page.add_style_tag(content=(ROOT/'web/reader.css').read_text())
    page.evaluate("""(args) => {
        const store=new Map();
        Object.defineProperty(window,'localStorage',{value:{getItem:k=>store.get(k)||null,setItem:(k,v)=>store.set(k,v)}});
        window.fetch=async (url)=>({ok:true,json:async()=>String(url).includes('release.json')?{commit:'local-fixture'}:args.data});
        window.__testURL=args.fragment;
        history.pushState=history.replaceState=(_a,_b,url)=>{window.__testURL=url;};
        if(args.fragment) location.hash=args.fragment;
    }""", {'data':json.loads((ROOT/'data.json').read_text()),'fragment':fragment})
    page.add_script_tag(content=(ROOT/'web/core.js').read_text())
    page.add_script_tag(content=(ROOT/'web/reader.js').read_text())
    page.wait_for_function('window.__atlas')
checks=[]
def check(label,value):
    assert value,label
    checks.append(label)
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1440,'height':1000})
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    prepare(page)
    check('opening has one primary location',page.locator('.map-node').count()==1)
    page.locator('#map [data-node="red-81"]').click()
    check('station map target opens details',page.locator('#panel').is_visible())
    page.locator('#reset').click()
    check('reset closes details',page.locator('#panel').is_hidden())
    page.locator('#progress').click();page.locator('#chapter').fill('14');page.locator('#phase').select_option('finished');page.get_by_role('button',name='Apply reading position').click()
    check('reading form updates cutoff',page.evaluate('__atlas.state.chapter===14 && __atlas.state.phase==="finished"'))
    check('inferred sequences absent',page.locator('[data-kind="sequence"]').count()==0)
    page.locator('#search').fill('83(b)');page.locator('#panelContent .result').click()
    check('global alias search opens correct physical station',page.evaluate('__atlas.state.node==="tangerine-plum-83"'))
    page.locator('summary',has_text='Private reading note').click();page.locator('#note').fill('PRIVATE TEST DO NOT SHARE')
    page.locator('#zoomIn').click();page.locator('#reset').click()
    check('reset preserves current chapter and group',page.evaluate('__atlas.state.chapter===14 && __atlas.state.group==="Carl"'))
    check('reset clears query and all selection',page.evaluate('__atlas.state.node===null && __atlas.state.route===null && __atlas.state.query===""'))
    check('reset synchronizes visible search and URL',page.locator('#search').input_value()=='' and 'station=' not in page.evaluate('window.__testURL') and 'q=' not in page.evaluate('window.__testURL'))
    check('note survives reset',page.evaluate('JSON.parse(localStorage.getItem("iron-tangle-atlas-v2")).notes["tangerine-plum-83"]==="PRIVATE TEST DO NOT SHARE"'))
    page.locator('#undo').click();check('undo restores selection',page.evaluate('__atlas.state.node==="tangerine-plum-83"'))
    page.locator('#more').click();page.get_by_role('button',name='Share this view',exact=True).click();link=page.locator('#shareText').input_value()
    check('share excludes notes', 'PRIVATE' not in link)
    page.locator('#closeDialog').click();page.locator('#reset').click()
    page.locator('#more').click();page.get_by_role('button',name='Start from chapter 1',exact=True).click();page.locator('#decline').click()
    check('restart cancel leaves position alone',page.evaluate('__atlas.state.chapter===14'))
    page.locator('#more').click();page.get_by_role('button',name='Start from chapter 1',exact=True).click();page.locator('#accept').click()
    check('restart is conservative and keeps notes',page.evaluate('__atlas.state.chapter===1 && __atlas.state.mode==="reading" && JSON.parse(localStorage.getItem("iron-tangle-atlas-v2")).notes["tangerine-plum-83"]==="PRIVATE TEST DO NOT SHARE"'))
    page.locator('#more').click();page.get_by_role('button',name='Open full reference map').click()
    check('reference is gated before future content appears',page.locator('#dialog').is_visible() and page.locator('.map-node').count()==1)
    page.locator('#accept').click();check('reference has thirty-seven plotted records',page.locator('.map-node').count()==37)
    page.locator('#search').fill('fulvis');check('sound-alike search finds Fulvous',page.locator('#panelContent .result strong').all_text_contents()==['Fulvous'])
    page.locator('#search').fill('mendaro');check('sound-alike search finds Mindaro',any('Mindaro' in x for x in page.locator('#panelContent .result strong').all_text_contents()))
    page.locator('#reset').click();page.locator('#layers').click();page.locator('#inferred').check();page.locator('#applyLayers').click()
    check('optional sequence guides have no arrows',page.locator('[data-kind="sequence"]').count()==11 and page.locator('[data-edge][marker-end]').count()==0)
    page.locator('#reset').click();check('reset restores default layers in reference mode',page.evaluate('__atlas.state.mode==="reference" && !__atlas.state.inferred'))
    page.screenshot(path=str(ROOT/'tests/desktop-0.3.png'),full_page=True)
    page.evaluate('__atlas.set({mode:"reading",chapter:24,phase:"finished",event:"carl-24-1",panel:null})')
    check('selected reverse journey has one contextual arrow',page.locator('[data-travel="carl-24-1"]').count()==1)
    check('general route paths remain directionless',page.locator('[data-edge][marker-end]').count()==0)
    page.locator('#search').fill('83(b)');page.locator('#search').press('ArrowDown');check('keyboard enters search results',page.evaluate('document.activeElement.classList.contains("result")'))
    page.keyboard.press('Enter');check('keyboard selects result',page.evaluate('__atlas.state.node==="tangerine-plum-83"'))
    page.keyboard.press('Escape');check('Escape closes details',page.locator('#panel').is_hidden())
    guest=browser.new_page(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
    prepare(guest,'#v=0.2.0-alpha&ch=14&mode=reading&station=tangerine-plum-83&line=nightmare')
    check('legacy link gated on fresh visit',guest.locator('#dialog').is_visible() and guest.locator('.map-node').count()==1)
    guest.locator('#accept').click();check('legacy duplicate alias restored',guest.evaluate('__atlas.state.node==="tangerine-plum-83"'))
    guest.locator('#reset').click();check('mobile search visible in initial viewport',guest.locator('#search').bounding_box()['y']<180)
    check('mobile reset visible in initial viewport',guest.locator('#reset').bounding_box()['y']<230)
    check('mobile no horizontal overflow',guest.evaluate('document.documentElement.scrollWidth<=innerWidth'))
    guest.locator('#search').fill('yard');check('mobile search opens bottom sheet',guest.locator('#panel').bounding_box()['y']>180)
    guest.locator('#expandPanel').click();check('bottom sheet expands',guest.locator('#panel').bounding_box()['height']>450)
    guest.locator('#reset').click();guest.screenshot(path=str(ROOT/'tests/mobile-0.3.png'),full_page=True)
    guest.set_viewport_size({'width':820,'height':1180});check('tablet no horizontal overflow',guest.evaluate('document.documentElement.scrollWidth<=innerWidth'))
    check('no browser exceptions',not errors)
    browser.close()
(ROOT/'tests/browser-results.json').write_text(json.dumps({'passed':len(checks),'checks':checks},indent=2))
print(json.dumps({'passed':len(checks),'checks':checks},indent=2))
