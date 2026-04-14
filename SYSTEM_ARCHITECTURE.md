# System Design Blueprint

---

## 1. System Overview

### 1.1 Purpose
- Detect and classify anomalies in smart grid systems  
- Address both physical disturbances and cyber attacks  
- Provide interpretable and controlled decision-making  
- Support operator-assisted response instead of fully automated enforcement  

---

### 1.2 Design Objectives
- Reliability (robust detection)  
- Interpretability (clear reasoning for decisions)  
- Real-time processing capability  
- Human-in-the-loop control  
- System stability and fault tolerance  
- Safe operation through controlled intervention  

---

### 1.3 High-Level Architecture
- Mode Selection  
- Data Pipeline  
- Physical Layer  
- Machine Learning Layer  
- Fusion Mechanism  
- Event System  
- Operator Actions  
- Logging & User Interface  

---

## 2. Operational Modes

### 2.1 Debug Mode
- Uses labelled dataset  
- Sequential data streaming  
- Reproducible experiments  
- Supports validation and testing  

### 2.2 Live Mode
- Simulated real-time operation  
- Random sampling of dataset  
- Represents deployment conditions  

### 2.3 Scenario Handling

The system maintains a unified `scenario` representation with context-dependent meaning:

- **Debug Mode**:
  - Scenario represents the ground truth label from the dataset (`marker`)
  - Used for validation and comparison

- **Live Mode**:
  - Scenario represents the predicted class from the ML model (`Final_class`)
  - No ground truth is available in real-time operation

Additionally:
- The system distinguishes between:
  - **Scenario** → system interpretation (prediction or selected case)
  - **Original Scenario** → ground truth (Debug Mode only)

This design ensures:
- Consistency in logging and UI representation  
- Realistic behaviour in live deployment  
- Clear separation between prediction and ground truth during evaluation  

---

## 3. Data Pipeline

### 3.1 Data Source
- Preprocessed smart grid dataset  
- Contains labelled events (normal / attack)  
- Structured as rows of features  

### 3.2 Data Flow
- Row selection based on mode  
- Preprocessing:
  - remove unused fields  
  - align feature columns  
- Generate clean input (`row_clean`)  

### 3.3 Streaming Logic
- Debug Mode:
  - Sequential index increment
  - Supports deterministic replay
  - Prevents index skipping after operator interaction

- Live Mode:
  - Random index sampling
  - Maintains last index during system freeze
  - Prevents abrupt jumps after resume
  - Ensures stable visual continuity during review

---

## 4. Physical Layer

### 4.1 Purpose
- Detect abnormal physical behaviour  
- Provide interpretable system insight  

### 4.2 Inputs
- Voltage measurements  
- Current measurements  
- Frequency  
- Sequence components (positive, negative, zero)  
- Impedance anomaly flags  

### 4.3 Processing
- Compare measurements against baseline  
- Apply feature scaling  
- Compute disturbance scores per relay  
- Apply directional weighting  
- Identify abnormal deviations  

### 4.4 Outputs
- Raw disturbance scores  
- Normalized scores  
- Most affected relay  
- Top contributing features  

---

## 5. Machine Learning Layer

### 5.1 Purpose
- Classify system state  
- Detect type of anomaly or attack  

### 5.2 Inputs
- Processed feature vector  

### 5.3 Model
- Supervised learning model  
- Binary classification (normal vs attack)  
- Multi-class classification (attack type or system condition)  

### 5.4 Outputs
- Final binary decision  
- Predicted class label  
- Confidence score  
- Contributing features  

---

## 6. Fusion Mechanism

### 6.1 Purpose
- Combine physical and ML outputs  

### 6.2 Logic
- Select relay with highest disturbance score  
- Combine with ML classification result  

### 6.3 Output
- Final affected relay  
- Final system label  
- Decision path explanation  

---

## 7. Event System

### 7.1 Trigger
- Activated when anomaly detected  

### 7.2 Event Creation
- Generate unique Event ID  
- Capture timestamp  
- Store physical snapshot  
- Store ML results  

### 7.3 System Freeze (Review State)
- Pause data streaming immediately upon anomaly detection  
- Lock current system state and event context  
- Prevent creation of new events during review  
- Maintain consistent data snapshot across UI components  
- Disable automatic progression until operator action  

This ensures:
- No event overwriting during investigation  
- Stable and traceable system behaviour  
- Accurate alignment between physical, ML, and UI states  

### 7.4 Event Persistence

Once an event is created, it remains active until explicitly resolved by the operator.

Key properties:
- Events are not overwritten during review
- New events are blocked while the system is in a frozen state
- The current event is preserved across UI reruns
- Event identity (Event ID) remains constant throughout the lifecycle

This prevents:
- Loss of investigation context  
- Inconsistent logging  
- UI-state desynchronisation  

---

## 8. Operator Interaction

### 8.1 Review Actions
- Investigate  
- Acknowledge  
- Ignore  

### 8.2 Control Actions
- Isolate relay  
- Lock relay (manual enforcement)  
- Restore system  

### 8.3 Effect on System
- Modify physical state representation  
- Update system behaviour and flow  
- Control actions are **manually triggered by the operator**  

---

## 9. Physical System Representation

### 9.1 Grid Model
- Relays (R1–R4)  
- Breakers (BR1–BR4)  
- Lines (L1–L2)  
- Buses (B1–B3)  
- Generators (G1–G2)  

