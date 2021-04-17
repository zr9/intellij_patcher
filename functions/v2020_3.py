import re

gd = {}

def clean_line(line):
  return re.sub('^L\d+:', '', line)

def not_changed():
  return False, False, False, []

def patch(data, is_finished = False, attribute_table = []):
  return True, data, is_finished, attribute_table

# return format for manual return is:
# offsetPatched(True|False) data(Str) patchFinished(True|False) attributeTable([])
# attributeTable only work when patch is finished
# avoid modifying of attribute table when possible

def scrolling_model_p1(l, l_prev, line, line_prev, found = []):
  line = clean_line(line)
  line_prev = clean_line(line_prev)

  return patch('L'+l+':'+line_prev, True)

def scrolling_model_p2(l, l_prev, line, line_prev, found = []):
  line = re.sub('(iconst)_2', '\\1_1', clean_line(line))

  return patch('L'+l+':'+line, True)

def caret_model_p1(l, l_prev, line, line_prev, found = []):
  m = re.search('ifeq L\d+', line)

  if m != None:
    line = re.sub('ifeq', 'ifne', clean_line(line))
    return patch('L'+l+':'+line, True)

  return not_changed()

def tool_window_manager_p1(l, l_prev, line, line_prev, found = []):
  cline = clean_line(line).strip()

  if re.search('invokespecial', cline) != None:
    return patch(' '*len(line), True)

  return patch(' '*len(line))

def tool_window_manager_p2(l, l_prev, line, line_prev, found = []):
  cline = clean_line(line).strip()
  line = clean_line(line)
  return_l = 30

  if cline == 'aload_0':
    gd['current_l'] = int(l_prev)
    gd['patch_started'] = True
    gd['attr_table'] = []

    spacing = line.count(' ')-1

    nline = 'L'+str(gd['current_l']+1)+':'+' '*spacing+'aload_1\n'
    nline += 'L'+str(gd['current_l']+2)+':'+' '*spacing+'invokevirtual ['+found[0]+']\n'
    nline += 'L'+str(gd['current_l']+3)+':'+' '*spacing+'getstatic ['+found[1]+']\n'
    nline += 'L'+str(gd['current_l']+4)+':'+' '*spacing+'if_acmpeq L'+str(return_l)+'\n'
    nline += 'L'+str(gd['current_l']+5)+':'+line

    gd['current_l'] += 5
    gd['attr_table'].append([int(l), gd['current_l']])

    return patch(nline)

  if cline == 'return':
    gd['attr_table'].append([int(l), return_l])

    nline  = '.stack same\n'
    nline += 'L'+str(return_l)+':'+line+'\n'

    return patch(nline)

  if len(cline) == 0:
    gd['attr_table'].append([int(l), return_l+1])
    attr_table = gd['attr_table']
    gd.clear()

    return patch('L'+str(return_l+1)+':'+line+'\n', True, attr_table)

  if 'patch_started' in gd and gd['patch_started']:
    gd['current_l'] += 1
    gd['attr_table'].append([int(l), gd['current_l']])

    return patch('L'+str(gd['current_l'])+':'+line)

  return not_changed()

def tool_brace_highlighting_handler_p1(l, l_prev, line, line_prev, found = []):
  m = re.search('ifeq L\d+', line)

  if m != None:
    line = re.sub('ifeq', 'ifne', clean_line(line))
    return patch('L'+l+':'+line, True)

  return not_changed()

def editor_gutter_component_impl_p1(l, l_prev, line, line_prev, found = []):
  # inject on invokespecial cos it L5 and have 3 free slots L5-L8
  line = clean_line(line)
  spacing = line.count(' ')-1

  line = 'L'+str(int(l_prev)+1)+':'+line
  line += 'L'+str(int(l_prev)+2)+':'+' '*spacing+'bipush 17\n'
  line += 'L'+str(int(l_prev)+3)+':'+' '*spacing+'isub\n'

  return patch(line, True)

