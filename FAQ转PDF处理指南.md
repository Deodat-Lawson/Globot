# FAQ 文档转 PDF 处理指南

## 📋 操作步骤

### 方案 A：使用 Word 转 PDF（推荐）

**步骤**：

1. 用 Microsoft Word 打开 DOCX 文件
2. 文件 → 另存为 → 选择"PDF"格式
3. 保存到同一目录（Project_Info）

**需要转换的文件**：

- FAQ_Dock3.docx → FAQ_Dock3.pdf
- FAQ_Matrice30.docx → FAQ_Matrice30.pdf
- FAQ_Matrice400.docx → FAQ_Matrice400.pdf

**完成后告诉我**，我会重新运行知识库构建脚本！

---

### 方案 B：批量转换（如果有很多文件）

如果您有 WPS Office 或其他 PDF 转换工具，也可以直接用。

---

### 方案 C：我帮您用更好的 DOCX 解析器（无需转 PDF）

如果不想转 PDF，我可以：

1. **安装更强大的 DOCX 解析库**

```bash
.\RoSP\Scripts\activate
pip install python-docx
```

2. **修改 build_kb.py 使用 python-docx**

```python
# 替换 Docx2txtLoader 为 python-docx
from docx import Document

def load_docx(file_path):
    doc = Document(file_path)
    text = []
    for para in doc.paragraphs:
        text.append(para.text)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                text.append(cell.text)
    return '\n'.join(text)
```

**优点**：

- 能提取表格内容
- 能提取文本框
- 更完整的内容

---

## 🎯 我的建议

**如果 FAQ 只有 3 个文件**：
→ **方案 A（Word 转 PDF）** - 最简单快速

**如果想保持原始格式**：
→ **方案 C（python-docx）** - 我来修改代码

---

## 转换后的操作

一旦您转换完成（或选择方案 C）：

```bash
# 1. 激活虚拟环境
cd c:\Users\AIGCG\Desktop\RoSP\ai-sales-mvp
.\RoSP\Scripts\activate

# 2. 重新构建知识库
cd backend\scripts
python build_kb.py

# 3. 测试新的FAQ检索
python build_kb.py --test
```

---

## 📊 预期结果

转换后应该能看到：

```
INFO:__main__:📄 处理文件: FAQ_Dock3.pdf
INFO:__main__:  ✅ 成功: XX 个文本块, 产品:Dock3, 类型:faq

INFO:__main__:📄 处理文件: FAQ_Matrice30.pdf
INFO:__main__:  ✅ 成功: XX 个文本块, 产品:M30, 类型:faq

INFO:__main__:📄 处理文件: FAQ_Matrice400.pdf
INFO:__main__:  ✅ 成功: XX 个文本块, 产品:M400, 类型:faq
```

最终文本块数量应该从 2237 增加到 2400+ 左右（取决于 FAQ 内容）

---

**您选择哪个方案？**

- A: 我去转 PDF（最简单）
- B: 帮我用 python-docx 处理（我来修改代码）
- C: 先保持现状，FAQ 后续再补充
