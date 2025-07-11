import os
import streamlit as st
import anthropic
from typing import List, Dict

def get_sensitive_terms_with_claude(page_text: str, page_num: int) -> List[Dict[str, str]]:
    """Uses Claude to detect sensitive terms in a block of text and return redaction targets."""
    claude_key = st.secrets.get("claude_api_key")
    if not claude_key:
        raise ValueError("Claude API key not found in Streamlit secrets.")

    client = anthropic.Anthropic(api_key=claude_key)

    prompt = f"""
You are a document redaction assistant.

Your job is to analyze the following text and extract all sensitive information that may need to be redacted for compliance, privacy, or confidentiality. Focus on PII, PHI, and financial or identifying data.

For each item, return it in this exact format (one per line):
Sensitive Term | Reason

Example:
john.doe@example.com | Email address
555-123-4567 | Phone number
123-45-6789 | SSN

Do not include any explanations or extra text. Just the matches.

TEXT:
{page_text}
"""

    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=1024,
        temperature=0,
        messages=[
            {
                "role": "user",
                "content": prompt.strip()
            }
        ]
    )

    lines = response.content[0].text.strip().split("\n")
    structured = []
    for line in lines:
        if "|" in line:
            parts = line.strip().split("|")
            if len(parts) == 2:
                text, reason = parts[0].strip(), parts[1].strip()
                structured.append({
                    "Text": text,
                    "Reason": reason,
                    "Page": page_num
                })
        elif line.strip():  # fallback
            structured.append({
                "Text": line.strip(),
                "Reason": "Sensitive",
                "Page": page_num
            })

    return structured
