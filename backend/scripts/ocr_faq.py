# """
# OCR处理FAQ PDF文档
# 将图片PDF转换为可搜索的文本
# """
# import sys
# from pathlib import Path
# import os

# # 检查是否安装了Tesseract
# def check_tesseract():
#     """检查Tesseract是否安装"""
#     import subprocess
#     try:
#         result = subprocess.run(['tesseract', '--version'], 
#                               capture_output=True, text=True)
#         if result.returncode == 0:
#             print("✅ Tesseract已安装")
#             return True
#     except FileNotFoundError:
#         pass
    
#     print("❌ Tesseract未安装")
#     print("\n请安装Tesseract OCR:")
#     print("1. 下载: https://github.com/UB-Mannheim/tesseract/wiki")
#     print("2. 安装后添加到PATH")
#     print("3. 或指定路径: pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'")
#     return False

# def ocr_pdf_simple(pdf_path: str, output_txt: str):
#     """
#     简单OCR处理（使用在线服务或手动）
    
#     由于Tesseract需要额外安装，这里提供替代方案
#     """
#     print(f"\n📄 处理文件: {Path(pdf_path).name}")
#     print("使用在线OCR服务:")
#     print(f"1. 访问: https://www.pdfocr.io/zh-cn/")
#     print(f"2. 上传: {pdf_path}")
#     print(f"3. 下载识别后的文本")
#     print(f"4. 保存为: {output_txt}")

# def ocr_pdf_with_tesseract(pdf_path: str, output_txt: str):
#     """
#     使用Tesseract OCR处理PDF
#     """
#     try:
#         import pytesseract
#         from pdf2image import convert_from_path
#         from PIL import Image
        
#         print(f"\n📄 处理文件: {Path(pdf_path).name}")
        
#         # 转换PDF为图片
#         print("  🔄 转换PDF为图片...")
#         images = convert_from_path(pdf_path, dpi=300)
        
#         # OCR识别
#         print(f"  🔍 OCR识别中 (共{len(images)}页)...")
#         text_content = []
        
#         for i, image in enumerate(images, 1):
#             # 识别中文和英文
#             text = pytesseract.image_to_string(image, lang='chi_sim+eng')
#             text_content.append(f"\n--- 第{i}页 ---\n{text}")
#             print(f"    ✅ 第{i}/{len(images)}页完成")
        
#         # 保存文本
#         full_text = '\n'.join(text_content)
#         with open(output_txt, 'w', encoding='utf-8') as f:
#             f.write(full_text)
        
#         print(f"  ✅ 保存到: {output_txt}")
#         print(f"  📊 提取文本: {len(full_text)} 字符")
        
#         return True
        
#     except Exception as e:
#         print(f"  ❌ OCR失败: {e}")
#         return False

# def main():
#     """主函数"""
#     print("="*60)
#     print("🔍 FAQ PDF OCR处理")
#     print("="*60)
    
#     # FAQ文件路径
#     faq_files = [
#         ("c:\\Users\\AIGCG\\Desktop\\RoSP\\Project_Info\\FAQ_Dock3.pdf",
#          "c:\\Users\\AIGCG\\Desktop\\RoSP\\Project_Info\\FAQ_Dock3_OCR.txt"),
#         ("c:\\Users\\AIGCG\\Desktop\\RoSP\\Project_Info\\FAQ_Matrice30.pdf",
#          "c:\\Users\\AIGCG\\Desktop\\RoSP\\Project_Info\\FAQ_Matrice30_OCR.txt"),
#         ("c:\\Users\\AIGCG\\Desktop\\RoSP\\Project_Info\\FAQ_Matrice400.pdf",
#          "c:\\Users\\AIGCG\\Desktop\\RoSP\\Project_Info\\FAQ_Matrice400_OCR.txt"),
#     ]
    
#     # 检查Tesseract
#     has_tesseract = check_tesseract()
    
#     if not has_tesseract:
#         print("\n" + "="*60)
#         print("💡 使用在线OCR服务（推荐）")
#         print("="*60)
#         for pdf_path, txt_path in faq_files:
#             ocr_pdf_simple(pdf_path, txt_path)
        
#         print("\n" + "="*60)
#         print("完成OCR后，运行知识库构建:")
#         print("  cd backend\\scripts")
#         print("  python build_kb.py")
#         print("="*60)
#     else:
#         print("\n开始OCR处理...")
#         success_count = 0
        
#         for pdf_path, txt_path in faq_files:
#             if ocr_pdf_with_tesseract(pdf_path, txt_path):
#                 success_count += 1
        
#         print("\n" + "="*60)
#         print(f"✅ 完成! 成功处理 {success_count}/{len(faq_files)} 个文件")
#         print("\n下一步:")
#         print("  cd backend\\scripts")
#         print("  python build_kb.py")
#         print("="*60)

# if __name__ == "__main__":
#     main()
