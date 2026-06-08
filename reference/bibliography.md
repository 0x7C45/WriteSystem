# AIGC检测算法研究参考文献目录

> 生成日期: 2026-05-29
> 涵盖范围: 2019-2026，含检测方法、对抗攻击、反检测技术

---

## 一、基础检测方法 (Foundational Detection Methods)

### [1] GLTR: Statistical Detection and Visualization of Generated Text
- **作者**: Sebastian Gehrmann, Hendrik Strobelt, Alexander M. Rush
- **发表**: ACL 2019 Demo Track
- **arXiv**: 1906.04043
- **核心贡献**: 首个系统性的生成文本统计检测工具。基于语言模型对每个token的排名分布进行可视化，利用生成文本倾向于使用高概率token的特性进行检测。人类使用GLTR后检测率从54%提升至72%。
- **检测原理**: Rank-based token analysis; 观察token在模型词汇表中的排名分布
- **PDF**: https://arxiv.org/pdf/1906.04043

### [2] A Watermark for Large Language Models
- **作者**: John Kirchenbauer, Jonas Geiping, Yuxin Wen, Jonathan Katz, Ian Miers, Tom Goldstein
- **发表**: ICML 2023
- **arXiv**: 2301.10226 (v4, May 2024)
- **核心贡献**: 提出在LLM生成过程中嵌入不可见水印的框架。通过在生成前随机选择一组"绿色"token，并软性地提高这些token的采样概率来嵌入水印。提出基于统计检验的p值检测方法，并给出信息论分析框架。
- **检测原理**: 统计假设检验; 绿色token比例; z-score检测
- **PDF**: https://arxiv.org/pdf/2301.10226

### [3] DetectGPT: Zero-Shot Machine-Generated Text Detection using Probability Curvature
- **作者**: Eric Mitchell, Yoonho Lee, Alexander Khazatsky, Christopher D. Manning, Chelsea Finn
- **发表**: ICML 2023
- **arXiv**: 2301.11305 (v2, Jul 2023)
- **核心贡献**: 发现LLM生成的文本倾向于位于模型对数概率函数的负曲率区域。利用这一特性，通过对文本进行随机扰动（使用T5等模型），比较原始文本与扰动文本的对数概率差异来进行检测。在GPT-NeoX 20B生成的假新闻检测上达到0.95 AUROC。
- **检测原理**: Probability curvature; 扰动敏感性分析; log probability对比
- **PDF**: https://arxiv.org/pdf/2301.11305

### [4] Fast-DetectGPT: Efficient Zero-Shot Detection of Machine-Generated Text via Conditional Probability Curvature
- **作者**: Guangsheng Bao, Yanbin Zhao, Zhiyang Teng, Linyi Yang, Yue Zhang
- **发表**: ICLR 2024
- **arXiv**: 2310.05130
- **核心贡献**: 对DetectGPT的显著加速版本。使用条件概率曲率替代原始的概率曲率计算，大幅降低计算成本的同时保持甚至提升检测性能。
- **检测原理**: Conditional probability curvature; 高效采样策略; 无需多次模型调用
- **PDF**: https://arxiv.org/pdf/2310.05130

---

## 二、鲁棒检测方法 (Robust Detection)

### [5] RADAR: Robust AI-Text Detection via Adversarial Learning
- **作者**: Xiaomeng Hu, Pin-Yu Chen, Tsung-Yi Ho
- **发表**: NeurIPS 2023
- **arXiv**: 2307.03838 (v2, Oct 2023)
- **核心贡献**: 提出对抗训练框架，联合训练释义器(paraphraser)和检测器(detector)。释义器试图生成能逃避检测的真实内容，检测器则利用释义器的反馈进行对抗学习。在8种LLM和4个数据集上显著超越现有方法，特别是在存在释义攻击的场景下。
- **检测原理**: 对抗训练; paraphraser-detector联合优化; 鲁棒特征学习
- **PDF**: https://arxiv.org/pdf/2307.03838

---

## 三、高级检测方法 (Advanced Detection)

### [6] Reasoning-Aware AIGC Detection via Alignment and Reinforcement
- **作者**: Zhao Wang, Max Xiong, Jianxun Lian, Zhicheng Dou
- **发表**: April 2026
- **arXiv**: 2604.19172
- **核心贡献**: 引入推理感知的AIGC检测方法。通过对齐和强化学习，使检测器能够理解文本中的推理逻辑链，从而更准确地判断文本是否为AI生成。
- **检测原理**: Reasoning-aware detection; 逻辑一致性分析; 对齐+强化学习
- **PDF**: https://arxiv.org/pdf/2604.19172

### [7] Log-Likelihood, Simpson's Paradox, and the Detection of Machine-Generated Text
- **作者**: Tom Kempton, Viktor Drobnyi, Maeve Madigan, Stuart Burrell
- **发表**: May 2026
- **arXiv**: 2605.06294
- **核心贡献**: 揭示对数似然检测中的辛普森悖论——在聚合层面有效的检测信号可能在分组后消失或反转。对基于似然的检测方法提出根本性质疑。
- **检测原理**: 对数似然分析的局限性; 辛普森悖论; 分组vs聚合
- **PDF**: https://arxiv.org/pdf/2605.06294

---

## 四、水印方法 (Watermarking)

