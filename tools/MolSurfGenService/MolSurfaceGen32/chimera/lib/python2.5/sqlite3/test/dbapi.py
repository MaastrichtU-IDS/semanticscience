#-*- coding: ISO-8859-1 -*-
# pysqlite2/test/dbapi.py: tests for DB-API compliance
#
# Copyright (C) 2004-2005 Gerhard H�ring <gh@ghaering.de>
#
# This file is part of pysqlite.
#
# This software is provided 'as-is', without any express or implied
# warranty.  In no event will the authors be held liable for any damages
# arising from the use of this software.
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
#
# 1. The origin of this software must not be misrepresented; you must not
#    claim that you wrote the original software. If you use this software
#    in a product, an acknowledgment in the product documentation would be
#    appreciated but is not required.
# 2. Altered source versions must be plainly marked as such, and must not be
#    misrepresented as being the original software.
# 3. This notice may not be removed or altered from any source distribution.

import unittest
import threading
import sqlite3 as sqlite

class ModuleTests(unittest.TestCase):
    def CheckAPILevel(self):
        self.assertEqual(sqlite.apilevel, "2.0",
                         "apilevel is %s, should be 2.0" % sqlite.apilevel)

    def CheckThreadSafety(self):
        self.assertEqual(sqlite.threadsafety, 1,
                         "threadsafety is %d, should be 1" % sqlite.threadsafety)

    def CheckParamStyle(self):
        self.assertEqual(sqlite.paramstyle, "qmark",
                         "paramstyle is '%s', should be 'qmark'" %
                         sqlite.paramstyle)

    def CheckWarning(self):
        self.assert_(issubclass(sqlite.Warning, StandardError),
                     "Warning is not a subclass of StandardError")

    def CheckError(self):
        self.failUnless(issubclass(sqlite.Error, StandardError),
                        "Error is not a subclass of StandardError")

    def CheckInterfaceError(self):
        self.failUnless(issubclass(sqlite.InterfaceError, sqlite.Error),
                        "InterfaceError is not a subclass of Error")

    def CheckDatabaseError(self):
        self.failUnless(issubclass(sqlite.DatabaseError, sqlite.Error),
                        "DatabaseError is not a subclass of Error")

    def CheckDataError(self):
        self.failUnless(issubclass(sqlite.DataError, sqlite.DatabaseError),
                        "DataError is not a subclass of DatabaseError")

    def CheckOperationalError(self):
        self.failUnless(issubclass(sqlite.OperationalError, sqlite.DatabaseError),
                        "OperationalError is not a subclass of DatabaseError")

    def CheckIntegrityError(self):
        self.failUnless(issubclass(sqlite.IntegrityError, sqlite.DatabaseError),
                        "IntegrityError is not a subclass of DatabaseError")

    def CheckInternalError(self):
        self.failUnless(issubclass(sqlite.InternalError, sqlite.DatabaseError),
                        "InternalError is not a subclass of DatabaseError")

    def CheckProgrammingError(self):
        self.failUnless(issubclass(sqlite.ProgrammingError, sqlite.DatabaseError),
                        "ProgrammingError is not a subclass of DatabaseError")

    def CheckNotSupportedError(self):
        self.failUnless(issubclass(sqlite.NotSupportedError,
                                   sqlite.DatabaseError),
                        "NotSupportedError is not a subclass of DatabaseError")

