from pathlib import Path
from bs4 import BeautifulSoup
import re, json
source=Path('source-backup');out=Path('public');out.mkdir(parents=True,exist_ok=True)
soup=BeautifulSoup((source/'index.html').read_text(),'html.parser')
css=(source/'style.css').read_text()+'\n'+'\n'.join(s.get_text() for s in soup.find_all('style'))
for n in soup.find_all(['script','style']):n.decompose()
for n in soup.select('link[rel=stylesheet]'):n.decompose()
soup.head.append(soup.new_tag('link',rel='stylesheet',href='/style.css'))
app=soup.select_one('#app');app.clear();app.append(BeautifulSoup(''.join((source/f'part{i}.html').read_text() for i in range(1,5)),'html.parser'))
def frag(v):return BeautifulSoup(v,'html.parser')
def text(q,v):
 n=soup.select_one(q)
 if n:n.clear();n.append(v)
def html(q,v):
 n=soup.select_one(q)
 if n:n.clear();n.append(frag(v))
text('title','HYOJIN — 서비스 기획 / 운영 개선')
soup.select_one('meta[name=description]')['content']='OneClick 서비스 기획, 운영 개선, VOC 분석, 백오피스 관리, Grafana 모니터링 포트폴리오'
text('.brand','HYOJIN / SERVICE PLANNING & OPERATIONS')
html('.nav','<a href="#case">CASE</a><a href="#planning">PLANNING</a><a href="#evolution">EVOLUTION</a><a href="#monitoring">MONITORING</a><a href="#skills">SKILLS</a>')
text('.hero .ey','서비스 기획 / 운영 개선');text('.hero h1','운영에서 기획까지')
text('.hero .lead','약 300개 공공·민간기관과 연결된 B2B 웹 서비스 OneClick을 4년간 운영·개선했습니다. 사용자 흐름과 운영 조건을 분석해 적용 대상, 예외사항, 화면 안내와 대체 제출 흐름을 정리했습니다. 개발·디자인·영업·CS와 적용 범위를 조율하고, 운영 반영 후 이용량과 문의 변화를 확인했습니다.')
html('.hero .chips',''.join(f'<span>{x}</span>' for x in ['서비스 기획','운영 조건','사용자 흐름','VOC 분석','고객사 협업','Grafana 모니터링']))
soup.select_one('.hero .metrics').insert_after(frag('<div class="top-focus"><article><small>SERVICE PLANNING</small><b>문제 발견 / 개선안 정리</b><p>반복 문의와 사용자 흐름을 기준으로 개선 대상과 해결 방식을 정리했습니다.</p></article><article><small>POLICY / RULE</small><b>적용 조건 / 예외 관리</b><p>지원 서류, 인증 방식, 사용자 유형과 백오피스 운영 기준을 함께 확인했습니다.</p></article><article><small>OPERATIONS</small><b>운영 반영 / 결과 확인</b><p>변경사항을 운영에 반영하고 발급상황, 이용량과 문의 변화를 확인했습니다.</p></article></div>'))
html('#case .head h2','브라우저 OneClick<br>고도화')
text('#case .head > p','웹 OneClick에서 브라우저 OneClick으로 전환되는 과정에 참여했습니다. 사용자 흐름, 인증 환경, 화면 안내와 기관별 운영 조건을 정리하고, 기존 설정과 달라지는 구간의 누락·예외를 보완해 개발·디자인과 수정 범위를 맞췄습니다.')
soup.select('#case .meta b')[2].string='문제 정의 / 요구사항 정리 / 운영 반영'
html('#case .problem','<b>개선 대상</b><br>등록 → 기관·서류 선택 → 인증 → 발급 → 제출 → 결과 확인 흐름에서 사용자 유형별로 달라지는 조건과 반복 문의를 확인했습니다.')
cards=soup.select('#case .cards > article')
cards[0].select_one('h3').string='사용자 흐름 / 조건 확인'
cards[0].select_one('p').string='개인, 개인사업자, 법인, 세무대리인에 따라 달라지는 인증 방식과 제출 조건을 구분했습니다.'
cards[1].select_one('h3').string='요구사항 / 예외 정리'
cards[2].decompose();cards[3].select_one('small').string='03 / OPERATION';cards[3].select_one('h3').string='운영 기준 / 문서화'
r=cards[3].select_one('.role');r.clear();r.append(frag('<b>담당 범위</b><br>운영 이슈 분석, 요구사항 정리, 유관부서 협의와 운영 반영을 담당했습니다. 개발 구현은 개발 담당자가 수행했습니다.'))
soup.select_one('#case .cards')['class']=['cards','case-process']
for h in soup.select('#case h2'):
 if '이용가이드' in h.get_text():h.string='이용가이드 / 실제 화면'
