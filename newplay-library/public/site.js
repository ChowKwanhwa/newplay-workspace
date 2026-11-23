import {resolveLanguage,itemsForLanguage,UI,SECTIONS} from './languages.js';
const $=s=>document.querySelector(s);
let saved;try{saved=localStorage.getItem('newplay-library-language');}catch{}
let language=resolveLanguage(new URL(location.href).searchParams.get('lang'),saved),catalog,category='',query='',format='';
const t=(key,vars={})=>Object.entries(vars).reduce((s,[k,v])=>s.replaceAll(`{${k}}`,v),UI[language][key]);
const title=i=>i.titles?.[language]||i.title;
const size=n=>n>=1e6?(n/1e6).toFixed(n>=10e6?0:1)+' MB':Math.max(1,Math.round(n/1e3))+' KB';
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const link=f=>`<a class="download" href="${esc(f.url)}?dl=1" download title="${t('download')} ${esc(f.name||f.type)}">${esc(f.type)} <span aria-hidden="true">↓</span></a>`;
function applyLanguage(){
 document.documentElement.lang=language==='zh'?'zh-CN':language;document.title=t('pageTitle');$('#language').value=language;
 document.querySelectorAll('[data-i18n]').forEach(e=>e.textContent=t(e.dataset.i18n));
 for(const [attr,key] of [['aria-label','i18nAria'],['placeholder','i18nPlaceholder'],['alt','i18nAlt']])document.querySelectorAll(`[data-${key.replace(/[A-Z]/g,c=>'-'+c.toLowerCase())}]`).forEach(e=>e.setAttribute(attr,t(e.dataset[key])));
}
function card(item){
 const f=item.files[0],types=[...new Set(item.files.map(f=>f.type))].join(' / '),dimensions=item.files.find(f=>f.dimensions)?.dimensions;
 const version=item.version==='正式版'?t('current'):item.version==='其他视觉版本'?t('otherVersions'):item.version;
 return `<article class="card ${/White_Reverse|反白/.test(f.name)?'dark':''}" data-item-id="${item.id}"><button class="thumb" data-preview="${item.id}" aria-label="${t('preview')} ${esc(title(item))}">${version?`<span class="version ${item.version==='正式版'?'current':''}">${esc(version)}</span>`:''}${item.preview?`<img src="${esc(item.preview)}" loading="lazy" decoding="async" alt="${esc(title(item))}">`:`<span class="file-placeholder">${esc(f.type)}</span>`}${item.video?'<span class="play" aria-hidden="true">▶</span>':''}<span class="preview-label">${t('clickPreview')}</span></button><div class="card-body"><h3>${esc(title(item))}</h3><p class="file-meta">${esc(types)} · ${size(item.files.reduce((s,f)=>s+f.size,0))}${dimensions?' · '+dimensions.join(' × '):''}</p><div class="card-actions">${item.files.map(link).join('')}</div></div></article>`;
}
function render(){
 if(!catalog)return;
 const available=itemsForLanguage(catalog.items,language),sections=catalog.sections.map(s=>({...s,title:SECTIONS[language][s.id][0],description:SECTIONS[language][s.id][1]}));
 $('#categories').innerHTML=[{id:'',title:t('all')},...sections].map(s=>{const n=available.filter(i=>!s.id||i.category===s.id).length;return n?`<a href="#${s.id||'library'}" class="category ${category===s.id?'active':''}" ${category===s.id?'aria-current="page"':''}>${esc(s.title)}<b>${n}</b></a>`:'';}).join('');
 let items=available.filter(i=>(!category||i.category===category)&&(!format||i.files.some(f=>f.type===format))&&(!query||`${title(i)} ${i.files.map(f=>f.name).join(' ')} ${SECTIONS[language][i.category][0]}`.toLocaleLowerCase().includes(query)));
 if($('#sort').value==='newest')items.sort((a,b)=>b.updated.localeCompare(a.updated));
 if($('#sort').value==='name')items.sort((a,b)=>title(a).localeCompare(title(b),language==='zh'?'zh-CN':language));
 $('#active-filter').textContent=query||format?t('found',{n:items.length})+(query?' · “'+$('#search').value+'”':''):'';
 $('#catalog').innerHTML=sections.map(s=>{
  const group=items.filter(i=>i.category===s.id);if(!group.length)return '';
  return `<section class="section" data-category="${s.id}" id="section-${s.id}"><div class="section-head"><div><h2>${esc(s.title)}<span>${t('groups',{n:group.length})}</span></h2><p class="section-description">${esc(s.description)}</p></div></div><div class="grid">${group.map(card).join('')}</div></section>`;
 }).join('');
 $('#empty').hidden=items.length>0;
 $('#summary').textContent=t('summary',{files:available.reduce((n,i)=>n+i.files.length,0),sections:sections.filter(s=>available.some(i=>i.category===s.id)).length});
 $('#updated').textContent=t('updated',{date:catalog.updated});
 $('#language-notice').hidden=available.some(i=>i.language===language);$('#language-notice').textContent=t('noLanguage');
}
function hashChanged(){const value=location.hash.slice(1);category=catalog?.sections.some(s=>s.id===value)?value:'';render();}
function resetFilters(){query='';format='';category='';$('#search').value='';$('#format').value='';const url=new URL(location.href);url.hash='';history.replaceState(null,'',url);}
$('#language').addEventListener('change',e=>{
 language=resolveLanguage(e.target.value,null);try{localStorage.setItem('newplay-library-language',language);}catch{}
 const url=new URL(location.href);url.searchParams.set('lang',language);history.replaceState(null,'',url);resetFilters();$('#preview').close();applyLanguage();render();
});
$('#search').addEventListener('input',e=>{query=e.target.value.trim().toLocaleLowerCase();render();});
$('#format').addEventListener('change',e=>{format=e.target.value;render();});$('#sort').addEventListener('change',render);
$('#reset').addEventListener('click',()=>{resetFilters();render();});
$('#focus-search').addEventListener('click',()=>{$('#library').scrollIntoView();$('#search').focus();});
document.addEventListener('keydown',e=>{if((e.metaKey||e.ctrlKey)&&e.key.toLowerCase()==='k'){e.preventDefault();$('#focus-search').click();}if(e.key==='/'&&!/INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName)&&!$('#preview').open){e.preventDefault();$('#focus-search').click();}});
window.addEventListener('hashchange',hashChanged);
$('#catalog').addEventListener('click',e=>{
 const button=e.target.closest('[data-preview]');if(!button)return;
 const item=itemsForLanguage(catalog.items,language).find(i=>i.id===button.dataset.preview);if(!item)return;
 const body=$('#preview-body');$('#preview-title').textContent=title(item);$('#preview-meta').textContent=item.files.map(f=>f.type+' · '+size(f.size)).join(' / ');
 const original=item.pdf||item.video||item.files[0].url;
 $('#preview-actions').innerHTML=`<a class="download" href="${esc(original)}" target="_blank" rel="noopener">${t('open')} ↗</a>`+item.files.map(link).join('');body.replaceChildren();body.style.backgroundColor=/White_Reverse|反白/.test(item.files[0].name)?'#264851':'';
 if(item.video){const v=document.createElement('video');v.controls=true;v.playsInline=true;v.src=item.video;v.poster=item.preview;v.preload='metadata';body.append(v);}
 else if(item.pdf){const frame=document.createElement('iframe');frame.title=title(item);frame.src=item.pdf;body.append(frame);}
 else if(['PNG','JPG','JPEG','WEBP','SVG'].includes(item.files[0].type)){const im=document.createElement('img');im.src=item.files[0].url;im.alt=title(item);body.append(im);}
 else{const p=document.createElement('p');p.className='text-fallback';p.textContent=t('fallback');body.append(p);}
 $('#preview').showModal();
});
$('#close-preview').addEventListener('click',()=>$('#preview').close());
$('#preview').addEventListener('click',e=>{if(e.target===$('#preview')){const r=e.target.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)e.target.close();}});
$('#preview').addEventListener('close',()=>$('#preview-body').replaceChildren());
applyLanguage();
fetch('/catalog.json').then(r=>{if(!r.ok)throw Error();return r.json();}).then(data=>{catalog=data;hashChanged();}).catch(()=>{$('#catalog').innerHTML=`<p class="loading">${t('loadError')}</p>`;$('#summary').textContent='NewPlay '+t('library');});
