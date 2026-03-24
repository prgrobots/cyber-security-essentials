### ---frontmatter---
---
title: Session 14: Implementing Secure Data Encryption in Practice
---

### Session 14: Implementing Secure Data Encryption in Practice

!!! note
    **Data encryption** is a critical component of data protection and plays a significant role in maintaining confidentiality and integrity in data storage and transmission.

!!! info
    Key Concepts:
        - Symmetric encryption (AES) and asymmetric encryption (RSA)
        - Hashing algorithms (SHA, MD5)
        - Public-key infrastructure (PKI)
        - Key exchange protocols (Diffie-Hellman)

---

### Learning Objectives

*   **LO1**: Select and apply symmetric encryption algorithms (AES) for secure data storage and transmission.
*   **LO2**: Design and implement asymmetric encryption using RSA.
*   **LO3**: Apply hashing algorithms (SHA, MD5) for data integrity verification.
*   **LO4**: Develop a basic public-key infrastructure (PKI) for secure key management.
*   **LO5**: Implement key exchange protocols (Diffie-Hellman) for secure communication.

---

### Implementing Symmetric Encryption with AES

Symmetric encryption is an efficient method for encrypting data when both the sender and recipient share the same secret key.

!!! example
    ### Encrypting data with AES in Python
    ```python
        from Crypto.Cipher import AES
        from Crypto.Random import get_random_bytes

        # Generate a random key
        key = get_random_bytes(32)

        # Define the data to encrypt
        data = b"This is the data to be encrypted"

        # Create an AES cipher instance
        cipher = AES.new(key, AES.MODE_EAX)

        # Encrypt the data
        ciphertext, tag = cipher.encrypt_and_digest(data)

        # Recover the original data
        recovered_data = cipher.decrypt(ciphertext, tag)

        print(recovered_data)
    ```

!!! warning
    **Do not hardcode keys** for use in production environments. Instead, use secure key management techniques.

<!-- .note: Use secure key management techniques instead of hardcoding keys -->

---

### Asymmetric Encryption with RSA

Asymmetric encryption uses a public/private key pair to encrypt and decrypt data.

!!! example
    ### Key Pair Generation with RSA
    ```python
        from Crypto.PublicKey import RSA

        # Generate a new RSA key pair
        key = RSA.generate(2048)

        # Print the public key
        print(key.publickey().exportKey('PEM'))

        # Print the private key
        print(key.exportKey('PEM'))
    ```

---

### Applying Hashing Algorithms

Hashing algorithms provide a way to verify data integrity.

!!! tip
    **Use SHA-256 or similar strong hashing algorithms** for data integrity.

!!! example
    ### Hashing Data with SHA in Python
    ```python
        import hashlib

        # Define the data to hash
        data = b"This is the data to be hashed"

        # Hash the data using SHA-256
        hash_object = hashlib.sha256(data)

        # Print the hashed data
        print(hash_object.hexdigest())
    ```

---

### Public-Key Infrastructure (PKI)

A PKI is a system used to manage public and private keys.

!!! note
    **A CA (Certificate Authority)** provides digital certificates.

!!! example
    ### Certificate Signing Request (CSR) Generation in OpenSSL
    ```bash
        openssl req -new -newkey rsa:2048 -nodes -keyout server_private_key.pem -out csr.txt
    ```

---

### Key Exchange Protocols

Key exchange protocols enable secure communication between parties.

!!! example
    ### Performing a Diffie-Hellman Key Exchange
    ```c
        // Key exchange parameters
        const int prime = 23;
        const int base = 5;

        // Initialize variables for Alice and Bob
        int alice_key, bob_key;

        // Generate Alice's and Bob's public values
        alice_pub = pow(base, alice_secret, prime);
        bob_pub = pow(base, bob_secret, prime);

        // Compute the shared secret key
        shared_key = pow(alice_pub, bob_secret, prime);

        // Verify the shared secret key
        if (shared_key == expected_shared_key)
            // Key exchange successful
        ```

---

### Summary

In this session, you learned the practical aspects of implementing secure data encryption, including the selection of encryption algorithms and key management.

*   Symmetric encryption (AES) is used for data storage and transmission.
*   Asymmetric encryption (RSA) uses a public/private key pair for encryption and decryption.
*   Hashing algorithms (SHA) provide a way to verify data integrity.
*   Public-key infrastructure (PKI) manages public and private keys.
*   Key exchange protocols (Diffie-Hellman) enable secure communication between parties.

---

### Knowledge Check

1.  What is symmetric encryption used for?
2.  What is the purpose of hashing algorithms?
3.  What is the role of a Certificate Authority (CA) in public-key infrastructure (PKI)?
4.  How do key exchange protocols enable secure communication between parties?

Please answer these questions and submit your knowledge check to the instructor.