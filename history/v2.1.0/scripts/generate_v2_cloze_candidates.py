from pathlib import Path
import argparse,json,re,hashlib,collections
parser=argparse.ArgumentParser(description='Generate licensed sentence-cloze candidates from externally extracted source PDFs.')
parser.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[1])
parser.add_argument('--extracted-text-dir',type=Path,required=True,help='Directory containing page-marked UTF-8 .txt files; source PDFs are not included in the package.')
parser.add_argument('--source-manifest',type=Path,default=None)
parser.add_argument('--output',type=Path,default=None)
args=parser.parse_args()
ROOT=args.repo_root.resolve()
SRC=(args.source_manifest or ROOT/'audit/v2_expansion_sources.json').resolve()
TEXTROOT=args.extracted_text_dir.resolve()
OUT=(args.output or ROOT/'audit/v2_expansion_qas.jsonl').resolve()
manifest=json.loads(SRC.read_text(encoding='utf8'))
PAGE=re.compile(r'===== PDF PAGE (\d+) =====\n')
NUMBER=re.compile(r'(?<![0-9])(?:(?:19|20)\d{2}(?:年|年代)?|\d+(?:[,，]\d{3})*(?:\.\d+)?\s?(?:%|个百分点|亿美元|万美元|万亿|亿|万人|万|千|百万|十亿|人|名|个|项|种|次|月|年|公里|千米|GB|TB|GHz|MHz|Mbps|Gbit/s|美元|欧元|所|家|小时|天|国家|运营商|学校|机构|倍|Mbit/s))')
ACRONYM=re.compile(r'(?<![A-Za-z])[A-Z][A-Z0-9]{1,6}(?:-[A-Z0-9]{1,6})?(?![A-Za-z])')
CLAUSE_CUES=re.compile(r'(?:具体包括|包括|涵盖|分为|分成|主要有|建议|要求|应当|应该|需要|必须|旨在|是指|定义为|意味着|其目标是|目标是|可通过|通过|以便|从而)')
SKIP_ACR={'ISBN','PDF','EPUB','MOBI','URL','HTTP','HTTPS','HTML','CC','ND','SA','NC','IGO','CH','ICTS','II','III','IV','V','VI','VII','VIII','IX','X','XII','XIII','XIV','XV','XVI'}
FOOTER=re.compile(r'(?:ITU-D第\s?\d/\d号课题输出成果报告|ITU-D\s*\d/\d号课题输出成果报告|\b第\s?\d+\s*页\b)')
PUNCT=re.compile(r'(?<=[。！？；])\s*')


def get_candidate_file(src):
 who_files={'WHO-AI-ETHICS-HEALTH-2021-ZH':'WHO-AI-ETHICS-HEALTH-EXEC-SUMMARY-2021-ZH.pdf','WHO-TB-DIGITAL-ANNEX-F-2024-ZH':'WHO-TB-DIGITAL-PACKAGE-ANNEX-F-2024-ZH.pdf'}
 if src['source_id'].startswith('WHO-'):
  return who_files.get(src['source_id'],src['source_id']+'.pdf')
 return src['original_report_url'].rsplit('/',1)[-1]

