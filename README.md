# AKGraph
**数据科学概论实验**（实验一）

## 实验内容
分析学者网用户网络中是否存在类似“六度关系理论”的现象，即通过少数几步，任何两个人都能建立联系。

## 实验目的
证明学者网的用户网络满足六度关系，即平均最短路径小于等于6

## 实验思路
使用golang的并发原语（mutex和goroutine），快速将数据节点和关系导入到neo4j数据库当中，再使用BFS广搜得出平均最短路径（4.7）。同时也使用了python的库画出数据节点之间最短路径的分布图。

## 代码结构
```
AKGraph
├─ app 接口
├─ diagram python画图
├─ go.mod 依赖包
├─ go.sum 依赖包
├─ initialize 数据库初始化
├─ log 日志
├─ main.go 入口
├─ result 运算结果
├─ scholar 数据文件
├─ service 数据处理
└─ utils 工具包
```

## 实验结果
### 原生计算结果
<img src="https://image.codepzj.cn/image/202411092323402.png" alt="原生计算结果">

### neo4j图谱
https://image.codepzj.cn/image/202411092340714.png
图片11MB，请点击链接查看

### python导库验证

<img src="https://image.codepzj.cn/image/202411092324411.png" alt="python导包验证">