text('#planning .head h2','문제 발견 / 서비스 개선')
text('#planning .head > p','사용자 환경과 원천기관 결과를 비교해 원인을 구분하고, 문의 빈도와 영향도에 따라 화면 안내, 운영 기준, 대체 제출 흐름으로 해결 방식을 나눴습니다.')
steps=[('문제 발견','반복 VOC 확인'),('원인 확인','사용자 환경과 원천기관 비교'),('개선안 정리','안내·운영 기준·대체 흐름'),('요구사항 협의','적용 대상과 예외 정리'),('운영 반영','화면·백오피스·매뉴얼'),('결과 확인','문의량과 이용 결과')]
html('#planning .planning-flow',''.join(f'<div><small>{i:02}</small><b>{t}</b><p>{d}</p></div>' for i,(t,d) in enumerate(steps,1)))
pcases=soup.select('#planning .case')
for c,t in zip(pcases,['표준재무제표 / 문의 개선','대용량 PDF / 대체 제출','인증 오류 / 안내 개선','기관 조건 / 백오피스','요구사항 / 협업']):c.select_one('h3').string=t
pcases[2].select_one('small').string='CASE 03 / AUTH UX'
pcases[2].select_one('p').string='인증 실패 사례를 인증서 종류, 발급기관, 지원 여부, OS·브라우저와 발생 단계별로 나눠 확인했습니다. 외부 인증 솔루션 업체와 재현 조건과 지원 범위를 맞추고, 사용자가 원인을 구분할 수 있도록 오류 메시지와 조치 기준 개선에 참여했습니다.'
p=pcases[2].select_one('.case-flow');p.clear();p.append(frag('<b>진행 과정</b> / 실패 사례 수집 → 원인 조건 분류 → 외부업체 협의 → 오류 메시지와 조치 기준 보완 → 적용 결과 확인'))
p=pcases[3].select_one('.case-flow');p.clear();p.append(frag('<b>진행 과정</b> / 요청 검수 → 운영 조건 확인 → 누락·충돌 보완 → 백오피스 설정 → 발급·제출 결과 확인'))
for s in soup.select('section'):
 if s.select_one('.visuals'):
  s['id']='evolution';s.select_one('h2').string='OneClick / 서비스 변화'
  p=s.select_one('.head > p');p.clear();p.append(frag('설치형 OneClick 4.0 → 웹 OneClick → 브라우저 OneClick의 서비스 변화입니다. <b>실제 업무 참여는 웹 OneClick부터 시작했으며</b>, 이후 브라우저 OneClick 고도화와 운영 반영에 참여했습니다.'))
  p=s.select_one('.participation-note');p.clear();p.append(frag('<b>참여 범위</b> / OneClick 4.0은 참여 이전 서비스로, 변화 과정을 설명하기 위해 포함했습니다. <b>2022년 웹 OneClick 운영부터 참여했습니다.</b>'))
  caps=s.select('.visual figcaption');caps[1].clear();caps[1].append(frag('<b>02 / 웹 OneClick</b><span class="stage-note">참여 시작</span><br>2022년부터 서비스 운영과 고객사·기관 설정 관리'))
  caps[2].clear();caps[2].append(frag('<b>03 / 브라우저 OneClick</b><span class="stage-note">고도화 참여</span><br>개선사항 정리, 요구사항 협의와 운영 반영'))
  s.select_one('.mobile h3').string='PC / 모바일 이용 화면';s.select_one('.mobile p').string='기관 선택과 인증, 발급과 제출까지 이어지는 실제 서비스 이용 화면입니다.'
