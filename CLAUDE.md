# CLAUDE.md - Google ADK Multi-Agent Development Guide

## 🚨 CRITICAL: ADK BEST PRACTICES FOR MULTI-AGENT SYSTEMS
**This guide ensures efficient, maintainable, and scalable multi-agent applications using Google ADK.**

## 🎯 Primary Development Objectives
1. **Agent Clarity** - Each agent must have a single, well-defined responsibility
2. **Efficient Communication** - Use appropriate patterns for agent interaction
3. **Tool Simplicity** - Keep tools focused and parameters minimal
4. **State Management** - Properly manage session state and data flow
5. **Production Readiness** - Build for scalability and reliability

## 🏗️ ADK Multi-Agent Architecture

### Core Agent Types to Use
```python
from google.adk.agents import (
    LlmAgent,           # Primary agent with LLM capabilities
    SequentialAgent,    # Execute agents in order
    ParallelAgent,      # Execute agents concurrently
    LoopAgent,          # Iterate based on conditions
    BaseAgent           # For custom agent implementations
)
```

### Multi-Agent Communication Patterns

#### 1. Coordinator Pattern (PREFERRED FOR COMPLEX SYSTEMS)
```python
# ✅ CORRECT: Clear hierarchy with specialized agents
coordinator = LlmAgent(
    name="coordinator",
    model="gemini-2.0-flash-exp",
    instruction="Route requests to appropriate specialists",
    description="Main coordinator for task delegation",
    sub_agents=[research_agent, developer_agent, analyst_agent]
)

# ❌ WRONG: Flat structure with unclear responsibilities
agent = LlmAgent(
    name="do_everything",
    instruction="Handle all tasks"  # Too broad!
)
```

#### 2. Sequential Pipeline Pattern
```python
# ✅ CORRECT: Clear data flow through pipeline
pipeline = SequentialAgent(
    name="data_pipeline",
    sub_agents=[
        validator,      # output_key="validation_status"
        processor,      # reads validation_status, output_key="result"
        reporter        # reads result
    ]
)

# ❌ WRONG: No clear data passing mechanism
pipeline = SequentialAgent(
    sub_agents=[agent1, agent2, agent3]  # How do they share data?
)
```

#### 3. Parallel Execution Pattern
```python
# ✅ CORRECT: Independent tasks run concurrently
parallel_fetch = ParallelAgent(
    name="concurrent_fetch",
    sub_agents=[
        api1_fetcher,  # output_key="api1_data"
        api2_fetcher,  # output_key="api2_data"
        api3_fetcher   # output_key="api3_data"
    ]
)

# Then aggregate results
aggregator = LlmAgent(
    instruction="Combine {api1_data}, {api2_data}, {api3_data}"
)
```

## 🛠️ Tool Development Standards

### Function Tool Best Practices

```python
# ✅ CORRECT: Simple, focused function with clear parameters
def calculate_metrics(
    revenue: float,
    costs: float,
    period: str = "monthly"
) -> dict:
    """
    Calculate business metrics.

    Args:
        revenue: Total revenue in USD
        costs: Total costs in USD
        period: Time period (monthly/quarterly/yearly)

    Returns:
        Dictionary with calculated metrics
    """
    margin = revenue - costs
    margin_percent = (margin / revenue * 100) if revenue > 0 else 0

    return {
        "status": "success",
        "revenue": revenue,
        "costs": costs,
        "margin": margin,
        "margin_percent": margin_percent,
        "period": period
    }

# ❌ WRONG: Complex parameters and unclear return
def process_data(data, config, *args, **kwargs):
    # No type hints, no docstring, uses *args/**kwargs
    return margin  # Returns single value, not descriptive
```

### Long-Running Function Tool Pattern
```python
from google.adk.tools import LongRunningFunctionTool

# ✅ CORRECT: For operations requiring external processing
def initiate_analysis(dataset_id: str, analysis_type: str) -> dict:
    """Start long-running analysis job."""
    job_id = start_external_job(dataset_id, analysis_type)
    return {
        "status": "initiated",
        "job_id": job_id,
        "message": f"Analysis {job_id} started"
    }

analysis_tool = LongRunningFunctionTool(func=initiate_analysis)
```

