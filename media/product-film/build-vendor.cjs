/* Bundle pinned, local dependencies. NODE_PATH may point at shared tool installs. */
const fs = require('node:fs');
const path = require('node:path');
const esbuild = require('esbuild');
const root = __dirname;
const vendor = path.join(root, 'vendor');
fs.mkdirSync(vendor, { recursive: true });
esbuild.buildSync({
  entryPoints: [path.join(vendor, 'three-entry.js')],
  outfile: path.join(vendor, 'three.min.js'),
  bundle: true, format: 'iife', globalName: 'THREE', platform: 'browser',
  minify: true, legalComments: 'linked',
  nodePaths: (process.env.NODE_PATH || '').split(path.delimiter).filter(Boolean)
});
const threeRoot = path.dirname(path.dirname(require.resolve('three')));
fs.copyFileSync(path.join(threeRoot, 'LICENSE'), path.join(vendor, 'THREE-LICENSE.txt'));
const gsapFile = require.resolve('gsap/dist/gsap.min.js');
fs.copyFileSync(gsapFile, path.join(vendor, 'gsap.min.js'));
const gsapRoot = path.dirname(path.dirname(gsapFile));
const license = fs.readdirSync(gsapRoot).find(name => /^license/i.test(name));
if (license) fs.copyFileSync(path.join(gsapRoot, license), path.join(vendor, 'GSAP-LICENSE.txt'));
console.log('Bundled Three.js, RoundedBoxGeometry, RoomEnvironment and GSAP with licence records.');
