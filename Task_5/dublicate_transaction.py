def find_first_duplicate_block(transactions):
    # Group transactions by their block number
    blocks = {}
    for txn in transactions:
        block_number = txn['block_number']
        sender = txn['sender']
        if block_number not in blocks:
            blocks[block_number] = []
        blocks[block_number].append(sender)
    
    # Sort the blocks by block number to process in order
    sorted_blocks = sorted(blocks.items(), key=lambda item: item[0])
    
    # Check each block for duplicate senders
    for block_number, senders in sorted_blocks:
        seen = set()
        for sender in senders:
            if sender in seen:
                return block_number
            seen.add(sender)
    return None

# Example usage:
transactions = [
    {'block_number': 0, 'sender': 'Alice'},
    {'block_number': 0, 'sender': 'Bob'},
    {'block_number': 1, 'sender': 'Alice'},
    {'block_number': 1, 'sender': 'Alice'},  # Duplicate in block 1
    {'block_number': 2, 'sender': 'Charlie'},
]

print(find_first_duplicate_block(transactions))