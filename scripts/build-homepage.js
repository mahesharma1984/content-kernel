// Scan dist/ for book folders
// Each folder with index.html = one book
// Generate homepage with links to each book

const fs = require('fs');
const path = require('path');

const DIST = './dist';
const TEMPLATE = './templates/homepage.html';
const OUTPUT = './dist/index.html';

function getBookFolders() {
  return fs.readdirSync(DIST)
    .filter(f => {
      const stat = fs.statSync(path.join(DIST, f));
      return stat.isDirectory() && fs.existsSync(path.join(DIST, f, 'index.html'));
    });
}

function buildHomepage() {
  const books = getBookFolders();
  const template = fs.readFileSync(TEMPLATE, 'utf8');
  
  const links = books.map(slug => {
    // Extract title from the book's index.html <title> tag
    const html = fs.readFileSync(path.join(DIST, slug, 'index.html'), 'utf8');
    const titleMatch = html.match(/<title>([^<]+)<\/title>/);
    const title = titleMatch ? titleMatch[1].replace(' — Analysis', '') : slug;
    
    return `<li><a href="/${slug}/">${title}</a></li>`;
  }).join('\n');
  
  const output = template.replace('{{BOOK_LINKS}}', links);
  fs.writeFileSync(OUTPUT, output);
  console.log(`Homepage generated with ${books.length} books`);
}

buildHomepage();

