from __future__ import generators
from rdflib import BNode
from rdflib import RDF
from rdflib.Literal import Literal
from rdflib.URIRef import URIRef
from rdflib.BNode import BNode
from pprint import pprint
import sha,sys, weakref
from rdflib.term_utils import *
from rdflib.Graph import QuotedGraph
from rdflib.store.REGEXMatching import REGEXTerm, PYTHON_REGEX
from rdflib.store import Store
Any = None

COUNT_SELECT   = 0
CONTEXT_SELECT = 1
TRIPLE_SELECT  = 2
TRIPLE_SELECT_NO_ORDER = 3

ASSERTED_NON_TYPE_PARTITION = 3
ASSERTED_TYPE_PARTITION     = 4
QUOTED_PARTITION            = 5
ASSERTED_LITERAL_PARTITION  = 6

FULL_TRIPLE_PARTITIONS = [QUOTED_PARTITION,ASSERTED_LITERAL_PARTITION]

INTERNED_PREFIX = 'kb_'

#Helper function for executing EXPLAIN on all dispatched SQL statements - for the pupose of analyzing
#index usage
def queryAnalysis(query,store,cursor):
    cursor.execute(store._normalizeSQLCmd('explain '+query))
    rt=cursor.fetchall()[0]
    table,joinType,posKeys,_key,key_len,comparedCol,rowsExamined,extra = rt
    if not _key:
        assert joinType == 'ALL'
        if not hasattr(store,'queryOptMarks'):
            store.queryOptMarks = {}
        hits = store.queryOptMarks.get(('FULL SCAN',table),0)
        store.queryOptMarks[('FULL SCAN',table)] = hits + 1

    if not hasattr(store,'queryOptMarks'):
        store.queryOptMarks = {}
    hits = store.queryOptMarks.get((_key,table),0)
    store.queryOptMarks[(_key,table)] = hits + 1


#Terms: u - uri refs  v - variables  b - bnodes l - literal f - formula

#Helper function for building union all select statement
#Takes a list of:
# - table name
# - table alias
# - table type (literal, type, asserted, quoted)
# - where clause string
def unionSELECT(selectComponents,distinct=False,selectType=TRIPLE_SELECT):
    selects = []
    for tableName,tableAlias,whereClause,tableType in selectComponents:

        if selectType == COUNT_SELECT:
            selectString = "select count(*)"
            tableSource = " from %s "%tableName
        elif selectType == CONTEXT_SELECT:
            selectString = "select %s.context"%tableAlias
            tableSource = " from %s as %s "%(tableName,tableAlias)
        elif tableType in FULL_TRIPLE_PARTITIONS:
            selectString = "select *"#%(tableAlias)
            tableSource = " from %s as %s "%(tableName,tableAlias)
        elif tableType == ASSERTED_TYPE_PARTITION:
            selectString =\
            """select %s.member as subject, "%s" as predicate, %s.klass as object, %s.context as context, %s.termComb as termComb, NULL as objLanguage, NULL as objDatatype"""%(tableAlias,RDF.type,tableAlias,tableAlias,tableAlias)
            tableSource = " from %s as %s "%(tableName,tableAlias)
        elif tableType == ASSERTED_NON_TYPE_PARTITION:
            selectString =\
            """select *,NULL as objLanguage, NULL as objDatatype"""
            tableSource = " from %s as %s "%(tableName,tableAlias)

        #selects.append('('+selectString + tableSource + whereClause+')')
        selects.append(selectString + tableSource + whereClause)

    orderStmt = ''
    if selectType == TRIPLE_SELECT:
        orderStmt = ' order by subject,predicate,object'
    if distinct:
        return ' union '.join(selects) + orderStmt
    else:
        return ' union all '.join(selects) + orderStmt

#Takes a tuple which represents an entry in a result set and
#converts it to a tuple of terms using the termComb integer
#to interpret how to instanciate each term
def extractTriple(tupleRt,store,hardCodedContext=None):
    subject,predicate,obj,rtContext,termComb,objLanguage,objDatatype = tupleRt
    context = rtContext is not None and rtContext or hardCodedContext.identifier
    termCombString=REVERSE_TERM_COMBINATIONS[termComb]
    subjTerm,predTerm,objTerm,ctxTerm = termCombString

    s=createTerm(subject,subjTerm,store)
    p=createTerm(predicate,predTerm,store)
    o=createTerm(obj,objTerm,store,objLanguage,objDatatype)

    graphKlass, idKlass = constructGraph(ctxTerm)
    return s,p,o,(graphKlass,idKlass,context)
