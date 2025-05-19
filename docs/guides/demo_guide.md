# Meta LCM Chatbot Demo Guide

## Overview

This document provides a guide for demonstrating the Meta LCM Chatbot MVP to stakeholders. The demo showcases a lightweight, concept-aware chatbot that uses Meta's Large Concept Model (LCM-7B) in a real-time Q-and-A experience.

## Demo Setup

1. **Local Deployment**:
   - Ensure Docker is installed on your MacBook
   - Clone the repository: `git clone <repository-url>`
   - Navigate to the project directory: `cd meta-lcm-chatbot`
   - Start the application: `docker-compose up`
   - Access the UI at http://localhost:8000

2. **Demo Environment Requirements**:
   - Stable internet connection
   - Modern web browser (Chrome, Firefox, Safari)
   - At least 8GB of RAM available
   - Docker with GPU support configured (optional, for best performance)

## Demo Scenarios

### 1. Oncology Researcher Persona

**Scenario**: Demonstrate how the chatbot can summarize trial excerpts.

**Steps**:
1. Open the chatbot UI
2. Paste the following trial excerpt:
   ```
   The phase III randomized controlled trial enrolled 428 patients with advanced non-small cell lung cancer (NSCLC) who had progressed on first-line platinum-based chemotherapy. Patients were randomized 1:1 to receive either the investigational agent (200mg daily) or standard of care (docetaxel 75mg/m2 every 3 weeks). The primary endpoint was progression-free survival (PFS), with secondary endpoints including overall survival (OS), objective response rate (ORR), and quality of life measures. Median follow-up was 24.3 months.
   ```
3. Ask: "Summarize the key endpoints."
4. Verify that the response is concise (single paragraph) and accurately identifies primary endpoint (PFS) and secondary endpoints (OS, ORR, quality of life)
5. Demonstrate the ability to copy the response for use in presentations

### 2. Data-Science Manager Persona

**Scenario**: Test multilingual capabilities and response times.

**Steps**:
1. Send a query in English: "What are the advantages of concept-level reasoning compared to token-level processing?"
2. Send a query in Spanish: "¿Cuáles son las ventajas del razonamiento a nivel de concepto en comparación con el procesamiento a nivel de token?"
3. Send a query in French: "Quels sont les avantages du raisonnement au niveau conceptuel par rapport au traitement au niveau des tokens?"
4. Point out the response times displayed in the metrics panel (should be < 1s median)
5. Demonstrate the system health endpoint at http://localhost:8000/health

### 3. AI Engineer Persona

**Scenario**: Demonstrate API access for regression testing.

**Steps**:
1. Open a terminal window
2. Run the following curl command:
   ```bash
   curl -X POST http://localhost:8000/api/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "What is concept-level reasoning?", "session_id": "test-session"}'
   ```
3. Show the JSON response with metrics
4. Demonstrate the metrics endpoint:
   ```bash
   curl http://localhost:8000/api/metrics
   ```
5. Show how the API could be integrated into automated testing scripts

## Key Features to Highlight

1. **Low Latency**:
   - Point out the < 1s median response time for short replies
   - Show the performance metrics in the UI

2. **Concept-Level Reasoning**:
   - Explain how the system processes text at the concept level rather than token-by-token
   - Highlight how this reduces hallucination and improves coherence

3. **Session Memory**:
   - Demonstrate how the system maintains context across multiple exchanges
   - Show the Clear History button functionality

4. **Markdown Support**:
   - Send a message with markdown formatting:
     ```
     Can you explain what *concept vectors* are? Also, please format this as a **list**:
     1. LCM architecture
     2. Concept encoding
     3. Inference pipeline
     ```

5. **Observability**:
   - Show the health endpoint and metrics
   - Explain how the system monitors GPU utilization and latency

## Collecting Feedback

After the demo, collect feedback using these questions:

1. How would you rate the response time of the chatbot? (1-5 scale)
2. Was the chat interface intuitive and easy to use? (1-5 scale)
3. How accurate and coherent were the responses? (1-5 scale)
4. What additional features would you like to see in the full version?
5. How would this tool fit into your current workflow?

## Troubleshooting

If you encounter issues during the demo:

1. **Slow responses**: Check GPU utilization via the health endpoint
2. **Connection errors**: Verify Docker containers are running with `docker ps`
3. **UI issues**: Try refreshing the page or clearing browser cache
4. **API errors**: Check the logs with `docker-compose logs`

## Next Steps

After the demo, discuss these potential next steps:

1. RAG with ontology-backed retrieval
2. Fine-tuned domain LCM checkpoint
3. Multi-agent orchestration
4. Enterprise auth & usage analytics

---

End of Demo Guide
