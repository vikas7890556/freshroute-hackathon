import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {join} from 'node:path';
const root=fileURLToPath(new URL('..',import.meta.url));
const python=join(root,'.venv',process.platform==='win32'?'Scripts/python.exe':'bin/python');
const args=process.argv.includes('--evaluate')?['scripts/evaluate.py']:['-m','unittest','discover','-s','backend/tests','-v'];
const result=spawnSync(python,args,{cwd:root,stdio:'inherit'});
if(result.error)console.error('Create the project .venv using README setup first. '+result.error.message);
process.exit(result.status??1);