text('#system .head h2','기관별 조건 / 운영 관리')
for n in soup.select('#system .step'):
 if 'Test/UAT' in n.get_text():n.clear();n.append(frag('<b>반영</b>백오피스 설정 → 운영 적용 → 이용 결과 확인'))
text('#integration .head h2','서비스 통합 / 전환 검토')
text('#integration .head > p','2025년 말 기존 OneClick과 서류제출 서비스 통합 프로젝트에서 사용자 화면, 백오피스, 데이터와 고객사 전환 항목을 운영 관점에서 검토했습니다.')
text('#integration .cards > article:nth-child(1) h3','기능 / 화면 / 데이터')
text('#integration .cards > article:nth-child(2) h3','운영 요구사항 / 일정 관리')
text('#integration .cards > article:nth-child(2) p','운영에 필요한 요구사항과 영향 기관, 고객사 전환 일정을 확인하고 개발·영업과 진행상태를 맞췄습니다. 통합 일정은 이후 이월되어 요구사항과 전환 항목 검토 범위로 참여했습니다.')
html('#integration .role','<b>담당 범위</b><br>운영 요구사항 / 영향 기관과 고객사 / 전환 일정 / 운영 반영 항목 검토')
html('#integration .integration-note','<b>서비스 변경 / 운영 반영</b><br>일상적인 서비스 변경에서는 요청 목적, 적용 대상, 담당자와 일정을 확인하고 승인과 운영 반영 이후의 상태까지 관리했습니다.')
steps=[('요청 확인','목적과 고객사 일정'),('영향 확인','사용자·기관·업무 범위'),('일정 조율','개발 난이도와 백로그'),('변경 승인','대상·일정·복구 항목'),('운영 반영','변경사항 적용'),('모니터링','발급상황과 문의 확인')]
html('#integration .release-flow',''.join(f'<div><small>{i:02}</small><b>{t}</b><p>{d}</p></div>' for i,(t,d) in enumerate(steps,1)))
text('#integration .release-criteria','우선순위 기준 / 요청 목적, 고객사 적용 일정, 장애 영향도, 개발 난이도와 기존 백로그를 함께 확인해 작업 순서와 반영 시점을 조율했습니다.')
soup.select_one('#uat').replace_with(frag('<section id="monitoring" class="pad dark"><div class="w"><div class="head"><div><p class="ey">SERVICE MONITORING</p><h2>서류 발급 / Grafana 모니터링</h2></div><p>OneClick 운영 중 Grafana 대시보드에서 서류 발급상황과 서비스 상태를 확인했습니다. 기능 변경과 배포 후에는 발급 흐름과 이상 여부를 함께 점검했습니다.</p></div><div class="cards"><article class="card"><small>GRAFANA</small><h3>발급상황 / 서비스 상태</h3><p>서류 발급 진행상황과 서비스 상태를 확인하고 이상 여부를 점검했습니다.</p></article><article class="card"><small>AFTER RELEASE</small><h3>변경 이후 / 운영 확인</h3><p>기능 변경과 배포 이후 발급상황과 CS 인입을 함께 확인했습니다. 반복 문의는 사용자 안내와 운영 기준에 반영했습니다.</p></article></div></div></section>'))
text('#skills .head h2','도구 / 활용 범위');text('#skills .head > p','서비스 기획과 운영 개선 과정에서 사용한 도구를 실제 활용 범위에 맞춰 정리했습니다.')
tools=soup.select('#skills .tool');tools[0].select_one('h3').string='문제 정의 / 요구사항 정리'
p=tools[0].select_one('p');p.clear();p.append(frag('업무 프로세스 분석 / UI·UX 검토 / VOC 분석 / 운영 기준·매뉴얼<br><strong>Figma를 활용한 서비스 기획 및 협업</strong>'))
p=tools[1].select_one('p');p.clear();p.append(frag('Grafana(OneClick 서류 발급상황 모니터링) / APM / Google Analytics / Postman / Linux·SSH<br>SQL은 기초 데이터 조회 수준'))
tools[2].select_one('h3').string='Adobe Photoshop / GTQ 1급'
for n in soup.select('.career .job:first-child p'):n.string='모닝인 파견 2년 → NICE평가정보 계약직 2년 / 약 300개 기관 연계 / 브라우저 OneClick 고도화 / VOC 기반 개선 / 요구사항 정리 / 운영 기준 관리'
for s in soup.select('section'):
 if s.select_one('.career'):s.select_one('h2').string='경력 / 주요 업무';s.select_one('.head > p').string='NICE평가정보의 B2B 서비스 운영과 이전 금융기관 IT 운영지원 경력입니다.'
