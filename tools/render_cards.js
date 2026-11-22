// Usage: node tools/render_cards.js <cards.html> <slug>
// Renders #c1..#c5 (1080x1080) to static/img/<slug>/N.png, then run: python3 tools/to_jpg.py <slug>
const {chromium} = require('playwright');
const path = require('path'), fs = require('fs');
(async () => {
  const [html, slug] = process.argv.slice(2);
  const out = path.join(__dirname, '..', 'static', 'img', slug);
  fs.mkdirSync(out, {recursive: true});
  const b = await chromium.launch();
  const p = await b.newPage({viewport: {width: 1080, height: 1080}});
  await p.goto('file://' + path.resolve(html));
  await p.waitForTimeout(500);
  for (let i = 1; i <= 5; i++) await p.locator('#c' + i).screenshot({path: path.join(out, i + '.png')});
  await b.close();
  console.log('rendered ->', out);
})();
