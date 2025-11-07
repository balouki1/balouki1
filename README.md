# A Comprehensive Guide to FPDEVSML Elements

This guide details the syntax and purpose of each section for both Atomic and Coupled models.

## Core Concepts

### Preconditions: Quantifiers and Guards

After the `pre-state` pattern is matched, the rule's applicability is further checked by optional quantifiers and a final guard. These are the rule's preconditions.

#### Quantifiers (`∀`, `∃`, `∄`)

Quantifiers are logical preconditions used when a rule's logic depends on inspecting the contents of a state collection (`set`, `array`, or `map`).

##### `∀` (For All)

* **Syntax:** `∀ var ∈ collection | predicate`
* **Logic:** Checks if **all** elements (`var`) in the `collection` satisfy the `predicate`.
* **Example (using projection):**
  `(...) → (...) ∀ slot ∈ buffer | π_1(slot) == FULL;`
* **Meaning:**
  This expression checks if *every* element (named `slot`) in the `buffer` collection satisfies the predicate. The predicate uses the **projection function `π_1`** to access the **first attribute** of the `slot` tuple and compares it to `FULL`.

---

##### `∃` (Exists)

* **Syntax:** `∃ var ∈ collection | predicate`
* **Logic:** Checks if **at least one** element (`var`) in the `collection` satisfies the `predicate`. If the predicate is omitted, it simply checks if the collection is non-empty.

* **Example 1 (using projection):**
  `(...) → (...) ∃ job ∈ job_queue | π_1(job) == HIGH;`
* **Meaning 1:**
  This checks if there is *at least one* element (named `job`) in the `job_queue` collection where its **first attribute** (accessed via `π_1`) is equal to `HIGH`. (Note: The index `1` assumes priority is the first element of the `job` tuple).

* **Example 2 (without projection):**
  `(...) → (...) ∃ job ∈ job_queue;`
* **Meaning 2:**
  This checks only if the `job_queue` collection is *not empty*.

---

##### `∄` (Does Not Exist)

* **Syntax:** `∄ var ∈ collection | predicate`
* **Logic:** Checks if **no** element (`var`) in the `collection` satisfies the `predicate`.

* **Example 1 (using projection):**
  `(...) → (...) ∄ sensor ∈ sensor_list | ¬π_1(sensor);`
* **Meaning 1:**
  This checks that *no* element (named `sensor`) in the `sensor_list` collection has its **first attribute** (accessed via `π_1`) set to `false`.

* **Example 2 (without projection):**
  `(...) → (...) ∄ sensor ∈ sensor_list;`
* **Meaning 2:**
  This checks if the `sensor_list` collection is *empty*.

---

#### Guard (`|`)

The **Guard** is a final boolean check applied to a transition rule. It is evaluated *after* any quantifiers have been resolved. The transition rule is only considered valid (applicable) if this `boolean_expression` evaluates to `true`.

* **Syntax:** `| boolean_expression`
* **Semantic:** The rule is selected **only if** this expression is `true`. The expression can use state variables, parameters, and standard logical connectors.

---

##### Examples of Guard Expressions

These examples illustrate the `boolean_expression` that would appear *after* the `|` symbol in a rule.

* **Example 1 (Simple Comparison):**
  `(...) → (...) | count < max_capacity;`
* **Meaning:** This guard checks if the value of the state variable `count` is strictly less than the value of the parameter `max_capacity`.

* **Example 2 (Logical AND `∧`):**
  `(...) → (...) | (status == IDLE) ∧ (job_queue_size > 0);`
* **Meaning:** This guard checks if two conditions are met simultaneously: the `status` variable must be `IDLE` AND the `job_queue_size` variable must be greater than 0.

* **Example 3 (Logical OR `∨`):**
  `(...) → (...) | (priority == HIGH) ∨ is_urgent;`
* **Meaning:** This guard checks if at least one of the conditions is met: either the `priority` variable is `HIGH` OR the `is_urgent` variable is `true`.

* **Example 4 (Logical NOT `¬`):**
  `(...) → (...) | ¬(is_full);`
* **Meaning:** This guard checks if the boolean variable `is_full` is `false`.

* **Example 5 (Combined Expression):**
  `(...) → (...) | ( (current_load > 0) ∧ ¬(is_locked) ) ∨ is_admin_request;`
* **Meaning:** This guard checks a more complex condition: the rule is applicable if (the `current_load` is positive AND the system is not `is_locked`) OR if it is an `is_admin_request`.

##### Quantifiers and Guards

Expressions such as

```fpdevsml
(...) → (...) ∃ job ∈ job_queue;
```

can be misleading if not explicitly explained.

A quantifier without a predicate (`| condition`) is **not a shorthand for a general existential expression** — it is valid **only** as a test for non-emptiness of the collection.
In other words, `∃ job ∈ job_queue;` simply checks whether `job_queue` contains at least one element.
This should be clarified to prevent readers from assuming that the quantifier supports implicit or context-dependent predicates.

The use of the guard operator (`|`) is clearly described, but its relationship to quantifiers can be better illustrated.
In FPDEVSML, **quantifiers are evaluated before the guard expression**, and the **guard** itself is evaluated last, once all variable bindings introduced by the quantifiers are established.
Clarifying this evaluation order — *quantifiers first, guard last* — helps avoid ambiguity in complex conditional transitions.
A short example showing both parts together would make this distinction explicit.

---

#### Catalog of Domain Types

Each `Domain_i` listed above is a `domain_definition` (Line 11). Here are all possibilities for the type of a *single* state variable.

##### Simple & Predefined Domains

These domains represent atomic or qualitative values.

* **`predefined set`**

  Represents the fundamental numeric and logical data types available in PFDEVSML.
  These are the atomic building blocks used to define quantitative and boolean state variables.

  * **Examples:**
    * R (Real numbers),
    * R+ (Non-negative real numbers),
    * N (Natural numbers: 0, 1, 2, …),
    * Z (Integers),
    * B (Booleans),
    * Q (Rational numbers).

  * **Usage Example:** `sigma ∈ R`

  Each predefined set defines a basic scalar domain.
  These domains cannot be further decomposed and are often used as components within more complex structures (e.g., tuples, sets, or arrays).

* **`symbol set`**
  An enumeration type used to define qualitative or categorical states, such as model phases or modes of operation.

    * **Syntax:** <symbol_1, symbol_2, ...>
    * **Usage Example:** phase ∈ <idle, busy, processing>

    Each symbol represents a distinct qualitative value within the domain. 
    Unlike numerical types, symbol sets have no inherent ordering — they are purely descriptive labels used for comparison or pattern matching in transitions.

##### Structured (Complex) Domains

These domains model collections and complex data structures.

* **`set`**
  An **unordered collection** of elements of the same type, with no duplicates.

    * **Syntax:** `{ domain_element }`
    * **Usage:** `my_set ∈ { N }` (a set of natural numbers).
    * **Typical Initial Value:** `∅` (EmptySet) or `{1, 5, 10}`.

* **`ordered set` (Array)**
  This domain defines an **ordered collection**. Based on the grammar (`-('@' > uint_)`), the size specification is **optional**.

    1.  **Fixed-Size Array:**

        * **Syntax:** `[ domain_element @ size ]`
        * **Usage:** `buffer ∈ [ N @ 10 ]` (A fixed-size array of 10 Naturals).

    2.  **Variable-Size Array:**

        * **Syntax:** `[ domain_element ]`
        * **Usage:** `dynamic_queue ∈ [ N ]` (A variable-size ordered set of Naturals).

  Note: If both structures share the same syntax (e.g., [N] or [N @ 10]) but differ in behavior — such as fixed 
versus variable size, or insertion order semantics — this distinction should be made explicit.
Clarifying whether an ordered set is conceptually identical to an array (and whether it supports head/tail 
pattern matching) would help avoid confusion.

* **`map` (Map/Dictionary)**
  A **key-value structure** (dictionary) associating elements from a Key-Domain to elements of a Value-Domain.

    * **Syntax:** `≪ Key_Domain → Value_Domain ≫`
    * **Usage:** `routing_table ∈ ≪ (id) ∈ (N) → (port) ∈ (N) ≫`.
    * **Typical Initial Value:** `≪ ≫` (empty map) or `≪ (1, 2), (10, 5) ≫`.

* **`tuple` (Tuple)**
  Allows a state variable to be a structured **n-tuple itself**.

    * **Syntax:** `(name1, ...) ∈ (Domain1, ...)`
    * **Usage:** `current_job ∈ (id, priority) ∈ (N, N)`
    * **Typical Initial Value:** `(1, 10)`.

-----

#### Composition and Advanced Examples

The true power of FPDEVSML comes from the **recursive composition** of these types. The grammar explicitly allows a collection type (like `set` or `array`) to contain elements that are themselves complex types (like `tuple`).

##### Example A: Fixed-Size Array of Tuples

**Concept:** A FIFO queue of size 5, where each entry is a task `(id, priority)`.

