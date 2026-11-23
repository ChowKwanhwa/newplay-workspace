import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {itemsForLanguage,SECTIONS} from '../public/languages.js';

const catalog=JSON.parse(readFileSync(new URL('../public/catalog.json',import.meta.url),'utf8'));
const uploads=JSON.parse(readFileSync(new URL('./fixtures/published-uploads.json',import.meta.url),'utf8'));
const bangkok=catalog.items.filter(item=>item.category==='bangkok');

test('Bangkok has its own localized category and complete current final materials',()=>{
 assert.ok(catalog.sections.some(section=>section.id==='bangkok'));
 for(const language of ['zh','en','th'])assert.ok(SECTIONS[language].bangkok);
 assert.equal(bangkok.length,20);
 assert.equal(bangkok.flatMap(item=>item.files).length,26);
 for(const edition of ['Original','Midnight Chrome','Mint Club','Afterglow'])assert.ok(bangkok.some(item=>item.title.includes(edition)));
});

test('Bangkok English resources stay isolated and expose only final PNG and PDF files',()=>{
 assert.equal(itemsForLanguage(bangkok,'en').length,20);
 for(const language of ['zh','th'])assert.equal(itemsForLanguage(bangkok,language).length,0);
 for(const item of bangkok){
  assert.ok(item.preview);
  assert.equal(item.language,'en');
  assert.ok(item.titles.en);
  for(const file of item.files){
   assert.match(file.key,/^bangkok\//);
   assert.ok(['PNG','PDF'].includes(file.type));
   assert.doesNotMatch(uploads[file.key],/assets\/|可编辑源文件|preview|overview|\.html$/i);
  }
 }
 assert.deepEqual(catalog.packs,[]);
});
