from spark import GenericScanner, GenericParser, GenericASTTraversal

ExprLevel = [ "MOLECULE", "RESIDUE", "ATOM" ]

E_SCALAR = "scalar"
E_VECTOR = "vector"

S_ATOM = "ATOM"
S_RESIDUE = "RESIDUE"
S_MOLECULE = "MOLECULE"

class AST:
	def __init__(self, type, *args):
		self.type = type.type
		self.attr = type.attr
		self.children = args

	def __getitem__(self, i):
		return self.children[i]

	def __str__(self):
		if self.children:
			args = ", ".join([ str(c) for c in self.children ])
			return "%s{%s}(%s)" % (self.type, str(self.attr), args)
		else:
			return "%s{%s}" % (self.type, str(self.attr))

class Token:
	def __init__(self, type, attr=None):
		self.type = type
		self.attr = attr

	def __cmp__(self, o):
		return cmp(self.type, o)

	def __repr__(self):
		return "%s{%s}" % (self.type, str(self.attr))

class Scanner(GenericScanner):
	def tokenize(self, input):
		self.rv = []
		GenericScanner.tokenize(self, input)
		return self.rv

	def error(self, s, pos):
		raise ValueError, "Lexical error at position %s" % pos

	def t_whitespace(self, s):
		r' \s+ '
		pass

	def t_dot(self, s):
		r' \. '
		self.rv.append(Token(type="DOT", attr=s))

	def t_add(self, s):
		r' \+ '
		self.rv.append(Token(type="ADD", attr=s))

	def t_sub(self, s):
		r' \- '
		self.rv.append(Token(type="SUB", attr=s))

	def t_mul(self, s):
		r' \* '
		self.rv.append(Token(type="MUL", attr=s))

	def t_div(self, s):
		r' / '
		self.rv.append(Token(type="DIV", attr=s))

	def t_lp(self, s):
		r' \( '
		self.rv.append(Token(type="LP", attr=s))

	def t_rp(self, s):
		r' \) '
		self.rv.append(Token(type="RP", attr=s))

	def t_number_float(self, s):
		r' \d+ \. \d* '
		self.rv.append(Token(type="NUMBER", attr=float(s)))

	def t_number_int(self, s):
		r' \d+ '
		self.rv.append(Token(type="NUMBER", attr=float(s)))

	# keywords

	def t_id_atom(self, s):
		r' atom '
		self.rv.append(Token(type=S_ATOM, attr=s))

	def t_id_residue(self, s):
		r' residue '
		self.rv.append(Token(type=S_RESIDUE, attr=s))

	def t_id_molecule(self, s):
		r' molecule '
		self.rv.append(Token(type=S_MOLECULE, attr=s))

	def t_id_sum(self, s):
		r' sum '
		self.rv.append(Token(type="SUM", attr=s))

	def t_id_average(self, s):
		r' average '
		self.rv.append(Token(type="AVERAGE", attr=s))

	def t_identifier(self, s):
		r' [a-zA-Z_]\w* '
		self.rv.append(Token(type="IDENTIFIER", attr=s))

class Parser(GenericParser):
	def __init__(self, start="expr"):
		GenericParser.__init__(self, start)

	def error(self, token):
		raise SyntaxError, "Syntax error at or near `%s' token" % token

	def p_expr_1(self, args):
		' expr ::= term '
		return args[0]

	def p_expr_2(self, args):
		' expr ::= expr ADD term '
		return AST(args[1], args[0], args[2])

	def p_expr_3(self, args):
		' expr ::= expr SUB term '
		return AST(args[1], args[0], args[2])

	def p_term_1(self, args):
		' term ::= factor '
		return args[0]

	def p_term_2(self, args):
		' term ::= term MUL factor '
		return AST(args[1], args[0], args[2])

	def p_term_3(self, args):
		' term ::= term DIV factor '
		return AST(args[1], args[0], args[2])

	def p_factor_1(self, args):
		' factor ::= NUMBER '
		return AST(args[0])

	def p_factor_2(self, args):
		' factor ::= LP expr RP '
		return args[1]

	def p_factor_3(self, args):
		' factor ::= attribute '
		return args[0]

	def p_factor_4(self, args):
		' factor ::= func LP expr RP '
		return AST(args[0], args[2])

	def p_attribute(self, args):
		' attribute ::= scope DOT IDENTIFIER '
		return AST(args[1], AST(args[0]), AST(args[2]))

	def p_scope_1(self, args):
		' scope ::= ATOM '
		return args[0]

	def p_scope_2(self, args):
		' scope ::= RESIDUE '
		return args[0]

	def p_scope_3(self, args):
		' scope ::= MOLECULE '
		return args[0]

	def p_func_1(self, args):
		' func ::= SUM '
		return args[0]

	def p_func_2(self, args):
		' func ::= AVERAGE '
		return args[0]

