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
expected_css = Path('public/cx-portfolio.css').read_bytes()
css_digest = hashlib.sha256(expected_css).hexdigest()

def download(path=''):
    separator = '&' if '?' in path else '?'
    request = urllib.request.Request(URL + path + separator + 'verify=' + str(time.time()), headers={'Cache-Control': 'no-cache'})
    with urllib.request.urlopen(request, timeout=15) as response:
        return response.read()

for attempt in range(24):
    try:
        deployed_html = download()
        deployed_css = download('cx-portfolio.css')
        if hashlib.sha256(deployed_html).hexdigest() == expected_digest and hashlib.sha256(deployed_css).hexdigest() == css_digest:
            break
    except Exception as error:
        print('Waiting for deployment:', type(error).__name__)
    time.sleep(8)
else:
    raise RuntimeError('Production did not serve the expected committed HTML and stylesheet')

with sync_playwright() as playwright:
    executable = shutil.which('google-chrome') or shutil.which('chromium')
    browser = playwright.chromium.launch(executable_path=executable, headless=True, args=['--no-sandbox'])
    context = browser.new_context(viewport={'width': 1280, 'height': 960}, device_scale_factor=1.5)
    page = context.new_page()
    errors = []
    failed_requests = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('requestfailed', lambda request: failed_requests.append({'url': request.url, 'error': request.failure}))
    response = page.goto(URL + '?verify=' + str(time.time()), wait_until='networkidle')
    assert response.status == 200
    assert page.locator('meta[name="portfolio-version"]').get_attribute('content') == 'modusign-cx-20261007'
    page.locator('img').evaluate_all('(images) => images.forEach(image => image.loading = "eager")')
    page.wait_for_function('document.images.length === 8 && [...document.images].every(i => i.complete && i.naturalWidth > 0)', timeout=30000)
    page.evaluate('document.fonts.ready')
    text = page.locator('body').inner_text()
    full_text = page.locator('body').text_content()
    assert re.sub(r'\s+', ' ', page.locator('h1').inner_text()).strip() == '고객 지원 / 서비스 개선'
    assert not re.search(r'\b(?:QA|UAT|NiFi|Prometheus)\b', full_text, re.I)
    assert '기여도' not in full_text
    for required in ['애니서포트', '정부24 연계 주소 오류', 'OID', 'payload(JSON)', '30건 내외 → 1건 내외', '300건 이상 → 10건 내외', '입사 후 활용 계획', 'Unity MCP', '직접 제작한 매뉴얼 2종과는 별도']:
        assert required in full_text, required
    assert '기능 구현: 개발실' in text
    assert '챗봇 시스템은 별도 개발 중' in text
    assert 'Google Analytics' in text and not re.search(r'\bGA\b', text)
    assert 'SQL 기초 SELECT' in text
    assert full_text.count('Figma') == 1
    assert 'Figma를 활용한 서비스 기획 및 협업' in page.locator('#skills details').text_content()
    assert '참여 이전' in page.locator('#evolution').inner_text()
    assert '2020.11 - 2022.03' in text and '2019.12 - 2020.10' in text
    sections = page.locator('#app > section').evaluate_all('(elements) => elements.map(e => e.id || "hero")')
    assert sections == ['hero', 'evolution', 'support', 'case', 'manuals', 'diagnosis', 'monitoring', 'system', 'ai', 'skills']
    assert 'Grafana' in text and '서류 발급상황' in text and '정상화 안내' in text
    images = page.locator('img').evaluate_all('(elements) => elements.map(i => ({url:i.src,width:i.naturalWidth,height:i.naturalHeight}))')
    assert len(images) == 8 and all(image['url'].startswith(URL + 'assets/') for image in images)
    for image in images:
        relative = image['url'].removeprefix(URL)
        expected_asset = Path('public', relative).read_bytes()
        image['sha256'] = hashlib.sha256(download(relative)).hexdigest()
        assert image['sha256'] == hashlib.sha256(expected_asset).hexdigest(), relative
    broken_anchors = page.locator('a[href^="#"]').evaluate_all('(links) => links.filter(a => !document.getElementById(a.hash.slice(1))).map(a => a.hash)')
    assert not broken_anchors
    page.screenshot(path=str(OUT / 'first-screen.png'))
    # Hide the sticky navigation only while taking section screenshots.
    page.locator('header').evaluate('(e) => e.style.visibility="hidden"')
    for selector, name in [('.hero','overview'),('#evolution','service-images'),('#support','support'),('#case','case'),('#manuals','manuals'),('#diagnosis','diagnosis'),('#monitoring','monitoring'),('#system','operations'),('#ai','ai'),('#skills','skills')]:
        page.locator(selector).screenshot(path=str(OUT / (name + '.png')))
    page.locator('header').evaluate('(e) => e.style.visibility=""')
    viewport_checks = []
    for width in [1440, 1280, 900, 780, 768, 540, 390, 360]:
        page.set_viewport_size({'width': width, 'height': 960})
        assert not page.evaluate('document.documentElement.scrollWidth > innerWidth'), f'Horizontal overflow at {width}px'
        viewport_checks.append({'width': width, 'horizontalOverflow': False})
    page.set_viewport_size({'width': 390, 'height': 844})
    page.locator('header').evaluate('(e) => e.style.visibility="hidden"')
    for selector, name in [('.hero','mobile-overview'),('#support','mobile-support'),('#monitoring','mobile-monitoring'),('#evolution','mobile-images')]:
        page.locator(selector).screenshot(path=str(OUT / (name + '.png')))
    page.locator('#skills details').evaluate('(e) => e.open=true')
    assert 'Figma를 활용한 서비스 기획 및 협업' in page.locator('#skills').inner_text()
    assert page.locator('#skills details .pairs > div').nth(1).inner_text().find('Figma') == -1
    page.locator('#skills').screenshot(path=str(OUT / 'mobile-skills.png'))
    report = {'url': URL, 'version': 'modusign-cx-20261007', 'httpStatus': response.status, 'htmlSha256': expected_digest, 'cssSha256': css_digest, 'sectionOrder': sections, 'approvedPortfolioApplied': True, 'metricsScopesSeparated': True, 'manualEvidenceSeparated': True, 'aiPlansSeparated': True, 'imageCount': len(images), 'images': images, 'allOriginalImageBytesPreserved': True, 'qaAndContributionAbsent': True, 'grafanaRetained': True, 'figmaInPlanningOnly': True, 'sqlBasicPreserved': True, 'viewportChecks': viewport_checks, 'brokenAnchors': broken_anchors, 'browserErrors': errors, 'failedRequests': failed_requests}
    (OUT / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    (OUT / 'visible-text.txt').write_text(full_text)
    (OUT / 'source-index.html').write_bytes(deployed_html)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    assert not errors and not failed_requests
    context.close()
    browser.close()
