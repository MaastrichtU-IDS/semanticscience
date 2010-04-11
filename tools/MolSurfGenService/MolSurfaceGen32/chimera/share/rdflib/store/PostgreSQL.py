## Copyright (c) 2009, Intel Corporation. All rights reserved.

## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:

##   * Redistributions of source code must retain the above copyright
## notice, this list of conditions and the following disclaimer.

##   * Redistributions in binary form must reproduce the above
## copyright notice, this list of conditions and the following
## disclaimer in the documentation and/or other materials provided
## with the distribution.

##   * Neither the name of Daniel Krech nor the names of its
## contributors may be used to endorse or promote products derived
## from this software without specific prior written permission.

## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from rdflib import BNode
from rdflib.Literal import Literal
import psycopg2
import sha,sys,re,os
from rdflib.term_utils import *
from rdflib.Graph import QuotedGraph
from rdflib.store import Store,VALID_STORE, CORRUPTED_STORE, NO_STORE, UNKNOWN
from rdflib.store.REGEXMatching import REGEXTerm, NATIVE_REGEX, PYTHON_REGEX
from rdflib.store.AbstractSQLStore import *
Any = None


def ParseConfigurationString(config_string):
    """
    Parses a configuration string in the form:
    key1=val1,key2=val2,key3=val3,...
    The following configuration keys are expected (not all are required):
    user
    password
    db
    host
    port (optional - defaults to 5432)
    """
    kvDict = dict([(part.split('=')[0],part.split('=')[-1]) for part in config_string.split(',')])
    for requiredKey in ['user','db']:
        assert requiredKey in kvDict
    if 'port' not in kvDict:
        kvDict['port']=5432
    if 'password' not in kvDict:
        kvDict['password']=''
    return kvDict

def GetConfigurationString(configuration):
    """
    Given a config-form string, return a dsn-form string
    """
    configDict = ParseConfigurationString(configuration)

    dsn = "dbname=%s user=%s password=%s" % (configDict['db'], configDict['user'], configDict['password'])
    if configDict.has_key('port'):
        try:
            port = int(configDict['port'])
            dsn += " port=%s" % port
        except:
            raise ArithmeticError('PostgreSQL port must be a valid integer')

    return dsn



# Though i appreciate that this was made into a function rather than
# a method since it was universal, sadly different DBs quote values
# differently. So i have to pull this, and all methods which call it,
# into the Postgres implementation level.
#
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
            selectString = "select *"
            tableSource = " from %s as %s "%(tableName,tableAlias)
        elif tableType == ASSERTED_TYPE_PARTITION:
            selectString =\
            """select %s.member as subject, '%s' as predicate, %s.klass as object, %s.context as context, %s.termComb as termComb, NULL as objLanguage, NULL as objDatatype"""%(tableAlias,RDF.type,tableAlias,tableAlias,tableAlias)
            tableSource = " from %s as %s "%(tableName,tableAlias)
        elif tableType == ASSERTED_NON_TYPE_PARTITION:
            selectString =\
            """select *,NULL as objLanguage, NULL as objDatatype"""
            tableSource = " from %s as %s "%(tableName,tableAlias)

        selects.append(selectString + tableSource + whereClause)

    orderStmt = ''
    if selectType == TRIPLE_SELECT:
        orderStmt = ' order by subject,predicate,object'
    if distinct:
        return ' union '.join(selects) + orderStmt
    else:
        return ' union all '.join(selects) + orderStmt


