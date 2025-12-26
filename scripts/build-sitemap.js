// Walk dist/ recursively
// Find all index.html files
// Generate sitemap.xml

const fs = require('fs');
const path = require('path');

const DIST = './dist';
const BASE_URL = 'https://luminait.app';
const OUTPUT = './dist/sitemap.xml';

function walkDir(dir, fileList = []) {
  const files = fs.readdirSync(dir);
  files.forEach(file => {
    const filePath = path.join(dir, file);
    if (fs.statSync(filePath).isDirectory()) {
      walkDir(filePath, fileList);
    } else if (file === 'index.html') {
      fileList.push(filePath);
    }
  });
  return fileList;
}

function buildSitemap() {
  const files = walkDir(DIST);
  
  const urls = files.map(file => {
    const relativePath = file.replace(DIST, '').replace('/index.html', '/').replace(/\\/g, '/');
    const url = relativePath === '/' ? BASE_URL + '/' : BASE_URL + relativePath;
    return `  <url><loc>${url}</loc></url>`;
  });
  
  const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls.join('\n')}
</urlset>`;
  
  fs.writeFileSync(OUTPUT, sitemap);
  console.log(`Sitemap generated with ${urls.length} URLs`);
}

buildSitemap();

