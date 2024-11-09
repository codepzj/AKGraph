import os
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np


# 读取 links.txt 文件并构建图
def build_graph(links_file):
    G = nx.Graph()  # 创建无向图
    with open(links_file, 'r') as f:
        for line in f:
            node1, node2 = map(int, line.strip().split())
            G.add_edge(node1, node2)

    print(f"Total number of nodes: {len(G.nodes())}")  # 打印节点总数
    return G


# 将节点分割成多个区域，每个区域包含300个节点
def create_regions(graph, step_size=300):
    nodes = list(graph.nodes())  # 获取所有节点
    regions = []  # 用于存放每个区域的节点
    for i in range(0, len(nodes), step_size):
        region_nodes = nodes[i:i + step_size]  # 获取每个区域的节点
        print(f"Region size: {len(region_nodes)}")  # 打印每个区域的节点数
        regions.append(region_nodes)

    print(f"Total nodes: {len(nodes)}")  # 打印总节点数
    print(f"Total regions: {len(regions)}")  # 打印区域总数
    return regions


# 计算两个区域之间的平均最短路径长度
def calculate_average_path_length(graph, region1, region2):
    total_distance = 0
    total_paths = 0
    for node1 in region1:
        for node2 in region2:
            try:
                # 计算节点对之间的最短路径
                distance = nx.shortest_path_length(graph, source=node1, target=node2)
                total_distance += distance
                total_paths += 1
            except nx.NetworkXNoPath:
                continue  # 如果两个节点不连通，跳过
    if total_paths > 0:
        return total_distance / total_paths
    else:
        return 0  # 如果没有可用路径，则返回0


# 计算每对区域之间的平均路径长度
def calculate_all_region_path_lengths(graph, regions):
    region_count = len(regions)
    print(f"Number of regions: {region_count}")  # 打印区域数量
    path_lengths_matrix = np.zeros((region_count, region_count))  # 初始化一个矩阵用于存储区域间路径长度

    for i in range(region_count):
        for j in range(i, region_count):  # 对称矩阵，只计算一半，另一半可以直接复制
            avg_path_length = calculate_average_path_length(graph, regions[i], regions[j])
            path_lengths_matrix[i, j] = avg_path_length
            path_lengths_matrix[j, i] = avg_path_length  # 矩阵是对称的

    return path_lengths_matrix


# 将路径长度矩阵保存到文件
def save_path_lengths_to_file(path_lengths_matrix, output_file):
    with open(output_file, 'w') as f:
        region_count = path_lengths_matrix.shape[0]
        for i in range(region_count):
            for j in range(region_count):
                f.write(f"Region {i + 1} to Region {j + 1}: {path_lengths_matrix[i, j]:.4f}\n")


# 主程序
def main(links_file, output_file):
    # 1. 读取数据并构建图
    graph = build_graph(links_file)

    # 2. 将节点分割成多个区域，每个区域包含300个节点
    regions = create_regions(graph, step_size=300)

    # 3. 计算每对区域之间的平均路径长度
    region_path_lengths_matrix = calculate_all_region_path_lengths(graph, regions)

    # 4. 保存计算结果到文件
    save_path_lengths_to_file(region_path_lengths_matrix, output_file)
    print(f"Results have been written to {output_file}")

    # 5. 绘制热力图
    plt.figure(figsize=(10, 8))
    im = plt.imshow(region_path_lengths_matrix, cmap='YlGnBu', interpolation='nearest', vmin=0,
                    vmax=6)  # 设置vmin和vmax的范围
    plt.colorbar(im, label='Average Path Length')  # 显示颜色条
    plt.title('Heatmap of Average Path Lengths Between Regions')
    plt.xlabel('Region Index')
    plt.ylabel('Region Index')
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    # 设定 links.txt 文件路径
    links_file = 'links.txt'

    # 设置输出文件路径为 E:\pythonProject5 目录
    output_file = r'E:\pythonProject5\region_path_lengths.txt'

    # 调用主函数
    main(links_file, output_file)
