#! /usr/bin/env python3
# -*- coding: utf-8 -*-

D_WIDTH = 90
D_HEIGHT = 20

import os.path
import re
import sys
import zipfile
import tempfile
import functools
import importlib.util
import io

# capture stdout
stdout_ = sys.stdout
sys.stdout = io.StringIO()
#

if not os.path.isdir('./lib'):
  print('Installing requirements')
  os.system('pip install -r requirements.txt -t ./lib')

  with open('lib/bin/disassemble.py', 'r+') as f:
    print('Patching unpatchable')

    patch_str0 = "start_time = time.time()"
    patch_str1 = "print(time.time() - start_time, ' seconds elapsed')"

    content = f.read()
    f.seek(0)

    m = re.search('(\s+)'+re.escape(patch_str0), content)
    indent = m.group(1)

    content = content.replace(patch_str0, patch_str0 + '\n' + indent + 'filenames = []')

    m = re.search('(\s+)'+re.escape(patch_str1), content)
    indent = m.group(1)
    indent2 = ' '*(indent.count(' ')-8)

    content = content.replace(patch_str1, patch_str1 + '\n' + indent + 'filenames.append(filename)\n' + indent2 + 'return filenames')
    f.write(content)
    f.close()

from lib.bin.disassemble import disassembleSub
from lib.bin.assemble import assembleClass
import lib.dialog
from lib.dialog import Dialog
from lib.Krakatau import script_util
from patcher import Patcher

try:
  d = Dialog(dialog="dialog")
except:
  print('No "dialog" presented in system')
  raise


def readArchive(archive, name):
  with archive.open(name) as f:
    return f.read()

def parse_patches_data(patches_raw, tags):
  patches = []
  dependencies = []
  tags = list(map(lambda t: int(t), tags))

  for i, patch in enumerate(patches_raw):
    if 'depends' in patch and any(e in tags for e in patch['depends']):
      dependencies.append(patch['id'])

  tags += dependencies

  return list(filter(lambda c, tags=tags: c['id'] in tags, classes))


jar = './res/platform-impl.jar'

if not os.path.isfile(jar):
  d.msgbox(
    title='No platform-impl.jar',
    text='You need to copy platform-impl.jar file in "./res/" dir and launch patch again',
    width=D_WIDTH,
    height=D_HEIGHT,
  )
  sys.exit()

code, tag = d.menu(
  title="Intellij Version",
  text="Choose the version you have",
  choices=[
    ("v2019", "2019.2"),
    ("v2020_1", "2020.1"),
    ("v2020_2", "2020.2"),
    ("v2020_3", "2020.3"),
    ("exit", "Duck this shit I'm out :)")
  ],
  width=D_WIDTH,
  height=D_HEIGHT
)

if tag != 'exit' and code != 'cancel':
  classes = importlib.import_module('classes.'+tag).classes

  patches_choices = [(str(c['id']), c['desc'], 0) for c in list(filter(lambda c: not 'depends' in c, classes))]

  code, tags = d.checklist(
    title="Patches",
    text="Choose the patches you wish to apply",
    choices=patches_choices,
    width=D_WIDTH,
    height=D_HEIGHT
  )

  if len(tags) >0 and code != 'cancel':
    patches = parse_patches_data(classes, tags)

    patches_finished = []
    iter_cnt = 100/len(patches)
    gauage = 0

    out_dsm = script_util.makeWriter('dsm_classes', '.j')

    targets = list(set(map(lambda c: c['class']+'.class', patches)))


    d.gauge_start(
      title='Patching everything',
      text='Please wait',
      percent=int(gauage),
      width=D_WIDTH,
      height=D_HEIGHT
    )


    tmpfd, tmpname = tempfile.mkstemp(dir=os.path.dirname(jar))
    os.close(tmpfd)

    with zipfile.ZipFile(jar, 'r') as z_in, zipfile.ZipFile(tmpname, 'w') as z_out:
      readFunc = functools.partial(readArchive, z_in)

      targets_dsm = disassembleSub(readFunc, out_dsm, targets = targets, roundtrip=True)

      for i, cls in enumerate(patches):
        with open('dsm_classes/'+str(cls['class'])+'.j', 'r+') as file:
          patcher = Patcher(cls, file)
          patch_res = patcher.patch()

          patch_id = str(cls['id'])

          if 'depends' in cls:
            patch_id += '/d'+str(cls['depends'])

          patches_finished.append([patch_id, patch_res])

          file.close()

          gauage += iter_cnt
          d.gauge_update(percent=int(gauage))


      for item in z_in.infolist():
       buffer = z_in.read(item.filename)

       if item.filename not in targets:
         z_out.writestr(item, buffer)

      for i, target in enumerate(targets_dsm):
        pairs = assembleClass(target)

        for name, data in pairs:
          z_out.writestr(name.decode()+'.class', data)

    os.remove(jar)
    os.rename(tmpname, jar)

    d.gauge_stop()

    results = list(set(map(lambda c: 'Finished' if c[1] else 'Failed', patches_finished)))

    results = '\n'.join(
      [str(c[0]) + ' - ' + ('Finished' if c[1] else 'Failed') for c in patches_finished]
    )

    d.msgbox(
      title='Patcher finished',
      text=results,
      width=D_WIDTH,
      height=D_HEIGHT,
    )