def editor_gutter_component_impl_p2(l, l_prev, line, line_prev, found = []):
  cline = clean_line(line).strip()
  line = clean_line(line)

  if cline == 'astore 6':
    gd['current_l'] = int(l_prev)
    gd['patch_started'] = True
    gd['attr_table'] = []

  if cline == 'aload 6':
    spacing = line.count(' ')-2

    nline = 'L'+str(gd['current_l']+1)+':'+' '*spacing+'bipush 21\n'
    nline += 'L'+str(gd['current_l']+2)+':'+' '*spacing+'isub\n'
    nline += 'L'+str(gd['current_l']+3)+':'+line

    gd['attr_table'].append([int(l), gd['current_l']+3])
    attr_table = gd['attr_table']

    gd.clear()
    return patch(nline, True, attr_table)

  if 'patch_started' in gd and gd['patch_started']:
    gd['current_l'] += 1
    gd['attr_table'].append([int(l), gd['current_l']])

    return patch('L'+str(gd['current_l'])+':'+line)

  return not_changed()

def editor_gutter_component_impl_p3(l, l_prev, line, line_prev, found = []):
  cline = clean_line(line).strip()
  line = clean_line(line)

  if cline == 'istore 18':
    gd['patch_started'] = True
    gd['current_l'] = int(l_prev)
    gd['attr_table'] = []

    spacing = line.count(' ')-2

    nline = 'L'+str(gd['current_l']+1)+':'+' '*spacing+'aload_0\n'
    nline += 'L'+str(gd['current_l']+2)+':'+' '*spacing+'getfield ['+found[0]+']\n'
    nline += 'L'+str(gd['current_l']+3)+':'+' '*spacing+'iadd\n'
    nline += 'L'+str(gd['current_l']+4)+':'+' '*spacing+'aload_0\n'
    nline += 'L'+str(gd['current_l']+5)+':'+' '*spacing+'invokespecial ['+found[1]+']\n'
    nline += 'L'+str(gd['current_l']+6)+':'+' '*spacing+'iadd\n'
    nline += 'L'+str(gd['current_l']+7)+':'+line

    gd['current_l'] += 7

    return patch(nline)

  if 'patch_started' in gd and gd['patch_started']:
    gd['current_l'] += 1
    l_i = gd['current_l']
    patch_finished = False

    gd['attr_table'].append([int(l), l_i])
    attr_table = gd['attr_table']

    if re.search('getfield \[\d+\]+', line) != None:
      patch_finished = True
      gd.clear()

    return patch('L'+str(l_i)+':'+line, patch_finished, attr_table)

  return not_changed()

def editor_gutter_component_impl_p4(l, l_prev, line, line_prev, found = []):
  cline = clean_line(line).strip()
  line = clean_line(line)

  if cline == 'i2d':
    gd['current_l'] = int(l_prev)
    gd['patch_started'] = True


  if cline == 'dadd':
    spacing = line.count(' ')-1

    nline = 'L'+str(gd['current_l']+1)+':'+line
    nline += 'L'+str(gd['current_l']+2)+':'+' '*spacing+'bipush 15\n'
    nline += 'L'+str(gd['current_l']+3)+':'+' '*spacing+'i2d\n'
    nline += 'L'+str(gd['current_l']+4)+':'+' '*spacing+'dsub\n'

    gd.clear()
    return patch(nline, True)


  if 'patch_started' in gd and gd['patch_started']:
    gd['current_l'] += 1

    return patch('L'+str(gd['current_l'])+':'+re.sub('\n', '', line))

  return not_changed()

def editor_gutter_component_impl_p5(l, l_prev, line, line_prev, found = []):
  cline = clean_line(line).strip()
  line = clean_line(line)

  if cline == 'aload_0':
    gd['current_l'] = int(l_prev)
    gd['patch_started'] = True

  if cline == 'iload_3':
    spacing = line.count(' ')-1

    nline = 'L'+str(gd['current_l']+1)+':'+' '*spacing+'aload_0\n'
    nline += 'L'+str(gd['current_l']+2)+':'+' '*spacing+'getfield ['+found[0]+']\n'
    nline += 'L'+str(gd['current_l']+3)+':'+' '*spacing+'isub\n'
    nline += 'L'+str(gd['current_l']+4)+':'+' '*spacing+'bipush 10\n'
    nline += 'L'+str(gd['current_l']+5)+':'+' '*spacing+'isub\n'
    nline += 'L'+str(gd['current_l']+6)+':'+line

    gd['current_l'] += 6

    return patch(nline)

  if cline == 'aload 6':
    l = gd['current_l'] + 1
    gd.clear()
    return patch('L'+str(l)+':'+line, True)

  if 'patch_started' in gd and gd['patch_started']:
    gd['current_l'] += 1

    return patch('L'+str(gd['current_l'])+':'+line)


  return not_changed()

