# Technical Architecture Diagrams for Convoscope Documentation

This file contains all the Mermaid diagrams planned for the MkDocs documentation. These diagrams will be embedded directly in the documentation pages.

## 1. System Architecture Diagram

```mermaid
architecture-beta
    group frontend(cloud)[Frontend Layer]
    group backend(cloud)[Backend Services] 
    group storage(database)[Data Storage]
    group external(cloud)[External APIs]

    service streamlit(internet)[Streamlit UI] in frontend
    service session(server)[Session Management] in frontend
    
    service llm_service(server)[LLM Service] in backend
    service conv_manager(server)[Conversation Manager] in backend
    service error_handler(server)[Error Handler] in backend
    
    service file_storage(disk)[File Storage] in storage
    service conversation_db(database)[Conversation Data] in storage
    
    service openai(internet)[OpenAI API] in external
    service anthropic(internet)[Anthropic API] in external
    service google(internet)[Google Gemini] in external

    streamlit:R -- L:session
    streamlit:D -- U:llm_service
    streamlit:D -- U:conv_manager
    
    llm_service:R -- L:error_handler
    llm_service:D -- U:openai
    llm_service:D -- U:anthropic
    llm_service:D -- U:google
    
    conv_manager:D -- U:file_storage
    conv_manager:D -- U:conversation_db
    
    session:D -- U:conv_manager
```

## 2. Data Flow Diagram

```mermaid
flowchart TD
    A[User Input] --> B[Input Validation]
    B --> |Valid| C[Session State Check]
    B --> |Invalid| D[Error Message]
    
    C --> E[LLM Service Router]
    E --> F{Provider Available?}
    
    F --> |OpenAI Available| G[OpenAI API Call]
    F --> |OpenAI Failed| H[Anthropic Fallback]
    F --> |All Failed| I[Error Handler]
    
    G --> J[Response Processing]
    H --> J
    I --> K[User Error Message]
    
    J --> L[Stream Response to UI]
    J --> M[Save to Conversation Manager]
    
    M --> N[File System Storage]
    M --> O[Auto-save Backup]
    
    L --> P[Display to User]
    N --> Q[Conversation History]
    O --> R[Recovery System]
    
    style A fill:#e1f5fe
    style P fill:#e8f5e8
    style K fill:#ffebee
    style I fill:#ffebee
```

## 3. LLM Service Class Diagram

```mermaid
classDiagram
    class LLMService {
        +PROVIDERS: Dict[str, LLMProvider]
        +__init__()
        +get_available_providers() Dict
        +get_available_models(provider) List
        +get_completion(provider, model, messages) str
        +get_completion_with_fallback(messages) str
        +validate_messages(messages) bool
        -_check_provider_availability() void
    }
    
    class LLMProvider {
        +name: str
        +models: List[str]
        +env_key: str
        +available: bool
    }
    
    class ConversationManager {
        +conversation_dir: Path
        +__init__(conversation_dir)
        +save_conversation(conversation, filename) Tuple
        +load_conversation(filename) Tuple
        +list_conversations() List
        +delete_conversation(filename) Tuple
        +auto_save_conversation(conversation) Tuple
        +validate_conversation(conversation) bool
        +sanitize_filename(filename) str
        +get_conversation_stats(filename) Dict
        -_ensure_directory_exists() void
    }
    
    class LLMServiceError {
        <<exception>>
    }
    
    class ConversationError {
        <<exception>>
    }
    
    LLMService --> LLMProvider : contains
    LLMService --> LLMServiceError : raises
    ConversationManager --> ConversationError : raises
    
    note for LLMService "Handles multi-provider LLM integration\nwith retry logic and fallbacks"
    note for ConversationManager "Manages conversation persistence\nwith validation and error handling"
```

## 4. User Interaction Sequence Diagram

```mermaid
sequenceDiagram
    participant U as User
    participant ST as Streamlit UI
    participant SS as Session State
    participant LLM as LLM Service
    participant CM as Conversation Manager
    participant API1 as OpenAI API
    participant API2 as Anthropic API
    
    U->>ST: Enter message
    ST->>SS: Update session state
    ST->>LLM: get_completion_with_fallback(message)
    
    LLM->>API1: Primary API call (OpenAI)
    API1-->>LLM: Error (rate limit)
    
    Note over LLM: Retry with exponential backoff
    LLM->>API1: Retry API call
    API1-->>LLM: Error (still rate limited)
    
    Note over LLM: Switch to fallback provider
    LLM->>API2: Fallback API call (Anthropic)
    API2-->>LLM: Success response
    
    LLM-->>ST: Stream response chunks
    
    loop Response streaming
        ST->>U: Display partial response
        ST->>SS: Update conversation state
    end
    
    ST->>CM: auto_save_conversation()
    CM->>CM: Validate conversation format
    CM->>CM: Create backup if needed
    CM-->>ST: Save confirmation
    
    ST->>U: Display complete response
```

