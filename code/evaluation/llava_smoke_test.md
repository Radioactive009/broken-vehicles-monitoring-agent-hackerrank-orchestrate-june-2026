# LLaVA Smoke Test Evaluation Report

This report evaluates the performance of `llava:7b` on 5 selected sample claims.

### Row 1 (Object: car)
- **Expected Part**: rear_bumper
- **Expected Issue**: dent
- **LLaVA Response**:
```json
Error: Status code 500
```

### Row 3 (Object: car)
- **Expected Part**: windshield
- **Expected Issue**: crack
- **LLaVA Response**:
```json
Error querying local Ollama (Llava:7b): HTTPConnectionPool(host='localhost', port=11434): Read timed out. (read timeout=30)
```

### Row 9 (Object: laptop)
- **Expected Part**: screen
- **Expected Issue**: crack
- **LLaVA Response**:
```json
Error querying local Ollama (Llava:7b): HTTPConnectionPool(host='localhost', port=11434): Read timed out. (read timeout=30)
```

### Row 10 (Object: laptop)
- **Expected Part**: hinge
- **Expected Issue**: broken_part
- **LLaVA Response**:
```json
Error querying local Ollama (Llava:7b): HTTPConnectionPool(host='localhost', port=11434): Read timed out. (read timeout=30)
```

### Row 15 (Object: package)
- **Expected Part**: package_corner
- **Expected Issue**: crushed_packaging
- **LLaVA Response**:
```json
Error: Status code 500
```

## Comparison and Capability Analysis

Note: If Ollama was offline or model was not present, the outputs will show connection failure. In case of connection failure, we determine model capability theoretically based on standard LLaVA evaluations, recommending fallback to commercial APIs (Gemini 1.5 Flash / GPT-4o-mini) for production stability.
