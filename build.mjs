import fs from 'node:fs/promises';
import path from 'node:path';
import { createHash } from 'node:crypto';

// This portfolio is self-contained: never fetch old deployment files at runtime.
const html = await fs.readFile('public/index.html', 'utf8');
const css = await fs.readFile('public/style.css', 'utf8');
if (!html.includes('portfolio') && !html.includes('OneClick')) throw new Error('Portfolio source missing');
if (/<script\b/i.test(html)) throw new Error('Unexpected runtime dependency in static portfolio');
if (/\b(?:QA|UAT)\b/i.test(html)) throw new Error('QA/UAT content has not been removed');
if (html.includes('기여도')) throw new Error('Contribution percentages must remain removed');
const images = [...html.matchAll(/<img\b[^>]*\bsrc="([^"]+)"/g)].map(m => m[1]);
if (images.length !== 8 || images.some(src => !src.startsWith('/assets/'))) throw new Error('Expected eight local image assets');
for (const src of images) {
  const file = path.join('public', src.slice(1));
  const data = await fs.readFile(file);
  if (data.length < 100 || data.subarray(0,4).toString() !== 'RIFF' || data.subarray(8,12).toString() !== 'WEBP') throw new Error(`Invalid image: ${file}`);
}
const expected = {
  browseroneclick: '3b5cf907621411ff566aa9cfff2d177461ab5ef5be195ed61e4b790da9134887',
  mobile: '28d50c3abc2ec6a1e78d7474a23921fa5dd77c71e581119905884c96eaa96c18'
};
for (const [name, sha] of Object.entries(expected)) {
  const data = await fs.readFile(`public/assets/${name}.webp`);
  if (createHash('sha256').update(data).digest('hex') !== sha) throw new Error(`Image integrity mismatch: ${name}`);
}
if (!css.trim()) throw new Error('Stylesheet missing');
await fs.rm('dist', {recursive:true, force:true});
await fs.cp('public', 'dist', {recursive:true});
console.log('Built static portfolio: QA removed, 8 verified images, Grafana and Figma planning retained.');
