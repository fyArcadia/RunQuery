import sublime_plugin
import sys
import string

debug = ""
reload(sys)
sys.setdefaultencoding(sys.getfilesystemencoding())


class DataTransform(sublime_plugin.TextCommand):
        def run(self, edit):
            try:
                strTempText = ""
                regionList = self.view.sel()
                for region in regionList:
                    row = self.view.substr(region)
                    if len(row) > 0:
                        if row.find("\n") == -1:
                            row = row + "\n"
                        strTempText = strTempText + row
                arr = strTempText.split("\n")
                index = 0
                maxHeadLength = 0
                pad_length = 5
                strText = ""
                SPLIT_LINE = "=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=--="
                for row in arr:
                    if index == 0:
                        head = row.split("\t")
                        for col in head:
                            if len(col) > maxHeadLength:
                                maxHeadLength = len(col)
                        maxHeadLength = maxHeadLength + pad_length
                    elif row != "":
                        x = 0
                        body = row.split("\t")

                        strText = strText + "[Line: %s]\n" % str(index)
                        for val in body:
                            if x < len(head):
                                strText = strText + string.ljust(head[x], maxHeadLength)
                            else:
                                strText = strText + string.ljust(" ", maxHeadLength)
                            strText = strText + val + "\n"
                            x = x + 1
                        strText = strText + SPLIT_LINE + "\n"
                    index = index + 1
                self.createWindowWithText(strText)
            except Exception, ex:
                self.createWindowWithText("unknow exception %s" % ex + "\ndebug info: " + debug)

        def createWindowWithText(self, textToDisplay):
            newView = self.view.window().new_file()
            edit = newView.begin_edit()
            newView.insert(edit, 0, textToDisplay)
            newView.end_edit(edit)
            newView.set_scratch(True)
            newView.set_read_only(True)
            newView.set_name("Data Transform Result")
            return newView.id()
