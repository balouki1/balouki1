# FPDEVSML Modeling Tips

## When to Use Atomic vs Coupled Models

### Use Atomic Models When:
- Implementing a single, cohesive component
- The behavior is best described as a state machine
- You need fine-grained control over timing and events

### Use Coupled Models When:
- Combining multiple components into a system
- You want to reuse existing models
- The system has clear hierarchical structure

## Common Model Types

### Queueing Systems
- Use atomic models for servers and queues
- Include arrival and service processes
- Track queue length and waiting times

### Manufacturing Systems
- Model machines, conveyors, buffers
- Include breakdown and repair processes
- Track throughput and utilization

### Network Systems
- Model routers, links, endpoints
- Include packet generation and routing
- Track latency and packet loss

### Traffic Systems
- Model vehicles, intersections, roads
- Include arrival patterns and routing logic
- Track flow rates and congestion

## Debugging FPDEVSML Models

1. **Check Structure**: Ensure all required elements are present
2. **Validate Types**: Verify port and variable types match
3. **Test Guards**: Ensure guards don't create deadlocks
4. **Initialize Properly**: Set initial states and variable values
5. **Check Couplings**: Verify all port connections are valid

## Performance Optimization

1. **Minimize State Space**: Use fewer states when possible
2. **Efficient Guards**: Keep guard conditions simple
3. **Reduce Couplings**: Minimize unnecessary connections
4. **Batch Processing**: Process multiple events together when possible
