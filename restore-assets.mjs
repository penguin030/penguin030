import fs from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { createHash } from 'node:crypto';
const dir = 'public/assets';
await fs.mkdir(dir, {recursive:true});
const old = 'https://hyojin-serviceops-69i8sc5d0-penguinantarctica123-2520s-projects.vercel.app';
const manuals = 'https://hyojin-serviceops-lfe9uhj2u-penguinantarctica123-2520s-projects.vercel.app';
const specs = [
 ...[14,24,27,29].map(n=>({name:`manual_${n}`, urls:[`${manuals}/manual_${n}.webp`, `https://hyojin-oneclick-manual-evidence.vercel.app/manual_${n}.webp`, `https://hyojin-oneclick-manual-a.vercel.app/manual_${n}.webp`]})),
 ...['oneclick40','weboneclick','browseroneclick','mobile'].map((name,i)=>{
  const project=['hyojin-oneclick40-asset','hyojin-web-oneclick-asset','hyojin-browser-oneclick-asset','hyojin-techlabs-assets'][i];
  return {name, urls:[`${old}/assets/${name}.webp`, ...[`${name}.webp`,`assets/${name}.webp`,`${name}.png`,`assets/${name}.png`,`${name}.svg`,'image.svg','image.png','image.webp'].map(p=>`https://${project}.vercel.app/${p}`), ...['hyojin-oneclick-screens-a','hyojin-oneclick-screens-b','hyojin-techlabs-assets','hyojin-portfolio'].flatMap(p=>[`https://${p}.vercel.app/assets/${name}.webp`,`https://${p}.vercel.app/${name}.webp`])]};
 })
];
function imageType(b){
 if(b.length<64) return null;
 if(b.subarray(0,4).toString()==='RIFF' && b.subarray(8,12).toString()==='WEBP')return 'webp';
 if(b.subarray(0,8).equals(Buffer.from([137,80,78,71,13,10,26,10])))return 'png';
 if(b[0]===255&&b[1]===216&&b[2]===255)return 'jpg';
 return null;
}
const report=[];
await Promise.all(specs.map(async spec=>{
 const row={name:spec.name,success:false,attempts:[]};
 for(const ext of ['webp','png','jpg'])if(existsSync(`${dir}/${spec.name}.${ext}`)){
  const b=await fs.readFile(`${dir}/${spec.name}.${ext}`);if(imageType(b)){row.success=true;row.path=`/assets/${spec.name}.${ext}`;row.bytes=b.length;break;}
 }
 if(!row.success)for(const url of spec.urls){
  try{
   const r=await fetch(url,{signal:AbortSignal.timeout(12000),headers:{'User-Agent':'PortfolioAssetRecovery/1.0'}});
   row.attempts.push({url,status:r.status,type:r.headers.get('content-type')});
   if(!r.ok)continue;
   let b=Buffer.from(await r.arrayBuffer());let ext=imageType(b);
   if(!ext && /svg|html/i.test(r.headers.get('content-type')||'')){
    const match=b.toString().match(/data:image\/(?:png|jpeg|webp);base64,([A-Za-z0-9+/=\s]+)/);
    if(match){b=Buffer.from(match[1].replace(/\s/g,''),'base64');ext=imageType(b);}
   }
   if(!ext)continue;
   const file=`${spec.name}.${ext}`;await fs.writeFile(`${dir}/${file}`,b);
   row.success=true;row.path=`/assets/${file}`;row.bytes=b.length;row.sha256=createHash('sha256').update(b).digest('hex');row.source=url;break;
  }catch(e){row.attempts.push({url,error:e.message});}
 }
 report.push(row);console.log(spec.name,row.success?'RESTORED':'MISSING',row.path||'');
}));
report.sort((a,b)=>a.name.localeCompare(b.name));
await fs.writeFile('asset-recovery-report.json',JSON.stringify({generatedAt:new Date().toISOString(),images:report},null,2)+'\n');
console.log(`Recovered ${report.filter(x=>x.success).length}/${specs.length} original images.`);
