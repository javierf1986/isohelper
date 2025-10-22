# Test AI Enhancement Feature (Option B)

## Testing AI Enhancement API - Mock Test

Since we don't have actual API keys yet, let's test the structure:

### 1. Test AI Status Endpoint

```bash
curl http://127.0.0.1:8000/api/v1/documents/ai/status
```

Expected response:
```json
{
  "ai_enabled": true,
  "default_provider": "mistral",
  "available_providers": ["mistral", "openai", "local"],
  "model": "mistral-medium",
  "temperature": 0.7,
  "max_tokens": 2000
}
```

### 2. Test AI Enhancement Endpoint (requires API key)

```powershell
$body = @{
    "clause" = "4.1"
    "company_name" = "TechCorp Industries"
    "industry" = "software development"
    "company_size" = "medium"
    "enhancement_level" = "moderate"
    "ai_provider" = "mistral"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/documents/enhance" `
    -Method Post `
    -Body $body `
    -ContentType "application/json"
```

### 3. Test Industry Examples Generation (requires API key)

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/documents/examples?clause=5.1&industry=manufacturing&company_size=large" `
    -Method Post
```

### 4. Generate Document with AI Enhancement (requires API key)

```json
{
  "company_name": "InnovateTech Solutions",
  "industry": "technology consulting",
  "company_size": "small",
  "clauses": ["4.1", "5.1", "8.1"],
  "format": "markdown",
  "generate_full_manual": true,
  "enable_ai_enhancement": true,
  "ai_enhancement_level": "comprehensive",
  "custom_context": "We specialize in cloud infrastructure and DevOps consulting"
}
```

## How to Get API Keys

### Mistral AI (Recommended)
1. Visit https://console.mistral.ai/
2. Sign up for account
3. Navigate to API Keys section
4. Create new API key
5. Add to `.env`: `MISTRAL_API_KEY=your_key_here`

### OpenAI (Alternative)
1. Visit https://platform.openai.com/
2. Sign up and add payment method
3. Go to API Keys
4. Create new key
5. Add to `.env`: `OPENAI_API_KEY=your_key_here`

### Local LLM (Free, No API Key Needed)
1. Install Ollama: https://ollama.ai/
2. Run: `ollama pull mistral`
3. Verify: `ollama serve`
4. Set in `.env`: `AI_PROVIDER=local`

## What's Included

### AI Enhancement Features ✅
- **Multiple Providers**: Mistral (primary), OpenAI (fallback), Local LLM (Ollama)
- **Context-Aware Generation**: Industry-specific content
- **Enhancement Levels**: Light, Moderate, Comprehensive
- **Optional Toggle**: Enable/disable AI per request
- **Industry Examples**: Real-world scenarios generator
- **Process Improvements**: QMS optimization suggestions

### API Endpoints ✅
- `POST /api/v1/documents/enhance` - Enhance existing clause content
- `POST /api/v1/documents/examples` - Generate industry examples
- `GET /api/v1/documents/ai/status` - Check AI configuration
- `POST /api/v1/documents/generate` - Now supports `enable_ai_enhancement` flag

### Flexible Architecture ✅
- Provider abstraction (easy to add new AI providers)
- Graceful fallback (returns base content if AI fails)
- Cost control (configurable enhancement levels)
- Privacy option (use local LLM for sensitive data)

## Testing Without API Keys

Until you get API keys, you can:

1. **Test AI Status**: Works without keys
   ```powershell
   Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/documents/ai/status"
   ```

2. **Test Base Generation**: Still works perfectly
   ```powershell
   $body = Get-Content test_api_request.json -Raw
   Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/documents/generate" `
       -Method Post -Body $body -ContentType "application/json"
   ```

3. **Install Local LLM**: Free, no API key required!
   ```bash
   # Install Ollama
   # Download from https://ollama.ai/download
   
   # Pull Mistral model
   ollama pull mistral
   
   # Update .env
   AI_PROVIDER=local
   LOCAL_LLM_URL=http://localhost:11434/v1
   
   # Test AI enhancement with local model!
   ```

## Next Steps

1. ✅ AI enhancement service created
2. ✅ Multiple provider support (Mistral/OpenAI/Local)
3. ✅ API endpoints implemented
4. ✅ Configuration added
5. ⏳ Get Mistral API key or install Ollama
6. ⏳ Test AI enhancement
7. ⏳ Document results
