package initialize

import (
	"context"
	"fmt"
	"log"
	
	"github.com/neo4j/neo4j-go-driver/v5/neo4j"
)

var Driver neo4j.DriverWithContext

func init() {
	ctx := context.Background()
	dbUri := "neo4j://ip:port" // 数据隐私，不方便透露
	dbUser := ""
	dbPassword := ""
	auth := neo4j.BasicAuth(dbUser, dbPassword, "")
	driver, err := neo4j.NewDriverWithContext(dbUri, auth)
	if err != nil {
		log.Fatal(err)
	}
	err = driver.VerifyAuthentication(ctx, &auth)
	if err != nil {
		fmt.Println("连接数据库失败")
	} else {
		fmt.Println("连接数据库成功")
	}
	Driver = driver
}
