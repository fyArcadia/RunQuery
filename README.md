## RunQuery说明
在Sublime Text中执行SQL语句的plugin。

## 功能
* 选中一段（或多段）SQL查询语句，按`alt+e`快捷键执行选中的SQL查询语句，并且会弹出一个新的编辑框显示查询结果。
* 通过`alt+t`快捷键可以将<br />
COL_1&nbsp;&nbsp;&nbsp;&nbsp;COL_2<br/>
a1&nbsp;&nbsp;&nbsp;&nbsp;b1<br/>
a2&nbsp;&nbsp;&nbsp;&nbsp;b2<br/>
转换成<br/>
[Line:&nbsp;1]<br/>
COL_1&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;a1<br/>
COL_2&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;b1<br/>
=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=--=<br/>
[Line:&nbsp;2]<br/>
COL_1&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;a2<br/>
COL_2&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;b2<br/>
=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=--=<br/>
* 选中一个表名按`alt+e`快捷键，可以查询到选中表名的表结构（现在仅支持Oracle）
* 在Sublime中编辑`select,T_TABLENAME`，然后再选中编辑的内容按`alt+e`快捷键，可自动生成T_TABLENAME的SELECT文。