### Agent-as-Tool vs Sub-Agent

```python
# Use AgentTool when you need the response back
from google.adk.tools import AgentTool

main_agent = LlmAgent(
    name="main",
    tools=[AgentTool(agent=analyzer_agent)]  # Response returns to main
)

# Use sub_agents for delegation/handoff
coordinator = LlmAgent(
    name="coordinator",
    sub_agents=[specialist_agent]  # Control transfers to specialist
)
```

## 📊 State Management Rules

### Session State Best Practices

```python
# ✅ CORRECT: Use output_key for state management
validator = LlmAgent(
    name="validator",
    instruction="Validate input and save status",
    output_key="validation_status"  # Saves to state['validation_status']
)

processor = LlmAgent(
    name="processor",
    instruction="Process if {validation_status} is valid"  # Reads from state
)

# ✅ CORRECT: Use temp: for transient data between tools
def fetch_data(source: str, context):
    data = get_from_source(source)
    context.state["temp:raw_data"] = data  # Available only this invocation
    return {"status": "fetched", "rows": len(data)}

# ❌ WRONG: Polluting permanent state unnecessarily
def fetch_data(source: str, context):
    context.state["data_1234"] = data  # Permanent state pollution
```

## 🚀 Agent Implementation Checklist

### Before Creating Any Agent
- [ ] **Single Responsibility**: Agent has ONE clear purpose
- [ ] **Clear Description**: LLM can understand when to use this agent
- [ ] **Defined Inputs/Outputs**: Clear data flow via output_key
- [ ] **Appropriate Model**: Use faster models for simple tasks
- [ ] **Tool Selection**: Only include necessary tools

### Agent Definition Template
```python
agent = LlmAgent(
    name="descriptive_name",           # Clear, specific name
    model="gemini-2.0-flash-exp",      # Or appropriate model
    description="Clear one-line purpose",  # For LLM routing
    instruction="""
    You are responsible for [specific task].

    Your capabilities:
    1. [Capability 1]
    2. [Capability 2]

    Process:
    1. [Step 1]
    2. [Step 2]

    Output format: [Expected output]
    """,
    tools=[...],                       # Minimal necessary tools
    output_key="result_key",           # If passing data forward
    sub_agents=[...]                   # If coordinator pattern
)
```

## 🧪 Testing Requirements

### Multi-Agent System Tests
```python
# Test agent interactions
async def test_agent_coordination():
    system = MultiAgentSystem()
    result = await system.process_request("test request")

    # Verify:
    # 1. Correct agent was selected
    # 2. Data passed correctly between agents
    # 3. Final output is as expected
    assert result["status"] == "success"
    assert "coordinator" in result["agents_used"]
```

## 🚫 Common ADK Anti-Patterns to AVOID

### 1. Over-Complex Agents
```python
# ❌ WRONG: Agent doing too much
super_agent = LlmAgent(
    name="everything",
    tools=[tool1, tool2, ..., tool50]  # Too many tools!
)

# ✅ CORRECT: Specialized agents
research_agent = LlmAgent(name="research", tools=[search, summarize])
analysis_agent = LlmAgent(name="analysis", tools=[calculate, visualize])
```

### 2. Circular Dependencies
```python
# ❌ WRONG: Agents calling each other in circles
agent_a.sub_agents = [agent_b]
agent_b.sub_agents = [agent_a]  # Infinite loop!

# ✅ CORRECT: Clear hierarchy
coordinator.sub_agents = [agent_a, agent_b]
```

### 3. Ignoring Parallel Opportunities
```python
# ❌ WRONG: Sequential when could be parallel
pipeline = SequentialAgent([
    fetch_api1,  # 2 seconds
    fetch_api2,  # 2 seconds
    fetch_api3   # 2 seconds
])  # Total: 6 seconds

# ✅ CORRECT: Parallel execution
parallel = ParallelAgent([
    fetch_api1, fetch_api2, fetch_api3
])  # Total: ~2 seconds
```

## 📈 Performance Optimization

### 1. Model Selection
```python
# Use appropriate models for task complexity
simple_agent = LlmAgent(model="gemini-1.5-flash")     # Fast, simple tasks
complex_agent = LlmAgent(model="gemini-2.0-flash-exp") # Complex reasoning
```

