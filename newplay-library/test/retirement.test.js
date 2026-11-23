import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const catalog=JSON.parse(readFileSync(new URL('../public/catalog.json',import.meta.url),'utf8'));
const uploads=JSON.parse(readFileSync(new URL('./fixtures/published-uploads.json',import.meta.url),'utf8'));
test('retired brand narrative, old operating plan and jelly mascot assets are absent',()=>{
 assert.ok(catalog.items.every(i=>i.title!=='品牌叙事'&&i.category!=='operations'));
 for(const p of Object.values(uploads))assert.doesNotMatch(p,/output\/(品牌叙事|运营网站|社媒\/普莱星座)\//);
 assert.ok(catalog.items.every(i=>!i.title.includes('历史角色姿态')));
});
test('vertical posters have no version badges or contact-sheet downloads',()=>{
 const posters=catalog.items.filter(i=>i.category==='social'&&i.files.some(f=>f.name.startsWith('NewPlay-竖版PR与12星座')||/^\d{2}-NewPlay-(项目介绍-竖版PR|PLAI启航节点-竖版PR|普莱星座-)/.test(f.name)));assert.equal(posters.length,15);
 for(const i of posters){assert.equal(i.version,'');assert.doesNotMatch(i.title,/v[12]/i);for(const f of i.files)assert.doesNotMatch(f.name,/v[12]|总览|overview/i);}
 assert.equal(posters.filter(i=>i.files.some(f=>f.type==='PNG')).length,14);
});
