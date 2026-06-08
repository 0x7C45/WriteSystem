# Graphviz Python 模板 — 六类图表

> 使用 `graphviz` Python 库（`pip install graphviz`）。
> 字体统一使用 PingFang SC，输出 PNG + SVG。
> 标准调色板：绿色 #4CAF50、蓝色 #2196F3、橙色 #FF9800、红色 #E91E63、紫色 #9C27B0

---

## A. 流程图 (Flowchart)

```python
"""流程框图模板 — 包含开始/结束、处理、判断、循环回边"""

import graphviz


def create_flowchart(output_dir: str = 'output') -> str:
    """创建流程框图并渲染为 PNG + SVG。"""
    g = graphviz.Digraph('flowchart', format='png')
    g.attr(rankdir='TB', dpi='300')
    # 全局字体设置
    g.attr('graph', fontname='PingFang SC',
           label='流程框图 (Flowchart)', labelloc='t', fontsize='20')
    g.attr('node', fontname='PingFang SC', fontsize='12')
    g.attr('edge', fontname='PingFang SC', fontsize='11')

    # ---- 节点 ----

    # 开始（椭圆）
    g.node('start', '开始\n(Start)',
           shape='ellipse', style='filled', fillcolor='#4CAF50', fontcolor='white')

    # 处理步骤（圆角矩形）
    g.node('init', '初始化 (Initialize)\n设置变量初值',
           shape='box', style='filled,rounded', fillcolor='#BBDEFB')

    g.node('process', '循环处理 (Process)\n遍历数据集',
           shape='box', style='filled,rounded', fillcolor='#BBDEFB')

    # 判断（菱形）
    g.node('cond', '条件满足?\n(Condition Met?)',
           shape='diamond', style='filled', fillcolor='#FFF9C4')

    # 分支操作
    g.node('action', '执行操作 (Action)\n处理当前项',
           shape='box', style='filled,rounded', fillcolor='#BBDEFB')

    g.node('update', '更新状态 (Update)\n记录中间结果',
           shape='box', style='filled,rounded', fillcolor='#BBDEFB')

    # 循环判断
    g.node('more', '还有数据?\n(More Data?)',
           shape='diamond', style='filled', fillcolor='#FFF9C4')

    # 结果输出
    g.node('result', '汇总结果\n(Aggregate Results)',
           shape='box', style='filled,rounded', fillcolor='#FCE4EC')

    # 结束（椭圆）
    g.node('end', '结束\n(End)',
           shape='ellipse', style='filled', fillcolor='#E91E63', fontcolor='white')

    # ---- 边 ----
    g.edge('start', 'init')
    g.edge('init', 'process')
    g.edge('process', 'cond')
    g.edge('cond', 'action', label='是 (Yes)')
    g.edge('cond', 'result', label='否 (No)')
    g.edge('action', 'update')
    g.edge('update', 'more')
    g.edge('more', 'process', label='是 (Yes)')
    g.edge('more', 'result', label='否 (No)')
    g.edge('result', 'end')

    # 渲染 PNG + SVG
    filepath = g.render(filename='flowchart', directory=output_dir, cleanup=True)
    g.format = 'svg'
    g.render(filename='flowchart', directory=output_dir, cleanup=True)
    return filepath


if __name__ == '__main__':
    print(f'流程框图已生成: {create_flowchart()}')
```

---

## B. 框架图 (Framework Diagram)

