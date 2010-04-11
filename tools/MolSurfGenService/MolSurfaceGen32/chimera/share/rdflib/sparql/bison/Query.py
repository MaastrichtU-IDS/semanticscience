from rdflib.sparql.bison.GraphPattern import GraphPattern

class Query(object):
    """
    Query ::= Prolog ( SelectQuery | ConstructQuery | DescribeQuery | AskQuery )
    See: http://www.w3.org/TR/rdf-sparql-query/#rQuery
    """
    def __init__(self,prolog,query):
        self.prolog = prolog
        self.query = query

    def __repr__(self):
        return repr(self.query)

class WhereClause(object):
    """
    The where clause is essentially a wrapper for an instance of a ParsedGraphPattern
    """
    def __init__(self,parsedGraphPattern):
        self.parsedGraphPattern = parsedGraphPattern

class SelectQuery(object):
    """
    SelectQuery ::= 'SELECT' 'DISTINCT'? ( Var+ | '*' ) DatasetClause* WhereClause SolutionModifier
    See: http://www.w3.org/TR/rdf-sparql-query/#rSelectQuery
    """
    def __init__(self,variables,dataSetList,whereClause,solutionModifier,distinct=None):
        self.variables = variables is not None and variables or []
        self.dataSets = dataSetList and dataSetList or []
        self.whereClause = whereClause
        self.solutionModifier = solutionModifier
        self.distinct = distinct is not None

    def __repr__(self):
        return "SELECT %s %s %s %s %s"%(self.distinct and 'DISTINCT' or '',self.variables and self.variables or '*',self.dataSets,self.whereClause.parsedGraphPattern,self.solutionModifier and self.solutionModifier or '')

class AskQuery(object):
    """
    AskQuery ::= 'ASK' DatasetClause* WhereClause
    See: http://www.w3.org/TR/rdf-sparql-query/#rAskQuery
    """
    def __init__(self,dataSetList,whereClause):
        self.dataSets = dataSetList and dataSetList or []
        self.whereClause = whereClause

    def __repr__(self):
        return "ASK %s %s"%(self.dataSets,self.whereClause.parsedGraphPattern)

class ConstructQuery(object):
    """
    ConstructQuery ::= 'CONSTRUCT' ConstructTemplate DatasetClause* WhereClause SolutionModifier
    See: http://www.w3.org/TR/rdf-sparql-query/#rConstructQuery
    """
    def __init__(self,triples,dataSetList,whereClause,solutionModifier):
        self.triples = GraphPattern(triples=triples)
        self.dataSets = dataSetList and dataSetList or []
        self.whereClause = whereClause
        self.solutionModifier = solutionModifier

class DescribeQuery(object):
    """
    DescribeQuery ::= 'DESCRIBE' ( VarOrIRIref+ | '*' ) DatasetClause* WhereClause? SolutionModifier
    http://www.w3.org/TR/rdf-sparql-query/#rConstructQuery
    """
    def __init__(self,variables,dataSetList,whereClause,solutionModifier):
        self.describeVars = variables is not None and variables or []
        self.dataSets = dataSetList and dataSetList or []
        self.whereClause = whereClause
        self.solutionModifier = solutionModifier

    def __repr__(self):
        return "DESCRIBE %s %s %s %s"%(
                       self.describeVars,
                       self.dataSets,
                       self.whereClause.parsedGraphPattern,
                       self.solutionModifier)


class Prolog(object):
    """
    Prolog ::= BaseDecl? PrefixDecl*
    See: http://www.w3.org/TR/rdf-sparql-query/#rProlog
    """
    def __init__(self,baseDeclaration,prefixDeclarations):
        self.baseDeclaration = baseDeclaration
        self.extensionFunctions={}
        self.prefixBindings = {}
        if prefixDeclarations:
            for prefixBind in prefixDeclarations:
                if hasattr(prefixBind,'base'):
                    self.prefixBindings[prefixBind.qName] = prefixBind.base 

    def __repr__(self):
        return repr(self.prefixBindings)
    