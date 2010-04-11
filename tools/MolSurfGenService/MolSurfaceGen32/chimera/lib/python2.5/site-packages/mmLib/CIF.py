# CIF Parser for CIF 1.1 format

from mmCIF import mmCIFSyntaxError
class CIFSyntaxError(mmCIFSyntaxError):
    pass

#
# Lexical type constants
#
L_EOF = "<eof>"
L_DATA = "<data>"
L_LOOP = "<loop>"
L_STOP = "<stop>"
L_SAVE = "<save>"
L_GLOBAL = "<global>"
L_TAG = "<tag>"
L_VALUE = "<value>"

#
# Parser classes
#
class CIFFile:

    "Parser for reading a CIF 1.1 file."

    def __init__(self):
        self.data_blocks = []

    def load_file(self, f):
        import types
        if isinstance(f, types.StringTypes):
            name = f
            f = open(f)
            needClose = True
        else:
            name = "<input>"
            needClose = False
        try:
            self.parse(f, name)
        finally:
            if needClose:
                f.close()

    def parse(self, f, name):
        lexer = Lexer(f, name)
        token = lexer.next_token()
        while token.type is L_DATA:
            self.data_blocks.append(DataBlock(token.value, lexer, name))
            token = lexer.next_token()
        if token.type is not L_EOF:
            raise CIFSyntaxError(token.line, "input after data block")


class DataBlock:

    "CIF data block of tags and tables."

    def __init__(self, name, lexer, filename):
        self.name = name
        self.tags = {}
        self.tables = []
        self.save_frames = []

        token = lexer.next_token()
        while token.type is not L_EOF:
            if token.type is L_TAG:
                self.get_tag(token, lexer, filename)
            elif token.type is L_LOOP:
                self.get_table(token, lexer, filename)
            elif token.type is L_DATA:
                lexer.push_back(token)
                break
            elif token.type is L_SAVE:
                self.get_save_frame(token, lexer, filename)
            else:
                raise CIFSyntaxError(token.line, "unexpected %s(%s)" %
                                                    (token.type, token.value))
            token = lexer.next_token()

    def get_tag(self, token, lexer, filename):
        if '.' in token.value:
            raise CIFSyntaxError(token.line, "'.' appears in tag name %s" %
                                                token.value)
        name = token.value.lower()
        t = lexer.next_token()
        if t.type is not L_VALUE:
            raise CIFSyntaxError(token.line, "missing value for tag %s" %
                                                token.value)
        self.tags[name] = t.value

    def get_table(self, token, lexer, filename):
        self.tables.append(Table(lexer, filename))

    def get_save_frame(self, token, lexer, filename):
        raise CIFSyntaxError(token.line, "SaveFrame unimplemented")


class Table:

    "CIF data table."

    def __init__(self, lexer, filename):
        self.columns = []
        self.rows = []
        token = lexer.next_token()
        if token.type is not L_TAG:
            raise CIFSyntaxError(token.line, "missing tags for table")
        while token.type is L_TAG:
            self.columns.append(token.value.lower())
            token = lexer.next_token()
        if token.type is not L_VALUE:
            raise CIFSyntaxError(token.line, "missing rows for table")
        numColumns = len(self.columns)
        while token.type is L_VALUE:
            row = []
            for i in range(numColumns):
                if token.type is not L_VALUE:
                    raise CIFSyntaxError(token.line, "expected value and got %s"
                                                    % token.type)
                row.append(token.value)
                token = lexer.next_token()
            self.rows.append(row)
        lexer.push_back(token)
        self._columnIndex = {}
        for n, name in enumerate(self.columns):
            self._columnIndex[name] = n

    def get_value(self, column, row):
        n = self._columnIndex[column]
        r = self.rows[row]
        return r[n]