#TODO: Stuff
#Takes a term value, term type, and store intance
#and Creates a term object.  QuotedGraphs are instanciated differently
def createTerm(termString,termType,store,objLanguage=None,objDatatype=None):
    if termType == 'L':
        cache = store.literalCache.get((termString,objLanguage,objDatatype))
        if cache is not None:
            #store.cacheHits += 1
            return cache
        else:
            #store.cacheMisses += 1
            rt = Literal(termString,objLanguage,objDatatype)
            store.literalCache[((termString,objLanguage,objDatatype))] = rt
            return rt
    elif termType=='F':
        cache = store.otherCache.get((termType,termString))
        if cache is not None:
            #store.cacheHits += 1
            return cache
        else:
            #store.cacheMisses += 1
            rt = QuotedGraph(store,URIRef(termString))
            store.otherCache[(termType,termString)] = rt
            return rt
    elif termType == 'B':
        cache = store.bnodeCache.get((termString))
        if cache is not None:
            #store.cacheHits += 1
            return cache
        else:
            #store.cacheMisses += 1
            rt = TERM_INSTANCIATION_DICT[termType](termString)
            store.bnodeCache[(termString)] = rt
            return rt
    elif termType =='U':
        cache = store.uriCache.get((termString))
        if cache is not None:
            #store.cacheHits += 1
            return cache
        else:
            #store.cacheMisses += 1
            rt = URIRef(termString)
            store.uriCache[(termString)] = rt
            return rt
    else:
        cache = store.otherCache.get((termType,termString))
        if cache is not None:
            #store.cacheHits += 1
            return cache
        else:
            #store.cacheMisses += 1
            rt = TERM_INSTANCIATION_DICT[termType](termString)
            store.otherCache[(termType,termString)] = rt
            return rt