### 2. Tool Design for Parallel Execution
```python
# Design tools to be async-friendly
async def fetch_data(source: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(source) as response:
            return {"data": await response.json()}
```

### 3. Efficient State Management
```python
# Only store what's needed
agent = LlmAgent(
    output_key="summary",  # Store only summary, not full text
    instruction="Summarize and save only key points"
)
```

## 🎯 Quick Reference

### Agent Selection Guide
- **LlmAgent**: General purpose with LLM reasoning
- **SequentialAgent**: Step-by-step workflows
- **ParallelAgent**: Concurrent independent tasks
- **LoopAgent**: Iterative processes
- **Custom BaseAgent**: Special business logic

### Communication Method Selection
- **sub_agents**: For hierarchical delegation
- **AgentTool**: When parent needs response back
- **output_key**: For passing data in pipelines
- **temp: state**: For transient tool communication
- **transfer_to_agent**: For explicit handoffs

### Tool Type Selection
- **FunctionTool**: Synchronous operations < 30s
- **LongRunningFunctionTool**: Async/external processes
- **AgentTool**: Delegating to another agent
- **Built-in Tools**: Google services integration
- **OpenAPI Tools**: REST API integration

## 🆘 Debugging Multi-Agent Systems

### Enable Verbose Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Track agent interactions
system = MultiAgentSystem()
system.enable_trace = True
```

### Common Issues and Solutions

1. **Agent Not Selected**: Check description clarity
2. **Data Not Passing**: Verify output_key and state references
3. **Infinite Loops**: Review agent hierarchy
4. **Slow Performance**: Consider ParallelAgent
5. **Tool Failures**: Validate parameters and returns

## 💻 General Software Engineering Best Practices

### 1. Code Organization & Structure

```python
# ✅ CORRECT: Clean module structure
project/
├── agents/
│   ├── __init__.py
│   ├── coordinator.py
│   ├── researcher.py
│   └── analyzer.py
├── tools/
│   ├── __init__.py
│   ├── api_tools.py
│   └── data_tools.py
├── config/
│   ├── __init__.py
│   └── settings.py
├── tests/
│   ├── test_agents/
│   └── test_tools/
├── requirements.txt
└── README.md

# ❌ WRONG: Everything in one file
main.py  # 5000 lines of mixed code
```

### 2. Error Handling & Logging

```python
# ✅ CORRECT: Comprehensive error handling
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

