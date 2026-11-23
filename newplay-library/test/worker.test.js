import test from 'node:test';
import assert from 'node:assert/strict';
import {serveFile} from '../src/worker.js';

const key = 'brand/普莱.png';
const worker={fetch:(r,e)=>serveFile(r,e,new URL(r.url),new Set([key]))};
function env() {
  const object = {size: 10, httpEtag: '"test"', body: '0123456789', writeHttpMetadata(h){h.set('content-type','image/png');}};
  return {ASSETS:{fetch:async()=>new Response('static')},FILES:{head:async k=>k===key?object:null,get:async(k,opts)=> {
    if(k!==key)return null;
    if(opts.onlyIf.get('if-none-match')==='"test"') { const {body,...rest}=object; return rest; }
    if(opts.range.has('range')) return {...object,body:'012',range:{offset:0,length:3}};
    return object;
  }}};
}
test('unknown keys and internal archives cannot be downloaded',async()=>{
 for(const path of ['archive/private.txt','missing.pdf','../.env']) {
  const r=await worker.fetch(new Request('https://library.test/files/'+path),env()); assert.equal(r.status,404);
 }
});
test('Unicode download name and HEAD size are retained',async()=>{
 const r=await worker.fetch(new Request('https://library.test/files/'+encodeURI(key)+'?dl=1',{method:'HEAD'}),env());
 assert.equal(r.status,200); assert.equal(r.headers.get('content-length'),'10');
 assert.match(r.headers.get('content-disposition'),/filename\*=UTF-8/); assert.equal(await r.text(),'');
});
test('video/image range and cache requests behave correctly',async()=>{
 const r=await worker.fetch(new Request('https://library.test/files/'+encodeURI(key),{headers:{range:'bytes=0-2'}}),env());
 assert.equal(r.status,206);assert.equal(r.headers.get('content-range'),'bytes 0-2/10');assert.equal(await r.text(),'012');
 const cached=await worker.fetch(new Request('https://library.test/files/'+encodeURI(key),{headers:{'if-none-match':'"test"'}}),env());assert.equal(cached.status,304);
});
test('file writes are rejected',async()=>assert.equal((await worker.fetch(new Request('https://library.test/files/'+encodeURI(key),{method:'POST'}),env())).status,405));
test('multipart content checksum is available for incremental sync',async()=>{
 const original=env();const object=await original.FILES.head(key);
 object.customMetadata={sha256:'a'.repeat(64)};
 const response=await worker.fetch(new Request('https://library.test/files/'+encodeURI(key),{method:'HEAD'}),original);
 assert.equal(response.headers.get('x-content-sha256'),'a'.repeat(64));
});
test('ZIP bundles stay unavailable even if an old allowlist includes them',async()=>{
 const k='packs/NewPlay-social.zip';const e=env();const original=e.FILES.head;
 e.FILES.head=async()=>original(key);
 const r=await serveFile(new Request('https://library.test/files/'+k,{method:'HEAD'}),e,new URL('https://library.test/files/'+k),new Set([k]));
 assert.equal(r.status,404);
});
