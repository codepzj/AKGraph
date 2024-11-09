import os
import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter


# 读取 links.txt 文件并构建图
def build_graph(links_file):
    G = nx.Graph()  # 创建无向图
    with open(links_file, 'r') as f:
        for line in f:
            # 假设每行格式是 "node1 node2"，即两个节点的关系
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
                # 尝试使用 utf-8 编码打开文件
                with open(attribute_file, 'r', encoding='utf-8') as f:
                    # 假设属性文件中的每行是该节点的一个属性
                    attributes[i] = [line.strip() for line in f.readlines()]
            except UnicodeDecodeError as e:
                print(f"警告: 文件 {attribute_file} 编码错误: {e}")
                attributes[i] = []  # 如果文件有问题，使用空列表
        else:
            # 如果文件不存在，使用空列表作为默认属性
            attributes[i] = []
            print(f"警告: 属性文件 {i}.txt 不存在")
    return attributes


# 计算全局平均最短路径，并统计路径长度
def calculate_shortest_path_distribution(graph):
    path_lengths = []  # 用来存储所有的最短路径长度
    total_paths = 0
    total_distance = 0

    # 遍历图中的所有节点对
    for node in graph.nodes():
        # 使用 BFS 或 Dijkstra 算法计算每个节点的最短路径
        distances = nx.single_source_shortest_path_length(graph, node)

        # 统计路径长度
        for target, distance in distances.items():
            if target != node:  # 排除节点到自身的路径
                path_lengths.append(distance)
                total_paths += 1
                total_distance += distance

    # 计算全局平均最短路径
    average_path_length = total_distance / total_paths if total_paths > 0 else 0
    return path_lengths, average_path_length


# 主程序
def main(links_file, lexicon_file, attribute_folder):
    # 1. 读取数据并构建图
    graph = build_graph(links_file)
    lexicon = read_lexicon(lexicon_file)

    # 2. 读取节点属性
    node_count = len(graph.nodes())  # 根据图中节点数来决定需要读取多少个属性文件
    attributes = read_attributes(attribute_folder, node_count)

    # 3. 计算路径分布和平均路径长度
    path_lengths, average_path_length = calculate_shortest_path_distribution(graph)

    # 4. 统计路径长度的频率
    path_length_counter = Counter(path_lengths)

    # 5. 绘制路径长度的分布图
    lengths = list(path_length_counter.keys())
    frequencies = list(path_length_counter.values())

    plt.figure(figsize=(10, 6))
    plt.bar(lengths, frequencies, color='skyblue')
    plt.xlabel('Path Length')
    plt.ylabel('Frequency')
    plt.title('Distribution of Shortest Path Lengths')
    plt.xticks(range(1, max(lengths) + 1))  # 设置x轴显示路径长度
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

    # 6. 打印路径长度的频率和平均路径长度
    print("路径长度的频率统计：")
    for length, frequency in path_length_counter.items():
        print(f"路径长度 {length} 的频率： {frequency} 次")

    print(f"全局平均最短路径长度：{average_path_length:.2f}")


# 假设你的文件名为 links.txt 和 lexicon.txt，attributes 文件夹存放属性文件
links_file = 'links.txt'
lexicon_file = 'lexicon.txt'
attribute_folder = 'attributes'  # 确保文件夹名正确

# 调用主程序
main(links_file, lexicon_file, attribute_folder)
