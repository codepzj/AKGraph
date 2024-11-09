package app

import (
	"AKGraph/service"
	"AKGraph/utils"
	"fmt"
	"time"
)

func InsertPeopleData() {
	startTime := time.Now()
	var n = new(service.NodeService)
	personInfo := utils.GetAttrInfo()
	n.CreatePersonNode("Person", personInfo)
	personLink := utils.GetLinksInfo()
	n.CreatePersonLink(personLink)
	duration := time.Since(startTime)
	fmt.Println("创建和连接节点耗时：", duration)
}

func GetShortestPath() {
	var n = new(service.NodeService)
	personIDList := utils.GetAttrNumber()
	var totalPathLength int
	var pathCount int
	
	for i := 0; i < len(personIDList)-1; i++ {
		p1ID := personIDList[i]
		for j := i + 1; j < len(personIDList); j++ {
			p2ID := personIDList[j]
			short, err := n.FindShortestPath(p1ID, p2ID)
			if err != nil {
				fmt.Printf("节点 %s 与 %s 之间没有路径\n", p1ID, p2ID)
				continue
			}
			
			// 只统计不超过6的路径长度
			if short <= 6 {
				totalPathLength += short
				pathCount++
			}
			fmt.Println(p1ID, "-->", p2ID, short)
		}
	}
	
	// 计算平均路径长度
	if pathCount > 0 {
		averagePathLength := float64(totalPathLength) / float64(pathCount)
		fmt.Printf("平均路径长度：%.2f\n", averagePathLength)
		if averagePathLength <= 6 {
			fmt.Println("符合六度分隔理论")
		} else {
			fmt.Println("不符合六度分隔理论")
		}
	} else {
		fmt.Println("没有找到符合条件的路径")
	}
}
