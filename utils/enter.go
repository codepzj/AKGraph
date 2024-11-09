package utils

import (
	"bytes"
	"encoding/csv"
	"fmt"
	"log"
	"os"
	"strconv"
	"strings"
)

type Person map[string]any
type PersonLink []map[string]any

const (
	AttrsBaseDir = "scholar/attributes"
	LinkPath     = "scholar/links.txt"
)

func GetFileName(basedir string) []string {
	// 获取目录下的所有文件和文件夹
	entries, err := os.ReadDir(basedir)
	if err != nil {
		log.Fatalln("无法读取目录:", err)
	}
	attrs := make([]string, 0)
	for _, entry := range entries {
		attrs = append(attrs, entry.Name())
	}
	return attrs
}

func ReadFile(filename string) *csv.Reader {
	file, err := os.ReadFile(filename)
	if err != nil {
		panic(fmt.Sprintf("文件读取失败%v", err))
	}
	reader := csv.NewReader(bytes.NewReader(file))
	return reader
}

func GetAttrNumber() []string {
	attrs := GetFileName(AttrsBaseDir)
	attrsNumber := make([]string, 0)
	for _, attr := range attrs {
		attrsNumber = append(attrsNumber, strings.Split(attr, ".")[0])
	}
	return attrsNumber
}

func GetAttrInfo() []Person {
	attrs := GetFileName(AttrsBaseDir)
	people := make([]Person, 0)
	for _, attr := range attrs {
		AttrFullPath := AttrsBaseDir + "/" + attr
		reader := ReadFile(AttrFullPath)
		records, err := reader.ReadAll()
		if err != nil {
			log.Println("读取文件失败", err)
		}
		ID := strings.Split(attr, ".")[0]
		person := Person{
			"ID": ID,
		}
		attri := 1
		for _, record := range records {
			person["attr"+strconv.Itoa(attri)] = record[0]
			attri++
		}
		people = append(people, person)
	}
	return people
}

func GetLinksInfo() PersonLink {
	reader := ReadFile(LinkPath)
	records, _ := reader.ReadAll()
	linkMap := make(PersonLink, 0)
	for _, record := range records {
		personRelation := strings.Split(record[0], "\t")
		linkMap = append(linkMap, map[string]any{
			"aID": personRelation[0],
			"bID": personRelation[1],
		})
	}
	return linkMap
}

func GenerateQuery(label string, p Person) string {
	var queryBuilder strings.Builder
	_, err := queryBuilder.WriteString("MERGE (n:" + label + " {ID: $ID}) SET ")
	if err != nil {
		log.Fatalln("创建失败")
	}

	i := 0
	for key := range p {
		if key == "ID" {
			continue
		}
		_, err = queryBuilder.WriteString(fmt.Sprintf("n.`%s` = $%s", key, key))
		if err != nil {
			continue
		}
		if i < len(p)-2 {
			queryBuilder.WriteString(", ")
		}
		i++
	}
	_, err = queryBuilder.WriteString(" RETURN n")
	if err != nil {
		log.Fatalln("创建失败")
	}

	return queryBuilder.String()
}
