import re
import os

class Patcher:
  def __init__(self, class_data, file):
    self.class_data = class_data
    self.method_name = class_data['method']
    self.file = file
    self.commited_changes = []
    self.file_content = self.file.read()

  def get_definition_offset(self):
    m = re.search('\.bootstrapmethods', self.file_content)

    if m == None:
      m = re.search('.const \[1\] =', self.file_content)

    return m.start()

  def get_method_boundaries(self, method_id):
    r_start = '\.method\s+(?:(?:private|public)\s+)?(?:static\s+)?(?:final\s+)?(?:synthetic\s+)?\['
    r_end = '\].+?\.end method'

    if re.search(':', self.method_name) != None:
      _, const_id = self.method_name.split(':')

      const_id = self.class_data['patch_data'][0]['found'][int(const_id.replace('\\', ''))]
      r_end = '\]\s:\s\['+const_id+r_end

    m = re.search(
      r_start+method_id+r_end,
      self.methods_data,
      re.MULTILINE | re.DOTALL
    )

    return len(self.file_content[0:m.start()]), len(self.file_content[0:m.end()])

  def get_line_table_boundaries(self):
    m = re.search(
      '\s+\.attribute \[\d+\]\s+\.linenumbertable.+?\.end linenumbertable',
      self.file_content[self.b_m_start:self.b_m_end],
      re.MULTILINE | re.DOTALL
    )

    return self.b_m_start+m.start(), self.b_m_start+m.end()

  def get_var_table_boundaries(self):
    m = re.search(
      '\s+\.attribute \[\d+\]\s+\.localvariabletable.+?\.end localvariabletable',
      self.file_content[self.b_m_start:self.b_m_end],
      re.MULTILINE | re.DOTALL
    )

    return self.b_m_start+m.start(), self.b_m_start+m.end()

  def find_method_id(self):
    start_offset = self.get_definition_offset()

    self.methods_definition = self.file_content[start_offset:]
    self.methods_data = self.file_content[0:start_offset]

    if re.search(':', self.method_name) != None:
      method_name, const_id = self.method_name.split(':')
    else:
      method_name = self.method_name

    method_id = re.search(
      '.const \[(\d+)\]\s+=\s+Utf8\s+' + re.escape(method_name),
      self.methods_definition
    ).group(1)

    return method_id

  def reverse_const_search(self, const):
    return re.search('.const \[(\d+)\]\s+=\s+'+const+'\s*\n', self.methods_definition).group(1)

  def search_for_call_name(self, const_id, second_const_id = False):
    try:
      if not second_const_id:
        call_name = re.search(
          '.const \[(\d+)\]\s+=\s+NameAndType\s+\['+const_id+'\][^\n]+',
          self.methods_definition
        ).group(1)
      else:
        call_name = re.search(
          '.const \[(\d+)\]\s+=\s+NameAndType\s+\['+const_id+'\]\s+\['+second_const_id+'\]',
          self.methods_definition
        ).group(1)
    except:
      call_name = re.search(
        '.const \[(\d+)\]\s+=\s+Class\s+\['+const_id+'\]',
        self.methods_definition
      ).group(1)

    return call_name

  def search_for_method_call_id(self, call_name_id):
    return re.search(
      '.const \[(\d+)\]\s+=\s+Method\s+\[[^\]]+\]\s+\['+call_name_id+'\]',
      self.methods_definition
    ).group(1)

  def search_for_interface_call_id(self, call_name_id):
    return re.search(
      '.const \[(\d+)\]\s+=\s+InterfaceMethod\s+\[[^\]]+\]\s+\['+call_name_id+'\]',
      self.methods_definition
    ).group(1)

  def search_for_field_name(self, call_name_id):
    return re.search(
      '.const \[(\d+)\]\s+=\s+Field\s+\[[^\]]+\]\s+\['+call_name_id+'\]',
      self.methods_definition
    ).group(1)

  def resolve_const_val(self, find):
    if re.search(':', find) != None:
      type, find = find.split(':')
    else:
      type = 'none'

    if type in ['call', 'rcall', 'rfcall']:
      find = find.split('-')

      if type in ['rcall', 'rfcall']:
        find.reverse()

      const_id = list(map(self.reverse_const_search, find))
      call_name_id = self.search_for_call_name(const_id[0], const_id[1])

      if type in ['call', 'rfcall']:
        field_name_id = self.search_for_field_name(call_name_id)

        return field_name_id
      elif type == 'rcall':
        field_name_id = self.search_for_method_call_id(call_name_id)

        return field_name_id

    elif type == 'prim':
      const_id = self.reverse_const_search(re.escape(find))
      return const_id

    const_id = self.reverse_const_search(find)
    call_name_id = self.search_for_call_name(const_id)

    if type == 'class':
      call_id = call_name_id
    elif type == 'interface':
      call_id = self.search_for_interface_call_id(call_name_id)
    else:
      call_id = self.search_for_method_call_id(call_name_id)

    return call_id

  def in_range_for_patch(self, l, pd):
    return l >= pd['l_offset'][0] and l <= pd['l_offset'][1]

  def get_line_table_updates(self, attribute_table):
    updates = []
    b_lnt_start, b_lnt_end = self.get_line_table_boundaries()
    self.file.seek(b_lnt_start)

    offset = b_lnt_start-5 # 5 cos empty below
    line = 'empty'
    l = 0

    while line:
      offset += len(line)
      line = self.file.readline()

      m = re.search('^\s*L(\d+)\s', line)

      if offset >= b_lnt_end:  break
      if m == None:  continue

      in_list_to_mod = [x for x in attribute_table if x[0] == int(m.group(1))]

      if len(in_list_to_mod) > 0:
        new_line = re.sub('L'+str(in_list_to_mod[0][0]), 'L'+str(in_list_to_mod[0][1]), line)
        updates.append([offset, new_line, line])

    return updates

  def get_var_table_updates(self, attribute_table):
    updates = []
    b_vnt_start, b_vnt_end = self.get_var_table_boundaries()
    self.file.seek(b_vnt_start)

    offset = b_vnt_start-5 # 5 cos empty below
    line = 'empty'
    l = 0

    while line:
      offset += len(line)
      line = self.file.readline()

      m = re.search('from\s+L(\d+)\s+to\s+L(\d+)\s*$', line)

      if offset >= b_vnt_end:  break
      if m == None:  continue

      in_list_to_mod = [x for x in attribute_table if x[0] == int(m.group(1)) or x[0] == int(m.group(2))]


      if len(in_list_to_mod) > 0:
        new_line = re.sub('L'+str(in_list_to_mod[0][0]), 'L'+str(in_list_to_mod[0][1]), line)
        updates.append([offset, new_line, line])

    return updates

  def commit_line(self, offset, line, old_line, prepend = False):
    if prepend:
      self.commited_changes.insert(0, [offset, line, len(old_line)])
    else:
      self.commited_changes.append([offset, line, len(old_line)])

  def commit_attributes_update(self, attribute_table):
    updates = self.get_line_table_updates(attribute_table)
    updates += self.get_var_table_updates(attribute_table)

    # prepend, cos attr table must be same in lenght always
    list(map(lambda u: self.commit_line(*u, True), updates))

  def write_changes(self):
    add_offset = 0

    for i, el in enumerate(self.commited_changes):
      if len(el[1]) > el[2]:
        # re read file
        self.file.seek(0)
        self.file_content = self.file.read()
        #

        self.file.seek(0)
        self.file.write(self.file_content[0:el[0]+add_offset]+el[1]+self.file_content[el[0]+add_offset+el[2]:])

        # offset updated after write
        add_offset += len(el[1])-el[2]
        #
      else:
        self.file.seek(el[0]+add_offset)
        self.file.write(el[1])

      self.file.flush()
      os.fsync(self.file.fileno())


  def prepare_patch_data(self):
    for i, pd in enumerate(self.class_data['patch_data']):
      pd['after_entry_line'] = False
      pd['patch_finished'] = False
      pd['found'] = []

      if 'find' in pd:
        found = list(map(self.resolve_const_val, pd['find']))
        pd['found'] = found

        m = re.finditer('\\\\(\d+)', pd['entry_line'])

        for j in m:
          pd['entry_line'] = pd['entry_line'].replace('\\'+j.group(1), found[int(j.group(1))])


  def patch_line(self, *argv):
    argv = list(argv)

    l = int(argv[2])
    line = argv[4]
    pd = argv.pop(0)
    offset = argv.pop(0)

    argv = tuple(argv)

    is_updated, new_line, patch_finished, atribute_table = pd['exec'](*argv, pd['found'])

    if is_updated:
      self.commit_line(offset, new_line, line)

    if patch_finished:
      pd['patch_finished'] = True

      if len(atribute_table) > 0:
        self.commit_attributes_update(atribute_table)

  def patch(self):
    method_id = self.find_method_id()
    self.prepare_patch_data();

    self.b_m_start, self.b_m_end = self.get_method_boundaries(method_id)

    self.file.seek(self.b_m_start)

    offset = self.b_m_start-5 # 5 cos empty below
    line = 'empty'
    l = 0

    while line:
      line_prev = line

      offset += len(line)
      line = self.file.readline()

      m = re.search('^\s*L(\d+):', line)

      if offset >= self.b_m_end:  break
      if m == None:  continue

      l_prev = l
      l = m.group(1)

      for i, pd in enumerate(self.class_data['patch_data']):
        if pd['patch_finished'] == False and self.in_range_for_patch(int(l), pd):
          if re.search(pd['entry_line'], line):
            pd['after_entry_line'] = True

          if pd['after_entry_line'] == True:
            self.patch_line(pd, offset, l, l_prev, line, line_prev)


    is_patch_successful = all(x['patch_finished']==True for x in self.class_data['patch_data'])



    if is_patch_successful:
      self.write_changes()
      return True
    else:
      return False