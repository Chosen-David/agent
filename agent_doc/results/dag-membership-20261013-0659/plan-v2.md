# 计划v2：保留str子类兼容

继承plan.md的全部预算、验收和权限，不变更性能门或workload。独立plan-review.md指出原计划ID允许str子类，其哈希/比较可与内置str不一致；依赖exactstr alone不够。

修正：原 any invalid IDs 检查先执行，保持短路；随后构建唯一性set并保留重复ID错误。仅当所有IDs type(i)is str，且dependency type(d)is str，才走集合；其他输入全部走原listmembership。计划正确性新增恶意hash str子类ID、str子类dependency、继承str普通类，以及重复/空/非法ID错误顺序。freeze门不变；case scope增量是计划审核发现的语义风险，尚未执行数据生产。