class ConnectionTests(unittest.TestCase):
    def setUp(self):
        self.cx = sqlite.connect(":memory:")
        cu = self.cx.cursor()
        cu.execute("create table test(id integer primary key, name text)")
        cu.execute("insert into test(name) values (?)", ("foo",))

    def tearDown(self):
        self.cx.close()

    def CheckCommit(self):
        self.cx.commit()

    def CheckCommitAfterNoChanges(self):
        """
        A commit should also work when no changes were made to the database.
        """
        self.cx.commit()
        self.cx.commit()

    def CheckRollback(self):
        self.cx.rollback()

    def CheckRollbackAfterNoChanges(self):
        """
        A rollback should also work when no changes were made to the database.
        """
        self.cx.rollback()
        self.cx.rollback()

    def CheckCursor(self):
        cu = self.cx.cursor()

    def CheckFailedOpen(self):
        YOU_CANNOT_OPEN_THIS = "/foo/bar/bla/23534/mydb.db"
        try:
            con = sqlite.connect(YOU_CANNOT_OPEN_THIS)
        except sqlite.OperationalError:
            return
        self.fail("should have raised an OperationalError")

    def CheckClose(self):
        self.cx.close()

    def CheckExceptions(self):
        # Optional DB-API extension.
        self.failUnlessEqual(self.cx.Warning, sqlite.Warning)
        self.failUnlessEqual(self.cx.Error, sqlite.Error)
        self.failUnlessEqual(self.cx.InterfaceError, sqlite.InterfaceError)
        self.failUnlessEqual(self.cx.DatabaseError, sqlite.DatabaseError)
        self.failUnlessEqual(self.cx.DataError, sqlite.DataError)
        self.failUnlessEqual(self.cx.OperationalError, sqlite.OperationalError)
        self.failUnlessEqual(self.cx.IntegrityError, sqlite.IntegrityError)
        self.failUnlessEqual(self.cx.InternalError, sqlite.InternalError)
        self.failUnlessEqual(self.cx.ProgrammingError, sqlite.ProgrammingError)
        self.failUnlessEqual(self.cx.NotSupportedError, sqlite.NotSupportedError)

