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

# Wait for the exact checked-out content, not an old version.json marker.
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
    assert page.locator('h1').inner_text() == '서비스 운영 / 개선 기획'
    assert not re.search(r'\b(?:QA|UAT|CX|NiFi|Prometheus)\b', text, re.I)
    assert '기여도' not in text
    assert '모니터링 / 초기 대응' in text and '원인 구분 / 즉시 조치' in text
    assert 'OneClick 서류 발급상황' in text and '정상화 확인' in text
    assert 'ITSM 승인' in text and '서버와 배치 운영은 부담당' in text
    assert 'Google Analytics' in text and not re.search(r'\bGA\b', text)
    assert 'SQL 기초' in text
    assert text.count('Figma') == 1
    assert 'Figma를 활용한 서비스 기획 및 협업' in page.locator('#skills .tool').nth(0).inner_text()
    assert 'Figma' not in page.locator('#skills .tool').nth(2).inner_text()
    assert '참여 이전' in page.locator('#evolution').inner_text()
    assert '요구사항와' not in text
    sections = page.locator('#app > section').evaluate_all('(elements) => elements.map(e => e.id || (e.classList.contains("hero") ? "hero" : e.classList.contains("contact") ? "summary" : "career"))')
    assert sections[:3] == ['hero', 'monitoring', 'system']
    assert page.locator('#planning .case').first.locator('h3').inner_text() == 'PDF 직접 첨부 / 제출 경로 개선'
    images = page.locator('img').evaluate_all('(elements) => elements.map(i => ({url:i.src,width:i.naturalWidth,height:i.naturalHeight}))')
    assert all(image['url'].startswith(URL + 'assets/') for image in images)
    assert len(images) == 8
    for selector, name in [('.hero', 'overview'), ('#monitoring', 'monitoring'), ('#case', 'manuals'), ('#evolution', 'service-images'), ('#skills', 'skills')]:
        page.locator(selector).screenshot(path=str(OUT / (name + '.png')))
    viewport_checks = []
    for width in [1280, 768, 390, 360]:
        page.set_viewport_size({'width': width, 'height': 960})
        assert not page.evaluate('document.documentElement.scrollWidth > innerWidth'), f'Horizontal overflow at {width}px'
        viewport_checks.append({'width': width, 'horizontalOverflow': False})
    page.set_viewport_size({'width': 390, 'height': 844})
    page.locator('#monitoring').screenshot(path=str(OUT / 'mobile-monitoring.png'))
    page.locator('#evolution').screenshot(path=str(OUT / 'mobile.png'))
    report = {'url': URL, 'httpStatus': response.status, 'htmlSha256': expected_digest, 'sectionOrder': sections, 'imageCount': len(images), 'images': images, 'monitoringAtTop': True, 'initialResponseExpanded': True, 'qaAndContributionAbsent': True, 'figmaInPlanningOnly': True, 'sqlBasicPreserved': True, 'viewportChecks': viewport_checks, 'browserErrors': errors}
    (OUT / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    (OUT / 'visible-text.txt').write_text(text)
    (OUT / 'source-index.html').write_bytes(deployed_html)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    assert not errors
    context.close()
    browser.close()
