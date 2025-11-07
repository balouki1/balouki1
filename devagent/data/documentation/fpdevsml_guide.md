# FPDEVSML - Formal Parallel DEVS Modeling Language

## Overview

FPDEVSML (Formal Parallel DEVS Modeling Language) is an XML-based specification language for defining discrete-event simulation models following the DEVS (Discrete Event System Specification) formalism.

## Model Types

### Atomic Models

Atomic models are the basic building blocks of DEVS models. They contain:

- **Ports**: Input and output interfaces
- **States**: Discrete states the model can be in
- **Variables**: Data storage
- **Transitions**: State change logic
- **Functions**: Reusable computation blocks

#### Structure

```xml
<model name="ModelName" type="atomic">
  <description>Model description</description>
  <ports>...</ports>
  <states>...</states>
  <variables>...</variables>
  <transitions>...</transitions>
  <functions>...</functions>
  <initialization>...</initialization>
</model>
```

### Coupled Models

Coupled models compose multiple submodels (atomic or coupled) through port connections.

#### Structure

```xml
<model name="ModelName" type="coupled">
  <description>Model description</description>
  <submodels>...</submodels>
  <couplings>...</couplings>
  <ports>...</ports>
  <externalCouplings>...</externalCouplings>
</model>
```

## Core Elements

### Ports

Define input and output interfaces:

```xml
<ports>
  <input name="portName" type="dataType"/>
  <output name="portName" type="dataType"/>
</ports>
```

### States

Define discrete states:

```xml
<states>
  <state name="stateName" initial="true|false"/>
</states>
```

### Variables

Define model variables:

```xml
<variables>
  <variable name="varName" type="dataType" initial="initialValue"/>
</variables>
```

### Transitions

Define state transitions with guards and actions:

```xml
<transition from="sourceState" to="targetState" event="eventName">
  <guard>condition</guard>
  <action>
    code to execute
  </action>
</transition>
```

### Functions

Define reusable functions:

```xml
<function name="functionName" returns="returnType">
  <body>
    function implementation
  </body>
</function>
```

## Common Patterns

### Queue Model Pattern

A queue model typically has:
- States: idle, busy
- Variables: queue (list), currentCustomer
- Transitions: arrive (add to queue), endService (serve next)

### Generator Pattern

A generator model typically has:
- State: active
- Variables: entityCount, interArrivalTime
- Transition: generate (create and output entity)

### Network Pattern (Coupled)

A network model typically connects:
- Generator → Queue/Server → Sink
- Uses couplings to connect submodel ports

## Data Types

Common data types in FPDEVSML:
- `integer`: Whole numbers
- `real`: Floating-point numbers
- `string`: Text
- `boolean`: True/false
- `list`: Collections
- Custom types: `customer`, `entity`, `packet`, etc.

## Distributions

Common probability distributions:
- `exponential(rate)`: Exponential distribution
- `uniform(min, max)`: Uniform distribution
- `normal(mean, stddev)`: Normal distribution

## Best Practices

1. **Clear Naming**: Use descriptive names for models, ports, and variables
2. **Documentation**: Include description elements
3. **Modularity**: Break complex models into coupled submodels
4. **Type Safety**: Declare types explicitly
5. **Guards**: Use guards to ensure valid transitions
6. **Initialization**: Initialize all variables properly