class SQLGenerator:
    def executeSQL(self,cursor,qStr,params=None,paramList=False):
        """
        This takes the query string and parameters and (depending on the SQL implementation) either fill in
        the parameter in-place or pass it on to the Python DB impl (if it supports this).
        The default (here) is to fill the parameters in-place surrounding each param with quote characters
        """
        #print qStr,params
        if not params:
            cursor.execute(unicode(qStr))
        elif paramList:
            raise Exception("Not supported!")
        else:
            params = tuple([not isinstance(item,int) and u'"%s"'%item or item for item in params])
            cursor.execute(qStr%params)

    #FIXME:  This *may* prove to be a performance bottleneck and should perhaps be implemented in C (as it was in 4Suite RDF)
    def EscapeQuotes(self,qstr):
        """
        Ported from Ft.Lib.DbUtil
        """
        if qstr is None:
            return ''
        tmp = qstr.replace("\\","\\\\")
        tmp = tmp.replace("'", "\\'")
        return tmp

    #Normalize a SQL command before executing it.  Commence unicode black magic
    def _normalizeSQLCmd(self,cmd):
        import types
        if not isinstance(cmd, types.UnicodeType):
            cmd = unicode(cmd, 'ascii')

        return cmd.encode('utf-8')

    #Takes a term and 'normalizes' it.
    #Literals are escaped, Graphs are replaced with just their identifiers
    def normalizeTerm(self,term):
        if isinstance(term,(QuotedGraph,Graph)):
            return term.identifier.encode('utf-8')
        elif isinstance(term,Literal):
            return self.EscapeQuotes(term).encode('utf-8')
        elif term is None or isinstance(term,(list,REGEXTerm)):
            return term
        else:
            return term.encode('utf-8')

    #Builds an insert command for a type table
    def buildTypeSQLCommand(self,member,klass,context,storeId):
        #columns: member,klass,context
        rt= "INSERT INTO %s_type_statements"%storeId + " VALUES (%s, %s, %s,%s)"
        return rt,[
            self.normalizeTerm(member),
            self.normalizeTerm(klass),
            self.normalizeTerm(context.identifier),
            int(type2TermCombination(member,klass,context))]

    #Builds an insert command for literal triples (statements where the object is a Literal)
    def buildLiteralTripleSQLCommand(self,subject,predicate,obj,context,storeId):
        triplePattern = int(statement2TermCombination(subject,predicate,obj,context))
        literal_table = "%s_literal_statements"%storeId
        command="INSERT INTO %s "%literal_table +"VALUES (%s, %s, %s, %s, %s,%s,%s)"
        return command,[
            self.normalizeTerm(subject),
            self.normalizeTerm(predicate),
            self.normalizeTerm(obj),
            self.normalizeTerm(context.identifier),
            triplePattern,
            isinstance(obj,Literal) and obj.language or 'NULL',
            isinstance(obj,Literal) and obj.datatype or 'NULL']

    #Builds an insert command for regular triple table
    def buildTripleSQLCommand(self,subject,predicate,obj,context,storeId,quoted):
        stmt_table = quoted and "%s_quoted_statements"%storeId or "%s_asserted_statements"%storeId
        triplePattern = statement2TermCombination(subject,predicate,obj,context)
        if quoted:
            command="INSERT INTO %s"%stmt_table +" VALUES (%s, %s, %s, %s, %s,%s,%s)"
            params = [
                self.normalizeTerm(subject),
                self.normalizeTerm(predicate),
                self.normalizeTerm(obj),
                self.normalizeTerm(context.identifier),
                triplePattern,
                isinstance(obj,Literal) and  obj.language or 'NULL',
                isinstance(obj,Literal) and obj.datatype or 'NULL']
        else:
            command="INSERT INTO %s"%stmt_table + " VALUES (%s, %s, %s, %s, %s)"
            params = [
                self.normalizeTerm(subject),
                self.normalizeTerm(predicate),
                self.normalizeTerm(obj),
                self.normalizeTerm(context.identifier),
                triplePattern]
        return command,params

    #Builds WHERE clauses for the supplied terms and, context
    def buildClause(self,tableName,subject,predicate, obj,context=None,typeTable=False):
        parameters=[]
        if typeTable:
            rdf_type_memberClause = rdf_type_contextClause = rdf_type_contextClause = None

            clauseParts = self.buildTypeMemberClause(self.normalizeTerm(subject),tableName)
            if clauseParts is not None:
                rdf_type_memberClause = clauseParts[0]
                parameters.extend([param for param in clauseParts[-1] if param])

            clauseParts = self.buildTypeClassClause(self.normalizeTerm(obj),tableName)
            if clauseParts is not None:
                rdf_type_klassClause = clauseParts[0]
                parameters.extend(clauseParts[-1])

            clauseParts = self.buildContextClause(context,tableName)
            if clauseParts is not None:
                rdf_type_contextClause = clauseParts[0]
                parameters.extend([param for param in clauseParts[-1] if param])

            typeClauses = [rdf_type_memberClause,rdf_type_klassClause,rdf_type_contextClause]
            clauseString = ' and '.join([clause for clause in typeClauses if clause])
            clauseString = clauseString and 'where '+clauseString or ''
        else:
            subjClause = predClause = objClause = contextClause = litDTypeClause = litLanguageClause = None

            clauseParts = self.buildSubjClause(self.normalizeTerm(subject),tableName)
            if clauseParts is not None:
                subjClause = clauseParts[0]
                parameters.extend([param for param in clauseParts[-1] if param])

            clauseParts = self.buildPredClause(self.normalizeTerm(predicate),tableName)
            if clauseParts is not None:
                predClause = clauseParts[0]
                parameters.extend([param for param in clauseParts[-1] if param])

            clauseParts = self.buildObjClause(self.normalizeTerm(obj),tableName)
            if clauseParts is not None:
                objClause = clauseParts[0]
                parameters.extend([param for param in clauseParts[-1] if param])

            clauseParts = self.buildContextClause(context,tableName)
            if clauseParts is not None:
                contextClause = clauseParts[0]
                parameters.extend([param for param in clauseParts[-1] if param])

            clauseParts = self.buildLitDTypeClause(obj,tableName)
            if clauseParts is not None:
                litDTypeClause = clauseParts[0]
                parameters.extend([param for param in clauseParts[-1] if param])

            clauseParts = self.buildLitLanguageClause(obj,tableName)
            if clauseParts is not None:
                litLanguageClause = clauseParts[0]
                parameters.extend([param for param in clauseParts[-1] if param])

            clauses=[subjClause,predClause,objClause,contextClause,litDTypeClause,litLanguageClause]
            clauseString = ' and '.join([clause for clause in clauses if clause])
            clauseString = clauseString and 'where '+clauseString or ''

        return clauseString, [p for p in parameters if p]

    def buildLitDTypeClause(self,obj,tableName):
        if isinstance(obj,Literal):
            return obj.datatype is not None and ("%s.objDatatype="%(tableName)+"%s",[obj.datatype.encode('utf-8')]) or None
        else:
            return None

    def buildLitLanguageClause(self,obj,tableName):
        if isinstance(obj,Literal):
            return obj.language is not None and ("%s.objLanguage="%(tableName)+"%s",[obj.language.encode('utf-8')]) or None
        else:
            return None

    #Stubs for Clause Functions that are overridden by specific implementations (MySQL vs SQLite for instance)
    def buildSubjClause(self,subject,tableName):
        pass
    def buildPredClause(self,predicate,tableName):
        pass
    def buildObjClause(self,obj,tableName):
        pass
    def buildContextClause(self,context,tableName):
        pass
    def buildTypeMemberClause(self,subject,tableName):
        pass
    def buildTypeClassClause(self,obj,tableName):
        pass