## 5. Conversation Lifecycle State Diagram

```mermaid
stateDiagram-v2
    [*] --> New : User starts chat
    
    New --> Active : First message sent
    Active --> Processing : LLM call initiated
    
    Processing --> Streaming : Response received
    Processing --> Error : API failure
    Processing --> Retrying : Temporary failure
    
    Retrying --> Processing : Retry attempt
    Retrying --> Fallback : Max retries reached
    Fallback --> Processing : Switch provider
    Fallback --> Error : All providers failed
    
    Streaming --> Active : Response complete
    Active --> Saving : Auto-save triggered
    Saving --> Active : Save successful
    Saving --> SaveError : Save failed
    SaveError --> Active : Continue despite error
    
    Active --> Exporting : User requests export
    Exporting --> Active : Export complete
    
    Active --> Loading : Load different conversation
    Loading --> Active : Load successful
    Loading --> LoadError : Load failed
    LoadError --> New : Reset to new conversation
    
    Error --> Active : User continues
    Active --> [*] : Session ends
    
    note right of Processing
        Multi-provider fallback
        with retry logic
    end note
    
    note right of Saving
        Automatic backup
        and validation
    end note
```

## 6. Testing Architecture Diagram

```mermaid
flowchart TB
    subgraph "Test Structure"
        A[pytest Configuration] --> B[Test Fixtures]
        B --> C[Mock Objects]
        C --> D[Test Suites]
    end
    
    subgraph "Test Categories" 
        D --> E[Unit Tests - Utils]
        D --> F[Unit Tests - Services]
        D --> G[Integration Tests]
        D --> H[Error Handling Tests]
    end
    
    subgraph "Test Coverage Areas"
        E --> E1[Helper Functions]
        E --> E2[Session State Management]
        
        F --> F1[LLM Service]
        F --> F2[Conversation Manager]
        F --> F3[Error Handling]
        
        G --> G1[End-to-End Workflows]
        G --> G2[Provider Fallbacks]
        
        H --> H1[API Failures]
        H --> H2[File System Errors]
        H --> H3[Validation Errors]
    end
    
    subgraph "Mocking Strategy"
        C --> M1[Streamlit Session State]
        C --> M2[LLM API Responses]
        C --> M3[File System Operations]
        C --> M4[Environment Variables]
    end
    
    style A fill:#e3f2fd
    style D fill:#f3e5f5
    style C fill:#fff3e0
```

## 7. Deployment & CI/CD Architecture

```mermaid
gitgraph
    commit id: "Initial Monolith"
    branch feature-refactor
    checkout feature-refactor
    commit id: "Extract Utils"
    commit id: "Add Tests"
    commit id: "LLM Service"
    commit id: "Error Handling"
    checkout main
    merge feature-refactor
    commit id: "Portfolio Ready"
    branch documentation
    checkout documentation
    commit id: "MkDocs Setup"
    commit id: "Architecture Docs"
    commit id: "API Reference"
    checkout main
    merge documentation
    commit id: "Production Deploy"
```

## Usage in Documentation

Each diagram serves a specific purpose in the portfolio documentation:

1. **System Architecture**: Homepage hero diagram showing technical sophistication
2. **Data Flow**: Implementation guide showing request processing
3. **Class Diagram**: API reference showing object relationships  
4. **Sequence Diagram**: Usage examples showing interaction patterns
5. **State Diagram**: Architecture section showing conversation lifecycle
6. **Testing Architecture**: Development process showing quality practices
7. **Git Flow**: Portfolio impact showing systematic development approach

These diagrams demonstrate:
- **Technical Communication Skills**: Clear visual explanation of complex systems
- **System Design Thinking**: Understanding of distributed systems and error handling
- **Professional Development Practices**: Comprehensive testing and documentation
- **Architecture Expertise**: Multi-provider integration with fallback strategies