```fpdevsml
S: (job_queue) ∈ (
    # Array of 5 elements
    [ 
      # Element Type: a tuple (id, prio)
      (id, prio) ∈ (N, N) 
      @ 5 
    ]
   ) 
   = (
    # Initial Value: An array of 5 (0,0) tuples
    [(0,0), (0,0), (0,0), (0,0), (0,0)]
   );
```

##### Example B: Variable-Size Array of Tuples

**Concept:** A dynamic task list containing `(id, priority)` tasks.

```fpdevsml
S: (task_list) ∈ (
    # Type: Variable-size array (no @ size)
    [ 
      # Element Type: a tuple (id, prio)
      (id, prio) ∈ (N, N) 
    ]
   ) 
   = ( 
    # Initial Value: An empty array
    ∅ 
   );
```

##### Example C: Set of Tuples

**Concept:** A "connection manager" that maintains a set (variable size) of active `(ip, port)` connections.

```fpdevsml
S: (connections) ∈ (
    # Type (Line 21): A set
    { 
      # Element Type (Line 22 -> 26): a tuple (ip, port)
      (ip, port) ∈ (N, N) 
    }
   ) 
   = ( 
    # Initial Value: the empty set
    ∅ 
   );
```

##### Example D: Set of Complex Tuples (Maximum Combination)

**Concept:** A "Scheduler" managing a set of "Processes". Each Process (a tuple) has a `pid` (N), a `stack` (fixed-size array), and file `handles` (map).

```fpdevsml
S: (process_set) ∈ (
     # Type (Line 21): A set
     {
       # Element Type (Line 22 -> 26): a tuple (pid, stack, handles)
       (pid, stack, handles) ∈ (
         N,                     # Domain 1: N
         [ N @ 256 ],           # Domain 2: Fixed-Array
         ≪ (handle_id) ∈ (N) → (resource_id) ∈ (N) ≫ # Domain 3: Map
       )
     }
   ) 
   = ( 
    # Initial Value: the empty set
    ∅ 
   );
```

### Accessing Tuple Elements (Projection `π`)

When a variable (e.g., `j`) is bound by a quantifier (`∀`, `∃`) and represents a tuple, "dot notation" (like `j.prio`) is **not** valid.

As you correctly stated, the formal **projection operator `π`** (Pi) must be used to access the elements of that tuple.

* **Syntax:** `π_i(tuple_variable)`
* **Semantic:** This extracts the **i-th** element from the `tuple_variable`. The index `i` is 1-based.
* **Example:** If `j` is a variable bound to a tuple `(id, prio) ∈ (N, N)`, then:
    * `π_1(j)` refers to the `id`.
    * `π_2(j)` refers to the `prio`.

### Accessing Map Elements

In FPDEVSML, **maps** (also known as *dictionaries* or *associative arrays*) associate **keys** from one domain to **values** from another domain.
The grammar defines a map as:

```fpdevsml
≪ (key_tuple) ∈ (TupleDomain) → (value_tuple) ∈ (TupleDomain) ≫
```

For example:

```fpdevsml
durations ∈ ≪ (product_id, po_index) ∈ (N, N)
              → (loading_time, setup_time, processing_time, unloading_time) ∈ (N, N, N, N) ≫;
```

This defines a map named `durations` where each key `(product_id, po_index)` corresponds to a 4-tuple of numeric processing times.

---

#### Access by Key (`≪ map : key ≫`)

To access the **value** associated with a specific key in a map, FPDEVSML uses the **selection operator** `≪ map : key ≫`.

* **Syntax:**

  ```fpdevsml
  ≪ map_variable : key_expression ≫
  ```

* **Semantics:**
  Returns the **value** bound to `key_expression` within `map_variable`.

* **Example 1 — Simple Access**

  ```fpdevsml
  routing_table ∈ ≪ (packet_id) ∈ (N) → (port_id) ∈ (N) ≫;

  ≪ routing_table : 10 ≫
  ```

  Returns the `port_id` associated with packet ID `10`.

* **Example 2 — Tuple Key and Tuple Value**

  ```fpdevsml
  durations ∈ ≪ (product_id, po_index) ∈ (N, N)
                → (loading_time, setup_time, processing_time, unloading_time) ∈ (N, N, N, N) ≫;

  ≪ durations : (2, 1) ≫
  ```

  Returns the tuple `(loading_time, setup_time, processing_time, unloading_time)` for product `2` and order `1`.

* **Notes:**

    * If the key is not present in the map, the result is undefined (the model must guarantee key existence).
    * This operator is purely functional — it does **not** modify the map.

---

#### Iterating Over Maps (Quantifiers with Tuple Binding)

When using quantifiers (`∀`, `∃`, `∄`) on a map, the iterator binds to **key–value pairs** as **tuples**.
Each iteration provides a two-element tuple `(key, value)`.

* **Syntax:**

  ```fpdevsml
  ∀ (key, value) ∈ map_variable | condition
  ∃ (key, value) ∈ map_variable | condition
  ```

* **Semantics:**
  Each map element is treated as a 2-tuple where:

    * the **first element** is the key (possibly itself a tuple),
    * the **second element** is the value (also possibly a tuple).

---

* **Example 3 — Existential Quantifier over a Map of Tuple Keys and Tuple Values**

```fpdevsml
assignments ∈ ≪ (product_id, po_index) ∈ (N, N)
                 → (machine_id, start_time, end_time) ∈ (N, R, R) ≫;

∃ ((prod, order), (machine, start, end)) ∈ assignments | end - start > 100.0;
```

This expression checks whether there exists at least one entry in the map `assignments`
whose **value tuple** `(machine, start, end)` corresponds to a job lasting more than `100` time units.

---

* **Example 4 — Universal Quantifier over a Map**

```fpdevsml
sensor_map ∈ ≪ (sensor_id) ∈ (N)
                → (status, value) ∈ (<OK, FAIL>, R) ≫;

∀ (sid, (st, val)) ∈ sensor_map | st = OK ∧ val ≥ 0.0;
```

This expression verifies that **all sensors** in the map `sensor_map`
have their `status` equal to `OK` and a non-negative `value`.
If at least one sensor violates this condition, the quantifier evaluates to `⊥`.

---

### Accessing Ordered Set Elements (Indexing `[ ]`)

An **ordered set** (also known as an *array*) represents an **indexed sequence** of elements.
Unlike a regular set `{ }`, it preserves order and supports **positional access** via index brackets `[ ]`.

An ordered set is declared as follows:

```fpdevsml
queue ∈ [ (id, duration) ∈ (N, R+) @ 5 ];
```

This defines a fixed-size ordered set of five tuples `(id, duration)`.

The indexing operator allows direct access to a specific element of an ordered set by position.

* **Syntax:**

  ```fpdevsml
  ordered_set_variable [ index_expression ]
  ```

* **Semantics:**
  Returns the element at the position `index_expression`.
  The index is **1-based** (the first element has index `1`).

---

* **Example 1 — Simple Index Access**

```fpdevsml
buffer ∈ [ (item_id) ∈ (N) @ 3 ] = [(11), (22), (33)];

buffer[2]
```

This expression returns the second element of the ordered set — here, `(22)`.

---

* **Example 2 — Accessing a Tuple Field**

```fpdevsml
jobs ∈ [ (id, time) ∈ (N, R+) @ 5 ];

π_2(jobs[3])
```

This returns the **second component** (`time`) of the **third tuple** stored in `jobs`.

---

* **Example 3 — Nested Example (Arrays of Tuples)**

```fpdevsml
task_list ∈ [ (task_id, duration, priority) ∈ (N, R+, N) @ 10 ];

π_3(task_list[1])
```

Retrieves the **priority** of the **first task** in the ordered set.

---

### Operations on Collections (`set` and `ordered set`)

The primary operations for manipulating these collections (whether ordered or unordered) are defined in the FPDEVSML grammar as set expressions (`set_expression`).

These operators are used in the "post-state" (right-hand side) of a transition to construct the new value of the state variable.

#### Union (`∪` - U+222A)

* **Purpose**: To add an element to a collection.
* **Grammar Syntax**: The operation is defined for adding a single element.
    * `{ element } ∪ collection`
    * `collection ∪ { element }`

Note: In the grammar, both forms are valid and equivalent. However, the left- or right-position of the new element may carry semantic meaning when working with ordered sets (lists), as it affects insertion order.

* **Example Usage (`ordered set`)**: In the `sink` model, the `finished_po` variable is an `ordered set` (a array). The following operation is used in an external transition to add a new element `(t, po)`:
    * `... → (SEND, 0, {(t, po)} ∪ finished_po);`

#### Difference / Removal (`∖` - U+2216)

* **Purpose**: To remove an element or a subset from a collection.
* **Grammar Syntax**: `collection ∖ { element }`).
* **Example Usage (`ordered set`)**: In the `machine` model, `jobs` is an `ordered set`. The following operation is used to remove a specific `job` element (previously identified):
    * `... → ( (jobs ∖ { job }), ... );`

---

### Manipulation via Pattern Matching (Head/Tail)

For list manipulation (`ordered set` or `set` defined with variable size), FPDEVSML supports structural decomposition (pattern matching) directly in the **pre-state** (left-hand side) of transition functions (`delta_int`, `delta_ext`).