### [8] TimeMark: A Trustworthy Time Watermarking Framework for Exact Generation-Time Recovery from AIGC
- **作者**: Shangkun Che, Silin Du, Ge Gao
- **发表**: April 2026
- **arXiv**: 2604.12216
- **核心贡献**: 提出可信的时间水印框架，能精确恢复AIGC内容的生成时间。增强了水印的不可伪造性和时间戳验证能力。
- **检测原理**: 时间编码水印; 精确生成时间恢复; 密码学可信验证
- **PDF**: https://arxiv.org/pdf/2604.12216

---

## 五、检测对抗/反检测方法 (Evasion & Counter-Detection)

### [9] Adversarial Paraphrasing: A Universal Attack for Humanizing AI-Generated Text
- **作者**: Yize Cheng, Vinu Sankar Sadasivan, Mehrdad Saberi, Shoumik Saha, Soheil Feizi
- **发表**: NeurIPS 2025
- **arXiv**: 2506.07001 (v2, Oct 2025)
- **核心贡献**: **本研究的关键参考文献**。提出无训练的对抗性释义攻击框架，利用现成的指令遵循LLM，在AI文本检测器的引导下对AI生成内容进行对抗性改写。平均使检测器的T@1%F降低87.88%（在OpenAI-RoBERTa-Large指导下）。对RADAR降低64.49%，对Fast-DetectGPT降低惊人的98.96%。
- **反检测原理**: 检测器引导的对抗性改写; 迭代优化; 多检测器迁移攻击
- **PDF**: https://arxiv.org/pdf/2506.07001

### [10] AuthorMist: Evading AI Text Detectors with Reinforcement Learning
- **作者**: Isaac David, Arthur Gervais
- **发表**: March 2025
- **arXiv**: 2503.08716
- **核心贡献**: 使用强化学习训练专门的改写模型以逃避AI文本检测器。将检测器分数作为奖励信号，训练策略模型生成难以检测的改写文本。
- **反检测原理**: RL-based改写; 检测分数作为奖励; 策略梯度优化
- **PDF**: https://arxiv.org/pdf/2503.08716

### [11] StealthRL: Reinforcement Learning Paraphrase Attacks for Multi-Detector Evasion of AI-Text Detectors
- **作者**: Suraj Ranganath, Atharv Ramesh
- **发表**: February 2026
- **arXiv**: 2602.08934
- **核心贡献**: 扩展了RL-based攻击，实现同时对多个检测器（多目标）的逃避。使用多目标强化学习同时优化针对多个不同检测器的逃避性能。
- **反检测原理**: Multi-objective RL; 多检测器联合逃避; 策略蒸馏
- **PDF**: https://arxiv.org/pdf/2602.08934

### [12] SilverSpeak: Evading AI-Generated Text Detectors using Homoglyphs
- **作者**: Aldan Creo, Shushanta Pudasaini
- **发表**: COLING 2025 Workshop on Detecting AI Generated Content
- **arXiv**: 2406.11239
- **核心贡献**: 提出使用同形字符（homoglyphs）替换来逃避AI文本检测。利用视觉上相似但编码不同的Unicode字符替换文本中的字符，使得检测器的分词和统计特征失效。
- **反检测原理**: Homoglyph替换; Unicode混淆; 分词器攻击
- **PDF**: https://arxiv.org/pdf/2406.11239

### [13] PADBen: A Comprehensive Benchmark for Evaluating AI Text Detectors Against Paraphrase Attacks
- **作者**: Yiwei Zha, Rui Min, Shanu Sushmita
- **发表**: November 2025
- **arXiv**: 2511.00416
- **核心贡献**: 建立全面的基准测试框架，系统评估各种AI文本检测器对抗释义攻击的鲁棒性。
- **PDF**: https://arxiv.org/pdf/2511.00416

---

## 六、综述与评估

### [14] A Practical Examination of AI-Generated Text Detectors for Large Language Models
- **作者**: Brian Tufts, Xuandong Zhao, Lei Li
- **发表**: December 2024
- **arXiv**: 2412.05139
- **核心贡献**: 对现有AI文本检测器进行实用的系统性评估，揭示各方法在实际场景中的性能局限和脆弱性。
- **PDF**: https://arxiv.org/pdf/2412.05139

### [15] Reliable and Responsible Foundation Models: A Comprehensive Survey
- **作者**: Xinyu Yang, Junlin Han, Rishi Bommasani et al. (35+ authors)
- **发表**: February 2026
- **arXiv**: 2602.08145
- **核心贡献**: 基础模型的可靠性与责任性综述，包含AIGC检测与水印相关章节。
- **PDF**: https://arxiv.org/pdf/2602.08145

---

## 附录：检测方法分类速查表

| 类别 | 代表方法 | 核心技术原理 | 是否需要模型访问 | 脆弱性 |
|------|---------|-------------|-----------------|--------|
| 统计特征 | GLTR | Token排名分布 | 需白盒/灰盒 | 高(改写可绕过) |
| 概率曲率 | DetectGPT, Fast-DetectGPT | Log概率曲率+扰动 | 需白盒 | 中(对抗性改写) |
| 水印 | Kirchenbauer, TimeMark | Token采样偏向+统计检验 | 生成时嵌入 | 低(需密码学攻击) |
| 对抗训练 | RADAR | Paraphraser-Detector联合训练 | 需分类器训练 | 中(迁移攻击) |
| 似然分析 | Log-likelihood methods | Perplexity/Burstiness | 需白盒/灰盒 | 高(辛普森悖论) |
| 神经网络分类器 | GPTZero, RoBERTa-classifier | 端到端二分类 | 黑盒 | 中(同形字攻击) |