class PostgreSQL(AbstractSQLStore):
    """
    PostgreSQL store formula-aware implementation.  It stores it's triples in the following partitions (per AbstractSQLStore:

    - Asserted non rdf:type statements
    - Asserted rdf:type statements (in a table which models Class membership)
    The motivation for this partition is primarily query speed and scalability as most graphs will always have more rdf:type statements than others
    - All Quoted statements

    In addition it persists namespace mappings in a seperate table
    """
    context_aware = True
    formula_aware = True
    transaction_aware = True
    regex_matching = NATIVE_REGEX
    autocommit_default = False

    def open(self, configuration, create=True):
        """
        Opens the store specified by the configuration string. If
        create is True a store will be created if it does not already
        exist. If create is False and a store does not already exist
        an exception is raised. An exception is also raised if a store
        exists, but there is insufficient permissions to open the
        store.
        """

        self._db = psycopg2.connect(GetConfigurationString(configuration))

        if self._db:
            if create:
                self.init_db()

            if self.db_exists():
                return VALID_STORE
            else:
                self._db = None
                return NO_STORE
        else:
            return NO_STORE




    def db_exists(self):
        c = self._db.cursor()
        c.execute("SELECT relname from pg_class")
        tbls = [rt[0] for rt in c.fetchall()]
        c.close()
        for tn in [tbl % (self._internedId) for tbl in table_name_prefixes]:
            if tn not in tbls:
                sys.stderr.write("table %s Doesn't exist\n" % (tn))
                return 0
        return 1


    def init_db(self):
        c=self._db.cursor()
        for x in CREATE_TABLE_STMTS:
            c.execute(x % (self._internedId))
        for tblName,indices in INDICES:
            for indexName,columns in indices:
                c.execute("CREATE INDEX %s on %s (%s)" % ((indexName % self._internedId),
                                                          (tblName % self._internedId),
                                                          ','.join(columns)))
        c.close()
        self._db.commit()


    # opposite of init_db, takes a config string
    def destroy(self, configuration):
        db = psycopg2.connect(GetConfigurationString(configuration))
        c = db.cursor()
        for tblname in table_name_prefixes:
            fullname = tblname % self._internedId
            try:
                c.execute("DROP TABLE %s" % fullname)
            except:
                sys.stderr.write("unable to drop table: %s\n" % fullname)

        db.commit()
        c.close()
        db.close()

        print "Destroyed Close World Universe %s (in PostgreSQL database %s)" % (self.identifier, configuration)


    def EscapeQuotes(self, qstr):
        # overridden because PostgreSQL is in its own quoting world
        if qstr is None:
            return ''
        tmp = qstr.replace("'", "''")

        return tmp



    # copied and pasted primarily to use the local unionSELECT instead
    # of the one provided by AbstractSQLStore
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




    # copied and pasted primarily to use the local unionSELECT instead
    # of the one provided by AbstractSQLStore
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
        return "<Parititioned PostgreSQL N3 Store: %s contexts, %s classification assertions, %s quoted statements, %s property/value assertions, and %s other assertions>"%(len([c for c in self.contexts()]),typeLen,quotedLen,literalLen,assertedLen)

    # copied and pasted primarily to use the local unionSELECT instead
    # of the one provided by AbstractSQLStore
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



    # This is taken from AbstractSQLStore, and modified, specifically
    # to not query quoted_statements. The comments in the original
    # indicate that quoted_statements were queried conditionally, but
    # the code does otherwise.
    #
    # As far as i can tell, quoted_statements contains formulae, which
    # should not be returned as valid global contexts (at least, as per
    # the in-memory and MySQL store implementations), so those queries
    # have been completely excised until a case is made that they are
    # necessary.
    #
    # It's reasonable that the AbstractSQLStore implementation is closer
    # to the original design, but this conforms to working implementations.
    def contexts(self, triple=None):
        c=self._db.cursor()
        asserted_table="%s_asserted_statements"%self._internedId
        asserted_type_table="%s_type_statements"%self._internedId
        literal_table = "%s_literal_statements"%self._internedId

        parameters = []

        if triple is not None:
            subject,predicate,obj=triple
            if predicate == RDF.type:
                #select from asserted rdf:type partition
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
                #Select from literal partition if (obj is Literal or None) and asserted non rdf:type partition (if obj is URIRef or None)
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
                #select from asserted non rdf:type partition (optionally) and literal partition (optionally)
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
        for contextId in [x[0] for x in rt]:
            yield Graph(self, URIRef(contextId))
        c.close()




    # overridden for quote-character reasons
    def executeSQL(self,cursor,qStr,params=None,paramList=False):
        """
        This takes the query string and parameters and (depending on the SQL implementation) either fill in
        the parameter in-place or pass it on to the Python DB impl (if it supports this).
        The default (here) is to fill the parameters in-place surrounding each param with quote characters
        """
        if not params:
            cursor.execute(unicode(qStr))
        elif paramList:
            raise Exception("Not supported!")
        else:
            params = tuple([item == 'NULL' and item
                            or not isinstance(item,int) and u"'%s'" % item
                            or item
                            for item in params])
            cursor.execute(qStr%params)


    # new method abstracting much cut/paste code from AbstractSQLStore.
    def buildGenericClause(self, generic, value, tableName):
        if isinstance(value,REGEXTerm):
            return " REGEXP (%s,"+" %s)" % (tableName and '%s.%s' % (tableName, generic) or generic), [value]
        elif isinstance(value,list):
            clauseStrings=[]
            paramStrings = []
            for s in value:
                if isinstance(s,REGEXTerm):
                    clauseStrings.append(" REGEXP (%s,"+" %s)" % (tableName and '%s.%s' % (tableName, generic) or generic) + " %s")
                    paramStrings.append(self.normalizeTerm(s))
                elif isinstance(s,(QuotedGraph,Graph)):
                    clauseStrings.append("%s="%(tableName and '%s.%s' % (tableName, generic) or generic) + "%s")
                    paramStrings.append(self.normalizeTerm(s.identifier))
                else:
                    clauseStrings.append("%s=" % (tableName and '%s.%s' % (tableName, generic) or generic) + "%s")
                    paramStrings.append(self.normalizeTerm(s))
            return '('+ ' or '.join(clauseStrings) + ')', paramStrings
        elif isinstance(value, (QuotedGraph,Graph)):
            return "%s=" % (tableName and '%s.%s' % (tableName, generic) or generic) + "%s", [self.normalizeTerm(value.identifier)]
        elif value == 'NULL':
            return "%s is null" % (tableName and '%s.%s' % (tableName, generic) or generic), []
        else:
            return value is not None and "%s=" % (tableName and '%s.%s' % (tableName, generic) or generic) + "%s", [value] or None


    def buildSubjClause(self,subject,tableName):
        return self.buildGenericClause("subject", subject, tableName)

    def buildPredClause(self,predicate,tableName):
        return self.buildGenericClause("predicate", predicate, tableName)

    def buildObjClause(self,obj,tableName):
        return self.buildGenericClause("object", obj, tableName)

    def buildContextClause(self,context,tableName):
        context = context is not None and self.normalizeTerm(context.identifier) or context
        return self.buildGenericClause("context", context, tableName)

    def buildTypeMemberClause(self,subject,tableName):
        return self.buildGenericClause("member", subject, tableName)

    def buildTypeClassClause(self,obj,tableName):
        return self.buildGenericClause("klass", obj, tableName)