#### `[H|T]` Decomposition Syntax

The notation `[ head_variable | tail_variable ]` is used to decompose an `ordered set`.

* `head_variable`: This variable is bound to the **first** element of the collection.
* `tail_variable`: This variable is bound to a **new** `ordered set` containing all elements except the first (the "tail").

#### Example of Use

Let's use the example you provided, applied to an internal transition.

> **State Context:**
> `S: (sigma, job_list, current_job) ∈ (R, [(id, duration) ∈ (N,R+)], (N,R+)) = ...`
>
> **Internal Transition (`delta_int`):**
> `(sigma, [job|next_jobs], _) → (sigma, next_jobs, job);`

**Analysis of this transition:**

1.  **Pre-state (Left): `(sigma, [job|next_jobs], _)`**
    * This rule only applies if `job_list` (the second attribute) is **not empty**.
    * `sigma`: The `sigma` variable is bound to the value of the first attribute.
    * `[job|next_jobs]`: The `job_list` is decomposed:
        * `job` is bound to the first element of `job_list` (which is a tuple `(id, duration)`).
        * `next_jobs` is bound to the list of remaining elements.
    * `_`: The value of `current_job` is ignored (wildcard).

2.  **Post-state (Right): `(sigma, next_jobs, job)`**
    * The state is updated as follows:
    * `sigma`: The first attribute (sigma) retains its value.
    * `next_jobs`: The `job_list` (second attribute) is replaced by the "tail" (`next_jobs`).
    * `job`: The `current_job` (third attribute) is replaced by the "head" (`job`) that was just extracted.

#### The Empty Set or Ordered Set Case

Pattern matching also allows specifying behavior for an empty list using the `∅` (U+2205) symbol.

* **Example:**
    * `# If the list is empty, transition to PASSIVE`
    * `(ACTIVE, ∅) → (PASSIVE, +∞);`
    * `# If the list is not empty, process it`
    * `(ACTIVE, [h|t]) → (PROCESSING, 1.0, h, t);`

---

### Set Comprehension and Aggregation Operators

This section documents the operators used to perform advanced operations on set collections within FPDEVSML expressions. These operators are typically used in transition functions, guards, or output functions.

These operators follow a formal, set-based notation, allowing for the construction of new sets (`map`) or the calculation of a single aggregated value (`max`, `min`, `∑`, `∏`).

-----

#### **General Syntax**

```
Operator{ iterator ∈ collection }( expression )
```

-----

#### **Syntax Breakdown**

1.  **`Operator`**

    * The function to be applied. This includes:
        * **Transformation:** `map`
        * **Aggregation (Extrema):** `max`, `min`
        * **Aggregation (Arithmetic):** `∑` (U+2211), `∏` (U+220F)

2.  **`{ iterator ∈ collection }`**

    * This clause defines the iteration scope.
    * `collection`: The state variable (must be a set, e.g., `{(N,R)}`) over which to iterate.
    * `iterator`: A temporary variable name bound to each element of the `collection` during the iteration.

3.  **`( expression )`**

    * The expression to be evaluated for each element.
    * This expression typically involves the `iterator` variable.
    * The projection operator `π_i` is used to access specific elements of the `iterator` if it is a tuple.

-----

#### **Operator Definitions and Examples**

Let us assume the following state variable definition for all examples:

`S: (..., jobs, ...) ∈ (..., {(N,R)}, ...)`

(Where `jobs` is a set of tuples, each representing `(priority, duration)`)

-----

##### `map` (Set Transformation)

* **Purpose:** Constructs a new set by applying the `expression` to every element in the `collection`.
* **Example:** To construct a new set containing only the priorities (the first element) of all jobs:
  ```
  map{ job ∈ jobs }( π_1(job) )
  ```
* **Result:** A new set of domain `{N}`.

-----

##### `max` / `min` (Aggregation: Extrema)

* **Purpose:** Returns a single value representing the maximum or minimum result of the `expression` evaluated over all elements.
* **Example (max priority):**
  ```
  max{ job ∈ jobs }( π_1(job) )
  ```
* **Result:** A single value of domain `N`.

-----

##### `∑` (Summation) / `∏` (Product)

* **Purpose:** Returns a single value representing the sum (`∑`) or product (`∏`) of the `expression` evaluated over all elements.
* **Example (total duration using Sum):**
  ```
  ∑{ j ∈ jobs }( π_2(j) )
  ```
* **Result:** A single value of domain `R`.

-----
### Wildcards and Empty Collections: `_` vs `∅`

In FPDEVSML, the underscore (`_`) and the empty set symbol (`∅`) are both used to represent “absence” but they have **distinct meanings and contexts**.

#### **`_` — Wildcard / “Don’t Care”**

* **Meaning:**
  The underscore is a **wildcard** used in **pattern matching**.
  It indicates that a value is **present but ignored** — the model does not check or bind it.

* **Typical Contexts:**

    * In state tuples or transition rules:

      ```fpdevsml
      (WAIT, sigma, _) → (SEND, 0, _);
      ```

      Here, `_` means “match any value” for that position, without caring about its content.

    * In expressions or guards, `_` **cannot** be used as a value; it is only a **syntactic placeholder** in patterns.

---

#### **`∅` — Empty Collection**

* **Meaning:**
  Represents a **concrete value** — specifically, the **empty set**, **empty array**, or **empty map**, depending on the declared domain.

* **Typical Contexts:**

    * As an initial value for collections:

      ```fpdevsml
      S: (job_queue) ∈ ([ (id, duration) ∈ (N, R+) ]) = (∅);
      ```

      This means the queue starts empty.

    * In guards or quantifiers to check emptiness:

      ```fpdevsml
      (...) → (...) ∄ job ∈ job_queue;
      ```

---

#### **Summary**

| Symbol | Meaning                      | Type                | Typical Use                                    |
|:-------|:-----------------------------|:--------------------|:-----------------------------------------------|
| `_`    | Wildcard (ignore this value) | *Syntactic pattern* | In `delta_int`, `delta_ext`, or `lambda` rules |
| `∅`    | Empty collection             | *Literal value*     | As initial value or in logical checks          |

---


Voici la section en **anglais** et en **Markdown**, que tu peux insérer juste après la précédente (`_` vs `∅`) ou dans la partie “Numerical Expressions” — elle s’y intègre parfaitement car elle concerne un littéral numérique spécial :

---

### Infinity Literal (`+∞` / `-∞`)

The symbols `+∞` and `-∞` represent **special numeric literals** in FPDEVSML.
They are **not variables** or keywords, but concrete constant values of the **infinity type**, used primarily in **time-related expressions**.

#### **Purpose and Semantics**

* **`+∞` (Positive Infinity):**
  Indicates an *unbounded duration* or *no scheduled internal event*.
  Commonly used in the **time advance function (`ta`)** or to represent a passive waiting state.

* **`-∞` (Negative Infinity):**
  Rarely used in standard models. It may appear in mathematical expressions or analytical extensions but has no operational meaning in simulation semantics.

---

#### **Typical Use Cases**

* **1. Time Advance Function (`ta`):**

  ```fpdevsml
  ta: {
    (PASSIVE, _) → +∞;   # The model will never trigger an internal transition
    (ACTIVE, _) → 0;      # The model transitions immediately
  }
  ```

* **2. State Initialization:**

  ```fpdevsml
  S: (phase, sigma) ∈ (<WAIT, SEND>, R) = (WAIT, +∞);
  ```

* **3. Guards and Comparisons:**

  ```fpdevsml
  (...) → (...) | sigma = +∞;
  ```

---

#### **Notes**

* The infinity symbols are **literals recognized by the grammar**, not user-defined identifiers.
  Their parsing is handled by the rule:

  ```cpp
  infinity = (char_('+') | char_('-')) > lit(u8"\u221e");
  ```
* They can be combined with arithmetic operators, but comparisons involving `+∞` or `-∞` follow conventional mathematical semantics (`x < +∞` is always true).

---
### Boolean Constants (`⊤` / `⊥`)

The symbols `⊤` and `⊥` represent the **boolean constants** `true` and `false` in FPDEVSML.
They are **literal values**, not identifiers, and are directly recognized by the grammar.

#### **Purpose and Meaning**

* **`⊤` (True):**
  Represents the boolean value *true*.
  Used in guards, predicates, and logical expressions.

* **`⊥` (False):**
  Represents the boolean value *false*.
  Used to express conditions that are always false, or to initialize boolean flags.

---

#### **Typical Use Cases**

* **1. In Guards:**

  ```fpdevsml
  (...) → (...) | (status = IDLE) ∧ ⊤;
  ```

  The guard always evaluates to true if `status = IDLE`.

* **2. In Quantifiers:**

  ```fpdevsml
  ∀ sensor ∈ sensors | π_1(sensor) = ⊥;
  ```

  Checks if all sensors have their first field set to false.

* **3. As Initial Values:**

  ```fpdevsml
  S: (is_active) ∈ (B) = (⊥);
  ```

---

#### **Grammar Note**

The boolean literals are defined by the grammar rule:

```cpp
boolean_term = boost::spirit::qi::unicode::string(u8"\u22a5")  // ⊥ (false)
             | boost::spirit::qi::unicode::string(u8"\u22a4")  // ⊤ (true)
             | ...
```

They can be combined with logical operators such as:

* `¬` (NOT)
* `∧` (AND)
* `∨` (OR)

---

## Atomic Models

An atomic model defines the indivisible behavior of a system component. It is specified by the following sections.

The specification includes several **mandatory** components that define the model's structure and behavior:
* **S (State Variables):** Defines the dynamic state and initial values.
* **X (Input Ports):** Defines the interfaces for receiving external events (mandatory even if empty).
* **Y (Output Ports):** Defines the interfaces for sending events (mandatory even if empty).
* **delta\_int (Internal Transition):** Governs state changes based on internal timing.
* **delta\_ext (External Transition):** Governs state changes in reaction to input events.
* **delta\_conf (Confluent Transition):** Defines behavior when internal and external events occur at the same time.
* **ta (Time Advance):** Determines the time the model stays in its current state.
* **lambda (Output Function):** Generates outputs just before an internal transition.

Additionally, the model can include one **optional** section:
* **P (Parameters):** Defines static configuration values set at initialization.

### `S:` (State)

The state is the core of an atomic model's behavior, and FPDEVSML provides a rich, recursive type system to 
model data structures from simple to highly complex.

#### The Fundamental State Structure

At the highest level, the `S:` section is **always an n-tuple**.

The formal grammar follows this syntax:

```fpdevsml
S: (var_1, ..., var_n) ∈ (Domain_1, ..., Domain_n) = (Initial_1, ..., Initial_n);
```

This declaration consists of three core parts:

1.  **`(var_1, ..., var_n)`** (`tuple_definition`, Line 27):
    The names you assign to your state variables (e.g., `(phase, sigma, buffer)`).

2.  **`(Domain_1, ..., Domain_n)`** (`tuple_domain_definition`, Line 28):
    The list of corresponding domains (types) for *each* state variable (e.g., `(<wait>, R, [N @ 10])`).

3.  **`(Initial_1, ..., Initial_n)`** (`tuple_value`, Line 93):
    The initial values for these variables, which must conform to the defined domains (e.g., `(wait, 0, [0,0,0,0,0,0,0,0,0,0])`).

The power and complexity lie in the possibilities for defining each `Domain_i`.

-----

### `P:` (Parameters)

This document provides the exhaustive reference for defining the atomic model `P:` (Parameters) section, based on the formal grammar.

Parameters define the **static configuration** of a model. They are set at initialization (or instantiation in a coupled model) and, unlike State (`S:`) variables, **cannot be changed** during the simulation run. They are used to make models reusable and configurable.

## The Fundamental Parameter Structure

The structure for defining parameters is **identical** to the structure for defining state. At the highest level, the `P:` section is **always an n-tuple**.

The formal grammar follows this syntax:

```fpdevsml
P: (param_1, ..., param_n) ∈ (Domain_1, ..., Domain_n) = (Default_1, ..., Default_n);
```

This declaration consists of three core parts:

1.  **`(param_1, ..., param_n)`** (`tuple_definition`):
    The names you assign to your parameters (e.g., `(timeout, buffer_size)`).

2.  **`(Domain_1, ..., Domain_n)`** (`tuple_domain_definition`):
    The list of corresponding domains (types) for *each* parameter (e.g., `(R, N)`).

3.  **`(Default_1, ..., Default_n)`** (`tuple_value`):
    The **default values** for these parameters. These values are used if not overridden when the model is instantiated inside a coupled model.

## Parameter Domains

The types of domains available for parameters are **exactly the same** as those available for the `S:` (State) section.

This includes all:

* **Simple Domains** (`predefined_set`, `symbol_set`)
* **Structured Domains** (`set`, `map`, `tuple_definition_in_domain`)
* **Array Domains** (`ordered set definition`), which can be fixed-size (e.g., `[N @ 10]`) or variable-size (e.g., `[N]`).

Please refer to the `S:` (State) documentation for a detailed catalog of these domain types and their composition rules.

## Key Differences from State (`S:`)

While the *syntax* is identical, the *semantics* are different:

* **Static:** Parameters are read-only during the simulation. Their values can be used in transition functions (e.g., `delta_int`) but never modified.
* **Default Values:** The values provided in the `P:` section are *defaults*. They can be overridden by a parent coupled model during instantiation.

## Examples of Use

The examples below focus on the role of parameters as static configuration.

### Example A: Simple Configuration

**Concept:** A `generator` model configured with a processing `duration` and a `limit` on items to produce.

```fpdevsml
P: (duration, limit) ∈ (R, N) = (10.0, 9999);
```

### Example B: Static Routing Table (Map)

**Concept:** A "router" model configured with a static, default `routing_table`.

```fpdevsml
P: (routing_table) ∈ (≪ (dest_id) ∈ (N) → (port_id) ∈ (N) ≫) 
   = ( ≪ (100, 1), (200, 2) ≫ );
```

### Example C: Fixed-Size Array as Parameter

**Concept:** A "filter" model that takes a static array of 5 floating-point `weights` as its configuration.

```fpdevsml
P: (weights) ∈ ([ R @ 5 ]) 
   = ( [0.0, 0.0, 0.0, 0.0, 0.0] );
```

### Example D: Set of Tuples as Configuration

**Concept:** A "firewall" model configured with a set of "allow rules," where each rule is a tuple of `(src_ip, src_port)`.

```fpdevsml
P: (allow_rules) ∈ ({ (ip, port) ∈ (N, N) }) 
   = ( ∅ );
```

## `X:` (Input Ports) and `Y:` (Output) Ports

This documentation covers the `X:` (Input) and `Y:` (Output) sections of an **Atomic Model**, including the multi-port definition feature.

