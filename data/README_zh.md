# PISA 2022 原始数据占位文件夹

本文件夹是复现所必需的 PISA 2022 SPSS 原始数据集的存放位置。由于数据文件体积庞大（总计约 1.5 GB），因此未直接打包上传至 GitHub 代码库。

关于英文版的下载指南，请参阅 [README.md](README.md)。

## 获取说明

要使复现代码成功运行，您必须将以下原始数据文件存放在本目录下：

1.  **`CY08MSP_STU_QQQ.sav`** （学生问卷数据）
2.  **`CY08MSP_SCH_QQQ.sav`** （学校问卷数据）

### 方案 A：自动下载（推荐）
直接在仓库根目录下运行下载脚本：
```bash
python scripts/download_data.py
```
这将会自动从 OECD 官网抓取、解压并放置这两份 `.sav` 数据文件到当前文件夹。

---

### 方案 B：手动下载
如果自动下载脚本失败，您可以手动获取：
1.  访问官方的 [OECD PISA 2022 数据库网页](https://www.oecd.org/pisa/data/2022database/)。
2.  定位并下载：
    *   **Student questionnaire data (SPSS™ format)** (`STU_QQQ_SPSS.zip`)
    *   **School questionnaire data (SPSS™ format)** (`SCH_QQQ_SPSS.zip`)
3.  解压这两个压缩包，并将解压得到的 `.sav` 格式数据文件（`CY08MSP_STU_QQQ.sav` 与 `CY08MSP_SCH_QQQ.sav`）移动到当前文件夹内。