class CursorTests(unittest.TestCase):
    def setUp(self):
        self.cx = sqlite.connect(":memory:")
        self.cu = self.cx.cursor()
        self.cu.execute("create table test(id integer primary key, name text, income number)")
        self.cu.execute("insert into test(name) values (?)", ("foo",))

    def tearDown(self):
        self.cu.close()
        self.cx.close()

    def CheckExecuteNoArgs(self):
        self.cu.execute("delete from test")

    def CheckExecuteIllegalSql(self):
        try:
            self.cu.execute("select asdf")
            self.fail("should have raised an OperationalError")
        except sqlite.OperationalError:
            return
        except:
            self.fail("raised wrong exception")

    def CheckExecuteTooMuchSql(self):
        try:
            self.cu.execute("select 5+4; select 4+5")
            self.fail("should have raised a Warning")
        except sqlite.Warning:
            return
        except:
            self.fail("raised wrong exception")

    def CheckExecuteTooMuchSql2(self):
        self.cu.execute("select 5+4; -- foo bar")

    def CheckExecuteTooMuchSql3(self):
        self.cu.execute("""
            select 5+4;

            /*
            foo
            */
            """)

    def CheckExecuteWrongSqlArg(self):
        try:
            self.cu.execute(42)
            self.fail("should have raised a ValueError")
        except ValueError:
            return
        except:
            self.fail("raised wrong exception.")

    def CheckExecuteArgInt(self):
        self.cu.execute("insert into test(id) values (?)", (42,))

    def CheckExecuteArgFloat(self):
        self.cu.execute("insert into test(income) values (?)", (2500.32,))

    def CheckExecuteArgString(self):
        self.cu.execute("insert into test(name) values (?)", ("Hugo",))

    def CheckExecuteWrongNoOfArgs1(self):
        # too many parameters
        try:
            self.cu.execute("insert into test(id) values (?)", (17, "Egon"))
            self.fail("should have raised ProgrammingError")
        except sqlite.ProgrammingError:
            pass

    def CheckExecuteWrongNoOfArgs2(self):
        # too little parameters
        try:
            self.cu.execute("insert into test(id) values (?)")
            self.fail("should have raised ProgrammingError")
        except sqlite.ProgrammingError:
            pass

    def CheckExecuteWrongNoOfArgs3(self):
        # no parameters, parameters are needed
        try:
            self.cu.execute("insert into test(id) values (?)")
            self.fail("should have raised ProgrammingError")
        except sqlite.ProgrammingError:
            pass

    def CheckExecuteDictMapping(self):
        self.cu.execute("insert into test(name) values ('foo')")
        self.cu.execute("select name from test where name=:name", {"name": "foo"})
        row = self.cu.fetchone()
        self.failUnlessEqual(row[0], "foo")

    def CheckExecuteDictMappingTooLittleArgs(self):
        self.cu.execute("insert into test(name) values ('foo')")
        try:
            self.cu.execute("select name from test where name=:name and id=:id", {"name": "foo"})
            self.fail("should have raised ProgrammingError")
        except sqlite.ProgrammingError:
            pass

    def CheckExecuteDictMappingNoArgs(self):
        self.cu.execute("insert into test(name) values ('foo')")
        try:
            self.cu.execute("select name from test where name=:name")
            self.fail("should have raised ProgrammingError")
        except sqlite.ProgrammingError:
            pass

    def CheckExecuteDictMappingUnnamed(self):
        self.cu.execute("insert into test(name) values ('foo')")
        try:
            self.cu.execute("select name from test where name=?", {"name": "foo"})
            self.fail("should have raised ProgrammingError")
        except sqlite.ProgrammingError:
            pass

    def CheckClose(self):
        self.cu.close()

    def CheckRowcountExecute(self):
        self.cu.execute("delete from test")
        self.cu.execute("insert into test(name) values ('foo')")
        self.cu.execute("insert into test(name) values ('foo')")
        self.cu.execute("update test set name='bar'")
        self.failUnlessEqual(self.cu.rowcount, 2)

    def CheckRowcountExecutemany(self):
        self.cu.execute("delete from test")
        self.cu.executemany("insert into test(name) values (?)", [(1,), (2,), (3,)])
        self.failUnlessEqual(self.cu.rowcount, 3)

    def CheckTotalChanges(self):
        self.cu.execute("insert into test(name) values ('foo')")
        self.cu.execute("insert into test(name) values ('foo')")
        if self.cx.total_changes < 2:
            self.fail("total changes reported wrong value")

    # Checks for executemany:
    # Sequences are required by the DB-API, iterators
    # enhancements in pysqlite.

    def CheckExecuteManySequence(self):
        self.cu.executemany("insert into test(income) values (?)", [(x,) for x in range(100, 110)])

    def CheckExecuteManyIterator(self):
        class MyIter:
            def __init__(self):
                self.value = 5

            def next(self):
                if self.value == 10:
                    raise StopIteration
                else:
                    self.value += 1
                    return (self.value,)

        self.cu.executemany("insert into test(income) values (?)", MyIter())

    def CheckExecuteManyGenerator(self):
        def mygen():
            for i in range(5):
                yield (i,)

        self.cu.executemany("insert into test(income) values (?)", mygen())

    def CheckExecuteManyWrongSqlArg(self):
        try:
            self.cu.executemany(42, [(3,)])
            self.fail("should have raised a ValueError")
        except ValueError:
            return
        except:
            self.fail("raised wrong exception.")

    def CheckExecuteManySelect(self):
        try:
            self.cu.executemany("select ?", [(3,)])
            self.fail("should have raised a ProgrammingError")
        except sqlite.ProgrammingError:
            return
        except:
            self.fail("raised wrong exception.")

    def CheckExecuteManyNotIterable(self):
        try:
            self.cu.executemany("insert into test(income) values (?)", 42)
            self.fail("should have raised a TypeError")
        except TypeError:
            return
        except Exception, e:
            print "raised", e.__class__
            self.fail("raised wrong exception.")

    def CheckFetchIter(self):
        # Optional DB-API extension.
        self.cu.execute("delete from test")
        self.cu.execute("insert into test(id) values (?)", (5,))
        self.cu.execute("insert into test(id) values (?)", (6,))
        self.cu.execute("select id from test order by id")
        lst = []
        for row in self.cu:
            lst.append(row[0])
        self.failUnlessEqual(lst[0], 5)
        self.failUnlessEqual(lst[1], 6)

    def CheckFetchone(self):
        self.cu.execute("select name from test")
        row = self.cu.fetchone()
        self.failUnlessEqual(row[0], "foo")
        row = self.cu.fetchone()
        self.failUnlessEqual(row, None)

    def CheckFetchoneNoStatement(self):
        cur = self.cx.cursor()
        row = cur.fetchone()
        self.failUnlessEqual(row, None)

    def CheckArraySize(self):
        # must default ot 1
        self.failUnlessEqual(self.cu.arraysize, 1)

        # now set to 2
        self.cu.arraysize = 2

        # now make the query return 3 rows
        self.cu.execute("delete from test")
        self.cu.execute("insert into test(name) values ('A')")
        self.cu.execute("insert into test(name) values ('B')")
        self.cu.execute("insert into test(name) values ('C')")
        self.cu.execute("select name from test")
        res = self.cu.fetchmany()

        self.failUnlessEqual(len(res), 2)

    def CheckFetchmany(self):
        self.cu.execute("select name from test")
        res = self.cu.fetchmany(100)
        self.failUnlessEqual(len(res), 1)
        res = self.cu.fetchmany(100)
        self.failUnlessEqual(res, [])

    def CheckFetchall(self):
        self.cu.execute("select name from test")
        res = self.cu.fetchall()
        self.failUnlessEqual(len(res), 1)
        res = self.cu.fetchall()
        self.failUnlessEqual(res, [])

    def CheckSetinputsizes(self):
        self.cu.setinputsizes([3, 4, 5])

    def CheckSetoutputsize(self):
        self.cu.setoutputsize(5, 0)

    def CheckSetoutputsizeNoColumn(self):
        self.cu.setoutputsize(42)

    def CheckCursorConnection(self):
        # Optional DB-API extension.
        self.failUnlessEqual(self.cu.connection, self.cx)

    def CheckWrongCursorCallable(self):
        try:
            def f(): pass
            cur = self.cx.cursor(f)
            self.fail("should have raised a TypeError")
        except TypeError:
            return
        self.fail("should have raised a ValueError")

    def CheckCursorWrongClass(self):
        class Foo: pass
        foo = Foo()
        try:
            cur = sqlite.Cursor(foo)
            self.fail("should have raised a ValueError")
        except TypeError:
            pass

