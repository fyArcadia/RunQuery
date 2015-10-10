import sublime
import sublime_plugin
import os
import subprocess
import sys
import string

reload(sys)
sys.setdefaultencoding(sys.getfilesystemencoding())


setting = sublime.load_settings('runquery.sublime-settings')
pkgpath = sublime.packages_path()
runQueryPath = setting.get('RunQueryPath')
runQueryPath = os.path.join(pkgpath, runQueryPath)


class RunQuery(sublime_plugin.TextCommand):
        def run(self, edit, database):

            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
            else:
                startupinfo = None
            if database == "":
                database = setting.get("DefaultDatabase")
            dbSetting = setting.get(database)
            if dbSetting is None:
                self.createWindowWithText("Not Found Database", "RunQuery")
                return
            provider = dbSetting['Provider']
            sqlFormat = self.getSqlFormat(provider)
            connectionString = dbSetting['ConnectionString']
            args = [runQueryPath, '-s', provider, connectionString]
            regionList = self.view.sel()
            for region in regionList:
                strSql = self.view.substr(region)
                if len(strSql) > 0:
                    args.append(sqlFormat.format(strSql))
            try:
                proc = subprocess.Popen(args, stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                        startupinfo=startupinfo)
                output, _ = proc.communicate()
                output = output.decode(sys.getfilesystemencoding())
                if sqlFormat.formatType == DefaultFormat.CREATE_SQL:
                    self.view.replace(edit, regionList[0], sqlFormat.resultFormat(output))
                else:
                    self.createWindowWithText(sqlFormat.resultFormat(output), sqlFormat.getTitle(database))
            except Exception, ex:
                self.createWindowWithText("unknow exception %s" % ex)

        def createWindowWithText(self, textToDisplay, database):
            newView = self.view.window().new_file()
            edit = newView.begin_edit()
            newView.insert(edit, 0, textToDisplay)
            newView.end_edit(edit)
            newView.set_scratch(True)
            newView.set_read_only(True)
            newView.set_name("%s result" % database)
            return newView.id()

        def getSqlFormat(self, provider):
            if provider == "Byd.Connection.OracleDbProvider":
                return OracleFormat()
            else:
                return DefaultFormat()


class DefaultFormat(object):
    NORMAL_SQL = "NormalSql"
    GET_TABLE_COLUMNS = "GetTableColumns"
    CREATE_SQL = "CreateSql"

    def format(self, sql):
        return sql

    def resultFormat(self, result):
        return result

    def getTitle(self, title):
        return title


class OracleFormat(object):

    def format(self, sql):
        self.sql = sql
        if (sql.upper().find("SELECT,") == 0 or sql.upper().find("INSERT,") == 0) and len(sql.split(",")) == 2:
            self.formatType = DefaultFormat.CREATE_SQL
            return '''
            SELECT
                DECODE(COLUMN_ID, 1, COLUMN_NAME, ',' || COLUMN_NAME) AS "%s"
            FROM
                USER_TAB_COLUMNS TAB
            WHERE TABLE_NAME = '%s'
            ORDER BY COLUMN_ID
            ''' % (sql, sql.split(",")[1])
        elif sql.find(' ') == -1:
            self.formatType = DefaultFormat.GET_TABLE_COLUMNS
            return """
            SELECT
                TAB.COLUMN_ID
                ,TAB.COLUMN_NAME
                ,TAB.DATA_TYPE || ' (' ||
                    DECODE(TAB.DATA_PRECISION, '', TO_CHAR(TAB.DATA_LENGTH), TAB.DATA_PRECISION || ',' || TAB.DATA_SCALE) || ')' DATA_TYPE
                ,DECODE(TAB.NULLABLE, 'N', 'NOT NULL', '') NULLABLE
                ,COL.COMMENTS
            FROM
                USER_TAB_COLUMNS TAB
                ,USER_COL_COMMENTS COL
            WHERE TAB.TABLE_NAME = '%s'
            AND TAB.TABLE_NAME = COL.TABLE_NAME
            AND TAB.COLUMN_NAME = COL.COLUMN_NAME
            ORDER BY TAB.COLUMN_ID
            """ % sql
        else:
            self.formatType = DefaultFormat.NORMAL_SQL
            return sql

    def resultFormat(self, result):
        if self.formatType == DefaultFormat.GET_TABLE_COLUMNS:
            padLength = 10
            COL_COUNT = 5
            maxLengthArr = [0, 0, 0, 0]
            arr = result.splitlines(1)
            if len(arr) > 1:
                del arr[0]
            for line in arr:
                subArr = line.split('\t')
                if len(subArr) == COL_COUNT:
                    for i in range(0, COL_COUNT-1):
                        if maxLengthArr[i] < len(subArr[i]):
                            maxLengthArr[i] = len(subArr[i])

            newResult = ""
            for line in arr:
                subArr = line.split('\t')
                if len(subArr) == COL_COUNT:
                    for i in range(0, COL_COUNT-1):
                        newResult = newResult + string.ljust(subArr[i], maxLengthArr[i] + padLength)
                    newResult = newResult + subArr[COL_COUNT - 1]

            if len(newResult) == 0:
                return "Table is not found."
            return newResult
        elif self.formatType == DefaultFormat.CREATE_SQL:
            arr = result.splitlines(1)
            if len(arr) > 1:
                param = arr[0].split(",")
                func = param[0].upper()
                tableName = param[1]
                del arr[0]

            if func == "SELECT":
                result = "SELECT\n%sFROM " + tableName + "WHERE 1=1"
            elif func == "INSERT":
                result = "INSERT INTO " + tableName + "(\n%s) VALUES ()"
            cols = ""
            for col in arr:
                if col != "\n":
                    cols = cols + "    " + col
            if len(cols) == 0:
                return "Table is not found."
            return result % cols
        else:
            return result

    def getTitle(self, title):
        if self.formatType == DefaultFormat.GET_TABLE_COLUMNS:
            return self.sql
        else:
            return title