```python
"""框架图模板 — 用 cluster subgraph 展示分层结构"""

import graphviz


def create_framework(output_dir: str = 'output') -> str:
    """创建框架图并渲染为 PNG + SVG。"""
    g = graphviz.Digraph('framework', format='png')
    g.attr(rankdir='TB', dpi='300')
    g.attr('graph', fontname='PingFang SC',
           label='框架图 (Framework Diagram)', labelloc='t', fontsize='20')
    g.attr('node', fontname='PingFang SC', fontsize='12')
    g.attr('edge', fontname='PingFang SC', fontsize='11')

    # ---- 输入层 ----
    with g.subgraph(name='cluster_input') as c:
        c.attr(label='输入层 (Input Layer)', style='filled', color='#4CAF50',
               bgcolor='#E8F5E9', fontname='PingFang SC', fontsize='14')
        c.node('input_a', '数据源 A\n(Source A)',
               shape='box', style='filled,rounded', fillcolor='white')
        c.node('input_b', '数据源 B\n(Source B)',
               shape='box', style='filled,rounded', fillcolor='white')

    # ---- 处理层 ----
    with g.subgraph(name='cluster_process') as c:
        c.attr(label='处理层 (Processing Layer)', style='filled', color='#2196F3',
               bgcolor='#E3F2FD', fontname='PingFang SC', fontsize='14')
        c.node('clean', '数据清洗\n(Cleaning)',
               shape='box', style='filled,rounded', fillcolor='white')
        c.node('extract', '特征提取\n(Extraction)',
               shape='box', style='filled,rounded', fillcolor='white')
        c.node('infer', '模型推理\n(Inference)',
               shape='box', style='filled,rounded', fillcolor='white')
        # 层内流向
        c.edge('clean', 'extract')
        c.edge('extract', 'infer')

    # ---- 输出层 ----
    with g.subgraph(name='cluster_output') as c:
        c.attr(label='输出层 (Output Layer)', style='filled', color='#E91E63',
               bgcolor='#FCE4EC', fontname='PingFang SC', fontsize='14')
        c.node('result', '结果输出\n(Output)',
               shape='box', style='filled,rounded', fillcolor='white')

    # ---- 层间数据流 ----
    g.edge('input_a', 'clean', label='数据输入')
    g.edge('input_b', 'clean', label='数据输入')
    g.edge('infer', 'result', label='最终结果')

    # 渲染 PNG + SVG
    filepath = g.render(filename='framework', directory=output_dir, cleanup=True)
    g.format = 'svg'
    g.render(filename='framework', directory=output_dir, cleanup=True)
    return filepath


if __name__ == '__main__':
    print(f'框架图已生成: {create_framework()}')
```

---

## C. 概念图 (Concept Map)

```python
"""概念图模板 — 无向图，中心节点辐射展开"""

import graphviz


def create_concept_map(output_dir: str = 'output') -> str:
    """创建概念图并渲染为 PNG + SVG。"""
    # 注意：概念图用 Graph（无向图），不是 Digraph
    g = graphviz.Graph('concept_map', format='png')
    g.attr(rankdir='TB', dpi='300')
    g.attr('graph', fontname='PingFang SC',
           label='概念图 (Concept Map)', labelloc='t', fontsize='20')
    g.attr('node', fontname='PingFang SC', fontsize='12')
    g.attr('edge', fontname='PingFang SC', fontsize='11')

    # ---- 中心节点（椭圆，大号） ----
    g.node('center', '核心主题\n(Core Topic)\n研究/算法名称',
           shape='ellipse', style='filled', fillcolor='#9C27B0', fontcolor='white',
           fontsize='16', width='3', height='1')

    # ---- 一级概念 ----
    g.node('c1', '概念 A\n(Concept A)',
           shape='box', style='filled,rounded', fillcolor='#2196F3', fontcolor='white',
           fontsize='14')
    g.node('c2', '概念 B\n(Concept B)',
           shape='box', style='filled,rounded', fillcolor='#FF9800', fontcolor='white',
           fontsize='14')
    g.node('c3', '概念 C\n(Concept C)',
           shape='box', style='filled,rounded', fillcolor='#4CAF50', fontcolor='white',
           fontsize='14')

    # ---- 二级细节 ----
    g.node('c1a', '细节 A-1\n(Detail A-1)',
           shape='box', style='filled,rounded', fillcolor='#90CAF9', fontsize='11')
    g.node('c1b', '细节 A-2\n(Detail A-2)',
           shape='box', style='filled,rounded', fillcolor='#90CAF9', fontsize='11')
    g.node('c2a', '细节 B-1\n(Detail B-1)',
           shape='box', style='filled,rounded', fillcolor='#FFE0B2', fontsize='11')
    g.node('c3a', '细节 C-1\n(Detail C-1)',
           shape='box', style='filled,rounded', fillcolor='#A5D6A7', fontsize='11')
    g.node('c3b', '细节 C-2\n(Detail C-2)',
           shape='box', style='filled,rounded', fillcolor='#A5D6A7', fontsize='11')

    # ---- 中心到一级 ----
    g.edge('center', 'c1', label='维度一', fontsize='11')
    g.edge('center', 'c2', label='维度二', fontsize='11')
    g.edge('center', 'c3', label='维度三', fontsize='11')

    # ---- 一级到二级 ----
    g.edge('c1', 'c1a', label='展开')
    g.edge('c1', 'c1b', label='展开')
    g.edge('c2', 'c2a')
    g.edge('c3', 'c3a')
    g.edge('c3', 'c3b')

    # 渲染 PNG + SVG
    filepath = g.render(filename='concept_map', directory=output_dir, cleanup=True)
    g.format = 'svg'
    g.render(filename='concept_map', directory=output_dir, cleanup=True)
    return filepath


if __name__ == '__main__':
    print(f'概念图已生成: {create_concept_map()}')
```