### 9.2 State Mapping
- Normal (green)  
- Warning (yellow)  
- Fault (red)  
- Isolated / Locked (special states)  

### 9.3 Flow Relationships
- Cause-effect propagation  
- Relay → breaker → line → bus interactions  

---

## 10. Logging System

### 10.1 Event Logs
- Physical events  
- ML results  
- User actions  

### 10.2 Structure
- Event ID  
- Timestamp  
- Source (Physical / IDS / User)  
- Decision  
- Scenario (system interpretation)  
- Original Scenario (Debug Mode only)  
- Action  

### 10.3 Purpose
- Traceability  
- Post-event analysis  
- Debugging support  

---

## 11. User Interface

### 11.1 Dashboard Layout
- Header (mode, status)  
- Left panel (controls, measurements)  
- Center panel (grid visualisation)  
- Right panel (alerts and actions)  

### 11.2 Visualisation
- Grid diagram  
- PMU waveform  
- Metric displays  

### 11.3 Design Principles
- Clarity over complexity  
- Separation of detection and control  
- Real-time feedback  

---

## 12. System Flow Summary

- Mode selection  
- Data ingestion  
- Physical analysis  
- ML classification  
- Scenario determination (mode-dependent)  
- Fusion decision  
- Event creation  
- **System enters review state (frozen)**  
- Event is locked and preserved  
- Operator review  
- Operator action (investigate / acknowledge / ignore / control)  
- Logging  
- System resumes operation  

---

## 13. Design Considerations

### 13.1 Hybrid Detection Approach
- Combines physical and ML layers  
- Improves robustness and accuracy  

### 13.2 Human-in-the-Loop Design
- Prevents incorrect automation  
- Ensures safe decision-making  
- System does **not automatically enforce lock actions**  
- Operator confirms mitigation before execution  

### 13.3 Limitations
- Simulated dataset  
- Model dependency  
- Simplified grid representation  
- Manual intervention may introduce response delay  

---

## 14. System State Management

### 14.1 Session State Control
- Maintain system variables across runs  
- Track running state and events  

### 14.2 Execution Modes
- Idle  
- Running  
- Paused (review state)  

### 14.3 State Transitions
Idle → Running → Detection → Frozen (Review State) → Action → Resume → Running

### 14.4 Freeze Control Logic

The system implements a controlled freeze mechanism:

- Triggered when:
  - An anomaly is detected
  - An operator selects an event for review

- Behaviour during freeze:
  - Data streaming is paused
  - Current index is preserved
  - PMU history is frozen
  - UI remains responsive
  - Event creation is disabled

- Resume condition:
  - Triggered by operator action (e.g. Acknowledge)

This ensures deterministic and stable system behaviour during critical analysis.

---

## 15. Data Preprocessing and Validation

### 15.1 Data Cleaning
- Remove unnecessary fields  
- Handle missing values  

### 15.2 Feature Consistency
- Ensure alignment with model input  

### 15.3 Validation
- Detect invalid or corrupted data  

---

## 16. Explainability and Interpretability

### 16.1 Physical Layer
- Relay disturbance scores  
- Feature-based explanation  

### 16.2 ML Layer
- Confidence scores  
- Contributing factors  

### 16.3 Combined Insight
- Align physical and ML outputs  
- Provide operator understanding  

---

## 17. Human-in-the-Loop Decision Framework

### 17.1 Philosophy
- System supports decision, does not enforce it  

### 17.2 Workflow
Detect → Pause → Review → Operator Action → Control Execution

### 17.3 Safety
- Reduces risk of incorrect automated response  
- Ensures operator validation before execution  

### 17.4 Event Lifecycle

Each event follows a structured lifecycle:

1. Detection  
2. Event Creation  
3. Freeze (Review State)  
4. Investigation / Acknowledgement / Ignore  
5. Control Action (optional)  
6. Logging  
7. Resume

This lifecycle ensures:
- Controlled handling of anomalies  
- Full traceability  
- Prevention of unintended automated actions  

---

## 18. Performance and Responsiveness

### 18.1 Real-Time Behaviour
- Continuous data streaming  

### 18.2 Efficiency
- Lightweight per-sample computation  

### 18.3 UI Responsiveness
- Controlled reruns using session state  
- Stable updates during review state  

---

## 19. Fault Tolerance and Robustness

### 19.1 Error Handling
- Safe defaults  
- Fallback mechanisms  

### 19.2 Stability
- Prevent crashes during interaction  
- Maintain consistent state during pause  

### 19.3 Graceful Degradation
- Operate with partial data  

---

## 20. Cyber-Physical Integration

### 20.1 Dual-Layer System
- Physical + ML integration  

### 20.2 Complementary Strengths
- Physical: interpretable  
- ML: adaptive  

### 20.3 Benefits
- Improved detection accuracy  
- Reduced false positives  

---

## 21. Scalability Considerations

### 21.1 System Expansion
- Additional relays supported  

### 21.2 Data Scaling
- Compatible with larger datasets  

### 21.3 Future Integration
- Real PMU streams possible  

---

## 22. Security Considerations

### 22.1 Attack Coverage
- Data injection  
- Measurement anomalies  

### 22.2 Limitations
- Unknown attack types  
- Dataset dependency  

### 22.3 Defensive Design
- Multi-layer detection  
- Human validation before enforcement  
- Reduced risk of false positives causing unintended actions  