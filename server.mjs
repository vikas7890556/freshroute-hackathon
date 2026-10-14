// Convenience launcher for the compiled offline demo. Python requirements must be installed.
import {spawn} from 'node:child_process';
import {existsSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {join} from 'node:path';
const root=fileURLToPath(new URL('.',import.meta.url));
const python=join(root,'.venv',process.platform==='win32'?'Scripts/python.exe':'bin/python');
if(!existsSync(python)){console.error('Missing project .venv. Complete README setup first.');process.exit(1);}
const child=spawn(python,['-m','uvicorn','backend.main:app','--host','127.0.0.1','--port','8000'],{cwd:root,stdio:'inherit'});
child.on('error',e=>{console.error(e.message);process.exitCode=1});
child.on('exit',code=>{process.exitCode=code??0});
process.on('SIGINT',()=>child.kill('SIGINT'));
process.on('SIGTERM',()=>child.kill('SIGTERM'));
