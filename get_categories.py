import logging
from typing import Dict, List, Tuple

import requests

# 配置日志格式
logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
)

# 全局cookie变量
cookie = ''

def get_document_tree() -> List[Dict] | None:
    """获取API文档树结构"""
    url = 'https://tushare.pro/wctapi/documents/tree'
    response = requests.get(url, headers={'Cookie': cookie})
    if response.status_code != 200:
        raise Exception(f'获取文档树失败，状态码: {response.status_code}')

    if response.json()['code'] != 0:
        logging.warning(f'获取文档树失败，错误信息: {response.json()["message"]}')
        return None
    return response.json()['data']

def extract_non_leaf_titles(tree_data: List[Dict]) -> List[Tuple[str, int]]:
    """
    提取所有非叶子节点的标题，并记录其层级
    
    Args:
        tree_data: 文档树数据
        
    Returns:
        包含(标题, 层级)元组的列表，按树的遍历顺序排序
    """
    titles = []
    
    def traverse_tree(node: Dict, level: int = 0):
        # 只有当节点有子节点时才添加标题
        if 'children' in node and node['children']:
            title = node['title']
            if title:
                # 检查标题是否已存在
                if not any(t[0] == title for t in titles):
                    titles.append((title, level))
            # 递归处理子节点
            for child in node['children']:
                traverse_tree(child, level + 1)
    
    # 遍历整个树
    for node in tree_data:
        traverse_tree(node)
    
    return titles

def main():
    # 检查cookie是否设置
    if not cookie:
        logging.error("请先设置cookie")
        return
        
    # 获取文档树
    tree_data = get_document_tree()
    if tree_data is None:
        logging.error("无法获取文档树")
        return
    
    # 提取非叶子节点标题并直接打印字典形式
    titles = extract_non_leaf_titles(tree_data)
    print("translations = {")
    for title, level in titles:
        print(f"    '{title}': '',")
    print("}")

if __name__ == '__main__':
    main() 
