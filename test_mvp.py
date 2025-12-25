"""
MVP测试脚本
自动测试核心功能
"""
import requests
import json
import time

API_BASE = "http://localhost:8000/api"

def test_health():
    """测试健康检查"""
    print("\n🔍 1. 测试健康检查...")
    try:
        response = requests.get("http://localhost:8000/")
        print(f"   ✅ 服务运行中: {response.json()}")
        return True
    except Exception as e:
        print(f"   ❌ 失败: {e}")
        return False

def test_create_customer():
    """测试创建客户"""
    print("\n🔍 2. 测试创建客户...")
    try:
        response = requests.post(f"{API_BASE}/customers", json={
            "name": "测试客户_张三",
            "email": "zhangsan@test.com",
            "company": "测试科技公司",
            "phone": "13800138000"
        })
        result = response.json()
        customer_id = result['customer_id']
        print(f"   ✅ 客户创建成功: ID={customer_id}")
        return customer_id
    except Exception as e:
        print(f"   ❌ 失败: {e}")
        return None

def test_chat(customer_id):
    """测试智能对话"""
    print("\n🔍 3. 测试智能对话...")
    
    test_messages = [
        "你好，我想了解Matrice 30的续航时间是多少？",
        "M30和M400有什么区别？",
        "价格是多少？我需要购买10台M30"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n   📝 对话 {i}: {message}")
        try:
            response = requests.post(f"{API_BASE}/chat", json={
                "customer_id": customer_id,
                "message": message,
                "language": "zh-cn"
            })
            result = response.json()
            print(f"   🤖 AI回复: {result['answer'][:100]}...")
            print(f"   📊 置信度: {result['confidence']:.2f}")
            print(f"   🔄 需转人工: {result['should_handoff']}")
            print(f"   🏷️  产品标签: {result.get('product_tag', 'N/A')}")
            
            time.sleep(1)  # 避免请求过快
        except Exception as e:
            print(f"   ❌ 失败: {e}")

def test_classify(customer_id):
    """测试客户分类"""
    print("\n🔍 4. 测试客户分类...")
    try:
        response = requests.post(f"{API_BASE}/classify/{customer_id}")
        result = response.json()
        print(f"   ✅ 分类结果:")
        print(f"      类别: {result['category']}")
        print(f"      优先级: {result['priority_score']}/5")
        print(f"      理由: {result['reason']}")
        return True
    except Exception as e:
        print(f"   ❌ 失败: {e}")
        return False

def test_list_customers():
    """测试客户列表"""
    print("\n🔍 5. 测试客户列表...")
    try:
        response = requests.get(f"{API_BASE}/customers")
        result = response.json()
        print(f"   ✅ 共有 {result['total']} 个客户")
        for customer in result['customers'][:3]:  # 显示前3个
            print(f"      - {customer['name']} ({customer.get('category', 'N/A')}) - 优先级{customer['priority_score']}")
        return True
    except Exception as e:
        print(f"   ❌ 失败: {e}")
        return False

def main():
    """主测试流程"""
    print("="*60)
    print("🚀 DJI Sales AI Assistant - MVP测试")
    print("="*60)
    
    # 等待服务启动
    print("\n⏳ 等待服务启动...")
    for i in range(10):
        if test_health():
            break
        print(f"   重试 {i+1}/10...")
        time.sleep(3)
    else:
        print("\n❌ 服务未启动，请检查Docker容器")
        return
    
    # 创建测试客户
    customer_id = test_create_customer()
    if not customer_id:
        print("\n❌ 测试终止：无法创建客户")
        return
    
    # 测试对话
    test_chat(customer_id)
    
    # 测试分类
    test_classify(customer_id)
    
    # 测试列表
    test_list_customers()
    
    print("\n" + "="*60)
    print("✅ 测试完成！")
    print("="*60)
    print("\n💡 下一步:")
    print("   1. 访问 http://localhost:8000/docs 查看完整API文档")
    print("   2. 检查数据库中的数据")
    print("   3. 调优Prompt或测试更多场景")

if __name__ == "__main__":
    main()