The domains used to define the *type* of data in an event (the event's "payload") are **exactly the same** as those available for the `S:` (State) and `P:` (Parameters) sections.

-----

### `X:` (Input Ports) Section

The `X:` section declares the set of ports through which the atomic model can **receive** external events.

#### Fundamental Structure

A port definition in the `X:` section can take one of two forms:

##### Single Port Definition

This is the standard definition for a port that exists only as a single instance.

* **Syntax:**
  `(port_name, (var_1, ...)) | (Domain_1, ...)`

##### Multi-Port (Port Array) Definition

This form uses the `*` notation to declare an array of ports, where the size of the array is determined by a dynamic expression.

* **Syntax:**
  `(port_name * expression, (var_1, ...)) | (Domain_1, ...)`
* **`port_name`**: The base name for the port array (e.g., `in_channel`).
* **`expression`**: This expression evaluates to an integer, defining the **number of ports** in the array. This expression can typically use:
    * Parameters (from the `P:` section), e.g., `N` or `N + 2`.
    * State cardinality, e.g., `|my_set|`.

#### Examples

```fpdevsml
X: {
  # Example of a Single Port (no payload)
  (in_start, ()) | ();
  
  # Example of a Multi-Port (size N)
  # This creates N ports: in_channel1, in_channel2, ... in_channelN
  (in_channel * N, (data)) | ([N]);
  
  # Example of a simple payload
  (in_task, (id, priority)) | (N, N);

  # Example of a Complex Payload (as requested)
  # An integer + a tuple (integer, real)
  (in_complex_job, (job_id, job_data)) | (N, (task_id, task_value) ∈ (N, R));
}
```

### `Y:` (Output Ports) Section

The `Y:` section declares the set of ports through which the atomic model can **emit** external events.

#### Fundamental Structure

The structure is syntactically identical to the `X:` section. A port definition can be either a **single port** or a **multi-port**.

##### Single Port Definition

* **Syntax:**
  `(port_name, (var_1, ...)) | (Domain_1, ...)`

##### Multi-Port (Port Array) Definition

* **Syntax:**
  `(port_name * expression, (var_1, ...)) | (Domain_1, ...)`
* **`expression`**: Defines the size of the port array, just like in the `X:` section.

#### Examples

```fpdevsml
Y: {
  # Example of a Single Port (with payload)
  (out_done, (result)) | (B)
  
  # Example of a Multi-Port (size N)
  # This creates N ports: out_channel1, out_channel2, ... out_channelN
  (out_channel * N, (data)) | ([N])

  # Example of a Complex Payload
  # An integer + a tuple (integer, real)
  (out_complex_result, (result_id, result_data)) | (N, (op_code, op_val) ∈ (N, R))
}
```

### `delta_int:` (Internal Transition Function)

The `delta_int` function defines the autonomous behavior of an atomic model. It is triggered when the model's internal timer, defined by the time advance function (`ta(s)`), expires.

The `delta_int` section supports two distinct syntactical structures, which imply two different evaluation semantics: a simple "first-match-wins" and a complex "sequential-composition-of-blocks".

#### Core Concept: Pattern Matching (`pre-state_tuple`)

As you correctly identified, the first step for any transition rule is **Pattern Matching**.

* **Syntax:** `(pre-state_tuple) → (post-state_tuple); [quantifier;] [ | guard;]`
* **Semantic:** This tuple is a **pattern** to be matched against the model's current state `S:`.
    * **Constant:** If a position is a constant (e.g., `<WAITING>`), the model's state variable in that position **must** equal that constant.
    * **Variable:** If a position is a variable (e.g., `counter`), the current value is captured into that variable.
    * **Wildcard (`_`):** If a position is `_`, the value is matched but ignored.

A rule is only considered for application if its `pre-state_tuple` pattern successfully matches the current state.

#### Syntax 1: Simple Block (Sequential, First-Match-Wins)

This is the most common form, where all transition rules are defined within a single, top-level block.

##### Structure

```fpdevsml
delta_int: {
  # Rule 1
  (pre_1) → (post_1); [quant_1;] [| guard_1;]

  # Rule 2
  (pre_2) → (post_2); [quant_2;] [| guard_2;]
  
  ...
}
```

##### Evaluation Semantic

* **Sequential Order is Critical:** The rules are evaluated sequentially from top to bottom.
* **First-Match Wins:** The **first rule** that satisfies all three conditions is the **only one** to be executed:
    1.  The `(pre-state_tuple)` matches the current state.
    2.  The `[quantifiers]` (if present) evaluate to `true`.
    3.  The `[| guard]` (if present) evaluates to `true`.
* Once a rule is applied, the `delta_int` function terminates.

#### Syntax 2: Complex (Multi-Block / Sequential Composition)

This advanced syntax uses multiple, nested, **unlabeled** blocks to define a **chain** of transitions.

##### Structure 

```fpdevsml
delta_int: {
  # Block 1
  {
    (pre_1_1) → (post_1_1); [q_1_1;] [| g_1_1;]
    (pre_1_2) → (post_1_2); [q_1_2;] [| g_1_2;]
    ...
  } [BLOCK_1_quantifiers;] [| BLOCK_1_guard;]

  # Block 2
  {
    (pre_2_1) → (post_2_1); [q_2_1;] [| g_2_1;]
    (pre_2_2) → (post_2_2); [q_2_2;] [| g_2_2;]
    ...
  } [BLOCK_2_quantifiers;] [| BLOCK_2_guard; ]
}
```

##### Evaluation Semantic (Sequential Composition)

This is a sequential chain. **There is no parallel evaluation.** The blocks are evaluated in the order they are written.

Let `S_current` be the state when `delta_int` is triggered.

1.  **Evaluate Block 1:**

    * The **block-level** `[quantifiers]` and `| [guard]` for Block 1 are evaluated against `S_current`.
    * If they are `true`, the rules *inside* Block 1 are evaluated sequentially (first-match-wins) against `S_current`.
    * If a rule is applied, the state is updated, producing `S_next`. If no rule applies (or the block guard was false), `S_next = S_current`.

2.  **Evaluate Block 2:**

    * The **block-level** `[quantifiers]` and `| [guard]` for Block 2 are evaluated against `S_next` (the result from Block 1).
    * If they are `true`, the rules *inside* Block 2 are evaluated sequentially against `S_next`.
    * If a rule is applied, the state is updated, producing `S_final`.

3.  **Result:** The final state of the model is the result of the last block in the chain.

-----

#### Examples 

##### Example A: Pattern Matching (Simple Block)

* **Concept:** A rule that only applies if the `phase` is `WAITING` and `counter` is `0`.
* **Code:**
  ```fpdevsml
  delta_int: {
    # This rule is *only* considered if S.phase == WAITING and S.counter == 0
    (WAITING, _, 0) → (IDLE, +∞, 0);
  }
  ```

##### Example B: Simple Block (Sequential with Guard)

* **Concept:** A predator is `STARVED`. If `pop > 0`, one dies. If `pop == 0`, it becomes `DEAD`.
* **Code:**
  ```fpdevsml
  delta_int: {
    # Rule 1: Pattern match (STARVED, _, pop) and Guard (pop > 0)
    (STARVED, _, pop) → (DEAD, 0, pop - 1)
    | pop > 0;

    # Rule 2: Only checked if Rule 1 fails
    (STARVED, _, pop) → (DEAD, +∞, 0)
    | pop == 0;
  }
  ```

##### Example C: Simple Block (with `∃` Quantifier)

* **Concept:** A dispatcher in `IDLE` state checks its `job_queue`. If there `∃` (exists) at least one high-priority job, it transitions to `URGENT`. Otherwise, it transitions to `SLEEP`.
* `S: (phase, sigma, queue) ∈ (<IDLE, URGENT, SLEEP>, R, { (id, prio) ∈ (N, N) }) ...`
* **Code:**
  ```fpdevsml
  delta_int: {
    # Rule 1: Check for urgent jobs. 'j' is a (id, prio) tuple.
    # We must use π_2(j) to access the 2nd element (prio).
    (IDLE, _, q) → (URGENT, 0, q)
    ∃ j ∈ q | π_2(j) == HIGH;

    # Rule 2: If no urgent jobs, sleep
    (IDLE, _, q) → (SLEEP, +∞, q);
  }
  ```

##### Example D: Simple Block (with `∀` Quantifier)

* **Concept:** A "validator" model is in state `CHECKING`. If `∀` (for all) items in its `data_pool` are marked as `valid is ⊤`, it transitions to `FINISHED`.
* `S: (phase, sigma, pool) ∈ (<CHECKING, FINISHED>, R, [ (id, valid) ∈ (N, B) @ 10 ]) ...`
* **Code:**
  ```fpdevsml
  delta_int: {
    # Rule 1: Check if all items are valid. 'item' is an (id, valid) tuple.
    # We must use π_2(item) to access the 2nd element (valid).
    (CHECKING, _, p) → (FINISHED, +∞, p)
    ∀ item ∈ p | π_2(item);

    # Rule 2: If Rule 1 fails (quantifier is false), loop.
    (CHECKING, _, p) → (CHECKING, timeout, p);
  }
  ```

##### Example E: Multi-Block (Sequential Composition)

* **Concept:** A model *first* checks its `queue` for urgent messages, *then* (if its state is still `ACTIVE`) it decrements its `counter`.
* `S: (phase, sigma, counter, queue) ∈ (<ACTIVE, URGENT>, R, N, { (id, prio) ∈ (N, N) }) ...`
* `P: (queue_check_enabled) ∈ (B) = (⊤);`
* **Code:**
  ```fpdevsml
  delta_int: {
    # Block 1 (handles queue logic)
    {
      # Use π_2(j) to access 'prio'
      (<ACTIVE>, _, c, q) → (<URGENT>, 0, c, q)
      ∃ j ∈ q | π_2(j) == HIGH;
    } 
    | queue_check_enabled;

    # Block 2 (handles counter logic)
    # This block is evaluated *after* Block 1.
    {
      (<ACTIVE>, _, c, _) → (<ACTIVE>, _, c - 1, _)
      | c > 0;
    }
  }
  ```
  
### `delta_ext:` (External Transition Function)

The external transition function, `delta_ext`, defines how an atomic model **reacts to external events** from its input ports.

This function is triggered whenever one or more events (an "event bag") arrive at the model's input ports. It is provided with the model's current state `S`, the **elapsed time** `e` since the last transition, and the bag of incoming events.

The `delta_ext` section is defined by a complex block containing up to three subsections:

1.  **`I:` (Intermediate State)** (Optional)
2.  **`behavior:` (Behavior Rules)** (Mandatory)
3.  **`order:` (Event Order Function)** (Optional)

<!-- end list -->

```fpdevsml
delta_ext: {
  # I: (Optional)
  I: (i_var_1, ...) ∈ (D_i1, ...) = (init_i1, ...);
  
  # behavior: (Mandatory)
  behavior: {
    # Rules
    rule_1;
    rule_2;
    ...
  }

  # order: (Optional)
  order: {
    # Ordering rules
    order_rule_1;
    ...
  }
}
```

-----

#### `I:` (Intermediate State) Section (Optional)

This section defines a temporary, **intermediate state** used *only* during the execution of the `delta_ext` function.

* **Purpose:** When multiple events arrive simultaneously, the `delta_ext` function processes them one by one. The `I:` state is used to store temporary data (e.g., an accumulator) *between* the processing of these individual events.
* **Syntax:** `I: (var_1, ...) ∈ (Domain_1, ...) = (Initial_1, ...);`
* **Semantics:** The intermediate state is **re-initialized** to this default value *every time* the `delta_ext` function is called.

#### `behavior:` (Behavior Rules) Section

This is the core of the `delta_ext` function. As you specified, it consists of a **single block** of rules.

* **Evaluation Semantic:** The rules are evaluated **sequentially, from top to bottom**. The **first rule** whose pre-conditions (pattern match, quantifiers, and guards) are all met is the **only one** to be executed *for the current event being processed*.

##### The Event Pattern

The `event_pattern` is a crucial part of the rule's pre-condition.

* **Single Port:** `(port_name, payload_tuple)`
    * *Example:* `(in_start, ())`
* **Multi-Port:** `(port_name * port_index, payload_tuple)`
    * `port_index` is a **variable** (not a number) that captures the index of the port on which the event arrived.
    * *Example:* `(in_channel * i, (data))` (The variable `i` will capture the port index, e.g., 3).

##### Rule Syntax

The syntax of a rule depends on whether the `I:` section is present.

###### Syntax A: Without Intermediate State (No `I:` section)

The rule defines a transition from the model state `S` to a new model state `S`.

**Structure:**
`S_pre_state_tuple, e, event_pattern_tuple → S_post_state_tuple [quantifiers] | [guard] ;`

* **`S_pre_state_tuple`**: A pattern match on the state `S:` (e.g., `(IDLE, _, _)`).
* **`e`**: A variable to capture the elapsed time (`R`).
* **`event_pattern_tuple`**: The event pattern (e.g., `(in_job, (id))`).
* **`→ S_post_state_tuple`**: The new state for `S:` (e.g., `(BUSY, 10.0, id)`).
* **`[quantifiers] | [guard]`**: Optional quantifiers and a guard.

###### Syntax B: With Intermediate State ( `I:` section is present)

The rule defines a transition from the combined state (`S ∪ I`) to a new combined state (`S ∪ I`).

**Structure (as per your corrections):**
`S_pre_state_tuple ∪ I_pre_state_tuple, e, event_pattern_tuple, last_event_check → S_post_state_tuple ∪ I_post_state_tuple [quantifiers] | [guard] ;`

* **`S_pre_state_tuple ∪ I_pre_state_tuple`**: The pre-condition state (using the union operator `∪` (U+222A)).
* **`last_event_check`**: A **mandatory boolean value** (typically a variable like `is_last` provided by the simulator) which is:
    * **`⊤`** (Top, U+22A4) if this is the final event in the ordered bag.
    * **`⊥`** (Bottom, U+22A5) if it is not.
* **`→ S_post_state_tuple ∪ I_post_state_tuple`**: The post-state (using `∪`).

#### `order:` (Order Function) Section (Optional)

This section defines the **processing order for simultaneous events**.

* **Purpose:** It specifies the order for processing an event bag. This is crucial when the model's behavior is state-dependent (the result of processing event A changes how event B is processed).
* **Syntax (as per your corrections):**
  `(event_pattern_1) < (event_pattern_2) <=> boolean_expression ;`
* **Semantics:**
    * The simulator takes any two events, `ev_A` and `ev_B`, from the bag.
    * **`event_pattern_1` / `event_pattern_2`**: These are event patterns, e.g., `(in_job, (id, prio))` or `(in_job, job_tuple)`.
    * **`<=>`**: The biconditional (if and only if).
    * **`boolean_expression`**: This expression defines the priority. It can use variables captured from the payloads of *both* `event_pattern_1` and `event_pattern_2`. It must evaluate to:
        * **`⊤`** (True): `event_pattern_1` is processed before `event_pattern_2`.
        * **`⊥`** (False): `event_pattern_1` is not processed before `event_pattern_2`.
* **If omitted:** The processing order is arbitrary and non-deterministic.

-----

#### Examples

##### Example A: Syntax 1 (No `I:`, Simple)

* **Concept:** A server ignores `in_job` events if it receives an `in_admin_stop` event at the same time.
* `S: (phase) ∈ (<IDLE, BUSY>) = (IDLE);`
* `X: { (in_admin_stop, ()) | (); (in_job, (id)) | (N); }`
* **Code:**
  ```fpdevsml
  delta_ext: {
    behavior: {
      # Rule 1: Admin stop takes priority.
      (IDLE), e, (in_admin_stop, ()) → (IDLE);
      (BUSY), e, (in_admin_stop, ()) → (IDLE);

      # Rule 2: Receive a job.
      # This rule will only run if the 'phase' is still IDLE (i.e.,
      # an 'in_admin_stop' event was not processed first).
      (IDLE), e, (in_job, (id)) → (BUSY);
    }
    order: {
      # 'in_admin_stop' is always processed before 'in_job'
      (in_admin_stop, ()) < (in_job, (_)) <=> ⊤;
    }
  }
  ```

##### Example B: Syntax 2 (With `I:` and simple `order:`)

* **Concept:** A model sums `in_value` events and commits with `in_commit`. `order:` ensures `in_commit` is processed last.
* `S: (total) ∈ (N) = (0);`
* `X: { (in_value, (val)) | (N); (in_commit, ()) | (); }`
* **Code:**
  ```fpdevsml
  delta_ext: {
    I: (temp_sum) ∈ (N) = (0);

    behavior: {
      # Rule 1: Accumulate 'in_value' into I:
      (total) ∪ (temp_sum), e, (in_value, (val)), _ → (total) ∪ (temp_sum + val);

      # Rule 2: Commit the sum to S: when 'in_commit' is processed
      # This rule works because 'order:' guarantees it runs last.
      (total) ∪ (temp_sum), e, (in_commit, ()), ⊤ → (total + temp_sum) ∪ (0);
    }

    order: {
      # 'in_value' events are always processed before 'in_commit'
      (in_value, (_)) < (in_commit, ()) <=> ⊤;
    }
  }
  ```

##### Example C: Syntax 2 (With `I:` and complex `order:`)

* **Concept:** A "priority scheduler" receives a bag of `in_job` events. It must process them sequentially, ordered by priority (a lower number means higher priority). The `order:` section sorts the jobs *before* the behavior rules run.
* `S: (job_queue) ∈ ([ (id, prio) ∈ (N, N) ]) = (∅);`
* `X: { (in_job, (id, prio)) | (N, N); }`
* **Code:**
  ```fpdevsml
  delta_ext: {
    # I: holds the partially built, sorted queue for this external transition
    I: (temp_queue) ∈ ([ (id, prio) ∈ (N, N) ]) = (∅);

    behavior: {
      # Rule 1: Add the (now sorted) job to the intermediate queue.
      (queue) ∪ (temp_queue), e, (in_job, (id, prio)), ⊥ 
        → (queue) ∪ (temp_queue ∪ {(id, prio)});

      # Rule 2: On the last event, commit the *entire* sorted temp_queue
      #         (plus the last event) to the main state queue.
      (queue) ∪ (temp_queue), e, (in_job, (id, prio)), ⊤ 
        → (queue ∪ temp_queue ∪ {(id, prio)}));
    }

    order: {
      # Compare two 'in_job' events.
      # 'job_a' and 'job_b' are variables that match the payload tuple.
      # Event 'a' comes before event 'b' <=> 'a' has a lower 'prio' (π_2).
      (in_job, job_a) < (in_job, job_b) <=> π_2(job_a) < π_2(job_b);
    }
  }
  ```
  
### `delta_con:` (Confluent Transition Function)

The confluent transition function, `delta_con`, is a defining feature of the Parallel DEVS formalism. It provides an unambiguous, formal solution to the "event collision" problem: **What happens when an internal event (`delta_int`) and one or more external events (`delta_ext`) are scheduled to occur at the exact same simulation time?**

This function is mandatory for all Parallel DEVS atomic models, as it ensures deterministic behavior.

#### Purpose

When a model's internal timer expires (`e = ta(s)`), it is scheduled to perform its `delta_int` transition and produce an output via `lambda`. If, at that exact moment, an external event bag `X` also arrives, the `delta_con` function is triggered *instead of* `delta_int` or `delta_ext` separately.

The `delta_con` section **must** declare one of four possible strategies to resolve this conflict.

#### FPDEVSML Syntax

The `delta_con` section is a mandatory, declarative block containing a single rule. As you correctly pointed out, this rule can be one of four, mutually exclusive, options.

**Structure:**
`delta_con: { strategy_rules }` or `delta_con: strategy_rule`

##### Rule Syntax

###### Compositional Strategies

These strategies execute *both* functions, but define the order.

* **Internal-First:** `delta_int` (and its `lambda` output) is executed first, and `delta_ext` is then executed on the *new* state.

    * **Syntax:** `delta_con: delta_int ∘ delta_ext;`

* **External-First:** `delta_ext` is executed first, and `delta_int` (and `lambda`) is then executed on the *new* state.

    * **Syntax:** `delta_con: delta_ext ∘ delta_int;`

###### Selective Strategies

As you noted, it is also possible to select only one function, **discarding the other**.

* **Internal-Only:** `delta_int` is executed, and the `lambda` output is produced. The entire external event bag `X` is **discarded** and ignored.

    * **Syntax:** `delta_con: delta_int;`

* **External-Only (Classic DEVS Behavior):** `delta_ext` is executed. The scheduled `delta_int` transition and its corresponding `lambda` output are **aborted** and do not happen.

    * **Syntax:** `delta_con: delta_ext;`

-----

#### Examples

##### Example A: Internal-First (Composition)

* **Behavior:** The model *first* outputs its message and transitions to `WAITING` (via `delta_int`). *Then*, from the `WAITING` state, it immediately processes the `STOP` event (via `delta_ext`).
* **Code:**
  ```fpdevsml
  delta_con: delta_int ∘ delta_ext;
  ```

##### Example B: External-First (Composition)

* **Behavior:** The model *first* processes the `STOP` event (via `delta_ext`), which (for example) transitions it to `IDLE`. *Then*, it attempts to run its `delta_int` from this new `IDLE` state (which may do nothing, as the original rule no longer matches).
* **Code:**
  ```fpdevsml
  delta_con: delta_ext ∘ delta_int;
  ```

##### Example C: Internal-Only (Selection)

* **Behavior:** A critical "heartbeat" model *must* send its `lambda` output. It treats any simultaneous external events (e.g., a 'config\_update') as noise to be **discarded** during this critical tick.
* **Code:**
  ```fpdevsml
  delta_con: delta_int;
  ```

#### Example D: External-Only (Selection)

* **Behavior:** An "emergency stop" must be obeyed. If the model was about to output a normal data packet (via `lambda`/`delta_int`), the `STOP` event (via `delta_ext`) **cancels** that output and takes priority. This is the implicit behavior of Classic DEVS.
* **Code:**
  ```fpdevsml
  delta_con: delta_ext;
  ```
  
### `ta:` (Time Advance Function)

The `ta` (time advance) function is a mandatory component of an atomic model. Its sole purpose is to answer the question: **"Given the model's current state `s`, how long will it remain in this state before it triggers its own internal transition (`delta_int`)?"**

The value returned by this function is a non-negative real number or infinity (`R+0 ∪ {∞}`).

* **If `ta(s)` returns a finite number (e.g., `10.0`):** The model schedules its `delta_int` to occur `10.0` time units from now. The model is considered **active**.
* **If `ta(s)` returns `∞` (infinity):** The model will *never* schedule an internal transition from this state. It is considered **passive** and will only transition if an external event arrives (triggering `delta_ext` or `delta_con`).

#### Fundamental Structure

The `ta` section is a block that contains one or more **sequentially evaluated rules**.

```fpdevsml
ta: {
  # Rules are defined here
  rule_1;
  rule_2;
  ...
}
```

#### Rule Syntax

The syntax for a `ta` rule is defined by the grammar:

`(pre-state_tuple) → numerical_expression ;`

* **`(pre-state_tuple)`**: This is a **pattern match** against the model's current state `S:`.
    * It uses constants (e.g., `<WAITING>`), variables (e.g., `s`), or the wildcard (`_`) to match the current state.
* **`→`**: The arrow (U+2192).
* **`numerical_expression`**: This is the value to be returned. It can be a constant (e.g., `0`, `10.0`, `∞`), a state variable captured in the pre-state (e.g., `sigma`), or a parameter (e.g., `timeout`).

#### Evaluation Semantic

The `ta` block follows the same **first-match-wins** logic as the `delta_int` (simple block) function.

* The rules are evaluated **sequentially, from top to bottom**.
* The **first rule** whose `(pre-state_tuple)` pattern successfully matches the model's current state is executed.
* The `numerical_expression` from that rule is returned as the time advance value.
* All subsequent rules are ignored.

For this reason, a "catch-all" rule using wildcards is often placed last.

-----

#### Examples

##### Example A: Standard `sigma` Implementation (Most Common)

This is the classic way to implement DEVS, where one of the state variables (named `sigma` by convention) explicitly holds the time advance value.

* `S: (phase, sigma) ∈ (<IDLE, BUSY>, R) = (IDLE, +∞);`
* **Code:**
  ```fpdevsml
  ta: {
    # The rule matches any state and returns the
    # value currently stored in the 'sigma' variable.
    (_, sigma) → sigma;
  }
  ```

##### Example B: State-Based (Pattern Matching)

* **Concept:** A model's `sigma` is defined by its `phase`.
* `S: (phase) ∈ (<WAITING, PROCESSING>) = (WAITING);`
* `P: (processing_time) ∈ (R) = (10.0);`
* **Code:**
  ```fpdevsml
  ta: {
    # Rule 1: If phase is WAITING, be passive (wait for an event).
    (WAITING) → +∞;

    # Rule 2: If phase is PROCESSING, wait for 'processing_time'.
    (PROCESSING) → processing_time;
  }
  ```

##### Example C: Combined (`sigma` and Pattern Matching)

* **Concept:** A model is passive (`+∞`) when `IDLE`, but uses its `sigma` variable in all other states.
* `S: (phase, sigma) ∈ (<IDLE, BUSY, ERROR>, R) = (IDLE, 0);`
* **Code:**
  ```fpdevsml
  ta: {
    # Rule 1: If IDLE, always return infinity (passive).
    (IDLE, _) → +∞;

    # Rule 2 (Catch-all): For any other state (BUSY, ERROR),
    # return the value stored in the 'sigma' variable.
    (_, sigma) → sigma;
  }
  ```
  
### `lambda:` (Output Function)

The `lambda` (output) function is a mandatory component of an atomic model. Its purpose is to **generate output events** based on the model's current state.

This function is triggered **immediately before** an internal transition (`delta_int`) occurs, i.e., when the elapsed time `e` has reached the value returned by `ta(s)`. The state `s` provided to `lambda` is the state *before* `delta_int` is applied.

#### Fundamental Structure

The `lambda` section is a single block that contains one or more **sequentially evaluated rules**.

```fpdevsml
lambda: {
  # Rules are defined here
  rule_1;
  rule_2;
  ...
}
```

#### Rule Syntax

The syntax for a `lambda` rule is defined by the grammar:

`(pre-state_tuple) → { output_event_set } ;`

* **`(pre-state_tuple)`**: This is a **pattern match** against the model's current state `S:`.
    * It uses constants (e.g., `<SENDING>`), variables (e.g., `id`), or the wildcard (`_`) to match the current state.
* **`→`**: The arrow (U+2192).
* **`{ output_event_set }`**: The result. This is a **set** of zero, one, or more output event tuples.
    * **No output:** An empty set (`{}`) or `∅` (U+2205).
    * **One output:** `{ (port_name, (value)) }`
    * **Multiple outputs:** `{ (port_name * index, (val_1)) (port_name * index, (val_2)) }`

#### Output Event Syntax

The format of the event tuple *inside* the output set depends on whether the `Y:` port is a single port or a multi-port.

##### Syntax A: Single Port Event

The event is a 2-tuple: `(port_name, payload_tuple)`

* `port_name`: The name of the output port.
* `payload_tuple`: The tuple of values to send, e.g., `(id)`.

##### Syntax B: Multi-Port Event

The event is a 3-tuple: `(port_name * port_index, payload_tuple)`

* `port_name`: The base name of the output port.
* `port_index`: The specific index of the port to output on (e.g., `3`).
* `payload_tuple`: The tuple of values to send, e.g., `(data)`.

#### Evaluation Semantic

The `lambda` block follows the same **first-match-wins** logic as the `ta` and `delta_int` (simple block) functions.

* The rules are evaluated **sequentially, from top to bottom**.
* The **first rule** whose `(pre-state_tuple)` pattern successfully matches the model's current state is executed.
* The `output_event_set` from that rule is generated.
* All subsequent rules are ignored.
* If no rule matches, the output is implicitly an empty set (`{}`), and no events are generated.

-----

#### Examples

##### Example A: Simple Output on Single Port

* **Concept:** When in the `SENDING` state, output the `id` value on port `out`.
* `S: (phase, sigma, id) ∈ (<SENDING, ...>, R, N) = ...;`
* `Y: { (out, (id)) | (N) }`
* **Code:**
  ```fpdevsml
  lambda: {
    # Match (SENDING, _, id)
    (SENDING, _, id) → { (out, (id)) };

    # Catch-all: all other states produce no output
    (_, _, _) → { };
  }
  ```

##### Example B: Output on Multi-Port

* **Concept:** A model with `N` output channels. When in state `ROUTING`, it sends the `data` to the channel specified by the `target_port` state variable.
* `S: (phase, target_port, data) ∈ (<ROUTING, ...>, N, N) = ...;`
* `Y: { (out_channel * N, (data)) | (N) }`
* **Code:**
  ```fpdevsml
  lambda: {
    # Match (ROUTING, port_idx, data_val)
    (ROUTING, port_idx, data_val) → { (out_channel * port_idx, (data_val)) };

    (_, _, _) → { };
  }
  ```

##### Example C: Conditional & Multiple Outputs

* **Concept:** A `predator` model. If it becomes `STARVED`, it outputs its new (decremented) population. If it is `HUNTING`, it outputs a "hunt attempt" event.
* `S: (phase, sigma, pop) ∈ (<HUNTING, STARVED>, R, N) = ...;`
* `Y: { (out_hunt_attempt, ()) | () (out_pop_update, (pop)) | (N) }`
* **Code:**
  ```fpdevsml
  lambda: {
    # Rule 1:
    (HUNTING, _, _) → { (out_hunt_attempt, ()) };

    # Rule 2:
    (STARVED, _, pop) → { (out_pop_update, (pop)) };

    # Rule 3 (No output for other states):
    (_, _, _) → { };
  }
  ```
  
##### Example D: Simultaneous Multiple Outputs

* **Concept:** A Distributor finishes processing a job. It must output the result on port out_data AND send a done signal on port out_status at the same time.
* `S: (phase, sigma, result) ∈ (<PROCESSING, ...>, R, N) = ...;`
* `Y: { (out_data, (result)) | (N) (out_status, ()) | () }`
* **Code:**
  ```fpdevsml
  lambda: {
  # Match (PROCESSING, _, res_val)
  # The set contains two event tuples
  (PROCESSING, _, res_val) → { (out_data, (res_val)) (out_status, ()) };

  # Catch-all
  (_, _,_) → { };
  }
  ```

-----

## Coupled Models

A coupled model defines the structure of a system by composing and connecting other sub-models (which can be atomic or coupled).

### `P:`, `X:`, `Y:` (Parameters, Input/Output Ports)

* **Purpose:** These sections define the *external interface* of the coupled model.
* **Syntax:** They follow the exact same syntax as their atomic model counterparts.

### `D:` (Components)

* **Purpose:** Declares the sub-model instances that are part of this coupled model.
* **Syntax:** A set of component definitions `  { ... } `. Each component is:
  `instance_name [$ index]: ModelType ← (parameter_values); [quantifier/guard];` 
* **Examples:**
    * A single static component `C1` of type `Counter`:
      ```fpdevsml
      C1: Counter ← (InitialCounter);
      ```
    * A 1D array of `Generator` models, where `GeneratorNumber` is a parameter:
      ```fpdevsml
      G $ GeneratorNumber: Generator ← (GeneratorDurations);
      ```
    * A 2D `N`x`N` grid of `Cell` models:
      ```fpdevsml
      cells $ N $ N: Cell ← (S);
      ```

### `eic:` (External Input Coupling)

* **Purpose:** Connects the coupled model's external input ports (from its `X:` section) to the input ports of its internal components (from `D:`).
* **Syntax:** `eic: { external_port → (component_instance, component_port); [quantifier/guard]; }` 
* **Example:**
    * Connects the external `in` port to the `in` port of *every* `G` instance:
      ```fpdevsml
      eic : {
      in → (G $ i, in)
      ∀ i ∈ {0 ... GeneratorNumber-1};
      }
      ```

### `eoc:` (External Output Coupling)

* **Purpose:** Connects the output ports of internal components (from `D:`) to the coupled model's external output ports (from its `Y:` section).
* **Syntax:** `eoc: { (component_instance, component_port) → external_port; [quantifier/guard]; }` 
* **Example:**
    * Connects the `out` port of `C1` to the external `out` port:
      ```fpdevsml
      eoc : {
      (C1, out) → out;
      }
      ```

### `ic:` (Internal Coupling)

* **Purpose:** Connects the output port of one internal component to the input port of another.
* **Syntax:** `ic: { (src_component, src_port) → (tgt_component, tgt_port); [quantifier/guard]; }`
* **Examples:**
    * Connects the `out` port of every `G` instance to the `in` port of `C1`:
      ```fpdevsml
      ic : {
      (G $ i, out) → (C1, in)
      ∀ i ∈ {0 ... GeneratorNumber-1};
      }
      ```
    * A "Game of Life" neighbor connection:
      ```fpdevsml
      ic : {
      (cells $ i $ j, out) → (cells $ i + 1 $ j, in)
      ∀ (i,j) ∈ ({0 ... N-2},{0 ... N-1});
      }
      ```
      
## Tables

Here is the complete table of symbols, including domains, constructors, and operators, translated into English.

### Predefined Domains

| Symbol        | Name                                      | Description / Usage                         |
|:--------------|:------------------------------------------|:--------------------------------------------|
| `B`           | **Boolean**                               | Logical values: `⊤` (true) or `⊥` (false).  |
| `N`           | **Naturals**                              | Non-negative integers (`0, 1, 2, …`).       |
| `N*`          | **Naturals (non-zero)**                   | Strictly positive integers (`1, 2, 3, …`).  |
| `Z`           | **Integers**                              | Relative integers (`…, -1, 0, 1, …`).       |
| `Z+` / `Z-*`  | **Positive / Strictly Negative Integers** | `Z+` → same as `N*`; `Z-*` → (`-1, -2, …`). |
| `Z*` / `Z+*`  | **Non-zero / Non-negative Integers**      | `Z*` → `Z \ {0}`; `Z+*` → same as `N`.      |
| `R`           | **Reals**                                 | Real numbers.                               |
| `R+` / `R-`   | **Non-negative / Non-positive Reals**     | `R+` (Reals ≥ 0), `R-` (Reals ≤ 0).         |
| `R*`          | **Non-zero Reals**                        | Real numbers except `0`.                    |
| `R+*` / `R-*` | **Strictly Positive / Negative Reals**    | `R+*` (Reals > 0), `R-*` (Reals < 0).       |
| `Q`           | **Rationals**                             | Rational numbers (fractions).               |
| `C`           | **Complex**                               | Complex numbers (`a + bi`).                 |

### Domain Constructors and Set Values

| Symbol (Unicode)           | Name / Delimiter Type     | Purpose / Usage                            | Example / Context                               |
|:---------------------------|:--------------------------|:-------------------------------------------|:------------------------------------------------|
| `{ }` (`U+007B`, `U+007D`) | **Braces**                | Define a **set** (unordered collection).   | `S: (ids) ∈ ({N});` → a set of natural numbers. |
| `< >` (`U+003C`, `U+003E`) | **Angle Brackets**        | Define a **symbol set** (enumeration).     | `S: (phase) ∈ (<wait, send>);`                  |
| `[ ]` (`U+005B`, `U+005D`) | **Square Brackets**       | Define an **ordered set** (array or list). | `S: (buffer) ∈ ([N]);`                          |
| `@` (`U+0040`)             | **At Sign**               | Specifies **array size** within `[ ]`.     | `[N @ 10]` → an array of 10 naturals.           |
| `≪ ≫` (`U+226A`, `U+226B`) | **Double Angle Brackets** | Define a **map** (key–value pairs).        | `S: (table) ∈ (≪N → R≫);`                       |

### Logical Connectors and Comparison

| Symbol (Unicode) | Name                                               | Usage                | Example / Context                            |
|:-----------------|:---------------------------------------------------|:---------------------|:---------------------------------------------|
| `⊤` (U+22A4)     | True                                               | Value/Guard          | `flag = ⊤;`                                  |
| `⊥` (U+22A5)     | False                                              | Value/Guard          | `S: (active) ∈ (B) = (⊥);`                   |
| `∧` (U+2227)     | Logical AND (Conjunction)                          | Guards               | `(i > 5) ∧ (j < 2);`                         |
| `∨` (U+2228)     | Logical OR (Disjunction)                           | Guards               | `(i = 0) ∨ (j = 0);`                         |
| `¬` (U+00AC)     | Logical NOT (Negation)                             | Guards               | `¬(flag);`                                   |
| `<=>`            | Logical Equivalence (Order)                        | Order                | `A <=> 0;`                                   |
| `=` (U+003D)     | Equality (Comparison) <br> Assignment (Definition) | Guards / Definitions | `phase = <wait>;` <br> `P: (c) ∈ (N) = (0);` |
| `≠` (U+2260)     | Inequality                                         | Guards               | `phase ≠ <wait>;`                            |
| `>` (U+003E)     | Greater than                                       | Guards               | `sigma > 0;`                                 |
| `<` (U+003C)     | Less than                                          | Guards               | `sigma < 0;`                                 |
| `≥` (U+2265)     | Greater than or equal                              | Guards               | `sigma ≥ 0;`                                 |
| `≤` (U+2264)     | Less than or equal                                 | Guards               | `sigma ≤ 0;`                                 |

### Structure and Transition Symbols

| Symbol (Unicode)     | Name              | Usage                              | Example / Context                                      |
|:---------------------|:------------------|:-----------------------------------|:-------------------------------------------------------|
| `∅` (U+2205)         | Empty Set         | Value of a set or ordered set.     | `S: (ids) ∈ ({N}) = (∅);` or `S: (ids) ∈ ([N]) = (∅);` |
| `∈` (U+2208)         | Belongs to        | Domain assignment.                 | `S: (var) ∈ (Domain);`                                 |
| `∪` (U+222A)         | Union             | Set Expression                     | `queue ∪ { 0 } or { 0 } ∪ queue`                       |
| `∩` (U+2229)         | Intersection      | Set Expression                     | `q1 ∩ q2`                                              |
| `+∞` (U+002B U+221E) | Positive Infinity | Value.                             | `ta: { (PASSIVE, _) → +∞; }`                           |
| `-∞` (U+002D U+221E) | Negative Infinity | Value.                             | `(-∞, a, _) → (0, a, 0)`                               |
| `∀` (U+2200)         | For all           | Quantification.                    | `ic: { ... ∀ i ∈ {0..N} }`                             |
| `∃` (U+2203)         | There exists      | Quantification.                    | `ic: { ... F j ∈ {0..M} }`                             |
| `\|` (U+007C)        | Guard (Condition) | Boolean condition.                 | `... → ...                                             | (i > 5);` |
| `→` (U+2192)         | Arrow             | Transition or coupling definition. | `(state1) → (state2);`                                 |
| `_` (U+005F)         | Wildcard          | Used in transitions (match-all).   | `(wait, _, val) → (send, 0, val);`                     |

