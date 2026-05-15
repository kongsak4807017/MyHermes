# Guardrails Templates

## Input Validation

### Prompt Injection Detection
```python
def detect_prompt_injection(user_input: str) -> dict:
    """Detect potential prompt injection attacks."""
    patterns = [
        r"ignore previous instructions",
        r"disregard.*prompt",
        r"you are now.*(admin|root)",
        r"system prompt.*override",
        r"DAN|Do Anything Now",
        r"jailbreak|goddess mode",
    ]
    
    matches = []
    for pattern in patterns:
        if re.search(pattern, user_input, re.IGNORECASE):
            matches.append(pattern)
    
    return {
        "safe": len(matches) == 0,
        "matches": matches,
        "score": 1.0 - (len(matches) / len(patterns))
    }
```

### PII Detection
```python
def detect_pii(text: str) -> list:
    """Detect personally identifiable information."""
    patterns = {
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        "phone": r"\b\d{3}-\d{3}-\d{4}\b",
        "credit_card": r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
    }
    
    findings = []
    for pii_type, pattern in patterns.items():
        matches = re.findall(pattern, text)
        if matches:
            findings.append({"type": pii_type, "matches": matches})
    
    return findings
```

## Output Filtering

### Hallucination Check
```python
def check_hallucination(response: str, context: str) -> dict:
    """Check if response contains hallucinated information."""
    # Extract claims from response
    claims = extract_claims(response)
    
    # Verify against context
    verified = []
    unverified = []
    
    for claim in claims:
        if verify_claim(claim, context):
            verified.append(claim)
        else:
            unverified.append(claim)
    
    return {
        "hallucination_score": len(unverified) / len(claims) if claims else 0,
        "verified_claims": verified,
        "unverified_claims": unverified
    }
```

### Toxicity Filter
```python
def filter_toxicity(text: str, threshold: float = 0.5) -> dict:
    """Filter toxic content."""
    toxic_keywords = [
        "hate", "violence", "harassment",
        "discrimination", "abuse"
    ]
    
    score = 0
    matches = []
    for keyword in toxic_keywords:
        if keyword in text.lower():
            score += 0.2
            matches.append(keyword)
    
    return {
        "safe": score < threshold,
        "score": min(score, 1.0),
        "matches": matches
    }
```

## Rate Limiting
```python
class RateLimiter:
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window = window_seconds
        self.requests = []
    
    def is_allowed(self) -> bool:
        now = time.time()
        self.requests = [r for r in self.requests if now - r < self.window]
        return len(self.requests) < self.max_requests
    
    def record_request(self):
        self.requests.append(time.time())
```