def editor_gutter_component_impl_p6(l, l_prev, line, line_prev, found = []):
  spacing = line.count(' ')-2

  return patch('L'+l+':'+' '*spacing+'fconst_2   ', True)

def editor_gutter_component_impl_p7(l, l_prev, line, line_prev, found = []):
  cline = clean_line(line).strip()
  line = clean_line(line)

  if cline == 'iload_2':
    if 'patch_started' not in gd:
      gd['current_l'] = int(l_prev)+1
      gd['patch_started'] = True
      gd['attr_table'] = []

      spacing = line.count(' ')-1

      nline = 'L'+str(gd['current_l'])+':'+line
      nline += 'L'+str(gd['current_l']+1)+':'+' '*spacing+'aload_0\n'
      nline += 'L'+str(gd['current_l']+2)+':'+' '*spacing+'invokevirtual ['+found[0]+']\n'
      nline += 'L'+str(gd['current_l']+3)+':'+' '*spacing+'iadd\n'
      nline += 'L'+str(gd['current_l']+4)+':'+' '*spacing+'bipush 8\n'
      nline += 'L'+str(gd['current_l']+5)+':'+' '*spacing+'iadd\n'

      gd['current_l'] += 5

      return patch(nline)

    else:
      spacing = line.count(' ')-1

      nline = 'L'+str(gd['current_l']+1)+':'+line
      nline += 'L'+str(gd['current_l']+2)+':'+' '*spacing+'aload_0\n'
      nline += 'L'+str(gd['current_l']+3)+':'+' '*spacing+'invokevirtual ['+found[0]+']\n'
      nline += 'L'+str(gd['current_l']+4)+':'+' '*spacing+'iadd\n'

      gd['current_l'] += 4

      return patch(nline)


  if 'patch_started' in gd and gd['patch_started']:
    gd['current_l'] += 1

    if cline == 'aload 7':
      l_i = gd['current_l']

      gd['attr_table'].append([int(l), l_i])
      attr_table = gd['attr_table']
      gd.clear()

      return patch('L'+str(l_i)+':'+line, True, attr_table)

    return patch('L'+str(gd['current_l'])+':'+line)

  return not_changed()

def editor_gutter_component_impl_p8(l, l_prev, line, line_prev, found = []):
  cline = clean_line(line).strip()
  line = clean_line(line)

  if cline == 'iadd':
    gd['current_l'] = int(l_prev)+1
    gd['patch_started'] = True

    spacing = line.count(' ')-1

    nline = 'L'+str(gd['current_l'])+':'+line
    nline += 'L'+str(gd['current_l']+1)+':'+' '*spacing+'aload_0\n'
    nline += 'L'+str(gd['current_l']+2)+':'+' '*spacing+'invokevirtual ['+found[0]+']\n'
    nline += 'L'+str(gd['current_l']+3)+':'+' '*spacing+'iadd\n'
    nline += 'L'+str(gd['current_l']+4)+':'+' '*spacing+'bipush 20\n'
    nline += 'L'+str(gd['current_l']+5)+':'+' '*spacing+'iadd\n'

    gd['current_l'] += 5

    return patch(nline)

  if re.search('getstatic \[\d+\]', line) != None:
    l = gd['current_l']+1
    gd.clear()

    return patch('L'+str(l)+':'+line, True)

  if 'patch_started' in gd and gd['patch_started']:
    gd['current_l'] += 1

    return patch('L'+str(gd['current_l'])+':'+line)

  return not_changed()

def auto_popup_controller_p1(l, l_prev, line, line_prev, found = []):
  line = clean_line(line)

  m = re.search('getstatic \[\d+\]', line)

  if m != None:
    spacing = line.count(' ')-2

    nline = 'getstatic Field com/intellij/codeInsight/completion/CompletionType SMART Lcom/intellij/codeInsight/completion/CompletionType;\n'

    return patch('L'+str(l)+':'+' '*spacing+nline, True)

  return not_changed()