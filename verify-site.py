from pathlib import Path
import json,re,time,urllib.request,shutil,hashlib
from playwright.sync_api import sync_playwright
url='https://hyojin-serviceops.vercel.app/'
out=Path('verification');out.mkdir(exist_ok=True)
for attempt in range(24):
    try:
        with urllib.request.urlopen(url+'version.json?check='+str(time.time()),timeout=12) as response:
            version=json.load(response)
        if version.get('version')=='portfolio-repair-20260920':break
    except Exception:pass
    time.sleep(10)
else:raise RuntimeError('Updated production version was not reachable after four minutes')
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=shutil.which('google-chrome') or shutil.which('chromium'),headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1280,'height':900},device_scale_factor=1.5)
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    response=page.goto(url+'?verify='+str(time.time()),wait_until='networkidle')
    assert response.status==200
    page.locator('img').evaluate_all('(imgs)=>imgs.forEach(img=>img.loading="eager")')
    page.wait_for_function('document.images.length===8 && [...document.images].every(i=>i.complete&&i.naturalWidth>0)',timeout=30000)
    page.evaluate('document.fonts.ready')
    text=page.locator('body').inner_text()
    assert not re.search(r'\b(?:QA|UAT)\b',text,re.I),'QA/UAT text is still visible'
    assert '기여도' not in text
    assert 'Grafana' in text and '서류 발급' in text
    assert 'Google Analytics' in text and not re.search(r'\bGA\b',text)
    assert text.count('Figma')==1
    assert 'Figma를 활용한 서비스 기획 및 협업' in text
    images=page.locator('img').evaluate_all('(imgs)=>imgs.map(i=>({url:i.src,width:i.naturalWidth,height:i.naturalHeight}))')
    assert all(i['url'].startswith(url+'assets/') for i in images)
    assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
    for selector,name in [('.hero','overview'),('#case','manuals'),('#evolution','service-images'),('#monitoring','monitoring'),('#skills','skills')]:
        page.locator(selector).screenshot(path=str(out/(name+'.png')))
    page.set_viewport_size({'width':390,'height':844})
    assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'),'Mobile horizontal overflow'
    page.locator('#evolution').screenshot(path=str(out/'mobile.png'))
    result={'url':url,'version':version,'httpStatus':response.status,'imageCount':len(images),'images':images,'qaRemoved':True,'contributionRemoved':True,'figmaInPlanningOnly':True,'monitoringRetained':True,'desktopAndMobileChecked':True,'browserErrors':errors}
    (out/'report.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    (out/'visible-text.txt').write_text(text)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    assert not errors
    browser.close()
