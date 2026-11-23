import published from './published.js';
const allowed = new Set(published);
const TYPES={pdf:'application/pdf',png:'image/png',jpg:'image/jpeg',jpeg:'image/jpeg',webp:'image/webp',svg:'image/svg+xml',mp4:'video/mp4',txt:'text/plain; charset=utf-8',md:'text/plain; charset=utf-8',html:'text/html; charset=utf-8',docx:'application/vnd.openxmlformats-officedocument.wordprocessingml.document',pptx:'application/vnd.openxmlformats-officedocument.presentationml.presentation'};
export default {async fetch(request,env){
 const url=new URL(request.url);
 if(url.pathname.startsWith('/files/'))return serveFile(request,env,url,allowed);
 return env.ASSETS.fetch(request);
}};
export async function serveFile(request,env,url,allowlist){
 if(!['GET','HEAD'].includes(request.method))return new Response('Method not allowed',{status:405,headers:{Allow:'GET, HEAD'}});
 let key;try{key=decodeURIComponent(url.pathname.slice(7));}catch{return new Response('Bad request',{status:400});}
 if(!key||key.toLowerCase().endsWith('.zip')||key.startsWith('packs/')||key.includes('..')||!allowlist.has(key))return new Response('Not found',{status:404});
 const obj=request.method==='HEAD'?await env.FILES.head(key):await env.FILES.get(key,{range:request.headers,onlyIf:request.headers});
 if(!obj)return new Response('Not found',{status:404});
 const h=new Headers();obj.writeHttpMetadata(h);
 if(!h.has('content-type'))h.set('content-type',TYPES[key.split('.').pop().toLowerCase()]||'application/octet-stream');
 h.set('etag',obj.httpEtag);h.set('accept-ranges','bytes');h.set('x-object-size',String(obj.size));
 if(obj.customMetadata?.sha256)h.set('x-content-sha256',obj.customMetadata.sha256);
 h.set('cache-control','public, max-age=300, must-revalidate');h.set('x-content-type-options','nosniff');
 const name=key.split('/').pop(),ascii=name.replace(/[^\x20-\x7e]/g,'_').replace(/["\\]/g,'');
 h.set('content-disposition',`${url.searchParams.has('dl')?'attachment':'inline'}; filename="${ascii}"; filename*=UTF-8''${encodeURIComponent(name)}`);
 if(key.endsWith('.html'))h.set('content-security-policy',"sandbox allow-scripts; default-src 'self' data: https:; style-src 'self' 'unsafe-inline' https:; script-src 'none'");
 if(request.method==='HEAD'){h.set('content-length',String(obj.size));return new Response(null,{headers:h});}
 if(!('body'in obj))return new Response(null,{status:304,headers:h});
 if(obj.range&&request.headers.has('range')){
  const {offset=0,length=obj.size-offset}=obj.range;
  h.set('content-range',`bytes ${offset}-${offset+length-1}/${obj.size}`);h.set('content-length',String(length));return new Response(obj.body,{status:206,headers:h});
 }
 h.set('content-length',String(obj.size));return new Response(obj.body,{headers:h});
}
