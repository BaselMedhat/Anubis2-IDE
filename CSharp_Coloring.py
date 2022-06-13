import sys
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter


def formatCS(color, style=''):
    """
    Return a QTextCharFormat with the given attributes.
    """
    
    _color = QColor()
    if type(color) is not str:
        _color.setRgb(color[0], color[1], color[2])
    else:
        _color.setNamedColor(color)

    _format = QTextCharFormat()
    _format.setForeground(_color)
    if 'bold' in style:
        _format.setFontWeight(QFont.Bold)
    if 'italic' in style:
        _format.setFontItalic(True)

    return _format



CSStyle = {
       'keyword': formatCS('blue'),
       'keywordsTwo' : formatCS('violet'),
      'operator': formatCS('darkblue'),
       'brace': formatCS('darkblue'),
       'string': formatCS('magenta'),
       'comment': formatCS('grey'),
       'numbers': formatCS('brown'),
   }

class CSharpHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for the C# language.
    """
    # C# keywords

    
    keywords = [
        'abstract','as','base','bool','break','byte','case','catch',
        'char','checked','class','const','continue','decimal','default',
        'delegate','do','double','else','enum','event','explicit','extern',
        'false','finally','fixed','float','for','foreach','goto','if','implicit',
        'in','int','interface','internal','is','lock','long','namespace','new','null',
        'object','operator','out','override','params','private','protected','public',
        'readonly','ref','return','sbyte','dealed','short','sizeof','stackalloc',
        'static','string','struct','switch','this','throw','true','try','typeof',
        'uint','ulong','unchecked','unsafe','ushort','using','virtual','void','volatile','while'
        ]

    # C# operators
    operators = [
        '=','+','*','/','%','++','--'
        # Comparison
        '==', '!=', '<', '<=', '>', '>=',
        # Arithmetic
        '\+', '-', '\*', '/', '//', '\%', '\*\*',
        # In-place
        '\+=', '-=', '\*=', '/=', '\%=',
        # Bitwise
        '\^', '\|', '\&', '\~', '>>', '<<',
    ]

    # C# braces
    braces = [
        '\{', '\}', '\(', '\)', '\[', '\]',';',"\'",'\"']

    def __init__(self, document):
        QSyntaxHighlighter.__init__(self, document)

        # Multi-line strings (expression, flag, style)
        # FIXME: The triple-quotes in these two lines will mess up the
        # syntax highlighting from this point onward
        self.starting = (QRegExp("/\*"), 1, CSStyle['comment'])
        self.ending = (QRegExp("\*/"), 1, CSStyle['comment'])

        rules = []

        # Keyword, operator, and brace rules
        rules += [(r'\b%s\b' % w, 0, CSStyle['keyword'])
                  for w in CSharpHighlighter.keywords]
        rules += [(r'%s' % o, 0, CSStyle['operator'])
                  for o in CSharpHighlighter.operators]
        rules += [(r'%s' % b, 0, CSStyle['brace'])
                  for b in CSharpHighlighter.braces]
      

        # All other rules
        rules += [

            # Double-quoted string, possibly containing escape sequences
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, CSStyle['string']),
            # Single-quoted string, possibly containing escape sequences
            (r"'[^'\\]*(\\.[^'\\]*)*'", 0, CSStyle['string']),


            # From '//' until a newline or a group of lines between '\*' and '\*'
            (r'//[^\n]*', 0, CSStyle['comment']),
            (r'/\*[^"\\]*(\\.[^"\\]*)*\*/', 0, CSStyle['comment']),


            # Numeric literals
            (r'\b[+-]?[0-9]+[lL]?\b', 0, CSStyle['numbers']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, CSStyle['numbers']),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0, CSStyle['numbers']),
        ]

        # Build a QRegExp for each pattern
        self.rules = [(QRegExp(pat), index, fmt)
                      for (pat, index, fmt) in rules]

    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text.
        """
        # Do other syntax formatCS
        for expression, nth, format in self.rules:
            index = expression.indexIn(text, 0)

            while index >= 0:
                # We actually want the index of the nth match
                index = expression.pos(nth)
                length = len(expression.cap(nth))
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

        # Do multi-line strings
        #in_multiline = self.match_multiline(text, *self.tri_single)
        #if not in_multiline:
        self.match_multiline(text, *self.starting,*self.ending)

    def match_multiline(self, text, delimiter, in_state, style,delimiterEnd, in_stateEnd, styleEnd):
        
        # If inside triple-single quotes, start at 0
        if self.previousBlockState() == in_state:
            start = 0
            add = 0
        # Otherwise, look for the delimiter on this line
        else:
            
            start = delimiter.indexIn(text)
            # Move past this match
            add = delimiter.matchedLength()

        # As long as there's a delimiter match on this line...
        while start >= 0:
            # Look for the ending delimiter
            end = delimiterEnd.indexIn(text, start + add)
            # Ending delimiter on this line?
            if end >= add:
                length = end - start + add + delimiter.matchedLength()
                self.setCurrentBlockState(0)
            # No; multi-line string
            else:
                self.setCurrentBlockState(in_state)
                length = len(text) - start + add
            # Apply formatCS
            self.setFormat(start, length, style)
            # Look for the next match
            start = delimiterEnd.indexIn(text, start + length)

        # Return True if still inside a multi-line string, False otherwise
        if self.currentBlockState() == in_state:
            return True
        else:
            return False