#
# Lexical analyzer classes
#
class Lexer:

    "Lexical analyzer for reading a CIF 1.1 file."

    def __init__(self, f, filename):
        self.f = f
        self.filename = filename
        self.prev_char = None
        self.cur_char = None
        self.peeked_char = None
        self.pushed_token = None
        self.line = 1

    def next_token(self):
        # Return any tokens from previous "push_back" calls
        if self.pushed_token is not None:
            t = self.pushed_token
            self.pushed_token = None
            return t

        from string import whitespace, digits
        while True:
            #
            # Skip over whitespaces
            #
            while True:
                c = self.next_char()
                if not c:
                    return self.token(L_EOF, None)
                if c not in whitespace:
                    break
            #
            # Check for comments
            #
            if c == '#':
                while True:
                    c = self.next_char()
                    if not c:
                        return self.token(L_EOF, None)
                    if c == '\n':
                        break
                # Start over with the next line
                continue
            #
            # Check for quoted strings
            #
            if c == "'" or c == '"':
                endQuote = c
                atEnd = False
                chars = []
                while True:
                    c = self.next_char()
                    if not c:
                        raise CIFSyntaxError(self.line,
                                "<eof> in quoted string")
                    if atEnd:
                        if c in whitespace:
                            return self.token(L_VALUE, ''.join(chars))
                        else:
                            chars.append(endQuote)
                            if c != endQuote:
                                chars.append(c)
                                atEnd = False
                    else:
                        if c == endQuote:
                            atEnd = True
                        else:
                            chars.append(c)
                            atEnd = False
            #
            # Check for (illegal) bracket string
            #
            if c == '[':
                raise CIFSyntaxError(self.line,
                        "bracket strings not permitted in CIF")
            #
            # Check for text field
            #
            if c == ';' and self.prev_char == '\n':
                chars = []
                atStart = False
                while True:
                    c = self.next_char()
                    if not c:
                        raise CIFSyntaxError(self.line, "<eof> in text field")
                    if c == ';' and atStart:
                        return self.token(L_VALUE, ''.join(chars))
                    if atStart:
                        chars.append('\n')
                    if c == '\n':
                        atStart = True
                    else:
                        chars.append(c)
                        atStart = False
            #
            # Check for tags
            #
            if c == '_':
                chars = []
                while True:
                    c = self.next_char()
                    if not c:
                        raise CIFSyntaxError(self.line, "<eof> in tag")
                    if c in whitespace:
                        return self.token(L_TAG, ''.join(chars))
                    chars.append(c)
            #
            # Check for simple values
            #
            if c == '?':
                return self.token(L_VALUE, c)
            if c == '.':
                if self.peek_char() in whitespace:
                    return self.token(L_VALUE, c)
            #
            # Get a value with no embedded whitespace
            #
            chars = [ c ]
            while True:
                c = self.next_char()
                if not c or c in whitespace:
                    break
                chars.append(c)
            data = ''.join(chars)
            lc = data.lower()
            if lc.startswith("data_"):
                return self.token(L_DATA, data[5:])
            elif lc.startswith("loop_"):
                return self.token(L_LOOP, data[5:])
            elif lc.startswith("save_"):
                return self.token(L_SAVE, data[5:])
            elif lc.startswith("stop_"):
                return self.token(L_STOP, data[5:])
            elif lc.startswith("global_"):
                return self.token(L_GLOBAL, data[5:])
            else:
                return self.token(L_VALUE, data)

    def next_char(self):
        if self.prev_char == '\n':
            self.line += 1
        self.prev_char = self.cur_char
        if self.peeked_char is None:
            self.cur_char = self.f.read(1)
        else:
            self.cur_char = self.peeked_char
            self.peeked_char = None
        return self.cur_char

    def peek_char(self):
        if self.peeked_char is None:
            self.peeked_char = self.f.read(1)
        return self.peeked_char

    def token(self, type, value):
        return Token(type, value, self.line)

    def push_back(self, token):
        assert(self.pushed_token is None)
        self.pushed_token = token

    def msg(self, s):
        return formatMessage(self.filename, self.line, s)


class Token:

    "Lexical token with type, value and line number."

    def __init__(self, type, value, line):
        self.type = type
        self.value = value
        self.line = line


#
# Utility functions
#
def formatMessage(filename, line, msg):
    return "%s(%d): %s" % (filename, line, msg)

def makeNumber(s):
    paren = s.find('(')         # ) for balance in vim
    if paren != -1:
        s = s[:paren]
    try:
        return int(s)
    except ValueError:
        return float(s)


#
# Module tests
#
if __name__ == "__main__":
        def lexer_test(test_file):
                f = open(test_file)
                lexer = Lexer(f, test_file)
                while True:
                        token = lexer.next_token()
                        if token.type is L_EOF:
                                break
                        print formatMessage(test_file, token.line,
                                        "%s: %s" % (token.type, token.value))
                f.close()

        def parser_test(test_file):
                cif = CIFFile()
                cif.load_file(test_file)
                print "%d data blocks" % len(cif.data_blocks)
                import pprint
                for db in cif.data_blocks:
                    print "%s: %d tags, %d tables" % (db.name,
                            len(db.tags), len(db.tables))
                    pprint.pprint(db.tags)

        #lexer_test("ccd.cif")
        parser_test("ccd.cif")