class AbstractSQLStore(SQLGenerator,Store):
    """
    SQL-92 formula-aware implementation of an rdflib Store.
    It stores it's triples in the following partitions:

    - Asserted non rdf:type statements
    - Asserted literal statements
    - Asserted rdf:type statements (in a table which models Class membership)
    The motivation for this partition is primarily query speed and scalability as most graphs will always have more rdf:type statements than others
    - All Quoted statements

    In addition it persists namespace mappings in a seperate table
    """
    context_aware = True
    formula_aware = True
    transaction_aware = True
    regex_matching = PYTHON_REGEX
    autocommit_default = True

    #Stubs for overidden

    def __init__(self, identifier=None, configuration=None):
        """
        identifier: URIRef of the Store. Defaults to CWD
        configuration: string containing infomation open can use to
        connect to datastore.
        """
        self.identifier = identifier and identifier or 'hardcoded'
        #Use only the first 10 bytes of the digest
        self._internedId = INTERNED_PREFIX + sha.new(self.identifier).hexdigest()[:10]

        #This parameter controls how exlusively the literal table is searched
        #If true, the Literal partition is searched *exclusively* if the object term
        #in a triple pattern is a Literal or a REGEXTerm.  Note, the latter case
        #prevents the matching of URIRef nodes as the objects of a triple in the store.
        #If the object term is a wildcard (None)
        #Then the Literal paritition is searched in addition to the others
        #If this parameter is false, the literal partition is searched regardless of what the object
        #of the triple pattern is
        self.STRONGLY_TYPED_TERMS = False

        if configuration is not None:
            self.open(configuration)

        self.cacheHits = 0
        self.cacheMisses = 0

        self.literalCache = {}
        self.uriCache = {}
        self.bnodeCache = {}
        self.otherCache = {}
        self._db = None

    def close(self, commit_pending_transaction=False):
        """
        FIXME:  Add documentation!!
        """
        if commit_pending_transaction:
            self._db.commit()
        self._db.close()

    #Triple Methods
    def add(self, (subject, predicate, obj), context=None, quoted=False):
        """ Add a triple to the store of triples. """
        c=self._db.cursor()
        if self.autocommit_default:
            c.execute("""SET AUTOCOMMIT=0""")
        if quoted or predicate != RDF.type:
            #quoted statement or non rdf:type predicate
            #check if object is a literal
            if isinstance(obj,Literal):
                addCmd,params=self.buildLiteralTripleSQLCommand(subject,predicate,obj,context,self._internedId)
            else:
                addCmd,params=self.buildTripleSQLCommand(subject,predicate,obj,context,self._internedId,quoted)
        elif predicate == RDF.type:
            #asserted rdf:type statement
            addCmd,params=self.buildTypeSQLCommand(subject,obj,context,self._internedId)
        self.executeSQL(c,addCmd,params)
        c.close()

    def addN(self,quads):
        c=self._db.cursor()
        if self.autocommit_default:
            c.execute("""SET AUTOCOMMIT=0""")
        literalTriples = []
        typeTriples = []
        otherTriples = []
        literalTripleInsertCmd = None
        typeTripleInsertCmd = None
        otherTripleInsertCmd = None
        for subject,predicate,obj,context in quads:
            if isinstance(context,QuotedGraph) or predicate != RDF.type:
                #quoted statement or non rdf:type predicate
                #check if object is a literal
                if isinstance(obj,Literal):
                    cmd,params=self.buildLiteralTripleSQLCommand(subject,predicate,obj,context,self._internedId)
                    literalTripleInsertCmd = literalTripleInsertCmd is not None and literalTripleInsertCmd or cmd
                    literalTriples.append(params)
                else:
                    cmd,params=self.buildTripleSQLCommand(subject,predicate,obj,context,self._internedId,isinstance(context,QuotedGraph))
                    otherTripleInsertCmd = otherTripleInsertCmd is not None and otherTripleInsertCmd or cmd
                    otherTriples.append(params)
            elif predicate == RDF.type:
                #asserted rdf:type statement
                cmd,params=self.buildTypeSQLCommand(subject,obj,context,self._internedId)
                typeTripleInsertCmd = typeTripleInsertCmd is not None and typeTripleInsertCmd or cmd
                typeTriples.append(params)

        if literalTriples:
            self.executeSQL(c,literalTripleInsertCmd,literalTriples,paramList=True)
        if typeTriples:
            self.executeSQL(c,typeTripleInsertCmd,typeTriples,paramList=True)
        if otherTriples:
            self.executeSQL(c,otherTripleInsertCmd,otherTriples,paramList=True)

        c.close()

    def remove(self, (subject, predicate, obj), context):
        """ Remove a triple from the store """
        if context is not None:
            if subject is None and predicate is None and object is None:
                self._remove_context(context)
                return
        c=self._db.cursor()
        if self.autocommit_default:
            c.execute("""SET AUTOCOMMIT=0""")
        quoted_table="%s_quoted_statements"%self._internedId
        asserted_table="%s_asserted_statements"%self._internedId
        asserted_type_table="%s_type_statements"%self._internedId
        literal_table = "%s_literal_statements"%self._internedId
        if not predicate or predicate != RDF.type:
            #Need to remove predicates other than rdf:type

            if not self.STRONGLY_TYPED_TERMS or isinstance(obj,Literal):
                #remove literal triple
                clauseString,params = self.buildClause(literal_table,subject,predicate, obj,context)
                if clauseString:
                    cmd ="DELETE FROM " + " ".join([literal_table,clauseString])
                else:
                    cmd ="DELETE FROM " + literal_table
                self.executeSQL(c,self._normalizeSQLCmd(cmd),params)

            for table in [quoted_table,asserted_table]:
                #If asserted non rdf:type table and obj is Literal, don't do anything (already taken care of)
                if table == asserted_table and isinstance(obj,Literal):
                    continue
                else:
                    clauseString,params = self.buildClause(table,subject,predicate,obj,context)
                    if clauseString:
                        cmd="DELETE FROM " + " ".join([table,clauseString])
                    else:
                        cmd = "DELETE FROM " + table

                    self.executeSQL(c,self._normalizeSQLCmd(cmd),params)

        if predicate == RDF.type or not predicate:
            #Need to check rdf:type and quoted partitions (in addition perhaps)
            clauseString,params = self.buildClause(asserted_type_table,subject,RDF.type,obj,context,True)
            if clauseString:
                cmd="DELETE FROM " + " ".join([asserted_type_table,clauseString])
            else:
                cmd='DELETE FROM '+asserted_type_table

            self.executeSQL(c,self._normalizeSQLCmd(cmd),params)

            clauseString,params = self.buildClause(quoted_table,subject,predicate, obj,context)
            if clauseString:
                cmd=clauseString and "DELETE FROM " + " ".join([quoted_table,clauseString])
            else:
                cmd = "DELETE FROM " + quoted_table

            self.executeSQL(c,self._normalizeSQLCmd(cmd),params)
        c.close()

    def triples(self, (subject, predicate, obj), context=None):
        """
        A generator over all the triples matching pattern. Pattern can
        be any objects for comparing against nodes in the store, for
        example, RegExLiteral, Date? DateRange?

        quoted table:                <id>_quoted_statements
        asserted rdf:type table:     <id>_type_statements
        asserted non rdf:type table: <id>_asserted_statements

        triple columns: subject,predicate,object,context,termComb,objLanguage,objDatatype
        class membership columns: member,klass,context termComb

        FIXME:  These union all selects *may* be further optimized by joins

        """
        quoted_table="%s_quoted_statements"%self._internedId
        asserted_table="%s_asserted_statements"%self._internedId
        asserted_type_table="%s_type_statements"%self._internedId
        literal_table = "%s_literal_statements"%self._internedId
        c=self._db.cursor()

        parameters = []

        if predicate == RDF.type:
            #select from asserted rdf:type partition and quoted table (if a context is specified)
            clauseString,params = self.buildClause('typeTable',subject,RDF.type, obj,context,True)
            parameters.extend(params)
            selects = [
                (
                  asserted_type_table,
                  'typeTable',
                  clauseString,
                  ASSERTED_TYPE_PARTITION
                ),
            ]

        elif isinstance(predicate,REGEXTerm) and predicate.compiledExpr.match(RDF.type) or not predicate:
            #Select from quoted partition (if context is specified), literal partition if (obj is Literal or None) and asserted non rdf:type partition (if obj is URIRef or None)
            selects = []
            if not self.STRONGLY_TYPED_TERMS or isinstance(obj,Literal) or not obj or (self.STRONGLY_TYPED_TERMS and isinstance(obj,REGEXTerm)):
                clauseString,params = self.buildClause('literal',subject,predicate,obj,context)
                parameters.extend(params)
                selects.append((
                  literal_table,
                  'literal',
                  clauseString,
                  ASSERTED_LITERAL_PARTITION
                ))
            if not isinstance(obj,Literal) and not (isinstance(obj,REGEXTerm) and self.STRONGLY_TYPED_TERMS) or not obj:
                clauseString,params = self.buildClause('asserted',subject,predicate,obj,context)
                parameters.extend(params)
                selects.append((
                  asserted_table,
                  'asserted',
                  clauseString,
                  ASSERTED_NON_TYPE_PARTITION
                ))

            clauseString,params = self.buildClause('typeTable',subject,RDF.type,obj,context,True)
            parameters.extend(params)
            selects.append(
                (
                  asserted_type_table,
                  'typeTable',
                  clauseString,
                  ASSERTED_TYPE_PARTITION
                )
            )


        elif predicate:
            #select from asserted non rdf:type partition (optionally), quoted partition (if context is speciied), and literal partition (optionally)
            selects = []
            if not self.STRONGLY_TYPED_TERMS or isinstance(obj,Literal) or not obj or (self.STRONGLY_TYPED_TERMS and isinstance(obj,REGEXTerm)):
                clauseString,params = self.buildClause('literal',subject,predicate,obj,context)
                parameters.extend(params)
                selects.append((
                  literal_table,
                  'literal',
                  clauseString,
                  ASSERTED_LITERAL_PARTITION
                ))
            if not isinstance(obj,Literal) and not (isinstance(obj,REGEXTerm) and self.STRONGLY_TYPED_TERMS) or not obj:
                clauseString,params = self.buildClause('asserted',subject,predicate,obj,context)
                parameters.extend(params)
                selects.append((
                  asserted_table,
                  'asserted',
                  clauseString,
                  ASSERTED_NON_TYPE_PARTITION
                ))

        if context is not None:
            clauseString,params = self.buildClause('quoted',subject,predicate, obj,context)
            parameters.extend(params)
            selects.append(
                (
                  quoted_table,
                  'quoted',
                  clauseString,
                  QUOTED_PARTITION
                )
            )


        q=self._normalizeSQLCmd(unionSELECT(selects))
        self.executeSQL(c,q,parameters)
        rt = c.fetchone()
        while rt:
            s,p,o,(graphKlass,idKlass,graphId) = extractTriple(rt,self,context)
            currentContext=graphKlass(self,idKlass(graphId))
            contexts = [currentContext]
            rt = next = c.fetchone()
            sameTriple = next and extractTriple(next,self,context)[:3] == (s,p,o)
            while sameTriple:
                s2,p2,o2,(graphKlass,idKlass,graphId) = extractTriple(next,self,context)
                c2 = graphKlass(self,idKlass(graphId))
                contexts.append(c2)
                rt = next = c.fetchone()
                sameTriple = next and extractTriple(next,self,context)[:3] == (s,p,o)

            yield (s,p,o),(c for c in contexts)

    def triples_choices(self, (subject, predicate, object_),context=None):
        """
        A variant of triples that can take a list of terms instead of a single
        term in any slot.  Stores can implement this to optimize the response time
        from the import default 'fallback' implementation, which will iterate
        over each term in the list and dispatch to tripless
        """
        if isinstance(object_,list):
            assert not isinstance(subject,list), "object_ / subject are both lists"
            assert not isinstance(predicate,list), "object_ / predicate are both lists"
            if not object_:
                object_ = None
            for (s1, p1, o1), cg in self.triples((subject,predicate,object_),context):
                yield (s1, p1, o1), cg

        elif isinstance(subject,list):
            assert not isinstance(predicate,list), "subject / predicate are both lists"
            if not subject:
                subject = None
            for (s1, p1, o1), cg in self.triples((subject,predicate,object_),context):
                yield (s1, p1, o1), cg

        elif isinstance(predicate,list):
            assert not isinstance(subject,list), "predicate / subject are both lists"
            if not predicate:
                predicate = None
            for (s1, p1, o1), cg in self.triples((subject,predicate,object_),context):
                yield (s1, p1, o1), cg


    def __repr__(self):
        c=self._db.cursor()
        quoted_table="%s_quoted_statements"%self._internedId
        asserted_table="%s_asserted_statements"%self._internedId
        asserted_type_table="%s_type_statements"%self._internedId
        literal_table = "%s_literal_statements"%self._internedId

        selects = [
            (
              asserted_type_table,
              'typeTable',
              '',
              ASSERTED_TYPE_PARTITION
            ),
            (
              quoted_table,
              'quoted',
              '',
              QUOTED_PARTITION
            ),
            (
              asserted_table,
              'asserted',
              '',
              ASSERTED_NON_TYPE_PARTITION
            ),
            (
              literal_table,
              'literal',
              '',
              ASSERTED_LITERAL_PARTITION
            ),
        ]
        q=unionSELECT(selects,distinct=False,selectType=COUNT_SELECT)
        self.executeSQL(c,self._normalizeSQLCmd(q))
        rt=c.fetchall()
        typeLen,quotedLen,assertedLen,literalLen = [rtTuple[0] for rtTuple in rt]
        return "<Parititioned MySQL N3 Store: %s contexts, %s classification assertions, %s quoted statements, %s property/value assertions, and %s other assertions>"%(len([c for c in self.contexts()]),typeLen,quotedLen,literalLen,assertedLen)

    def __len__(self, context=None):
        """ Number of statements in the store. """
        c=self._db.cursor()
        quoted_table="%s_quoted_statements"%self._internedId
        asserted_table="%s_asserted_statements"%self._internedId
        asserted_type_table="%s_type_statements"%self._internedId
        literal_table = "%s_literal_statements"%self._internedId

        parameters = []
        quotedContext = assertedContext = typeContext = literalContext = None

        clauseParts = self.buildContextClause(context,quoted_table)
        if clauseParts:
            quotedContext,params = clauseParts
            parameters.extend([p for p in params if p])

        clauseParts = self.buildContextClause(context,asserted_table)
        if clauseParts:
            assertedContext,params = clauseParts
            parameters.extend([p for p in params if p])

        clauseParts = self.buildContextClause(context,asserted_type_table)
        if clauseParts:
            typeContext ,params = clauseParts
            parameters.extend([p for p in params if p])

        clauseParts = self.buildContextClause(context,literal_table)
        if clauseParts:
            literalContext,params = clauseParts
            parameters.extend([p for p in params if p])

        if context is not None:
            selects = [
                (
                  asserted_type_table,
                  'typeTable',
                  typeContext and 'where ' + typeContext or '',
                  ASSERTED_TYPE_PARTITION
                ),
                (
                  quoted_table,
                  'quoted',
                  quotedContext and 'where ' + quotedContext or '',
                  QUOTED_PARTITION
                ),
                (
                  asserted_table,
                  'asserted',
                  assertedContext and 'where ' + assertedContext or '',
                  ASSERTED_NON_TYPE_PARTITION
                ),
                (
                  literal_table,
                  'literal',
                  literalContext and 'where ' + literalContext or '',
                  ASSERTED_LITERAL_PARTITION
                ),
            ]
            q=unionSELECT(selects,distinct=True,selectType=COUNT_SELECT)
        else:
            selects = [
                (
                  asserted_type_table,
                  'typeTable',
                  typeContext and 'where ' + typeContext or '',
                  ASSERTED_TYPE_PARTITION
                ),
                (
                  asserted_table,
                  'asserted',
                  assertedContext and 'where ' + assertedContext or '',
                  ASSERTED_NON_TYPE_PARTITION
                ),
                (
                  literal_table,
                  'literal',
                  literalContext and 'where ' + literalContext or '',
                  ASSERTED_LITERAL_PARTITION
                ),
            ]
            q=unionSELECT(selects,distinct=False,selectType=COUNT_SELECT)

        self.executeSQL(c,self._normalizeSQLCmd(q),parameters)
        rt=c.fetchall()
        c.close()
        return reduce(lambda x,y: x+y,  [rtTuple[0] for rtTuple in rt])

    def contexts(self, triple=None):
        c=self._db.cursor()
        quoted_table="%s_quoted_statements"%self._internedId
        asserted_table="%s_asserted_statements"%self._internedId
        asserted_type_table="%s_type_statements"%self._internedId
        literal_table = "%s_literal_statements"%self._internedId

        parameters = []

        if triple is not None:
            subject,predicate,obj=triple
            if predicate == RDF.type:
                #select from asserted rdf:type partition and quoted table (if a context is specified)
                clauseString,params = self.buildClause('typeTable',subject,RDF.type, obj,Any,True)
                parameters.extend(params)
                selects = [
                    (
                      asserted_type_table,
                      'typeTable',
                      clauseString,
                      ASSERTED_TYPE_PARTITION
                    ),
                ]

            elif isinstance(predicate,REGEXTerm) and predicate.compiledExpr.match(RDF.type) or not predicate:
                #Select from quoted partition (if context is specified), literal partition if (obj is Literal or None) and asserted non rdf:type partition (if obj is URIRef or None)
                clauseString,params = self.buildClause('typeTable',subject,RDF.type,obj,Any,True)
                parameters.extend(params)
                selects = [
                    (
                      asserted_type_table,
                      'typeTable',
                      clauseString,
                      ASSERTED_TYPE_PARTITION
                    ),
                ]

                if not self.STRONGLY_TYPED_TERMS or isinstance(obj,Literal) or not obj or (self.STRONGLY_TYPED_TERMS and isinstance(obj,REGEXTerm)):
                    clauseString,params = self.buildClause('literal',subject,predicate,obj)
                    parameters.extend(params)
                    selects.append((
                      literal_table,
                      'literal',
                      clauseString,
                      ASSERTED_LITERAL_PARTITION
                    ))
                if not isinstance(obj,Literal) and not (isinstance(obj,REGEXTerm) and self.STRONGLY_TYPED_TERMS) or not obj:
                    clauseString,params = self.buildClause('asserted',subject,predicate,obj)
                    parameters.extend(params)
                    selects.append((
                      asserted_table,
                      'asserted',
                      clauseString,
                      ASSERTED_NON_TYPE_PARTITION
                    ))

            elif predicate:
                #select from asserted non rdf:type partition (optionally), quoted partition (if context is speciied), and literal partition (optionally)
                selects = []
                if not self.STRONGLY_TYPED_TERMS or isinstance(obj,Literal) or not obj or (self.STRONGLY_TYPED_TERMS and isinstance(obj,REGEXTerm)):
                    clauseString,params = self.buildClause('literal',subject,predicate,obj)
                    parameters.extend(params)
                    selects.append((
                      literal_table,
                      'literal',
                      clauseString,
                      ASSERTED_LITERAL_PARTITION
                    ))
                if not isinstance(obj,Literal) and not (isinstance(obj,REGEXTerm) and self.STRONGLY_TYPED_TERMS) or not obj:
                    clauseString,params = self.buildClause('asserted',subject,predicate,obj)
                    parameters.extend(params)
                    selects.append((
                      asserted_table,
                      'asserted',
                      clauseString,
                      ASSERTED_NON_TYPE_PARTITION
                ))

            clauseString,params = self.buildClause('quoted',subject,predicate, obj)
            parameters.extend(params)
            selects.append(
                (
                  quoted_table,
                  'quoted',
                  clauseString,
                  QUOTED_PARTITION
                )
            )
            q=unionSELECT(selects,distinct=True,selectType=CONTEXT_SELECT)
        else:
            selects = [
                (
                  asserted_type_table,
                  'typeTable',
                  '',
                  ASSERTED_TYPE_PARTITION
                ),
                (
                  quoted_table,
                  'quoted',
                  '',
                  QUOTED_PARTITION
                ),
                (
                  asserted_table,
                  'asserted',
                  '',
                  ASSERTED_NON_TYPE_PARTITION
                ),
                (
                  literal_table,
                  'literal',
                  '',
                  ASSERTED_LITERAL_PARTITION
                ),
            ]
            q=unionSELECT(selects,distinct=True,selectType=CONTEXT_SELECT)

        self.executeSQL(c,self._normalizeSQLCmd(q),parameters)
        rt=c.fetchall()
        for context in [rtTuple[0] for rtTuple in rt]:
            yield context
        c.close()

    def _remove_context(self, identifier):
        """ """
        assert identifier
        c=self._db.cursor()
        if self.autocommit_default:
            c.execute("""SET AUTOCOMMIT=0""")
        quoted_table="%s_quoted_statements"%self._internedId
        asserted_table="%s_asserted_statements"%self._internedId
        asserted_type_table="%s_type_statements"%self._internedId
        literal_table = "%s_literal_statements"%self._internedId
        for table in [quoted_table,asserted_table,asserted_type_table,literal_table]:
            clauseString,params = self.buildContextClause(identifier,table)
            self.executeSQL(
                c,
                self._normalizeSQLCmd("DELETE from %s "%table + "where %s"%clauseString),
                [p for p in params if p]
            )
        c.close()

    # Optional Namespace methods
    #optimized interfaces (those needed in order to port Versa)
    def subjects(self, predicate=None, obj=None):
        """
        A generator of subjects with the given predicate and object.
        """
        raise Exception("Not implemented")

    #capable of taking a list of predicate terms instead of a single term
    def objects(self, subject=None, predicate=None):
        """
        A generator of objects with the given subject and predicate.
        """
        raise Exception("Not implemented")

    #optimized interfaces (others)
    def predicate_objects(self, subject=None):
        """
        A generator of (predicate, object) tuples for the given subject
        """
        raise Exception("Not implemented")

    def subject_objects(self, predicate=None):
        """
        A generator of (subject, object) tuples for the given predicate
        """
        raise Exception("Not implemented")

    def subject_predicates(self, object=None):
        """
        A generator of (subject, predicate) tuples for the given object
        """
        raise Exception("Not implemented")

    def value(self, subject, predicate=u'http://www.w3.org/1999/02/22-rdf-syntax-ns#value', object=None, default=None, any=False):
        """
        Get a value for a subject/predicate, predicate/object, or
        subject/object pair -- exactly one of subject, predicate,
        object must be None. Useful if one knows that there may only
        be one value.

        It is one of those situations that occur a lot, hence this
        'macro' like utility

        Parameters:
        -----------
        subject, predicate, object  -- exactly one must be None
        default -- value to be returned if no values found
        any -- if True:
                 return any value in the case there is more than one
               else:
                 raise UniquenessError"""
        raise Exception("Not implemented")



    #Namespace persistence interface implementation
    def bind(self, prefix, namespace):
        """ """
        c=self._db.cursor()
        try:
            c.execute("INSERT INTO %s_namespace_binds VALUES ('%s', '%s')"%(
                self._internedId,
                prefix,
                namespace)
            )
        except:
            pass
        c.close()

    def prefix(self, namespace):
        """ """
        c=self._db.cursor()
        c.execute("select prefix from %s_namespace_binds where uri = '%s'"%(
            self._internedId,
            namespace)
        )
        rt = [rtTuple[0] for rtTuple in c.fetchall()]
        c.close()
        return rt and rt[0] or None

    def namespace(self, prefix):
        """ """
        c=self._db.cursor()
        try:
            c.execute("select uri from %s_namespace_binds where prefix = '%s'"%(
                self._internedId,
                prefix)
                      )
        except:
            return None
        rt = [rtTuple[0] for rtTuple in c.fetchall()]
        c.close()
        return rt and rt[0] or None

    def namespaces(self):
        """ """
        c=self._db.cursor()
        c.execute("select prefix, uri from %s_namespace_binds where 1;"%(
            self._internedId
            )
        )
        rt=c.fetchall()
        c.close()
        for prefix,uri in rt:
            yield prefix,uri


    #Transactional interfaces
    def commit(self):
        """ """
        self._db.commit()

    def rollback(self):
        """ """
        self._db.rollback()

table_name_prefixes = [
    '%s_asserted_statements',
    '%s_type_statements',
    '%s_quoted_statements',
    '%s_namespace_binds',
    '%s_literal_statements'
]
