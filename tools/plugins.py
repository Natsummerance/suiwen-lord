#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Suiwen optional language pack manager. Python 3.12+, standard library only.
No shell commands, model downloads, system input-source registration or auto-run.
"""
import argparse, hashlib, json, os, shutil, sys, tarfile, tempfile, urllib.request
from pathlib import Path

CATALOG=Path(__file__).resolve().parents[1]/'plugins/catalog.json'
DEFAULT=Path.home()/'Library/Application Support/Suiwen/plugins'

def sha256(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
 return h.hexdigest()

def catalog():return json.loads(CATALOG.read_text())['plugins']
def pack(identifier):
 result=next((p for p in catalog()if p['id']==identifier),None)
 if result is None:raise ValueError('未知插件')
 return result

def atomic(path,value):
 temp=path.with_suffix('.tmp');temp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');temp.chmod(0o600);os.replace(temp,path)

def install(identifier,root=DEFAULT,progress=lambda v:None):
 p=pack(identifier);root=Path(root);root.mkdir(parents=True,exist_ok=True)
 if root.is_symlink():raise ValueError('插件根目录不能是符号链接')
 target=root/identifier
 if target.exists():
  receipt=target/'.suiwen-package.json'
  if receipt.exists()and json.loads(receipt.read_text()).get('fingerprint')==p['fingerprint']:return {'status':'installed','plugin':identifier,'path':str(target)}
  raise ValueError('目录已存在且版本不同；先从插件管理移到回收区')
 opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
 with tempfile.TemporaryDirectory(prefix='.'+identifier+'-',dir=root) as tmp:
  temp=Path(tmp);stage=temp/'unpacked';stage.mkdir();expanded=0;total=0
  for a in p['assets']:
   archive=temp/a['name']
   with opener.open(urllib.request.Request(a['url'],headers={'User-Agent':'Suiwen-Plugin-Manager/0.8','Accept-Encoding':'identity'}),timeout=30) as r,archive.open('wb') as f:
    count=0
    for block in iter(lambda:r.read(256*1024),b''):
     count+=len(block);total+=len(block)
     if count>a['bytes']:raise ValueError('下载超过固定大小；拒绝滚动版本')
     f.write(block);progress({'status':'downloading','plugin':identifier,'received':total,'bytes':p['bytes']})
   if count!=a['bytes']or sha256(archive)!=a['sha256']:raise ValueError('SHA256 或大小不符')
   with tarfile.open(archive,'r:bz2') as tar:
    for m in tar.getmembers():
     expanded+=max(0,m.size)
     if expanded>400*1024**2:raise ValueError('解包超出预算')
    tar.extractall(stage,filter='data')
  atomic(stage/'.suiwen-package.json',{'schema':1,'id':identifier,'fingerprint':p['fingerprint'],'license':p['license'],'sources':p['sources'],'download_bytes':total})
  os.replace(stage,target)
 return {'status':'installed','plugin':identifier,'path':str(target),'download_bytes':total,'system_input_source_changed':False}

def remove(identifier,root=DEFAULT):
 # Recoverable removal, never recursive deletion of arbitrary paths.
 pack(identifier);root=Path(root);target=root/identifier;receipt=target/'.suiwen-package.json'
 if target.is_symlink()or not receipt.is_file()or json.loads(receipt.read_text()).get('id')!=identifier:raise ValueError('不是本管理器拥有的插件')
 trash=root/'.trash';trash.mkdir(exist_ok=True)
 import uuid
 dest=trash/(identifier+'-'+uuid.uuid4().hex[:8]);os.replace(target,dest)
 return {'status':'removed','recoverable_path':str(dest)}

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=['list','install','remove']);parser.add_argument('id',nargs='?');parser.add_argument('--root',type=Path,default=DEFAULT);a=parser.parse_args()
 try:
  result=[{k:p[k]for k in ['id','name','bytes','license']}for p in catalog()]if a.action=='list'else install(a.id,a.root)if a.action=='install'else remove(a.id,a.root)
  print(json.dumps(result,ensure_ascii=False,indent=2))
 except Exception as e:print(json.dumps({'error':str(e)},ensure_ascii=False),file=sys.stderr);raise SystemExit(1)
if __name__=='__main__':main()
