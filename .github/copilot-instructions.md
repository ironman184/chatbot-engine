# Copilot Instructions for RFP Automation Chatbot

## Project Overview

This project is a backend service for a customer care chatbot.  
It acts as a webhook for WhatsApp and handles incoming user messages.

When a message is received:
- The system performs intent classification.
- It fetches order and customer-related data from Shopify.
- It retrieves conversational context from a vector database.
- It generates and sends a response back to WhatsApp.

---

## Tech Stack
- Backend Framework: FastAPI (Python)
- Messaging Platform: WhatsApp (Meta Cloud API)
- E-commerce Integration: Shopify (REST APIs)
- Vector Database: Qdrant

---

## 🚨 PRIME DIRECTIVES

### 1. Single File Focus
- **ALWAYS work on ONE file at a time**
- Never modify multiple files simultaneously to prevent corruption
- Complete changes in one file before moving to another

### 2. Pre-Code Planning (MANDATORY)
Before writing ANY code, you MUST:
1. Create an instruction file that specifies:
   - Which file(s) will be updated or created
   - What changes will be made
   - Why these changes are needed
2. Wait for user confirmation before proceeding

### 3. Documentation Updates
- Update `documentation.md` after every significant change
- Include:
  - Feature added/modified
  - Files changed
  - Date of change
  - Any breaking changes or migration notes

### 4. Educational Approach
- Be conversational and explain your reasoning
- Don't just write code - explain WHY you're doing it
- Discuss tradeoffs when multiple approaches exist

### 5. Quality First
- Prioritize code quality, performance, and maintainability
- Follow existing patterns religiously
- If you're unsure, ASK before implementing

---

## 📁 Project Structure
- Here are the key files and directories in this project:
.
├── __pycache__
│   ├── driver.cpython-311.pyc
│   ├── main.cpython-311.pyc
│   ├── registry.cpython-311.pyc
│   ├── session.cpython-311.pyc
│   └── whatsApp.cpython-311.pyc
├── actions
│   ├── common_actions.py
│   └── order_actions.py
├── chat.py
├── documentation.md
├── driver.py
├── load_actions.py
├── main.py
├── message_1.json
├── message.json
├── registry.py
├── requirements.txt
├── session.py
├── structure.txt
└── WORKFLOWS
    ├── common.yaml
    └── order_status.yaml

---

🚨 BEFORE CODING:
1. Create instruction file in .github/instructions/ for the requested feature/changes
2. List files to change
3. Explain changes
4. Wait for approval

✏️ WHILE CODING:
1. One file at a time
2. If you are modifying an existing file, use lines of ####### to separate your changes from existing code
4. Add type hints
5. Add docstrings
6. Handle errors

✅ AFTER CODING:
1. Update documentation.md
2. Explain what you did
3. Explain why you did it
4. Ask if it meets expectations