class Evaluator(GenericASTTraversal):
	def __init__(self, ast):
		GenericASTTraversal.__init__(self, ast)
		self.errors = {}

	def evaluate(self, data):
		self.ast.value = None
		self.data = data
		self.postorder()
		value = self.ast.value
		del self.ast.value
		del self.data
		return value

	def logError(self, msg):
		try:
			self.errors[msg] += 1
		except KeyError:
			self.errors[msg] = 1

	def _functionCheck(self, node):
		if node.children[0].exprType is not E_VECTOR:
			raise TypeError, "expecting vector argument in function"
		node.exprType = E_SCALAR
	def n_SUM(self, node):
		self._functionCheck(node)
		vector = node.children[0].value
		sum = 0.0
		count = 0
		for v in vector:
			if v is not None:
				sum += v
				count += 1
		if count == 0:
			sum = None
			self.logError("sum over empty list")
		node.value = sum
	def n_AVERAGE(self, node):
		self._functionCheck(node)
		vector = node.children[0].value
		sum = 0.0
		count = 0
		for v in vector:
			if v is not None:
				sum += v
				count += 1
		if count == 0:
			avg = None
			self.logError("average over empty list")
		else:
			avg = sum / count
		node.value = avg

	def n_NUMBER(self, node):
		node.exprType = E_SCALAR
		node.value = node.attr

	def n_DOT(self, node):
		level = node.children[0]
		attr = node.children[1]
		try:
			node.value = self.data.getAttribute(level.type,
								attr.attr)
		except AttributeError:
			self.logError("missing %s attribute \"%s\""
					% (level.type, attr.attr))
			node.value = None
		if type(node.value) is type([]):
			node.exprType = E_VECTOR
		else:
			node.exprType = E_SCALAR

	def _termCheck(self, node):
		left = node.children[0]
		right = node.children[1]
		if left.exprType is not right.exprType:
			raise TypeError, ("incompatible arguments to %s"
						% node.type)
		node.exprType = left.exprType
	def n_ADD(self, node):
		self._termCheck(node)
		left = node.children[0]
		right = node.children[1]
		if left.exprType is E_SCALAR:
			node.value = self._add(left.value, right.value)
		else:
			node.value = [ self._add(l, r) for l, r in
						zip(left.value, right.value) ]
	def _add(self, left, right):
		try:
			return left + right
		except TypeError:
			return None
	def n_SUB(self, node):
		self._termCheck(node)
		left = node.children[0]
		right = node.children[1]
		if left.exprType is E_SCALAR:
			node.value = self._sub(left.value, right.value)
		else:
			node.value = [ self._sub(l, r) for l, r in
						zip(left.value, right.value) ]
	def _sub(self, left, right):
		try:
			return left - right
		except TypeError:
			return None

	def n_MUL(self, node):
		left = node.children[0]
		right = node.children[1]
		if (left.exprType is not E_SCALAR
		and right.exprType is not E_SCALAR):
			raise TypeError, "cannot MUL two non-scalars"
		if left.exprType is E_SCALAR:
			if right.exprType is E_SCALAR:
				node.exprType = E_SCALAR
				node.value = self._mul(left.value, right.value)
			elif right.exprType is E_VECTOR:
				node.exprType = E_VECTOR
				scale = left.value
				node.value = [ self._mul(scale, v)
						for v in right.value ]
			else:
				raise TypeError, ("bad right MUL operand `%s'"
							% right.exprType)
		elif left.exprType is E_VECTOR:
			node.exprType = E_VECTOR
			scale = right.value
			node.value = [ self._mul(scale, v) for v in left.value ]
		else:
			raise TypeError, ("bad left MUL operand `%s'"
						% left.exprType)
	def _mul(self, left, right):
		try:
			return left * right
		except TypeError:
			return None
	def n_DIV(self, node):
		left = node.children[0]
		right = node.children[1]
		if right.exprType is not E_SCALAR:
			raise TypeError, "RHS of DIV must be scalar"
		node.exprType = left.exprType
		denom = right.value
		if denom == 0.0:
			self.logError("division by zero")
			node.value = None
			return
		if left.exprType is E_SCALAR:
			node.value = self._div(left.value, denom)
		elif left.exprType is E_VECTOR:
			denom = right.value
			node.value = [ self._div(v, denom) for v in left.value ]
		else:
			raise TypeError, ("bad left DIV operand `%s'"
						% left.exprType)
	def _div(self, left, right):
		try:
			return left / right
		except TypeError:
			return None

	def _noop(self, node):
		pass
	n_ATOM = _noop
	n_RESIDUE = _noop
	n_MOLECULE = _noop
	n_IDENTIFIER = _noop

	def default(self, node):
		print >> sys.stderr, node.type