class ThreadTests(unittest.TestCase):
    def setUp(self):
        self.con = sqlite.connect(":memory:")
        self.cur = self.con.cursor()
        self.cur.execute("create table test(id integer primary key, name text, bin binary, ratio number, ts timestamp)")

    def tearDown(self):
        self.cur.close()
        self.con.close()

    def CheckConCursor(self):
        def run(con, errors):
            try:
                cur = con.cursor()
                errors.append("did not raise ProgrammingError")
                return
            except sqlite.ProgrammingError:
                return
            except:
                errors.append("raised wrong exception")

        errors = []
        t = threading.Thread(target=run, kwargs={"con": self.con, "errors": errors})
        t.start()
        t.join()
        if len(errors) > 0:
            self.fail("\n".join(errors))

    def CheckConCommit(self):
        def run(con, errors):
            try:
                con.commit()
                errors.append("did not raise ProgrammingError")
                return
            except sqlite.ProgrammingError:
                return
            except:
                errors.append("raised wrong exception")

        errors = []
        t = threading.Thread(target=run, kwargs={"con": self.con, "errors": errors})
        t.start()
        t.join()
        if len(errors) > 0:
            self.fail("\n".join(errors))

    def CheckConRollback(self):
        def run(con, errors):
            try:
                con.rollback()
                errors.append("did not raise ProgrammingError")
                return
            except sqlite.ProgrammingError:
                return
            except:
                errors.append("raised wrong exception")

        errors = []
        t = threading.Thread(target=run, kwargs={"con": self.con, "errors": errors})
        t.start()
        t.join()
        if len(errors) > 0:
            self.fail("\n".join(errors))

    def CheckConClose(self):
        def run(con, errors):
            try:
                con.close()
                errors.append("did not raise ProgrammingError")
                return
            except sqlite.ProgrammingError:
                return
            except:
                errors.append("raised wrong exception")

        errors = []
        t = threading.Thread(target=run, kwargs={"con": self.con, "errors": errors})
        t.start()
        t.join()
        if len(errors) > 0:
            self.fail("\n".join(errors))

    def CheckCurImplicitBegin(self):
        def run(cur, errors):
            try:
                cur.execute("insert into test(name) values ('a')")
                errors.append("did not raise ProgrammingError")
                return
            except sqlite.ProgrammingError:
                return
            except:
                errors.append("raised wrong exception")

        errors = []
        t = threading.Thread(target=run, kwargs={"cur": self.cur, "errors": errors})
        t.start()
        t.join()
        if len(errors) > 0:
            self.fail("\n".join(errors))

    def CheckCurClose(self):
        def run(cur, errors):
            try:
                cur.close()
                errors.append("did not raise ProgrammingError")
                return
            except sqlite.ProgrammingError:
                return
            except:
                errors.append("raised wrong exception")

        errors = []
        t = threading.Thread(target=run, kwargs={"cur": self.cur, "errors": errors})
        t.start()
        t.join()
        if len(errors) > 0:
            self.fail("\n".join(errors))

    def CheckCurExecute(self):
        def run(cur, errors):
            try:
                cur.execute("select name from test")
                errors.append("did not raise ProgrammingError")
                return
            except sqlite.ProgrammingError:
                return
            except:
                errors.append("raised wrong exception")

        errors = []
        self.cur.execute("insert into test(name) values ('a')")
        t = threading.Thread(target=run, kwargs={"cur": self.cur, "errors": errors})
        t.start()
        t.join()
        if len(errors) > 0:
            self.fail("\n".join(errors))

    def CheckCurIterNext(self):
        def run(cur, errors):
            try:
                row = cur.fetchone()
                errors.append("did not raise ProgrammingError")
                return
            except sqlite.ProgrammingError:
                return
            except:
                errors.append("raised wrong exception")

        errors = []
        self.cur.execute("insert into test(name) values ('a')")
        self.cur.execute("select name from test")
        t = threading.Thread(target=run, kwargs={"cur": self.cur, "errors": errors})
        t.start()
        t.join()
        if len(errors) > 0:
            self.fail("\n".join(errors))

