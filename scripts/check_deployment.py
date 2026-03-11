#!/usr/bin/env python3
"""Check which Azure OpenAI deployment names exist and work with your resource.

Run from project root: python scripts/check_deployment.py
"""

from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from openai import AzureOpenAI

# Legacy API (may still work on some resources)
DEPLOYMENTS_API = "2023-03-15-preview"

# Common deployment names used in Azure OpenAI
COMMON_DEPLOYMENTS = [
    "gpt-4o",
    "gpt-4o-mini",
    "gpt-4",
    "gpt-4-turbo",
    "gpt-35-turbo",
    "gpt-4o-2024-04-09",
    "gpt-4o-mini-2024-07-18",
    "o1",
    "o1-mini",
]


def fetch_deployments_via_api(endpoint: str, api_key: str) -> list[str]:
    """Try legacy deployments API (2023-03-15-preview)."""
    url = endpoint.rstrip("/") + f"/openai/deployments?api-version={DEPLOYMENTS_API}"
    req = urllib.request.Request(url, headers={"api-key": api_key})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = __import__("json").loads(resp.read().decode())
            return [d["id"] for d in data.get("data", [])]
    except Exception:
        return []


def main() -> None:
    from config.settings import get_settings

    settings = get_settings()
    if not settings.azure_openai_endpoint or not settings.azure_openai_key:
        print("Error: AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_KEY must be set in .env")
        sys.exit(1)

    # Try to fetch deployments from legacy API
    api_deployments = fetch_deployments_via_api(
        settings.azure_openai_endpoint, settings.azure_openai_key
    )
    if api_deployments:
        print("Deployments found via API:")
        for d in api_deployments:
            print(f"  • {d}")
        print()

    client = AzureOpenAI(
        azure_endpoint=settings.azure_openai_endpoint,
        api_key=settings.azure_openai_key,
        api_version=settings.azure_openai_api_version,
    )

    print(f"Testing against: {settings.azure_openai_endpoint}")
    print(f"Current AZURE_OPENAI_DEPLOYMENT in .env: {settings.azure_openai_deployment}")
    print()

    # Combine API deployments (if any) with common names, dedupe
    to_try = list(dict.fromkeys(api_deployments + COMMON_DEPLOYMENTS))
    print(f"Testing {len(to_try)} deployment names...\n")

    working: list[str] = []
    for deployment in to_try:
        try:
            client.chat.completions.create(
                model=deployment,
                messages=[{"role": "user", "content": "Say OK"}],
                max_tokens=5,
            )
            working.append(deployment)
            print(f"  ✓ {deployment}")
        except Exception as e:
            err = str(e)
            if "DeploymentNotFound" in err or "404" in err:
                print(f"  ✗ {deployment} (not found)")
            else:
                print(f"  ✗ {deployment} ({err[:60]}...)")

    print()
    if working:
        print("=" * 60)
        print("WORKING DEPLOYMENTS:")
        for d in working:
            print(f"  {d}")
        print()
        current = settings.azure_openai_deployment
        if current in working:
            print(f"Your current deployment '{current}' is valid. No change needed.")
        else:
            print(f"ACTION REQUIRED: Update .env")
            print(f"  Set AZURE_OPENAI_DEPLOYMENT to one of: {', '.join(working)}")
            print(f"  Example: AZURE_OPENAI_DEPLOYMENT={working[0]}")
    else:
        print("No working deployments found.")
        print("Please check:")
        print("  1. Your deployment name in Azure Portal (Model deployments)")
        print("  2. Endpoint and key are correct for the resource")
        print("  3. Run: az login  (if using Azure CLI) then check deployments in portal")


if __name__ == "__main__":
    main()
