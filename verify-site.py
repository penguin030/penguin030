from pathlib import Path
import hashlib
import json
import re
import shutil
import time
import urllib.request
from playwright.sync_api import sync_playwright

URL = 'https://hyojin-serviceops.vercel.app/'
OUT = Path('verification')
OUT.mkdir(exist_ok=True)
expected_html = Path('public/index.html').read_bytes()
expected_digest = hashlib.sha256(expected_html).hexdigest()

# Wait for this exact source revision, not a stale deployment marker.
for attempt in range(24):
    try:
        request = urllib.request.Request(URL + '?verify=' + str(time.time()), headers={'Cache-Control': 'no-cache'})
        with urllib.request.urlopen(request, timeout=15) as response:
            deployed_html = response.read()
        if hashlib.sha256(deployed_html).hexdigest() == expected_digest:
            break
    except Exception as error:
        print('Waiting for deployment:', type(error).__name__)
    time.sleep(8)
else:
    raise RuntimeError('Production did not serve the expected committed HTML within the verification window')

# These canonical text hashes preserve the reviewed copy and existing operations cases.
expected_text = {
    'body': '0c0db7349b71b94b687bda60c8a90c786a6da28cf8724fc4ff76e34516ed9753',
    '.hero': '28fdcc0cae2b185165f92ed3f8e88038fcac263cd3168cd21e7cc6e245bf68be',
    '#oneclick': '478a84396f012bbfce19f83975aaa605f66079898538efb5253a416ae0243b98',
    '#monitoring': 'a9abe14d195595d178bc57bec4f11dd7ea7a3990d8e58feee8421712893472d9',
    '#system': 'ff8a89a488ea011000225234026354bc4c6735a72b26af8671d04b189e782768',
    '#modernization': '4c787d2229ff73f97e573de8af939ccf3b299c70bc727e8939840b5fe8efd875',
    '#planning': '5ef543ada217a6688a49c7d9de7bc9decea919b2eb8b1ccacf3a58b31ff312c1',
    '#integration': 'bbc330520d1464e95e0aa5dcba25d82d3ee60f8ea4d0d6c51f0c6d3cba57de2e',
    '#skills': '4e8bf48cf2da33deaebdaa2bc595f01c933264bdae38103e7028b2877ddce69b',
    '#evolution': '005f19d8b57ec5ee2819eaaa6243698dda357bd49ffb896835f58a81829d0a8d'
}