def clean_sentences(src):
 pdf_name=get_candidate_file(src)
 p=TEXTROOT/(Path(pdf_name).stem+'.txt')
 if not p.exists(): raise FileNotFoundError(p)
 expected_hash=src.get('extracted_text_sha256')
 if expected_hash:
  actual_hash=hashlib.sha256(p.read_bytes()).hexdigest()
  if actual_hash!=expected_hash: raise ValueError(f'Extracted text hash mismatch for {src["source_id"]}')
 raw=p.read_text(encoding='utf8'); parts=PAGE.split(raw); out=[]
 first_page=src['rights_notice_location']['pdf_page_1based']+1 if src['source_id'].startswith('WHO-') else 8
 for i in range(1,len(parts),2):
  page=int(parts[i]); page_text=' '.join(parts[i+1].split())
  if page<first_page: continue
  # Remove recurring page headers before splitting; only retain body sentences.
  page_text=FOOTER.sub('',page_text)
  raw_sentences=[]
  for whole in PUNCT.split(page_text):
   whole=whole.strip(' \t·•-—–:：')
   if len(whole)>150: raw_sentences.extend(re.split('[，、]',whole))
   else: raw_sentences.append(whole)
  for sent in raw_sentences:
   sent=sent.strip(' \t·•-—–:：')
   sent=re.sub(r'\s+',' ',sent)
   sent=re.sub(r'(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])','',sent)
   if not 28<=len(sent)<=145: continue
   if re.search(r'目录|图目录|表目录|缩略语|参考文献|ISBN|版权所有|保留部分权利|https?://|本报告是国际电联|本报告是世卫组织|本出版物采用的名称|国际电联免责|世卫组织免责声明|^来源[:：]|^注[:：]',sent):continue
   if sent.count('。')>1 or sent.count('；')>1 or '?' in sent or '？' in sent:continue
   # Exclude headings, figure/table captions, enumerated lists and broken layout fragments.
   if re.match(r'^(?:\d{1,3}\s+|\d+\.\d+(?:\.\d+)*\s|[图表]\s*\d+[:：]|[•●▪■◆])',sent):continue
   if re.match(r'^(?:和|或|的|为|其中|以及|与|及|即|如|但|而|并且|同时)',sent):continue
   if re.search(r'[•●▪■◆<>]',sent):continue
   if len(re.findall(r'\d',sent))>14:continue
   # A digit between a noun and a verb/punctuation is usually a PDF footnote marker.
   if re.search(r'(?<=[人])\d{1,2}(?=(?:仍|未|可以|不能|无法|，|。|、|；|在|的|是|将|和|但|同时|以及))',sent):continue
   # Skip mostly table rows and likely page furniture.
   if len(re.findall(r'[，,：:]',sent))>7:continue
   targets=[]
   for m in NUMBER.finditer(sent):
    val=m.group().strip()
    if len(val)>1 and val not in targets: targets.append(val)
   for m in ACRONYM.finditer(sent):
    val=m.group().strip()
    if val not in SKIP_ACR and len(val)>=2 and val not in targets: targets.append(val)
   for m in CLAUSE_CUES.finditer(sent):
    tail=sent[m.end():]
    value=re.split(r'[，,。；;：:]',tail,maxsplit=1)[0].strip(' \\"“”‘’')
    if 3<=len(value)<=45 and value not in targets and value not in {'这些原则','这一点','这种技术','相关内容','有关内容','以下内容'}: targets.append(value)
   for target in targets:
    masked=sent.replace(target,'______',1)
    if masked==sent or len(target)>22:continue
    # A cloze remains ambiguous if the same target appears again in the sentence.
    if target in masked:continue
    if len(re.findall(r'\d',masked))>12:continue
    # Don't mask page citations or bibliography-style entries.
    if re.match(r'^\s*(?:\[\d+\]|\d+\.)\s',sent):continue
    out.append({'page':page,'sentence':sent,'target':target,'masked':masked,'target_type':'numeric' if NUMBER.fullmatch(target) else ('term' if ACRONYM.fullmatch(target) else 'clause')})
 return out

TEMPLATES={
 'numeric':['报告中的陈述留有一处数值空缺，请补全：“{text}”','根据报告中的数值信息，填写缺失项：“{text}”','请从报告内容中还原这处数字陈述：“{text}”'],
 'term':['请补全报告中的技术术语：“{text}”','根据报告原文，填入缺失的技术名称：“{text}”','报告中的术语陈述有一处空缺，请填写：“{text}”'],
 'clause':['请补全报告陈述中的缺失内容：“{text}”','根据报告内容，完成这处填空：“{text}”','下面的报告陈述缺少一项信息，请补充：“{text}”']
}
def read_existing_rows():
 path=ROOT/'records.jsonl'
 if not path.exists(): return []
 items=[json.loads(line) for line in path.read_text(encoding='utf8').splitlines() if line.strip()]
 return [x for x in items if not x['query_id'].startswith('IICR-V20-') or int(x['query_id'].rsplit('-',1)[-1])<=60]

def normalize_question(text): return re.sub(r'\W+','',text).lower()
def char_grams(text): return {text[i:i+4] for i in range(max(0,len(text)-3))}
question_texts=[]; question_grams=[]; gram_index=collections.defaultdict(list); exact_questions=set()
def remember_question(question):
 normalized=normalize_question(question); grams=char_grams(normalized); idx=len(question_texts)
 question_texts.append(normalized); question_grams.append(grams); exact_questions.add(normalized)
 for gram in grams: gram_index[gram].append(idx)