CREATE_ASSERTED_STATEMENTS_TABLE = """
CREATE TABLE %s_asserted_statements (
    subject       text not NULL,
    predicate     text not NULL,
    object        text not NULL,
    context       text not NULL,
    termComb      smallint not NULL)"""

CREATE_ASSERTED_TYPE_STATEMENTS_TABLE = """
CREATE TABLE %s_type_statements (
    member        text not NULL,
    klass         text not NULL,
    context       text not NULL,
    termComb      smallint not NULL)"""

CREATE_LITERAL_STATEMENTS_TABLE = """
CREATE TABLE %s_literal_statements (
    subject       text not NULL,
    predicate     text not NULL,
    object        text,
    context       text not NULL,
    termComb      smallint not NULL,
    objLanguage   varchar(3),
    objDatatype   text)"""

CREATE_QUOTED_STATEMENTS_TABLE = """
CREATE TABLE %s_quoted_statements (
    subject       text not NULL,
    predicate     text not NULL,
    object        text,
    context       text not NULL,
    termComb      smallint not NULL,
    objLanguage   varchar(3),
    objDatatype   text)"""

CREATE_NS_BINDS_TABLE = """
CREATE TABLE %s_namespace_binds (
    prefix        varchar(20) UNIQUE not NULL,
    uri           text,
    PRIMARY KEY (prefix))"""


CREATE_TABLE_STMTS = [CREATE_ASSERTED_STATEMENTS_TABLE,
                      CREATE_ASSERTED_TYPE_STATEMENTS_TABLE,
                      CREATE_QUOTED_STATEMENTS_TABLE,
                      CREATE_NS_BINDS_TABLE,
                      CREATE_LITERAL_STATEMENTS_TABLE]


INDICES = [
    (
        "%s_asserted_statements",
        [
            ("%s_A_termComb_index",('termComb',)),
            ("%s_A_s_index",('subject',)),
            ("%s_A_p_index",('predicate',)),
            ("%s_A_o_index",('object',)),
            ("%s_A_c_index",('context',)),
            ],
        ),
    (
        "%s_type_statements",
        [
            ("%s_T_termComb_index",('termComb',)),
            ("%s_member_index",('member',)),
            ("%s_klass_index",('klass',)),
            ("%s_c_index",('context',)),
            ],
        ),
    (
        "%s_literal_statements",
        [
            ("%s_L_termComb_index",('termComb',)),
            ("%s_L_s_index",('subject',)),
            ("%s_L_p_index",('predicate',)),
            ("%s_L_c_index",('context',)),
            ],
        ),
    (
        "%s_quoted_statements",
        [
            ("%s_Q_termComb_index",('termComb',)),
            ("%s_Q_s_index",('subject',)),
            ("%s_Q_p_index",('predicate',)),
            ("%s_Q_o_index",('object',)),
            ("%s_Q_c_index",('context',)),
            ],
        ),
    (
        "%s_namespace_binds",
        [
            ("%s_uri_index",('uri',)),
            ],
        )]

