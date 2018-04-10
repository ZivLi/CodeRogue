##本地开发分支
> 1.git checkout -b dev

    在本地创建自己的dev分支（基准分支）

> 2.git fetch --all    /     git fetch origin dev

    fetch从远端仓库中拉取所有分支信息到本地/拉取远端仓库中某一特定上游分支信息到本地

> 3.git rebase origin/dev

    将拉取的origin:dev的内容合并到本地当前分支，这样就保证当前分支dev同步于远端分支并且避免提交一次merge commit

> 4.git checkout -b (feature、bug、refactor)/PROJ/NO-Branch-Name

    创建自己的开发分支一定要以dev为基础。通过checkout -b创建某一具体开发分支

    分支名格式：（新需求feature、修复bug、重构refactor)/项目名称/Issue编号-对当前分支的描述命名-号连接单词
    
   ![](/Users/ziv/fetch_name.jpeg)

> 5.git status

> 6.git add . / git add filenames

> 7.git commit -m 'commit-msg' / git commit --amend

    提交代码推荐使用第一种方式，并进行原子化提交。这样在找问题的时候，方便通过当时留下的commit-msg更快速准确定位问题。如果用追加方式的话，会错过很多commit时的重要信息。

> 8.git fetch -p

    在push代码之前，一定要再次同步代码。保证当前代码跟远端版本没有冲突！！！

    同步骤3。-p参数会在本地删除远端已经删除的分支。

> 9.git rebase origin/dev

    如果远端仓库分支和我们修改了同一个文件，在调用该命令时会提示冲突

    找到冲突文件，并修改冲突。主要是找到<<< 远端内容 ==== 本地内容 >>>>三行的内容 进行修改即可。

    解决后执行

    git add <the_conflict_file>  （将解决内容提交）

    git rebase --continue （将rebase操作执行完成，即可push操作）
  
  ![](/Users/ziv/branch.jpeg)

> 10.git push origin feature/PROJ/NO-Branch-Name

    将代码push到远端仓库的分支，并发起pull/merge request。