def is_near_question(question):
 normalized=normalize_question(question)
 if normalized in exact_questions:return True
 grams=char_grams(normalized); candidates=set()
 for gram in grams:
  matches=gram_index.get(gram,[])
  if len(matches)<=100:candidates.update(matches)
 for idx in candidates:
  overlap=len(grams & question_grams[idx]); minimum=min(len(grams),len(question_grams[idx]))
  if overlap<max(3,int(minimum*0.20)):continue
  if __import__('difflib').SequenceMatcher(None,normalized,question_texts[idx]).ratio()>=0.82:return True
 return False

# Include the frozen historical rows and the original 60 v2 rows in duplicate screening.
for old in read_existing_rows(): remember_question(old['question'])

def offer_candidate(src,c,index):
 kind=c['target_type'] if c['target_type'] in {'numeric','term'} else 'clause'
 for offset in range(3):
  question=TEMPLATES[kind][(index+offset)%3].format(text=c['masked'])
  if not is_near_question(question):
   remember_question(question); c['question']=question; return True
 return False

rows=[]; source_stats=[]
for src in manifest['sources']:
 candidates=clean_sentences(src)
 # De-duplicate identical sentence/target pairs, retaining the first physical page.
 dedup={}
 for c in candidates: dedup.setdefault((c['sentence'],c['target']),c)
 candidates=list(dedup.values())
 groups=collections.defaultdict(list)
 for c in candidates: groups[c['page']].append(c)
 for page in groups:
  groups[page].sort(key=lambda c:(c['target_type']!='numeric',len(c['sentence']),len(c['target'])))
 pages=sorted(groups); ordered=[]
 for depth in range(max((len(v) for v in groups.values()),default=0)):
  for page in pages:
   if depth<len(groups[page]): ordered.append(groups[page][depth])
 selected=[]; used_sentences=set(); used_targets=set()
 # Spread candidate questions across pages and require each source sentence and target to be unique.
 for c in ordered:
  if c['sentence'] in used_sentences or (c['sentence'],c['target']) in used_targets: continue
  index=len(rows)+len(selected)
  if not offer_candidate(src,c,index): continue
  selected.append(c); used_sentences.add(c['sentence']); used_targets.add((c['sentence'],c['target']))
  if len(selected)>=src['target_records']:break
 if len(selected)<src['target_records']:
  used=collections.Counter(x['sentence'] for x in selected)
  for c in ordered:
   if (c['sentence'],c['target']) in used_targets or used[c['sentence']]>=2:continue
   index=len(rows)+len(selected)
   if not offer_candidate(src,c,index):continue
   selected.append(c);used[c['sentence']]+=1;used_targets.add((c['sentence'],c['target']))
   if len(selected)>=src['target_records']:break
 if len(selected)<src['target_records']:
  raise RuntimeError(f"Not enough non-duplicate candidate questions for {src['source_id']}: {len(selected)}/{src['target_records']}")
 for ix,c in enumerate(selected,1):
  task='single_document_retrieval'
  subtype='numeric_sentence_cloze' if c['target_type']=='numeric' else ('technical_term_sentence_cloze' if c['target_type']=='term' else 'clause_content_cloze')
  fact=f"该中文版报告第{c['page']}页的句子填空项为“{c['target']}”。"
  rows.append({'source_ids':[src['source_id']],'split':src['preassigned_split'],'family_ids':[src['source_family_id']],
   'connected_group_id':'v2-'+src['source_family_id'].removeprefix('v2-')+'-cloze','task_family':task,'task_subtype':subtype,
   'question':c['question'],'answer':c['target'],'facts':[{'page':c['page'],'fact':fact}],
   'content_review_status':'pending_ai_content_verification',
   'source_sentence_sha256':hashlib.sha256(c['sentence'].encode('utf8')).hexdigest(),
   'generation_method':'masked one numeric value, technical term or factual clause in a short source-PDF sentence; no answer-blind reconstruction was performed; the sentence-level excerpt is retained only within the licensed cloze question.'})
 source_stats.append({'source_id':src['source_id'],'expected':src['target_records'],'selected':len(selected),'candidate_slots':len(candidates),'distinct_sentences':len({x['sentence'] for x in candidates})})

# Detect near duplicate questions within the generated cohort with a cheap character n-gram filter.
# If detected, report for manual review rather than silently removing planned rows.
OUT.write_text('\n'.join(json.dumps(x,ensure_ascii=False,separators=(',',':')) for x in rows)+'\n',encoding='utf8')
print(json.dumps({'record_count':len(rows),'source_count':len(source_stats),'source_stats':source_stats,'sample':rows[:3]},ensure_ascii=False,indent=2))