class TypeChecker(GenericASTTraversal):
	def __init__(self, ast, context):
		GenericASTTraversal.__init__(self, ast)
		self.context = context
		self.contextLevel = ExprLevel.index(context)
		self.postorder()

	def _functionCheck(self, node):
		if node.children[0].exprType is not E_VECTOR:
			raise TypeError, "expecting vector argument in function"
		node.exprType = E_SCALAR
	n_SUM = _functionCheck
	n_AVERAGE = _functionCheck

	def n_NUMBER(self, node):
		node.exprType = E_SCALAR

	def n_DOT(self, node):
		exprLevel = ExprLevel.index(node.children[0].type)
		if exprLevel > self.contextLevel:
			node.exprType = E_VECTOR
		else:
			node.exprType = E_SCALAR

	def _termCheck(self, node):
		left = node.children[0]
		right = node.children[1]
		if left.exprType is not right.exprType:
			raise TypeError, ("incompatible arguments to %s"
						% node.type)
		node.exprType = left.exprType
	n_ADD = _termCheck
	n_SUB = _termCheck

	def _factorCheck(self, node):
		left = node.children[0]
		right = node.children[1]
		if right.exprType is not E_SCALAR:
			raise TypeError, "RHS of %s must be scalar" % node.type
		node.exprType = left.exprType
	n_MUL = _factorCheck
	n_DIV = _factorCheck

	def _noop(self, node):
		pass
	n_ATOM = _noop
	n_RESIDUE = _noop
	n_MOLECULE = _noop
	n_IDENTIFIER = _noop

	def default(self, node):
		print >> sys.stderr, node.type

if __name__ == "__main__":
	import sys, traceback
	testScanner = 1
	testParser = 0
	context = "RESIDUE"
	def scannerTest():
		scanner = Scanner()
		while 1:
			sys.stdout.write("Expression: ")
			sys.stdout.flush()
			line = sys.stdin.readline()
			if not line:
				break
			try:
				for t in scanner.tokenize(line):
					print t.type, t.attr
			except ValueError, s:
				print >> sys.stderr, s
	def parserTest(context):
		parser = Parser()
		scanner = Scanner()
		while 1:
			sys.stdout.write("Expression: ")
			sys.stdout.flush()
			line = sys.stdin.readline()
			if not line:
				break
			try:
				ast = parser.parse(scanner.tokenize(line))
			except SyntaxError, s:
				print >> sys.stderr, s
				continue
			if context:
				try:
					#TypeChecker(ast, context)
					v = Evaluator(ast).evaluate(context)
				except (ValueError, TypeError), s:
					print >> sys.stderr, s
				else:
					print "Value:", v
			print ast
	if testScanner:
		scannerTest()
	if testParser:
		parserTest(context)