with sync_playwright() as playwright:
    executable = shutil.which('google-chrome') or shutil.which('chromium')
    browser = playwright.chromium.launch(executable_path=executable, headless=True, args=['--no-sandbox'])
    context = browser.new_context(viewport={'width': 1280, 'height': 960}, device_scale_factor=1.5)
    page = context.new_page()
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    response = page.goto(URL + '?verify=' + str(time.time()), wait_until='networkidle')
    assert response.status == 200
    page.locator('img').evaluate_all('(images) => images.forEach(image => image.loading = "eager")')
    page.wait_for_function('document.images.length === 8 && [...document.images].every(i => i.complete && i.naturalWidth > 0)', timeout=30000)
    page.evaluate('document.fonts.ready')
    text = page.locator('body').inner_text()
    (OUT / 'visible-text.txt').write_text(text)
    (OUT / 'source-index.html').write_bytes(deployed_html)
    content_checks = []
    for selector, expected in expected_text.items():
        canonical = re.sub(r'\s+', '', page.locator(selector).text_content())
        actual = hashlib.sha256(canonical.encode()).hexdigest()
        content_checks.append({'selector': selector, 'sha256': actual, 'matched': actual == expected})
    (OUT / 'content-checks.json').write_text(json.dumps(content_checks, indent=2))
    assert all(item['matched'] for item in content_checks), 'Reviewed portfolio text changed unexpectedly'
    assert page.locator('h1').inner_text() == '서비스 운영 / 개선 기획'
    assert not re.search(r'\b(?:QA|UAT|CX|NiFi|Prometheus)\b', text, re.I)
    assert '기여도' not in text
    assert '원클릭 / 서비스 개요' in text and '고도화 배경 / 기존 제약' in text
    assert '최대 300개는 고객사별로 개설된 서비스 수' in text
    assert '지정된 폴더 경로' in text and '최초 등록한 뒤 재사용' in text
    assert '모니터링 / 초기 대응' in text and '원인 구분 / 즉시 조치' in text
    assert 'OneClick 서류 발급상황' in text and '정상화 확인' in text
    assert 'ITSM 승인' in text and '서버와 배치 운영은 부담당' in text
    assert 'Google Analytics' in text and not re.search(r'\bGA\b', text)
    assert 'SQL 기초' in text and text.count('Figma') == 1
    assert 'Figma를 활용한 서비스 기획 및 협업' in page.locator('#skills .tool').nth(0).inner_text()
    assert 'Figma' not in page.locator('#skills .tool').nth(2).inner_text()
    assert '참여 이전' in page.locator('#evolution').inner_text()
    sections = page.locator('#app > section').evaluate_all('(elements) => elements.map(e => e.id || (e.classList.contains("hero") ? "hero" : e.classList.contains("contact") ? "summary" : "career"))')
    assert sections[:4] == ['hero', 'oneclick', 'monitoring', 'system']
    assert page.locator('#planning .case').first.locator('h3').inner_text() == 'PDF 직접 첨부 / 제출 경로 개선'
    images = page.locator('img').evaluate_all('(elements) => elements.map(i => ({url:i.src,width:i.naturalWidth,height:i.naturalHeight}))')
    assert all(image['url'].startswith(URL + 'assets/') for image in images)
    assert len(images) == 8
    asset_checks = []
    for image in images:
        asset_path = image['url'][len(URL):]
        with urllib.request.urlopen(image['url'], timeout=15) as asset_response:
            downloaded = asset_response.read()
        local_bytes = (Path('public') / asset_path).read_bytes()
        assert hashlib.sha256(downloaded).digest() == hashlib.sha256(local_bytes).digest(), asset_path
        asset_checks.append({'path':asset_path,'sha256':hashlib.sha256(downloaded).hexdigest(),'matchesRepository':True})
    for link in page.locator('nav a').all():
        href = link.get_attribute('href')
        assert href and href.startswith('#') and page.locator(href).count() == 1, href
    for selector, name in [('.hero', 'overview'), ('#oneclick','service-overview'), ('#modernization','modernization'), ('#monitoring', 'monitoring'), ('#case .shots', 'manuals'), ('#evolution', 'service-images'), ('#skills', 'skills')]:
        page.locator(selector).screenshot(path=str(OUT / (name + '.png')))
    viewport_checks = []
    for width in [1280, 1024, 900, 800, 768, 390, 360]:
        page.set_viewport_size({'width': width, 'height': 960})
        assert not page.evaluate('document.documentElement.scrollWidth > innerWidth'), f'Horizontal overflow at {width}px'
        viewport_checks.append({'width': width, 'horizontalOverflow': False})
    page.set_viewport_size({'width': 390, 'height': 844})
    page.locator('#oneclick').screenshot(path=str(OUT / 'mobile-service-overview.png'))
    page.locator('#modernization').screenshot(path=str(OUT / 'mobile-modernization.png'))
    page.locator('#evolution').screenshot(path=str(OUT / 'mobile.png'))
    report = {'url': URL, 'httpStatus': response.status, 'htmlSha256': expected_digest, 'sectionOrder': sections, 'contentChecks':content_checks, 'imageCount': len(images), 'images': images, 'assetChecks':asset_checks, 'serviceContextAdded':True, 'modernizationReasonsAdded':True, 'originalOperationsCopyPreserved':True, 'qaAndContributionAbsent': True, 'figmaInPlanningOnly': True, 'sqlBasicPreserved': True, 'viewportChecks': viewport_checks, 'browserErrors': errors}
    (OUT / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    assert not errors
    context.close()
    browser.close()
