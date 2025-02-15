import { readFileSync, writeFileSync } from 'fs';

const template = readFileSync('./serve.template.json', 'utf-8');
const config = template.replace('${API_URL}', process.env.API_URL || '/index.html');

writeFileSync('./serve.json', config); 