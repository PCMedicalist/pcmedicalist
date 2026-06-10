🖥️ 💾 🔐 🚀 🦾 🟦

# LOCAL OLLAMA MODEL SELECTION - QUICK REFERENCE

**Active Provider:** Local Ollama  
**Current Default:** qwen3.5:9b (6.6 GB)  
**Available Models:** 11  

---

## 🎯 Quick Model Switching

### Switch Default Model (Host)
```bash
# View current
hermes config show | grep "Model:"

# Switch to Qwen 2.5 (7B - larger, slower)
hermes config set model.default qwen2.5:7b

# Switch to Gemma 3 (4B - small, fast)
hermes config set model.default gemma3:4b

# Switch back to Qwen 3.5 (9B - balanced)
hermes config set model.default qwen3.5:9b
```

---

## 📦 All Available Models

| Size Category | Model | Parameters | Speed | Reasoning |
|---|---|---|---|---|
| **Lightweight** | qwen2.5:3b | 3.1B | 🚀 Very Fast | Simple tasks |
| **Small** | qwen2.5-coder:3b | 3.1B | 🚀 Very Fast | Code, small tasks |
| **Small** | gemma3:4b | 4.3B | 🚀 Fast | Fast inference |
| **Medium** | qwen2.5:7b | 7.6B | ⚡ Balanced | Good quality/speed |
| **Medium** | llama3.1:8b | 8.0B | ⚡ Balanced | Meta's model |
| **Medium** | 0xpcmedicalist:8b | 8.0B | ⚡ Balanced | PCMedicalist |
| **Medium-Large** | 0xpcmedicalist:8b-stable | 7.6B | ⚡ Balanced | Stable variant |
| **DEFAULT** | **qwen3.5:9b** | **9.7B** | ⚡ **Balanced** | **Best all-around** |
| **Large** | gemma4:latest | 8.0B | ⏱️ Slower | Latest Google |
| **Large** | openbmb/minicpm-o2.6:8b | 7.6B | ⏱️ Slower | Multi-modal |
| **XL** | gpt-oss:20b | 20.9B | ⏱️ Slowest | Heavy reasoning |

---

## 🔄 Model Tiers by Use Case

### For Speed (DevOps, Quick Tasks)
```bash
hermes config set model.default qwen2.5:3b  # Fastest
```
- **Model:** qwen2.5:3b
- **Speed:** ~300ms/token on GPU
- **Use:** Simple generation, quick tests

### For Balance (DEFAULT)
```bash
hermes config set model.default qwen3.5:9b  # Current default
```
- **Model:** qwen3.5:9b
- **Speed:** ~100ms/token on GPU
- **Use:** General-purpose, code, reasoning

### For Quality (Deep Reasoning)
```bash
hermes config set model.default gpt-oss:20b  # Slowest
```
- **Model:** gpt-oss:20b
- **Speed:** ~400ms/token on GPU
- **Use:** Complex reasoning, planning

### For Coding
```bash
hermes config set model.default qwen2.5-coder:3b  # Fast + code
```
- **Model:** qwen2.5-coder:3b
- **Speed:** ~300ms/token
- **Use:** Code generation, syntax

---

## 🐳 Docker Container Model Switching

### Inside Container
```bash
docker exec pcmedicalist-hermes \
  hermes config set model.default qwen2.5:7b
```

### Verify Container is Using Local Ollama
```bash
docker exec pcmedicalist-hermes \
  hermes config show | grep "Model:"
# Output: Model: {'default': 'qwen2.5:7b', 'provider': 'pcmedicalist-local-ollama', ...}
```

---

## ✅ Configuration Verification

### Check Host Runtime
```bash
# View full config
hermes config show

# Just model info
hermes config show | grep -A 3 "Model:"
```

**Expected Output:**
```
Model:  {'default': 'qwen3.5:9b', 'provider': 'pcmedicalist llm', 'api_mode': 'chat_completions'}
```

### Check Docker Container
```bash
# View full config
docker exec pcmedicalist-hermes hermes config show

# Just model info
docker exec pcmedicalist-hermes hermes config show | grep -A 3 "Model:"
```

**Expected Output:**
```
Model:  {'default': 'qwen3.5:9b', 'provider': 'pcmedicalist-local-ollama', 'api_mode': 'chat_completions'}
```

### Check Ollama Availability
```bash
# Host
curl -s http://localhost:11434/api/tags | jq '.models | map(.name)'

# Docker
docker exec pcmedicalist-hermes \
  curl -s http://host.docker.internal:11434/api/tags | jq '.models | map(.name)'
```

---

## 🛠️ Troubleshooting

### Model Responds Slowly
**Solution:** Switch to smaller model
```bash
hermes config set model.default qwen2.5:3b  # Fast
```

### Response Quality is Low
**Solution:** Switch to larger model
```bash
hermes config set model.default gpt-oss:20b  # Large
```

### Changes Not Applied
**Solution:** Restart Hermes or Docker container
```bash
# Host
hermes gateway restart

# Docker
docker restart pcmedicalist-hermes
```

### Ollama Not Responding
**Solution:** Check Ollama status
```bash
# Check if running
curl http://localhost:11434/api/tags | jq '.models | length'

# Start if needed
ollama serve
```

---

## 📊 Resource Usage Estimate

| Model | VRAM | Speed | Quality |
|-------|------|-------|---------|
| qwen2.5:3b | 2-3 GB | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| gemma3:4b | 3-4 GB | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| qwen2.5:7b | 5-6 GB | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| qwen3.5:9b | 6-7 GB | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| gpt-oss:20b | 13-14 GB | ⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 🔒 Local-Only Guarantee

All models run on your local machine:
- ✅ No data sent to cloud
- ✅ No external API calls
- ✅ Full privacy control
- ✅ Can work offline
- ✅ No vendor lock-in

---

## 📌 Configuration Files

**Host Configuration:**
```
/home/pcmedicalist/.hermes/config.yaml
  → model.default: qwen3.5:9b
  → model.provider: pcmedicalist llm
```

**Docker Configuration:**
```
/home/pcmedicalist/.pcmedicalist/hermes/home/config.yaml
  → model.default: qwen3.5:9b
  → model.provider: pcmedicalist-local-ollama
```

---

**Current Status:** ✅ All 11 models available  
**Primary Provider:** Local Ollama  
**Default Model:** qwen3.5:9b  

🔐 **SECURE. LOCAL. SHIPPED.** 🚀