text('.contact h2','문제 발견 / 개선 / 운영');text('.contact p:not(.ey)','반복 문의의 원인을 구분하고 적용 조건과 해결 방식을 정리했습니다. 유관부서와 변경 범위를 맞춘 뒤 운영에 반영하고, 이용 결과와 문의 변화를 확인했습니다.')
for im in soup.select('img'):
 im['src']='/assets/'+im['src'].rsplit('/',1)[-1];im['loading']='lazy';im['decoding']='async'
 if im.parent.name=='a':im.parent['href']=im['src']
for n in list(soup.find_all(string=True)):
 if n.parent.name in ('script','style'):continue
 st=str(n).replace('DALL·E','__DALLE__').replace('·',' / ').replace('__DALLE__','DALL·E');n.replace_with(re.sub(r'\bGA\b','Google Analytics',st))
assert len(soup.select('img'))==8
assert not re.search(r'\b(?:QA|UAT)\b|Test/UAT',soup.get_text(),re.I)
assert not soup.select('script')
assert '기여도' not in soup.get_text()
assert not any('Figma' in t.get_text() for t in soup.select('.tool') if 'AI / DESIGN' in t.get_text())
css+='\nhtml{scroll-padding-top:80px}body{font-family:Pretendard,"Noto Sans KR","Noto Sans CJK KR","Malgun Gothic",Arial,sans-serif}.pad{padding:76px 0}.case-process{grid-template-columns:repeat(3,minmax(0,1fr))}.planning-flow,.release-flow{grid-template-columns:repeat(3,minmax(0,1fr))}.visual img{object-fit:contain;background:var(--paper)}.visual.before{opacity:1;filter:none}.visual.before img{filter:saturate(.65)}.dark .ey,.dark .card small{color:#efb7c5}.role{font-family:inherit;font-size:11px;line-height:1.7}img{max-width:100%}.top-focus article,.tool,.card,.case{min-width:0}.case .tag{white-space:normal}@media(max-width:780px){.case-process{grid-template-columns:1fr}.planning-flow,.release-flow{grid-template-columns:1fr 1fr}}@media(max-width:520px){.pad{padding:56px 0}.planning-flow,.release-flow{grid-template-columns:1fr}.hero h1{font-size:38px}}'
(out/'index.html').write_text(str(soup),encoding='utf-8');(out/'style.css').write_text(css,encoding='utf-8')
(out/'version.json').write_text(json.dumps({'version':'portfolio-repair-20260920','qaRemoved':True,'sameOriginImages':8,'figmaSection':'service-planning','monitoring':'Grafana OneClick document issuance'},indent=2))
print('Static source saved with eight same-origin image references.')
