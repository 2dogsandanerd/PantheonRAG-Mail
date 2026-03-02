#!/usr/bin/env node
/**
 * Fix HTML webpack output to use relative paths instead of absolute
 * This is needed because loadFile() in Electron needs relative paths
 */

const fs = require('fs');
const path = require('path');

const htmlPath = path.join(__dirname, '.webpack/renderer/main_window/index.html');

if (fs.existsSync(htmlPath)) {
  let html = fs.readFileSync(htmlPath, 'utf8');

  // Replace absolute paths with relative
  html = html.replace(/src="\/main_window\//g, 'src="./');
  html = html.replace(/href="\/main_window\//g, 'href="./');

  fs.writeFileSync(htmlPath, html);
  console.log('✅ Fixed HTML paths to be relative');
} else {
  console.log('⚠️  HTML file not found, skipping fix');
}