class ConstructorTests(unittest.TestCase):
    def CheckDate(self):
        d = sqlite.Date(2004, 10, 28)

    def CheckTime(self):
        t = sqlite.Time(12, 39, 35)

    def CheckTimestamp(self):
        ts = sqlite.Timestamp(2004, 10, 28, 12, 39, 35)

    def CheckDateFromTicks(self):
        d = sqlite.DateFromTicks(42)

    def CheckTimeFromTicks(self):
        t = sqlite.TimeFromTicks(42)

    def CheckTimestampFromTicks(self):
        ts = sqlite.TimestampFromTicks(42)

    def CheckBinary(self):
        b = sqlite.Binary(chr(0) + "'")

class ExtensionTests(unittest.TestCase):
    def CheckScriptStringSql(self):
        con = sqlite.connect(":memory:")
        cur = con.cursor()
        cur.executescript("""
            -- bla bla
            /* a stupid comment */
            create table a(i);
            insert into a(i) values (5);
            """)
        cur.execute("select i from a")
        res = cur.fetchone()[0]
        self.failUnlessEqual(res, 5)

    def CheckScriptStringUnicode(self):
        con = sqlite.connect(":memory:")
        cur = con.cursor()
        cur.executescript(u"""
            create table a(i);
            insert into a(i) values (5);
            select i from a;
            delete from a;
            insert into a(i) values (6);
            """)
        cur.execute("select i from a")
        res = cur.fetchone()[0]
        self.failUnlessEqual(res, 6)

    def CheckScriptErrorIncomplete(self):
        con = sqlite.connect(":memory:")
        cur = con.cursor()
        raised = False
        try:
            cur.executescript("create table test(sadfsadfdsa")
        except sqlite.ProgrammingError:
            raised = True
        self.failUnlessEqual(raised, True, "should have raised an exception")

    def CheckScriptErrorNormal(self):
        con = sqlite.connect(":memory:")
        cur = con.cursor()
        raised = False
        try:
            cur.executescript("create table test(sadfsadfdsa); select foo from hurz;")
        except sqlite.OperationalError:
            raised = True
        self.failUnlessEqual(raised, True, "should have raised an exception")

    def CheckConnectionExecute(self):
        con = sqlite.connect(":memory:")
        result = con.execute("select 5").fetchone()[0]
        self.failUnlessEqual(result, 5, "Basic test of Connection.execute")

    def CheckConnectionExecutemany(self):
        con = sqlite.connect(":memory:")
        con.execute("create table test(foo)")
        con.executemany("insert into test(foo) values (?)", [(3,), (4,)])
        result = con.execute("select foo from test order by foo").fetchall()
        self.failUnlessEqual(result[0][0], 3, "Basic test of Connection.executemany")
        self.failUnlessEqual(result[1][0], 4, "Basic test of Connection.executemany")

    def CheckConnectionExecutescript(self):
        con = sqlite.connect(":memory:")
        con.executescript("create table test(foo); insert into test(foo) values (5);")
        result = con.execute("select foo from test").fetchone()[0]
        self.failUnlessEqual(result, 5, "Basic test of Connection.executescript")

class ClosedTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def CheckClosedConCursor(self):
        con = sqlite.connect(":memory:")
        con.close()
        try:
            cur = con.cursor()
            self.fail("Should have raised a ProgrammingError")
        except sqlite.ProgrammingError:
            pass
        except:
            self.fail("Should have raised a ProgrammingError")

    def CheckClosedConCommit(self):
        con = sqlite.connect(":memory:")
        con.close()
        try:
            con.commit()
            self.fail("Should have raised a ProgrammingError")
        except sqlite.ProgrammingError:
            pass
        except:
            self.fail("Should have raised a ProgrammingError")

    def CheckClosedConRollback(self):
        con = sqlite.connect(":memory:")
        con.close()
        try:
            con.rollback()
            self.fail("Should have raised a ProgrammingError")
        except sqlite.ProgrammingError:
            pass
        except:
            self.fail("Should have raised a ProgrammingError")

    def CheckClosedCurExecute(self):
        con = sqlite.connect(":memory:")
        cur = con.cursor()
        con.close()
        try:
            cur.execute("select 4")
            self.fail("Should have raised a ProgrammingError")
        except sqlite.ProgrammingError:
            pass
        except:
            self.fail("Should have raised a ProgrammingError")

def suite():
    module_suite = unittest.makeSuite(ModuleTests, "Check")
    connection_suite = unittest.makeSuite(ConnectionTests, "Check")
    cursor_suite = unittest.makeSuite(CursorTests, "Check")
    thread_suite = unittest.makeSuite(ThreadTests, "Check")
    constructor_suite = unittest.makeSuite(ConstructorTests, "Check")
    ext_suite = unittest.makeSuite(ExtensionTests, "Check")
    closed_suite = unittest.makeSuite(ClosedTests, "Check")
    return unittest.TestSuite((module_suite, connection_suite, cursor_suite, thread_suite, constructor_suite, ext_suite, closed_suite))

def test():
    runner = unittest.TextTestRunner()
    runner.run(suite())

if __name__ == "__main__":
    test()
