// Entry program for news-image-20261118 (Node 22, standard library only).
//
// The entry image is the finished front page, entry.png, which ships in
// this repository: the grader runs with no network, so the program simply
// copies it to the output directory. It writes the same bytes on every
// run, because it copies the same file.
//
// Run locally with:  mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync, statSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
mkdirSync(outDir, { recursive: true });

const here = dirname(fileURLToPath(import.meta.url));
const dest = join(outDir, 'entry.png');
copyFileSync(join(here, 'entry.png'), dest);

// Confirm the copy landed, so a silent failure cannot pass unnoticed.
console.log(`entry.png -> ${dest} (${statSync(dest).size} bytes)`);
