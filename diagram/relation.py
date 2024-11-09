import os
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter


# 读取 links.txt 文件并构建图
def build_graph(links_file):
    G = nx.Graph()  # 创建无向图
    with open(links_file, 'r') as f:
        for line in f:
            node1, node2 = map(int, line.strip().split())
            G.add_edge(node1, node2)
    return G


# 读取 lexicon.txt 文件并返回节点的标签/属性映射
def read_lexicon(lexicon_file):
    lexicon = {}
    with open(lexicon_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()  # 去掉前后的空格和换行符
            if line:
                parts = line.split()
                if len(parts) == 2:
                    node_id, label = parts
                    lexicon[int(node_id)] = label
    return lexicon


# 读取 attributes 文件夹中的节点属性，并处理文件缺失的情况
def read_attributes(attribute_folder, node_count):
    attributes = {}
    for i in range(1, node_count + 1):
        attribute_file = os.path.join(attribute_folder, f"{i}.txt")
        if os.path.exists(attribute_file):
            try:
                with open(attribute_file, 'r', encoding='utf-8') as f:  # 使用 utf-8 编码
                    # 假设属性文件中的每行是该节点的一个属性
                    attributes[i] = [line.strip() for line in f.readlines()]
            except UnicodeDecodeError as e:
                print(f"警告: 文件 {attribute_file} 编码错误: {e}")
                attributes[i] = []  # 如果文件有问题，使用空列表
        else:
            attributes[i] = []  # 默认使用空列表作为属性
            print(f"警告: 属性文件 {i}.txt 不存在")
    return attributes


# 绘制节点的关系网状图
def draw_network_graph(graph, attributes):
    # 计算每个节点的度数（即连接的边的数量）
    degrees = dict(graph.degree())

    # 根据属性数量给节点着色
    node_colors = []
    node_sizes = []

    for node in graph.nodes():
        num_attributes = len(attributes.get(node, []))  # 获取该节点的属性数量
        node_colors.append(plt.cm.viridis(num_attributes / max(len(attr) for attr in attributes.values())))
        node_sizes.append(degrees[node] * 20)  # 节点大小与度数成正比，乘以20来放大

    # 计算每条边的颜色
    edge_colors = []
    for edge in graph.edges():
        # 根据连接的节点的度数决定边的颜色
        degree1 = degrees[edge[0]]
        degree2 = degrees[edge[1]]
        edge_colors.append(plt.cm.Blues(min(degree1, degree2) / max(degrees.values())))

    # 绘制图形
    plt.figure(figsize=(12, 12))
    nx.draw(graph, with_labels=True, node_color=node_colors, node_size=node_sizes,
            edge_color=edge_colors, font_size=10, font_weight='bold', alpha=0.8,
            cmap=plt.cm.viridis)
    plt.title('Node Relationship Network (Node Size: Degree, Node Color: Attribute Count)')
    plt.show()


# 主程序
def main(links_file, lexicon_file, attribute_folder):
    # 1. 读取数据并构建图
    graph = build_graph(links_file)
    lexicon = read_lexicon(lexicon_file)

    # 2. 读取节点属性
    node_count = len(graph.nodes())  # 根据图中节点数来决定需要读取多少个属性文件
    attributes = read_attributes(attribute_folder, node_count)

    # 3. 绘制网络图
    draw_network_graph(graph, attributes)


# 假设你的文件名为 links.txt 和 lexicon.txt，attributes 文件夹存放属性文件
links_file = 'links.txt'
lexicon_file = 'lexicon.txt'
attribute_folder = 'attributes'  # 确保文件夹名正确

# 调用主程序
main(links_file, lexicon_file, attribute_folder)