---

## D. 机制图 (Mechanism)

```python
"""机制图模板 — 双向边、反馈环，使用 neato 引擎实现自由布局"""

import graphviz


def create_mechanism(output_dir: str = 'output') -> str:
    """创建机制图并渲染为 PNG + SVG。"""
    g = graphviz.Digraph('mechanism', format='png', engine='neato')
    g.attr(dpi='300', overlap='false', splines='true')
    g.attr('graph', fontname='PingFang SC',
           label='机制图 (Mechanism Diagram)', labelloc='t', fontsize='20')
    g.attr('node', fontname='PingFang SC', fontsize='12')
    g.attr('edge', fontname='PingFang SC', fontsize='11')

    # ---- 主路径节点 ----
    g.node('input', '输入信号\n(Input)',
           shape='box', style='filled,rounded', fillcolor='#4CAF50', fontcolor='white',
           pos='0,0!')
    g.node('mod_a', '处理模块 A\n(Module A)',
           shape='box', style='filled,rounded', fillcolor='#2196F3', fontcolor='white',
           pos='3,0!')
    g.node('mod_b', '处理模块 B\n(Module B)',
           shape='box', style='filled,rounded', fillcolor='#2196F3', fontcolor='white',
           pos='6,0!')
    g.node('output', '输出结果\n(Output)',
           shape='box', style='filled,rounded', fillcolor='#E91E63', fontcolor='white',
           pos='9,0!')

    # ---- 辅助模块 ----
    g.node('aux', '辅助模块\n(Auxiliary)',
           shape='box', style='filled,rounded', fillcolor='#FF9800', fontcolor='white',
           pos='4.5,-2!')

    # ---- 主路径边 ----
    g.edge('input', 'mod_a', label='信号传递')
    g.edge('mod_a', 'mod_b', label='中间结果')
    g.edge('mod_b', 'output', label='最终输出')

    # ---- 反馈环（虚线） ----
    g.edge('output', 'mod_a', label='反馈调节\n(Feedback)',
           style='dashed', color='#9C27B0', fontcolor='#9C27B0')

    # ---- 辅助连接 ----
    g.edge('aux', 'mod_a', label='辅助输入', style='dashed')
    g.edge('aux', 'mod_b', label='辅助输入', style='dashed')

    # ---- 旁路信号 ----
    g.edge('input', 'mod_b', label='旁路信号\n(Bypass)',
           style='dotted', color='#FF9800', fontcolor='#FF9800')

    # 渲染 PNG + SVG
    filepath = g.render(filename='mechanism', directory=output_dir, cleanup=True)
    g.format = 'svg'
    g.render(filename='mechanism', directory=output_dir, cleanup=True)
    return filepath


if __name__ == '__main__':
    print(f'机制图已生成: {create_mechanism()}')
```

---

## E. 泳道图 (Swimlane Diagram)

> **注意**：时序图（Sequence Diagram）不推荐用 Graphviz，请使用 Mermaid `sequenceDiagram`。

