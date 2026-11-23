import test from 'node:test';
import assert from 'node:assert/strict';
import {existsSync,readFileSync} from 'node:fs';
const src=new URL('../public/languages.js',import.meta.url);
const m=existsSync(src)?await import(src):{};
test('language selection uses a valid URL, then saved choice, then Chinese',()=>{
 assert.equal(typeof m.resolveLanguage,'function');
 assert.equal(m.resolveLanguage('en','th'),'en');
 assert.equal(m.resolveLanguage('xx','th'),'th');
 assert.equal(m.resolveLanguage(null,'bad'),'zh');
});
test('documents are isolated by language while language-neutral assets stay available',()=>{
 assert.equal(typeof m.itemsForLanguage,'function');
 const items=[{id:'cn',language:'zh'},{id:'en',language:'en'},{id:'th',language:'th'},{id:'logo',language:'und'}];
 assert.deepEqual(m.itemsForLanguage(items,'en').map(x=>x.id),['en','logo']);
 assert.deepEqual(m.itemsForLanguage(items,'zh').map(x=>x.id),['cn','logo']);
 assert.deepEqual(m.itemsForLanguage(items,'th').map(x=>x.id),['th','logo']);
});
test('every interface language has the same translation keys and localized section names',()=>{
 assert.ok(m.UI);
 assert.deepEqual(Object.keys(m.UI).sort(),['en','th','zh']);
 const keys=Object.keys(m.UI.zh).sort();
 for(const lang of ['en','th'])assert.deepEqual(Object.keys(m.UI[lang]).sort(),keys);
 for(const lang of ['zh','en','th'])assert.equal(Object.keys(m.SECTIONS[lang]).length,8);
 assert.match(m.UI.th.emptyTitle,/[\u0E00-\u0E7F]/);
});
test('published English resources never appear in Chinese or Thai lists',()=>{
 const catalog=JSON.parse(readFileSync(new URL('../public/catalog.json',import.meta.url),'utf8'));
 assert.ok(catalog.items.every(i=>['zh','en','th','und'].includes(i.language)));
 const english=catalog.items.filter(i=>i.language==='en');assert.ok(english.some(i=>i.category==='decks'&&i.title.includes('市场与商业模式')));
 for(const lang of ['zh','th'])assert.ok(m.itemsForLanguage(catalog.items,lang).every(i=>i.language!== 'en'));
 for(const lang of ['en','th'])for(const i of m.itemsForLanguage(catalog.items,lang)){
  assert.ok(i.titles[lang],i.id);assert.doesNotMatch(i.titles[lang],/[\u3400-\u9fff]/);
 }
 const deck=english.find(i=>i.category==='decks'&&i.title.includes('品牌与产品'));
 assert.equal(deck.title,'NewPlay 品牌与产品 Deck｜英文版');
 assert.ok(deck.files.every(f=>/^NewPlay 品牌与产品 Deck｜英文版\.(pdf|pptx)$/.test(f.name)));
});
test('trilingual poster additions are isolated and keep existing Chinese originals',()=>{
 const catalog=JSON.parse(readFileSync(new URL('../public/catalog.json',import.meta.url),'utf8'));
 const campaign=catalog.items.filter(item=>item.translationGroup?.startsWith('newplay-pr-zodiac-'));
 assert.ok([0,30].includes(campaign.length),'The translated campaign is either fully staged or fully registered');
 if(!campaign.length)return;
 for(const language of ['en','th']){
  const selected=m.itemsForLanguage(catalog.items,language).filter(item=>campaign.includes(item));
  assert.equal(selected.length,15);
  assert.ok(selected.every(item=>item.language===language&&item.titles[language]));
 }
 assert.equal(m.itemsForLanguage(catalog.items,'zh').filter(item=>campaign.includes(item)).length,0);
 assert.ok(catalog.items.some(item=>item.language==='zh'&&item.files.some(file=>file.name.includes('普莱星座-巨蟹座.png'))));
});
