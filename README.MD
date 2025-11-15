# Gnutella-like Application, Distributed System CO3071
## Overview
This application is a course assignment for the Distributed Systems class at Ho Chi Minh City University of Technology (HCMUT). It is a lightweight clone of the Gnutella peer-to-peer (P2P) file sharing protocol, built to explore the fundamentals of decentralized networking.

While it omits many advanced features found in full-fledged Gnutella clients, this minimalist implementation of the Gnutella 0.6 protocol is designed for learning and experimentation. It demonstrates key concepts such as:

- A two-tier P2P architecture with ultra peers and leaf peers
- Query routing using Bloom filters for efficient search propagation
- Basic file discovery and transfer mechanisms

## Feature
- Two-tier peer architecture (ultra peers and leaf peers)
- Query routing using Bloom filters
- Ping/Pong peer discovery
- Query and QueryHit message handling
- Push protocol for NAT traversal
- Lightweight packet formatting and parsing
## Architecture
- **Peer-to-Peer**: Decentralized, 1 host cache server to help user join the network
- **Layered Design**:
  - Transport Layer: TCP socket communication
  - Protocol Layer: Packet encoding/decoding
  - Application Layer: File search and transfer
- **Data Flow Diagram**: [Gnutella-like.drawio](https://drive.google.com/file/d/1ylwlpljaLZEu3fy_trc9XQRE70ZjnGJj/view?usp=sharing)