```python
"""泳道图模板 — 横向排列泳道，每泳道纵向排列步骤"""

import graphviz


def create_swimlane(output_dir: str = 'output') -> str:
    """创建泳道图并渲染为 PNG + SVG。"""
    g = graphviz.Digraph('swimlane', format='png')
    g.attr(rankdir='LR', dpi='300')
    g.attr('graph', fontname='PingFang SC',
           label='泳道图 (Swimlane Diagram)', labelloc='t', fontsize='20')
    g.attr('node', fontname='PingFang SC', fontsize='12')
    g.attr('edge', fontname='PingFang SC', fontsize='11')

    # ---- 泳道 1：角色 A ----
    with g.subgraph(name='cluster_lane_a') as c:
        c.attr(label='角色 A (Role A)', style='filled', color='#4CAF50',
               bgcolor='#E8F5E9', fontname='PingFang SC', fontsize='14')
        c.node('s1', '① 接收请求\n(Receive Request)',
               shape='box', style='filled,rounded', fillcolor='white')
        c.node('s2', '② 初步验证\n(Validate)',
               shape='box', style='filled,rounded', fillcolor='white')
        # 泳道内流转
        c.edge('s1', 's2')

    # ---- 泳道 2：角色 B ----
    with g.subgraph(name='cluster_lane_b') as c:
        c.attr(label='角色 B (Role B)', style='filled', color='#2196F3',
               bgcolor='#E3F2FD', fontname='PingFang SC', fontsize='14')
        c.node('s3', '③ 核心处理\n(Core Process)',
               shape='box', style='filled,rounded', fillcolor='white')
        c.node('s4', '④ 结果校验\n(Verify)',
               shape='diamond', style='filled', fillcolor='#FFF9C4')

    # ---- 泳道 3：角色 C ----
    with g.subgraph(name='cluster_lane_c') as c:
        c.attr(label='角色 C (Role C)', style='filled', color='#E91E63',
               bgcolor='#FCE4EC', fontname='PingFang SC', fontsize='14')
        c.node('s5', '⑤ 输出生成\n(Generate Output)',
               shape='box', style='filled,rounded', fillcolor='white')
        c.node('s6', '⑥ 交付完成\n(Deliver)',
               shape='box', style='filled,rounded', fillcolor='white')
        c.edge('s5', 's6')

    # ---- 跨泳道流转 ----
    g.edge('s2', 's3', label='验证通过')
    g.edge('s3', 's4', label='处理完成')
    g.edge('s4', 's5', label='校验通过')
    # 回退路径（虚线）
    g.edge('s4', 's3', label='校验失败\n(Fallback)',
           style='dashed', color='#FF9800')

    # 渲染 PNG + SVG
    filepath = g.render(filename='swimlane', directory=output_dir, cleanup=True)
    g.format = 'svg'
    g.render(filename='swimlane', directory=output_dir, cleanup=True)
    return filepath


if __name__ == '__main__':
    print(f'泳道图已生成: {create_swimlane()}')
```

---

## F. 总结图 (Summary)

```python
"""总结图模板 — 无向图做方案对比"""

import graphviz


def create_summary(output_dir: str = 'output') -> str:
    """创建总结图并渲染为 PNG + SVG。"""
    g = graphviz.Graph('summary', format='png')
    g.attr(rankdir='LR', dpi='300')
    g.attr('graph', fontname='PingFang SC',
           label='总结图 (Summary Diagram)', labelloc='t', fontsize='20')
    g.attr('node', fontname='PingFang SC', fontsize='12')
    g.attr('edge', fontname='PingFang SC', fontsize='11')

    # ---- 共同输入 ----
    g.node('input', '共同输入\n(Common Input)',
           shape='box', style='filled,rounded', fillcolor='#4CAF50', fontcolor='white',
           fontsize='14')

    # ---- 方案 A ----
    with g.subgraph(name='cluster_plan_a') as c:
        c.attr(label='方案 A (Plan A)', style='filled', color='#2196F3',
               bgcolor='#E3F2FD', fontname='PingFang SC', fontsize='14')
        c.node('a1', '特点 1\n(Feature 1)',
               shape='box', style='filled,rounded', fillcolor='white')
        c.node('a2', '特点 2\n(Feature 2)',
               shape='box', style='filled,rounded', fillcolor='white')
        c.edge('a1', 'a2')

    # ---- 方案 B ----
    with g.subgraph(name='cluster_plan_b') as c:
        c.attr(label='方案 B (Plan B)', style='filled', color='#FF9800',
               bgcolor='#FFF3E0', fontname='PingFang SC', fontsize='14')
        c.node('b1', '特点 1\n(Feature 1)',
               shape='box', style='filled,rounded', fillcolor='white')
        c.node('b2', '特点 2\n(Feature 2)',
               shape='box', style='filled,rounded', fillcolor='white')
        c.edge('b1', 'b2')

    # ---- 选择结果 ----
    g.node('pick', '选择结果\n(Selection)',
           shape='box', style='filled,rounded', fillcolor='#E91E63', fontcolor='white',
           fontsize='14')

    # ---- 连接 ----
    g.edge('input', 'a1')
    g.edge('input', 'b1')
    g.edge('a2', 'pick', label='推荐 (Recommended)', fontsize='11', color='#2196F3')
    g.edge('b2', 'pick', label='备选 (Alternative)', fontsize='11',
           style='dashed', color='#FF9800')

    # 渲染 PNG + SVG
    filepath = g.render(filename='summary', directory=output_dir, cleanup=True)
    g.format = 'svg'
    g.render(filename='summary', directory=output_dir, cleanup=True)
    return filepath


if __name__ == '__main__':
    print(f'总结图已生成: {create_summary()}')
```
