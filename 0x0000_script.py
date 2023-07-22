import os
import binascii
import ecdsa
import hashlib
import multiprocessing

from Crypto.Hash import keccak

def generate_ethereum_address():
    # Generate a new private key
    private_key = os.urandom(32)
    public_key = ecdsa.SigningKey.from_string(private_key, curve=ecdsa.SECP256k1).get_verifying_key().to_string()

    # Get the Ethereum address by taking the last 20 bytes of the Keccak-256 hash of the public key
    keccak_hash = keccak.new(digest_bits=256)
    keccak_hash.update(public_key)
    address = keccak_hash.hexdigest()[-40:]

    return binascii.hexlify(private_key).decode(), address

def generate_ethereum_address_with_condition(finished):
    # Get the thread number from the process ID
    thread_num = os.getpid()

    attempts = 0
    while not finished.value:
        # Generate a new Ethereum address
        private_key, address = generate_ethereum_address()

        # Check if the address matches the pattern
        if address[:4] == "0000" and address[-4:] == "0000":
            print(f"Thread {thread_num}: Found a matching Ethereum address after {attempts} attempts")
            print(f"Private key: {private_key}")
            print(f"Address: 0x{address}")
            finished.value = True
            break

        attempts += 1

        # Print the number of checked addresses every 10000 attempts for progress tracking
        if attempts % 10000 == 0:
            print(f"Thread {thread_num}: Checked {attempts} addresses so far...")

if __name__ == '__main__':
    # Get the number of CPUs
    num_cpus = multiprocessing.cpu_count()

    # Create a Manager object to manage shared data
    manager = multiprocessing.Manager()

    # Create a shared boolean variable
    finished = manager.Value('b', False)

    # Create a pool of workers
    pool = multiprocessing.Pool(processes=num_cpus)

    # Generate addresses in parallel until a valid address is found
    while True:
        # Generate a list of tasks
        tasks = [pool.apply_async(generate_ethereum_address_with_condition, args=(finished,)) for _ in range(num_cpus)]

        # Collect the results
        results = [task.get() for task in tasks]

        # Check if a valid address was found
        if finished.value:
            break