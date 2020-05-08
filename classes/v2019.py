import functions.v2019 as fn

# !!! "\\" in entry_line is index of a found list, so starts with a "0" !!!
# !!! also entry_line is a regex, but parsing on above goes first !!!

classes = [
  {
    # Disabling auto scroll of editor
    'id': 0,
    'file': 'platform-impl.jar',
    'class': 'com/intellij/openapi/editor/impl/ScrollingModelImpl',
    'method': 'calcOffsetsToScroll',
    'desc': 'Removing 1 line scroll ahead',
    'patch_data': [
      {
        'l_offset': [220, 240],
        'find': ['Utf8 max\W'],
        'entry_line': 'invokestatic \[\\0\]',
        'exec': fn.scrolling_model_p1
      },
      {
        'l_offset': [270, 280],
        'entry_line': 'iconst_2',
        'exec': fn.scrolling_model_p2
      }
    ]
  },

  {
    # Sets highlight current row only on gutter area
    'id': 1,
    'file': 'platform-impl.jar',
    'class': 'com/intellij/openapi/editor/impl/CaretModelImpl',
    'method': 'getTextAttributes',
    'desc': 'Removing highlight on whole row, leaving only on left sidebar',
    'patch_data': [
      {
        'l_offset': [20, 40],
        'find': ['interface:Utf8 isCaretRowShown'],
        'entry_line': 'invokeinterface \[\\0\] 1',
        'exec': fn.caret_model_p1
      }
    ]
  },

  {
    # Disabling auto hide on undocked tool windows
    'id': 2,
    'file': 'platform-impl.jar',
    'class': 'com/intellij/openapi/wm/impl/ToolWindowManagerImpl',
    'method': 'lambda$new$5',
    'desc': 'Removing auto hide on tool windows (dock unpinned)',
    'patch_data': [
      {
        'l_offset': [0, 20],
        'find': ['class:Utf8 java/util/ArrayList'],
        'entry_line': 'new \[\\0\]',
        'exec': fn.tool_window_manager_p1
      }
    ]
  },

  {
    # Removing function name tooltip on bracket
    'id': 3,
    'file': 'platform-impl.jar',
    'class': 'com/intellij/codeInsight/highlighting/BraceHighlightingHandler',
    'method': 'lambda$null$10',
    'desc': 'Removing tooltip which appears on top when cursor is on bracket',
    'patch_data': [
      {
        'l_offset': [1, 9],
        'find': ['interface:Utf8 isDisposed'],
        'entry_line': 'invokeinterface \[\\0\] 1',
        'exec': fn.tool_brace_highlighting_handler_p1
      }
    ]
  },

  {
    # reducing gutter size, but if used alone skewing folding
    'id': 4,
    'file': 'platform-impl.jar',
    'class': 'com/intellij/openapi/editor/impl/EditorGutterComponentImpl',
    'method': 'getPreferredSize',
    'desc': 'Reduce spacing between gutter and editor (shrink)',
    'patch_data': [
      {
        'l_offset': [3, 11],
        'entry_line': 'iadd',
        'exec': fn.editor_gutter_component_impl_p1
      }
    ]
  },

  {
    # Moves carret row on gutter more to left (to create a gap between)
    'id': 5,
    'file': 'platform-impl.jar',
    'class': 'com/intellij/openapi/editor/impl/EditorGutterComponentImpl',
    'method': 'paintCaretRowBackground',
    'desc': 'Reduce spacing between gutter and editor (shrink)',
    'depends': [4],
    'patch_data': [
      {
        'l_offset': [40, 70],
        'entry_line': 'ifnull L\d+',
        'exec': fn.editor_gutter_component_impl_p2
      }
    ]
  },

  {
    # Changes offset of where line numbers are painted
    'id': 6,
    'file': 'platform-impl.jar',
    'class': 'com/intellij/openapi/editor/impl/EditorGutterComponentImpl',
    'method': 'doPaintLineNumbers',
    'desc': 'Changes line numbers and icons order',
    'patch_data': [
      {
        'l_offset': [290, 330],
        'find': ['call:Utf8 myIconsAreaWidth-Utf8 I'],
        'entry_line': 'aload 15',
        'exec': fn.editor_gutter_component_impl_p3
      }
    ]
  },

  {
    # reduce gutter size, more to left
    'id': 7,
    'file': 'platform-impl.jar',
    'class': 'com/intellij/openapi/editor/impl/EditorGutterComponentImpl',
    'method': 'getWhitespaceSeparatorOffset2D',
    'desc': 'Reduce spacing between gutter and editor (shrink)',
    'depends': [4],
    'patch_data': [
      {
        'l_offset': [5, 20],
        'entry_line': 'aload_0',
        'exec': fn.editor_gutter_component_impl_p4
      }
    ]
  },

  {
    # Changes offset of where action icons are painted
    'id': 8,
    'file': 'platform-impl.jar',
    'class': 'com/intellij/openapi/editor/impl/EditorGutterComponentImpl',
    'method': 'lambda$paintIconRow$11',
    'desc': 'Changes line numbers and icons order',
    'depends': [6],
    'patch_data': [
      {
        'l_offset': [27, 39],
        'find': ['call:Utf8 myLineNumberAreaWidth-Utf8 I'],
        'entry_line': 'aload_0',
        'exec': fn.editor_gutter_component_impl_p5
      }
    ]
  },

  {
    # reducing gap between areas
    'id': 9,
    'file': 'platform-impl.jar',
    'class': 'com/intellij/openapi/editor/impl/EditorGutterComponentImpl',
    'method': '<clinit>',
    'desc': 'Reducing gap between areas (better with #4)',
    'patch_data': [
      {
        'l_offset': [65, 75],
        'find': ['prim:Float +0xA00000p-21f'],
        'entry_line': 'ldc_w \[\\0\]',
        'exec': fn.editor_gutter_component_impl_p6
      }
    ]
  },

  {
    # Sets proper area for icons onclick event
    'id': 10,
    'file': 'platform-impl.jar',
    'class': 'com/intellij/openapi/editor/impl/EditorGutterComponentImpl',
    'method': 'lambda$getGutterRenderer$20',
    'desc': 'Changes line numbers and icons order',
    'depends': [6],
    'patch_data': [
      {
        'l_offset': [20, 40],
        'entry_line': 'iload_3',
        'exec': fn.editor_gutter_component_impl_p7
      }
    ]
  },

  {
    # Sets proper area for line number onclick event and disabled debug onclick event
    'id': 11,
    'file': 'platform-impl.jar',
    'class': 'com/intellij/openapi/editor/impl/EditorGutterComponentImpl',
    'method': 'getEditorMouseAreaByOffset',
    'desc': 'Changes line numbers and icons order',
    'depends': [6],
    'patch_data': [
      {
        'l_offset': [5, 30],
        'find': ['call:Utf8 myIconsAreaWidth-Utf8 I'],
        'entry_line': 'iadd',
        'exec': fn.editor_gutter_component_impl_p8
      }
    ]
  },
]