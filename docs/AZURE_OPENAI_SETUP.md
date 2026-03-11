# Azure OpenAI Deployment Setup

## Problem

If you see `DeploymentNotFound` or `The API deployment for this resource does not exist`, your `AZURE_OPENAI_DEPLOYMENT` in `.env` does not match any deployment in your Azure OpenAI resource.

## Solution

### Step 1: Find or Create Your Deployment

1. Go to [Azure Portal](https://portal.azure.com)
2. Search for **Azure OpenAI** or navigate to your resource: `iconnectdevopenai01`
3. Open **Model deployments** (or **Deployments** under Azure AI Studio)
4. Check the **Deployment name** column for each deployment

**If you have deployments:**
- Copy the exact deployment name (e.g. `gpt-4o`, `my-gpt4-deployment`)

**If you have no deployments:**
- Click **Create new deployment**
- Choose a model (e.g. **gpt-4o** for vision support)
- Set a **Deployment name** (e.g. `gpt-4o`)
- Deploy and wait for it to become active

### Step 2: Update .env

Edit `.env` and set:

```
AZURE_OPENAI_DEPLOYMENT=<exact-deployment-name-from-portal>
```

### Step 3: Verify

Run the check script:

```bash
python3 scripts/check_deployment.py
```

Or run the extract sample:

```bash
python3 examples/extract_sample.py <path-to-pdf>
```

## Alternative: Use Azure CLI

If you have Azure CLI and are logged in:

```bash
az login
az cognitiveservices account deployment list \
  --name iconnectdevopenai01 \
  --resource-group <your-resource-group> \
  --query "[].{name:name, model:properties.model.name}" -o table
```

Use the `name` column as `AZURE_OPENAI_DEPLOYMENT`.
