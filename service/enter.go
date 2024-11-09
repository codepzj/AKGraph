package service

import (
	"AKGraph/initialize"
	"AKGraph/utils"
	"context"
	"github.com/neo4j/neo4j-go-driver/v5/neo4j"
	"log"
	"os"
	"sync"
)

var (
	driver           = initialize.Driver
	concurrencyLimit = 10
	sem              = make(chan struct{}, concurrencyLimit)

	// 日志文件配置
	personLog *log.Logger
	linkLog   *log.Logger
)

// 初始化日志文件
func init() {
	personFile, err := os.OpenFile("log/create_person.txt", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0666)
	if err != nil {
		log.Fatalf("无法创建日志文件: %v", err)
	}
	linkFile, err := os.OpenFile("log/create_link.txt", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0666)
	if err != nil {
		log.Fatalf("无法创建日志文件: %v", err)
	}

	// 创建不同的日志记录器
	personLog = log.New(personFile, "PERSON_LOG: ", log.Ldate|log.Ltime|log.Lshortfile)
	linkLog = log.New(linkFile, "LINK_LOG: ", log.Ldate|log.Ltime|log.Lshortfile)
}

type NodeService struct {
	mu sync.Mutex
}

func (n *NodeService) CreatePersonNode(label string, people []utils.Person) {
	n.mu.Lock()
	defer n.mu.Unlock()
	ctx := context.Background()
	session := driver.NewSession(ctx, neo4j.SessionConfig{AccessMode: neo4j.AccessModeWrite})
	defer func() {
		if err := session.Close(ctx); err != nil {
			personLog.Println("关闭事务失败:", err)
		}
	}()
	var wg sync.WaitGroup
	for _, person := range people {
		wg.Add(1)
		sem <- struct{}{}
		go func(person utils.Person) {
			defer wg.Done()
			defer func() { <-sem }()
			_, err := session.ExecuteWrite(ctx, func(tx neo4j.ManagedTransaction) (any, error) {
				query := utils.GenerateQuery(label, person)
				_, err := tx.Run(ctx, query, person)
				if err != nil {
					personLog.Println("创建节点失败:", err)
					return nil, err
				}
				personLog.Printf("成功创建节点: %v\n", person["ID"]) // 假设 person 有 ID 字段
				return nil, nil
			})
			if err != nil {
				personLog.Println("执行事务失败:", err)
			}
		}(person)
	}
	wg.Wait()
}

func (n *NodeService) CreatePersonLink(linkMap []map[string]any) {
	n.mu.Lock()
	defer n.mu.Unlock()
	ctx := context.Background()
	session := driver.NewSession(ctx, neo4j.SessionConfig{AccessMode: neo4j.AccessModeWrite})
	defer func() {
		if err := session.Close(ctx); err != nil {
			linkLog.Println("关闭事务失败:", err)
		}
	}()
	var wg sync.WaitGroup
	for _, param := range linkMap {
		wg.Add(1)
		sem <- struct{}{}
		go func(param map[string]any) {
			defer wg.Done()
			defer func() { <-sem }()
			_, err := session.ExecuteWrite(ctx, func(tx neo4j.ManagedTransaction) (any, error) {
				query := `MATCH (a:Person {ID: $aID}), (b:Person {ID: $bID}) MERGE (a)-[:KNOWS]->(b)`
				_, err := tx.Run(ctx, query, param)
				if err != nil {
					return nil, err
				}
				linkLog.Printf("成功创建关系: %v --> %v\n", param["aID"], param["bID"])
				return nil, nil
			})
			if err != nil {
				linkLog.Println("执行事务失败:", err)
			}
		}(param)
	}
	wg.Wait()
}

func (n *NodeService) FindShortestPath(aID, bID string) (int, error) {
	ctx := context.Background()
	session := driver.NewSession(ctx, neo4j.SessionConfig{AccessMode: neo4j.AccessModeRead})
	defer func() {
		if err := session.Close(ctx); err != nil {
			personLog.Println("关闭会话失败:", err)
		}
	}()

	// 设置 BFS 队列和已访问节点集
	queue := []struct {
		id    string
		depth int
	}{{id: aID, depth: 0}}
	visited := map[string]bool{aID: true}

	for len(queue) > 0 {
		node := queue[0]
		queue = queue[1:]

		// 如果达到目标节点，返回路径深度
		if node.id == bID {
			return node.depth, nil
		}

		// 如果当前深度已达到 6，跳过该节点
		if node.depth >= 6 {
			continue
		}

		// 查询当前节点的邻居节点
		query := `
            MATCH (a:Person {ID: $currentID})-[:KNOWS]->(b)
            WHERE NOT b.ID IN $visited
            RETURN b.ID AS neighborID
        `
		result, err := session.Run(ctx, query, map[string]any{"currentID": node.id, "visited": keys(visited)})
		if err != nil {
			return 0, err
		}

		// 遍历邻居节点，将尚未访问的邻居节点加入队列
		for result.Next(ctx) {
			neighborID, _ := result.Record().Get("neighborID")
			if !visited[neighborID.(string)] {
				visited[neighborID.(string)] = true
				queue = append(queue, struct {
					id    string
					depth int
				}{id: neighborID.(string), depth: node.depth + 1})
			}
		}
	}

	// 找不到路径，返回默认的6
	personLog.Println("路径不存在:", aID, bID)
	return 6, nil
}

// CalculateAveragePath 计算平均路径长度，并排除连续10次返回6的节点
func (n *NodeService) CalculateAveragePath(pairs [][]string) float64 {
	var totalPathLength, validPairCount int
	nodeSixCount := make(map[string]int)

	for _, pair := range pairs {
		p1ID, p2ID := pair[0], pair[1]
		pathLength, err := n.FindShortestPath(p1ID, p2ID)
		if err != nil {
			continue
		}

		if pathLength == 6 {
			nodeSixCount[p1ID]++
		} else {
			nodeSixCount[p1ID] = 0
			totalPathLength += pathLength
			validPairCount++
		}

		// 排除连续10次为6的节点
		if nodeSixCount[p1ID] >= 10 {
			personLog.Println("节点", p1ID, "连续10次为6，排除在平均路径计算之外")
			nodeSixCount[p1ID] = 0
			continue
		}
	}

	if validPairCount == 0 {
		return 0
	}
	return float64(totalPathLength) / float64(validPairCount)
}

// 辅助函数：将 map 的键转换为切片
func keys(m map[string]bool) []string {
	result := make([]string, 0, len(m))
	for k := range m {
		result = append(result, k)
	}
	return result
}
