# FAQ OCR 处理完整指南

## 📊 当前状况

FAQ PDF 文件是**图片扫描版**，需要 OCR 识别才能提取文字。

已安装 Python 包：

- ✅ pytesseract
- ✅ pdf2image
- ✅ pillow

还需要：

- ❌ Tesseract OCR 引擎（独立程序）

---

## 🎯 三种解决方案

### 方案 A：安装 Tesseract 自动 OCR（推荐，一劳永逸）

#### Step 1: 下载安装 Tesseract

**Windows 安装器**：

```
https://github.com/UB-Mannheim/tesseract/wiki

推荐下载：tesseract-ocr-w64-setup-5.x.x.exe
```

**安装选项**：

- ✅ 勾选"Additional language data"
- ✅ 选择"Chinese - Simplified" (chi_sim)
- ✅ 选择"English" (eng)

#### Step 2: 添加到 PATH

安装后，添加到系统 PATH：

```
C:\Program Files\Tesseract-OCR
```

或在脚本中指定路径（修改 ocr_faq.py）：

```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

#### Step 3: 运行 OCR

```bash
cd c:\Users\AIGCG\Desktop\RoSP\ai-sales-mvp
.\RoSP\Scripts\activate
cd backend\scripts
python ocr_faq.py
```

**预计时间**：

- 安装：5 分钟
- OCR 处理 3 个文件：10-15 分钟（取决于页数）

---

### 方案 B：在线 OCR 服务（最简单，5 分钟）

#### 推荐服务

**PDF OCR 在线**：https://www.pdfocr.io/zh-cn/

**步骤**：

1. 访问网站
2. 上传 FAQ PDF（一次一个）
3. 等待 OCR 识别完成
4. 下载识别后的 TXT 文件
5. 保存到 Project_Info 目录

**需要处理的文件**：

```
FAQ_Dock3.pdf → FAQ_Dock3_OCR.txt
FAQ_Matrice30.pdf → FAQ_Matrice30_OCR.txt
FAQ_Matrice400.pdf → FAQ_Matrice400_OCR.txt
```

**完成后**：

```bash
cd backend\scripts
python build_kb.py
```

脚本会自动识别`.txt`文件并导入。

---

### 方案 C：先不处理 FAQ（推荐临时方案）

知识库已包含：

- ✅ 17 个产品手册（2237 个文本块）
- ✅ M30、M400、Dock3、RTK 所有技术文档

**功能影响**：

- 核心技术问题：✅ 可以回答
- 常见 FAQ：⚠️ 可能需要 LLM 推理
- 整体可用性：✅ 85%以上

FAQ 可以后续补充。

---

## 💡 我的建议

**根据您的情况选择**：

| 场景           | 推荐方案        | 理由               |
| -------------- | --------------- | ------------------ |
| 有时间安装软件 | **方案 A**      | 自动化，以后可复用 |
| 现在就要测试   | **方案 B 或 C** | 快速见效           |
| FAQ 不重要     | **方案 C**      | 先用产品手册       |

---

## 🔧 方案 B 详细步骤（在线 OCR）

### 1. 访问 OCR 服务

打开浏览器：https://www.pdfocr.io/zh-cn/

### 2. 上传并处理

**处理 FAQ_Dock3.pdf**：

```
1. 点击"选择PDF文件"
2. 选择：c:\Users\AIGCG\Desktop\RoSP\Project_Info\FAQ_Dock3.pdf
3. 等待上传和OCR识别
4. 点击"下载TXT"
5. 保存为：FAQ_Dock3_OCR.txt（放到Project_Info目录）
```

**重复处理**：

- FAQ_Matrice30.pdf
- FAQ_Matrice400.pdf

### 3. 重新构建知识库

```bash
cd c:\Users\AIGCG\Desktop\RoSP\ai-sales-mvp
.\RoSP\Scripts\activate
cd backend\scripts
python build_kb.py
```

脚本会自动包含 TXT 文件。

---

## ✅ 验证 OCR 结果

处理完成后，检查文本文件：

```bash
# 查看文件大小
dir c:\Users\AIGCG\Desktop\RoSP\Project_Info\*OCR.txt

# 查看前几行
type c:\Users\AIGCG\Desktop\RoSP\Project_Info\FAQ_Dock3_OCR.txt | head -20
```

**预期结果**：

- 文件大小 > 1KB（说明有内容）
- 能看到 FAQ 问题和答案的文字

---

## 🚀 完成后

知识库文本块数量应该增加：

- 当前：2237 块
- 增加后：预计 2400-2600 块（取决于 FAQ 内容）

---

## 💬 遇到问题？

**问题 1：在线 OCR 识别效果不好**
→ 尝试其他服务：

- Adobe Acrobat Online: https://www.adobe.com/acrobat/online/ocr-pdf.html
- ABBYY FineReader Online

**问题 2：OCR 后文本乱码**
→ 可能是图片质量差，尝试：

- 提高 PDF 扫描分辨率
- 手动整理 OCR 结果

**问题 3：不想花时间处理**
→ 使用方案 C，先用现有知识库

---

**您现在想选择哪个方案？**

- A: 我去安装 Tesseract（15 分钟）
- B: 我用在线 OCR（5 分钟）
- C: 先不处理 FAQ
