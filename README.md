# zerow

### Online obfuscator [Viewhere](https://noisyboy.github.io/zerow)
---

# Threat Advisory: Fileless Python Execution via Zero-Width Steganography

## Overview

This report details an advanced obfuscation and fileless execution technique utilizing **Zero-Width Unicode Characters** (e.g., `U+200B`, `U+200C`). By encoding binary payloads into invisible characters and embedding them within benign carrier strings, threat actors can completely bypass traditional static analysis, visual code reviews, and signature-based antivirus detection.

When applied to interpreted languages like Python, this technique allows for the stealthy, in-memory execution of arbitrary code without ever writing a malicious binary to disk.

---

## The Threat Scenario: The "Innocent" Program

The primary danger of this technique lies in its ability to masquerade as harmless, functional code. An attacker can distribute a seemingly benign Python project—perhaps a small utility script, a data scraper, or a homework assignment—that secretly contains a weaponized payload.

### The Attack Chain

The attack relies on decoupling the execution logic (the "loader") from the payload.

1. **The Binder/Executor (`stego_decoder.py`):** The attacker includes a utility module in the project that contains the decoding logic. To a reviewer, this might look like a string parsing tool or be buried in a deeply nested dependency.
2. **The Carrier Script (`main.py`):** The main application appears completely normal but contains a poisoned string and an execution trigger.

### The Weaponized Code

If a victim runs the main script, the execution flow looks like this:

```python
# main.py - The visibly benign script
from stego_decoder import decode_and_execute as dex

# To the human eye, this string is exactly 11 characters.
# In reality, it contains thousands of zero-width characters encoding a payload.
txt = "Hello World"

def main():
    print("Running initial setup...")
    print(txt) # Prints normally to the console, raising no suspicion
    
    # The invisible payload is silently extracted and passed to exec()
    dex(txt)

if __name__ == "__main__":
    main()

```

---

## Technical Breakdown: Why This is Dangerous

This technique subverts standard security protocols at multiple layers:

### 1. Visual Evasion (The Human Element)

Zero-width characters are ignored by standard text editors, IDEs (like VS Code or PyCharm), and web rendering engines (like GitHub's code viewer). A manual code review will almost always fail to detect the payload because the malicious code physically cannot be seen.

### 2. Static Analysis Bypass

Standard Antivirus (AV) and static analysis tools rely on signature matching. Because the malicious Python functions (e.g., `os.system`, `subprocess`, `socket`) do not exist in the file as standard ASCII text, static YARA rules targeting those keywords will not trigger.

### 3. Fileless In-Memory Execution

Because Python's `exec()` function can compile and run strings dynamically, the decoded payload is executed entirely in RAM. No secondary `.exe` or `.py` file is dropped to the filesystem, eliminating a massive footprint usually caught by Endpoint Detection and Response (EDR) platforms.

---

## Detection and Mitigation Strategies

While highly stealthy, this technique leaves specific mathematical and behavioral anomalies that can be hunted.

### 1. Entropy and File Size Anomalies

Encoding data in zero-width characters causes massive data bloat (typically an 8x to 24x expansion depending on the encoding scheme). A script that appears to have 20 lines of code but is 45 KB in size is highly suspicious. Security pipelines should flag raw text files with unusually high entropy or mismatched size-to-visible-character ratios.

### 2. Hex/Byte-Level Inspection

While invisible in standard text editors, the underlying UTF-8 bytes (`e2 80 8b` and `e2 80 8c`) are highly visible in a hex editor.

* **Defensive Action:** Implement CI/CD checks or Git pre-commit hooks that strictly reject files containing unnecessary zero-width Unicode blocks.

### 3. Dynamic Analysis & Hooking

No matter how the code is obfuscated, it must eventually be passed to Python's execution engine.

* **Defensive Action:** Utilize Python's audit hooks (introduced in PEP 578). By hooking `sys.addaudithook()`, defenders can monitor calls to `exec` and `compile`, intercepting the reconstructed plaintext payload the millisecond before it executes.