def process_request(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Process request with proper error handling."""
    try:
        # Validate input
        if not data or 'id' not in data:
            raise ValueError("Invalid input: missing required 'id' field")

        # Process with logging
        logger.info(f"Processing request {data['id']}")
        result = perform_operation(data)

        # Log success
        logger.info(f"Successfully processed request {data['id']}")
        return result

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return {"error": str(e), "status": "validation_failed"}

    except Exception as e:
        logger.exception(f"Unexpected error processing request: {e}")
        return {"error": "Internal error", "status": "failed"}

# ❌ WRONG: No error handling
def process_request(data):
    result = perform_operation(data)  # Will crash on error
    print(f"Done")  # Using print instead of logging
    return result
```

### 3. Type Hints & Documentation

```python
# ✅ CORRECT: Full type hints and documentation
from typing import List, Dict, Optional, Union
from dataclasses import dataclass

@dataclass
class AgentConfig:
    """Configuration for an agent.

    Attributes:
        name: Unique identifier for the agent
        model: Model to use (e.g., 'gemini-2.0-flash-exp')
        max_retries: Maximum retry attempts for failures
    """
    name: str
    model: str
    max_retries: int = 3

def create_agent(
    config: AgentConfig,
    tools: Optional[List[str]] = None
) -> Union[LlmAgent, None]:
    """Create an agent with the given configuration.

    Args:
        config: Agent configuration object
        tools: Optional list of tool names to attach

    Returns:
        Configured LlmAgent instance or None if creation fails

    Raises:
        ValueError: If config is invalid
    """
    if not config.name:
        raise ValueError("Agent name is required")

    return LlmAgent(name=config.name, model=config.model)

# ❌ WRONG: No types or documentation
def create_agent(config, tools=None):
    # What does this do? What's config? What's returned?
    return LlmAgent(name=config['name'])
```

### 4. Configuration Management

```python
# ✅ CORRECT: Environment-based configuration
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    """Application configuration."""
    api_key: str
    model_name: str = "gemini-2.0-flash-exp"
    max_agents: int = 10
    timeout: int = 30
    debug: bool = False

    @classmethod
    def from_env(cls) -> 'Config':
        """Load configuration from environment variables."""
        return cls(
            api_key=os.environ.get("GOOGLE_AI_API_KEY", ""),
            model_name=os.environ.get("MODEL_NAME", "gemini-2.0-flash-exp"),
            max_agents=int(os.environ.get("MAX_AGENTS", "10")),
            timeout=int(os.environ.get("TIMEOUT", "30")),
            debug=os.environ.get("DEBUG", "false").lower() == "true"
        )

    def validate(self) -> None:
        """Validate configuration."""
        if not self.api_key:
            raise ValueError("GOOGLE_AI_API_KEY is required")

# ❌ WRONG: Hardcoded configuration
API_KEY = "sk-1234567890"  # NEVER hardcode secrets!
MODEL = "some-model"
DEBUG = True
```

### 5. Dependency Injection

```python
# ✅ CORRECT: Dependency injection for testability
from abc import ABC, abstractmethod

class DataStore(ABC):
    @abstractmethod
    def get(self, key: str) -> Any:
        pass

class RedisStore(DataStore):
    def __init__(self, client):
        self.client = client

    def get(self, key: str) -> Any:
        return self.client.get(key)

class Agent:
    def __init__(self, name: str, store: DataStore):
        self.name = name
        self.store = store  # Injected dependency

    def retrieve_context(self, key: str):
        return self.store.get(key)

# ❌ WRONG: Hard dependencies
class Agent:
    def __init__(self, name: str):
        self.name = name
        self.store = RedisClient()  # Hard-coded, can't test!
```

### 6. Testing Best Practices

```python
# ✅ CORRECT: Comprehensive testing
import pytest
from unittest.mock import Mock, patch

class TestAgent:
    """Test suite for Agent functionality."""

    @pytest.fixture
    def mock_store(self):
        """Create a mock data store."""
        store = Mock(spec=DataStore)
        store.get.return_value = {"data": "test"}
        return store

    def test_agent_creation(self, mock_store):
        """Test agent can be created with valid config."""
        agent = Agent(name="test", store=mock_store)
        assert agent.name == "test"
        assert agent.store == mock_store

    def test_retrieve_context(self, mock_store):
        """Test context retrieval from store."""
        agent = Agent(name="test", store=mock_store)
        result = agent.retrieve_context("key1")

        mock_store.get.assert_called_once_with("key1")
        assert result == {"data": "test"}

    @pytest.mark.parametrize("invalid_name", [None, "", " "])
    def test_invalid_names(self, invalid_name, mock_store):
        """Test agent creation fails with invalid names."""
        with pytest.raises(ValueError):
            Agent(name=invalid_name, store=mock_store)

# ❌ WRONG: No tests or poor test coverage
def test_something():
    assert True  # Not actually testing anything!
```

### 7. Async/Await Best Practices

```python
# ✅ CORRECT: Proper async implementation
import asyncio
from typing import List
import aiohttp

async def fetch_data(session: aiohttp.ClientSession, url: str) -> dict:
    """Fetch data from URL asynchronously."""
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.json()
    except aiohttp.ClientError as e:
        logger.error(f"Failed to fetch {url}: {e}")
        return {}

async def fetch_multiple(urls: List[str]) -> List[dict]:
    """Fetch multiple URLs concurrently."""
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_data(session, url) for url in urls]
        return await asyncio.gather(*tasks)

# ❌ WRONG: Blocking in async or improper error handling
async def fetch_data(url: str):
    response = requests.get(url)  # Blocking call in async!
    return response.json()  # No error handling!
```

### 8. Resource Management

```python
# ✅ CORRECT: Proper resource management
from contextlib import contextmanager
import threading

@contextmanager
def managed_resource(resource_factory):
    """Context manager for resource lifecycle."""
    resource = None
    try:
        resource = resource_factory()
        yield resource
    finally:
        if resource and hasattr(resource, 'close'):
            resource.close()

class ConnectionPool:
    """Thread-safe connection pool."""

    def __init__(self, max_connections: int = 10):
        self._connections = []
        self._lock = threading.Lock()
        self._max = max_connections

    def acquire(self):
        """Acquire a connection from the pool."""
        with self._lock:
            if self._connections:
                return self._connections.pop()
            elif len(self._connections) < self._max:
                return self._create_connection()
            else:
                raise RuntimeError("No connections available")

    def release(self, conn):
        """Return connection to pool."""
        with self._lock:
            self._connections.append(conn)

# ❌ WRONG: Resource leaks
def process_file(filename):
    f = open(filename)  # File never closed!
    data = f.read()
    # No error handling, file handle leaked
    return data
```

### 9. Security Best Practices

```python
# ✅ CORRECT: Security-conscious code
import secrets
import hashlib
from typing import Optional

def generate_api_key() -> str:
    """Generate cryptographically secure API key."""
    return secrets.token_urlsafe(32)

def validate_input(user_input: str) -> Optional[str]:
    """Validate and sanitize user input."""
    # Remove potentially dangerous characters
    sanitized = user_input.strip()

    # Check length limits
    if len(sanitized) > 1000:
        raise ValueError("Input too long")

    # Validate against whitelist pattern
    import re
    if not re.match(r'^[a-zA-Z0-9\s\-_.]+$', sanitized):
        raise ValueError("Invalid characters in input")

    return sanitized

def hash_password(password: str, salt: bytes) -> str:
    """Securely hash password with salt."""
    return hashlib.pbkdf2_hmac('sha256',
                                password.encode('utf-8'),
                                salt,
                                100000)

# ❌ WRONG: Security vulnerabilities
def validate_input(user_input):
    return user_input  # No validation!

password = "admin123"  # Hardcoded password
api_key = "12345"  # Weak key
```

### 10. Performance Optimization

```python
# ✅ CORRECT: Performance-conscious code
from functools import lru_cache
import time

@lru_cache(maxsize=128)
def expensive_computation(n: int) -> int:
    """Cache results of expensive computations."""
    time.sleep(1)  # Simulate expensive operation
    return n * n

class BatchProcessor:
    """Process items in efficient batches."""

    def __init__(self, batch_size: int = 100):
        self.batch_size = batch_size
        self.buffer = []

    def add(self, item):
        """Add item to buffer, process when full."""
        self.buffer.append(item)
        if len(self.buffer) >= self.batch_size:
            self.process_batch()

    def process_batch(self):
        """Process accumulated items efficiently."""
        if not self.buffer:
            return

        # Process all items at once
        results = bulk_operation(self.buffer)
        self.buffer.clear()
        return results

# ❌ WRONG: Inefficient code
def process_items(items):
    results = []
    for item in items:
        # Making individual DB calls instead of batch
        result = db.query(f"SELECT * FROM table WHERE id = {item}")
        results.append(result)
    return results
```

### 11. Code Review Checklist

Before merging any code:
- [ ] **Type hints** on all functions
- [ ] **Docstrings** for classes and public methods
- [ ] **Error handling** for all external calls
- [ ] **Unit tests** with >80% coverage
- [ ] **No hardcoded** secrets or configuration
- [ ] **Logging** instead of print statements
- [ ] **Resource cleanup** (files, connections)
- [ ] **Input validation** for user data
- [ ] **Async/await** used correctly
- [ ] **Performance** considered (caching, batching)

### 12. Git Best Practices

```bash
# ✅ CORRECT: Clear, atomic commits
git add -p  # Stage specific changes
git commit -m "feat: Add retry logic to API client

- Implement exponential backoff
- Add max retry configuration
- Handle rate limit errors"

# ❌ WRONG: Unclear, mixed commits
git add .
git commit -m "stuff"  # What stuff?!
```

---

**Remember**: Build simple, focused agents that do one thing well. Complex behaviors emerge from well-orchestrated simple agents. Follow software engineering best practices to ensure maintainable, scalable, and reliable code.

**Last Updated**: December 2024
**ADK Version**: 1.15.1
**Model**: gemini-2.0-flash-exp