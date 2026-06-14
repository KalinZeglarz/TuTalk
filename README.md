# TuTalk 💬

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

⚠️**Note: This repository is a Proof of Concept (PoC) designed to demonstrate distributed systems logic and multi-threaded socket communication. It is not intended for production environments.**

---

A lightweight, high-performance, decentralized peer-to-peer (P2P) mesh chat network built with ```Python```. 

**TuTalk** operates fully distributed without any central servers — each instance acts simultaneously as a client, a server, and an autonomous message router using an optimized flood routing mechanism.

---

## 🚀 Key Features

- **Pure P2P Architecture:** No central authority or server dependency.
- **Thread-Safe Routing:** Full state synchronization using multi-threading primitives (`threading.Lock`) protecting against race conditions.
- **Robust Protocol Guard:** Protection against Denial of Service (DoS) buffer overflows with line-length constraints.
- **Loop-Prevention Mechanism:** UUID-based packet deduplication layer preventing routing loops in full-mesh topologies.
- **Clean Protocol Definitions:** Type-safe messaging layer backed by dedicated Python `Enum` representations.
- **Cross-Platform Automated Testing:** Embedded CI-style verification pipelines and standalone deterministic stress-testing modules compatible with Unix and Windows subsystem sockets.

---

## 🧠 System Architecture

Every active node inside the TuTalk network maintains a concurrent execution loop handling three core layers:

1. **TCP Listener Socket:** Accepts incoming peer connections in an isolated background thread.
2. **Dynamic Connection Pool:** Explicitly manages thread-safe socket states wrapping read/write operations.
3. **Flood Router Layer:** Dispatches received packets across all connected peers while logging transactions via the standard `logging` facility.

### Mesh Topology Layout

```
          Peer A
        /   |   \
   Peer B ----- Peer C
        \   |   /
          Peer D
```

- Every peer broadcasts payload packages outward to all current pipe connections.
- Deduplication keys (`seen` registry) act as cryptographic filters ensuring packets are handled exactly once.

---

## ⚙️ Protocol & Wire Format

Communication runs over raw TCP using **Newline-Delimited JSON (NDJSON)**.

### Packet Frame Schema

```json
{
  "type": "message",
  "id": "7b0d2d31-fb91-4cf5-9df0-7bc404288b39",
  "sender": "Alice",
  "content": "Hello world!",
  "time": "23:45:12"
}
```
### Supported Message Primitives (```MessageType```)

- ```message```: Standard text payload routed across the mesh layout.
- ```hello```: Handshake frame transmitted when a new node joins a connection pipeline.
- ```leave```: Graceful closure signal ensuring automated connection pool cleanup.
---

## 🖥️ Getting Started

### Prerequisites
- ```Python 3.10``` or higher is required.
- No external third-party library dependencies (built entirely on the standard Python toolchain).

### Launching the Client
Execute the entrypoint file from your terminal:
```
python tutalk.py
```
### Interactive Usage Flow

1. Define your local session ```Username```.
2. Allocate a dedicated TCP network interface ```Port``` (e.g., ```5001```).
3. Link existing mesh endpoints by appending ```IP:Port``` paths (leave blank and press ```ENTER``` to host standalone).
4. Type standard text to broadcast messages, or use ```/quit``` to cleanly exit the chat session.

---

## 🧪 Comprehensive Verification Suite

The repository includes a dedicated test engine covering deterministic component states and high-load performance under concurrency stress.

1. **Execute Unit Testing Framework**:
Run the integrated runner script to inspect state management, deduplication accuracy, and socket closure cycles:
  ```
  python tests/test_runner.py
  ```
2. **Run Comprehensive Stress Simulation**:
Simulate a high-frequency packet flood attack across a dense 10-peer virtual network layout to verify thread locks under heavy load:
  ```
  python tests/stress/stress_test.py
  ```
3. **Pytest Integration**:
The full suite is completely compatible with modern testing frameworks. Run via ```pytest``` for advanced execution reporting:
  ```
  python -m pytest tests/ -s
  ```
---

## 📌 Architectural Implementation Choices

### Structural Defenses & Security
- **Memory Boundary Bounds**: 
Buffers are restricted to a ```MAX_LINE_LENGTH``` threshold of ```64 KB```. This mitigates memory exhaustion exploits if an adversarial node sends a non-terminated data stream.
- **Socket Timeouts**: 
Connection attempts use a deterministic ```180.0s``` timeout threshold, avoiding permanent process blocks on dead or unresponsive IP routes.

### Structural Tradeoffs
- **Pros**: 
Completely decentralized architecture, simple horizontal integration, instant zero-configuration local networking, and robust thread safety.
- **Cons**: 
Network traffic scales at  *O(N^2)* density due to flood routing limitations, missing an encrypted TLS handshake layer, and no local cold-storage message history.

---

## 🔮 Improvement Ideas

- **Gossip Protocol Optimization**: 
Refactor routing mechanisms to limit transmission redundancy across larger network groups.

- **Transport Security**: 
Wrap raw socket layers inside native ```ssl.SSLContext``` structures to enforce peer-to-peer TLS encryption.

---
