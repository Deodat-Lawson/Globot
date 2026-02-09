---
trigger: always_on
---

# AI Model API Keys Security Guidelines

## Key Storage Locations

- Gemini Key: Stored in `GEMINI_API_KEY` environment variable

## Code Requirements

1. **Strictly Forbidden** to hardcode keys
2. **Must** use `os.getenv()` or similar methods to read environment variables
3. **Must** include key validation code (e.g., check for None)
4. **Recommended** to use configuration classes or functions to encapsulate API calls

## Error Handling

- If the key doesn't exist, provide a clear prompt
- Do not expose any key-related information in production code

## Example Structure

Follow this pattern when writing code:

```python
import os

def get_api_key(service_name):
    key = os.getenv(f"{service_name.upper()}_API_KEY")
    if not key:
        raise ValueError(f"Please set {service_name.upper()}_API_KEY in environment variables")
    return key

```

#

## 🛡️ **Multi-layer Defense Strategy**

In addition to prompts, implement these protections:

### **1. Code-Level Protection**

```python
# safe_api.py - Security encapsulation example
import os
import hashlib

class SecureAPIClient:
    def __init__(self, service_name):
        self.service_name = service_name
        self.api_key = self._load_key()

    def _load_key(self):
        """Safely load API keys"""
        env_var = f"{self.service_name.upper()}_API_KEY"
        key = os.getenv(env_var)

        if not key:
            raise ValueError(
                f"Please set environment variable {env_var}\n"
                f"For example: export {env_var}='your-key-here'"
            )

        # 记录密钥哈希（用于日志，不暴露密钥）
        key_hash = hashlib.sha256(key.encode()).hexdigest()[:8]
        print(f"[Security Note] Loaded {self.service_name} API key (hash: ...{key_hash})")
        return key

```

### **2. Establish Environment Variable Check Script**

```python
# check_env.py - Environment variable security check
import os

REQUIRED_KEYS = ['GEMINI_API_KEY']

def check_environment():
    missing = []
    for key in REQUIRED_KEYS:
        if not os.getenv(key):
            missing.append(key)

    if missing:
        print("❌ Missing the following environment variables:")
        for key in missing:
            print(f"   - {key}")
        print("\n💡 Setup method:")
        print(f"   export {missing[0]}='your-key-here'")
        return False

    print("✅ All API keys configured correctly (securely stored in environment variables)")
    return True

if __name__ == "__main__":
    check_environment()

```

### **3. API Key Existence Check**

Perform API Key existence check:

```python
print("API key loaded:", bool(os.getenv("GEMINI_API_KEY")))
```
