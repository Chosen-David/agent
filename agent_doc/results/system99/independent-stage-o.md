# SYSTEM-99 阶段O独立结果验收

结论：`usable-with-scope`，无发布阻塞。

独立只读复核确认 `task_source_snapshot` 从一次有界普通文件读取的同一原字节完成SHA、严格UTF-8
解码和任务解析；validate不再按路径二次解析。prepare把该身份与project-doc task_index核对；
publication依次核对冻结候选树、任务所有权ID和project-doc身份；外部构造的source/doc冲突也被
validate拒绝。1 MiB边界同时以`st_size`和`limit+1`读取检查，默认未指定上限的其它文档消费者
不受隐式限流。

方案初审指出原测试偏实现细节后，主控补充三项真实临时文件语义测试：读取A后磁盘变B由
project-doc重检拒绝；读取A后A→B→A仅接受A的ID与标题；恰好1 MiB成功且原始SHA一致，和
limit+1拒绝形成闭区间。独立复跑新快照/publication测试39/39通过；另核对FIFO不阻塞、非法
UTF-8/目录/文件及父目录符号链接/超限失败闭合、runtime与research-assistant镜像逐字节相同，
`git diff --check`通过。

全库1406（1398通过/8跳过）、`-O`定向125、Reader2及同步结果由主控实际运行；独立只读复核
未发现与代码、测试或短日志不一致，但未把这些当第二份独立重跑样本。

接受范围仅为单个TASK原字节快照的一致摘要/解析，以及task source、project-documents、
publication candidate间的身份核对；不证明多文件事务原子性、不抵御有写权限的恶意OS对手，
也不关闭SYSTEM-99其余系统级缺口。
