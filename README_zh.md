# 家庭社会经济地位、数字学习资源与学生学业表现：基于 PISA 2022 的跨国证据

## 复现包说明文档

本仓库包含论文**《家庭社会经济地位、数字学习资源与学生学业表现：基于 PISA 2022 的跨国证据》**的完整复现数据下载脚本与数据分析代码。

关于英文版的说明文档，请参阅 [README.md](README.md)。

---

## 1. 仓库结构

```text
replication_package/
├── data/                 # 原始 PISA 2022 数据占位文件夹
│   ├── README.md         # 原始数据下载指南（英文版）
│   └── README_zh.md      # 原始数据下载指南（中文版）
├── scripts/              # Python 数据处理与分析脚本
│   ├── download_data.py  # 自动下载和解压数据的脚本
│   ├── fast_download.py  # 用于多线程分块快速下载的依赖脚本
│   ├── get_tables.py     # 生成描述性统计表和相关系数矩阵的脚本
│   ├── plot_results.py   # 绘制交互效应图的脚本（手稿中的图 2 和图 3）
│   └── run_regression.py # 执行基于 Rubin 规则的 WLS 聚类稳健回归分析脚本
└── README_zh.md          # 本文件（中文版复现指南）
```

---

## 2. 环境依赖

所有分析均在 **Python 3.12** 环境下测试运行（兼容 Python 3.8+）。在运行代码前，请在您的终端中执行以下命令安装所需的第三方库：

```bash
pip install pandas numpy statsmodels requests pyreadstat matplotlib seaborn
```

*注意：`pyreadstat` 是读取 OECD 提供的原始 SPSS 格式数据（`.sav` 后缀）所必需的依赖包。*

---

## 3. 逐步复现指南

请按照以下顺序执行脚本，以复现手稿中的全部数据表格和分析图表：

### 步骤 1：下载 PISA 2022 原始数据
您可以使用我们提供的下载脚本，自动从 OECD 服务器拉取数据。请在项目根目录下运行：

```bash
python scripts/download_data.py
```

*脚本作用：* 该脚本将自动从 OECD 服务器下载学生问卷数据（`STU_QQQ_SPSS.zip`）和学校问卷数据（`SCH_QQQ_SPSS.zip`），将其解压为原始 Sav 文件（`CY08MSP_STU_QQQ.sav` 和 `CY08MSP_SCH_QQQ.sav`），并保存在 `data/` 目录下。
*(注意：文件总大小约为 1.5 GB，请确保网络连接稳定)*。

**备选方案（手动下载）：**  
如果自动下载脚本由于网络原因失败，您可以手动访问 [OECD PISA 2022 数据库官网](https://www.oecd.org/pisa/data/2022database/)，下载 SPSS 格式的 Student questionnaire data 和 School questionnaire data。解压后将以下两个文件直接放入 `data/` 目录中：
1. `CY08MSP_STU_QQQ.sav`
2. `CY08MSP_SCH_QQQ.sav`

---

### 步骤 2：运行回归分析
执行加权最小二乘回归（WLS），包含学校聚类稳健标准误，并使用 Rubin 规则合并 10 个 Plausible Values（合理值）：

```bash
python scripts/run_regression.py
```

*复现结果：* 该脚本将对数据进行清洗，筛选出文章分析的 10 个国家样本，标准化连续自变量，并运行数学、阅读和科学的 Models 1–4。回归模型总结和系数表（即手稿中的 **Table 4** 和 **Table 5**）将自动输出并保存在根目录下的 `regression_results.txt` 文件中。

---

### 步骤 3：生成描述性统计表格
运行以下命令以生成样本分布表、描述性统计和相关系数矩阵：

```bash
python scripts/get_tables.py
```

*复现结果：* 该脚本将在终端控制台中直接格式化打印出样本国家与样本量构成（**Table 1**）、变量描述性统计（**Table 2**）和变量相关性矩阵（**Table 3**），您可以直接对照手稿数据进行核对。

---

### 步骤 4：生成交互效应分析图
运行以下命令绘制展示家庭和学校数字资源“补偿效应”的交互作用折线图：

```bash
python scripts/plot_results.py
```

*复现结果：* 该脚本将绘制分析图并将其保存在根目录下自动创建的 `figures/` 文件夹中：
- `fig_interaction_home_math.png`（家庭数字资源与 ESCS 的交互效应，即 **Figure 2**）
- `fig_interaction_school_math.png`（学校生均电脑比率与 ESCS 的交互效应，即 **Figure 3**）

---

## 4. 论文引用

如果您在学术工作中使用到了本复现包的代码或分析结果，请引用我们的论文：

```text
[论文录用后将补充引用格式]
```

---

## 5. 联系与支持

如对代码复现有任何疑问，请通过审稿系统或匿名代码库的相关渠道与作者联系（联系方式将在论文录用后补充）。
