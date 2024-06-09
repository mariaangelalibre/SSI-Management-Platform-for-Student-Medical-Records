import asyncio
import json
from indy import anoncreds, did, ledger, pool, wallet, error

async def run():
    # Admin inputs for wallet name and credentials
    wallet_name = input("Enter the wallet name: ")
    wallet_key = input("Enter the wallet key: ")

    wallet_config = json.dumps({"id": wallet_name})
    wallet_credentials = json.dumps({"key": wallet_key})

    # Set protocol version
    await pool.set_protocol_version(2)

    # Define pool name
    pool_name = 'sandbox'

    # Create pool ledger configuration to connect to the ledger
    pool_genesis_txn_path = '/var/lib/indy/sandbox/pool_transactions_genesis'
    pool_config = json.dumps({"genesis_txn": str(pool_genesis_txn_path)})
    try:
        await pool.create_pool_ledger_config(pool_name, pool_config)
        print(f"Pool ledger config created: {pool_name}")
    except error.PoolLedgerConfigAlreadyExistsError:
        print(f"Pool ledger config already exists: {pool_name}")
    pool_handle = await pool.open_pool_ledger(pool_name, None)
    print(f"Pool ledger opened: {pool_name}")

    # Create a new wallet
    try:
        await wallet.create_wallet(wallet_config, wallet_credentials)
        print(f"Wallet created: {wallet_name}")
    except error.WalletAlreadyExistsError:
        print(f"Wallet already exists: {wallet_name}")
    wallet_handle = await wallet.open_wallet(wallet_config, wallet_credentials)
    print(f"Wallet opened: {wallet_name}")

    # Generate a new DID for the owner
    (owner_did, owner_verkey) = await did.create_and_store_my_did(wallet_handle, "{}")
    print(f"Owner DID: {owner_did}")
    print(f"Owner Verkey: {owner_verkey}")

    # Create Master Secret
    master_secret_id = 'prover_master_secret'
    try:
        await anoncreds.prover_create_master_secret(wallet_handle, master_secret_id)
        print(f"Master secret created: {master_secret_id}")
    except error.AnoncredsMasterSecretDuplicateNameError:
        print(f"Master secret already exists: {master_secret_id}")

    # Schema and Credential Definition
    schema_name = 'degree'
    schema_version = '1.0'
    schema_attributes = ['name', 'degree', 'university', 'graduation_date']
    (schema_id, schema) = await anoncreds.issuer_create_schema(owner_did, schema_name, schema_version, json.dumps(schema_attributes))
    print(f"Schema created: {schema_id}")
    schema_request = await ledger.build_schema_request(owner_did, schema)
    await ledger.sign_and_submit_request(pool_handle, wallet_handle, owner_did, schema_request)
    print(f"Schema request submitted: {schema_id}")

    # Define Credential
    cred_def_tag = 'TAG1'
    cred_def_config = json.dumps({"support_revocation": False})
    (cred_def_id, cred_def) = await anoncreds.issuer_create_and_store_credential_def(wallet_handle, owner_did, schema, cred_def_tag, None, cred_def_config)
    print(f"Credential definition created: {cred_def_id}")
    cred_def_request = await ledger.build_cred_def_request(owner_did, cred_def)
    await ledger.sign_and_submit_request(pool_handle, wallet_handle, owner_did, cred_def_request)
    print(f"Credential definition request submitted: {cred_def_id}")

    # Admin inputs for credential values
    name = input("Enter the name: ")
    degree = input("Enter the degree: ")
    university = input("Enter the university: ")
    graduation_date = input("Enter the graduation date: ")

    # Issue Credential
    prover_did = owner_did  # Assuming the prover is the owner for demo purposes
    cred_offer = await anoncreds.issuer_create_credential_offer(wallet_handle, cred_def_id)
    print(f"Credential offer created: {cred_offer}")
    cred_request, cred_request_metadata = await anoncreds.prover_create_credential_req(wallet_handle, prover_did, cred_offer, cred_def, master_secret_id)
    print(f"Credential request created: {cred_request}")
    cred_values = json.dumps({
        "name": {"raw": name, "encoded": "1139481716457488690172217916278103335"},
        "degree": {"raw": degree, "encoded": "12434523576212321"},
        "university": {"raw": university, "encoded": "2213454313412354"},
        "graduation_date": {"raw": graduation_date, "encoded": "20200515"}
    })
    (credential, _, _) = await anoncreds.issuer_create_credential(wallet_handle, cred_offer, cred_request, cred_values, None, None)
    print(f"Credential issued: {credential}")
    await anoncreds.prover_store_credential(wallet_handle, None, cred_request_metadata, credential, cred_def, None)
    print("Credential stored successfully.")

    # Show requestor possible credentials to request
    print("Possible credentials to request:")
    for attr in schema_attributes:
        print(f"- {attr}")

    # Requestor specifies the credential to request
    requested_attrs = input("Enter the attributes you want to request (comma separated): ").split(',')

    # Proof Request and Verification
    proof_request = {
        "nonce": "123432421212",
        "name": "proof_req_1",
        "version": "0.1",
        "requested_attributes": {
            f"attr{i}_referent": {"name": attr.strip()}
            for i, attr in enumerate(requested_attrs, start=1)
        },
        "requested_predicates": {}
    }
    print(f"Proof request created: {proof_request}")

    # Ask the owner for approval
    approve = input(f"Do you agree to share the following attributes? {requested_attrs} (yes/no): ").strip().lower()
    if approve != "yes":
        print("Owner denied the request.")
        return

    # Wallet owner (prover) creates the proof when requested
    proof_request_json = json.dumps(proof_request)
    search_handle = await anoncreds.prover_search_credentials_for_proof_req(wallet_handle, proof_request_json, None)
    credentials = {}
    for i in range(1, len(requested_attrs) + 1):
        credential_str = await anoncreds.prover_fetch_credentials_for_proof_req(search_handle, f"attr{i}_referent", 1)
        credential = json.loads(credential_str)
        if not credential:
            break
        credentials[f"attr{i}_referent"] = {"cred_id": credential[0]['cred_info']['referent'], "revealed": True}
    await anoncreds.prover_close_credentials_search_for_proof_req(search_handle)
    print(f"Credentials for proof request: {credentials}")

    requested_credentials = json.dumps({
        "self_attested_attributes": {},
        "requested_attributes": credentials,
        "requested_predicates": {}
    })
    print(f"Requested credentials: {requested_credentials}")

    schemas = json.dumps({schema_id: schema})
    cred_defs = json.dumps({cred_def_id: cred_def})
    revoc_states = json.dumps({})

    # Debug print statements for proof creation inputs
    print(f"Schemas: {schemas}")
    print(f"Credential Definitions: {cred_defs}")
    print(f"Revocation States: {revoc_states}")
    print(f"Proof Request: {proof_request}")
    print(f"Requested Credentials: {requested_credentials}")

    try:
        proof = await anoncreds.prover_create_proof(wallet_handle, proof_request_json, requested_credentials, master_secret_id, schemas, cred_defs, revoc_states)
        print(f"Proof created: {proof}")
    except error.IndyError as e:
        print(f"Error creating proof: {str(e)}")
        return

    # Verifier verifies the proof
    try:
        verified = await anoncreds.verifier_verify_proof(proof_request_json, proof, schemas, cred_defs, revoc_states, revoc_states)
        print(f"Proof verified: {verified}")
    except error.IndyError as e:
        print(f"Error verifying proof: {str(e)}")

    # Clean up
    await wallet.close_wallet(wallet_handle)
    await pool.close_pool_ledger(pool_handle)
    print("Clean up completed. Wallet and pool closed.")

asyncio.get_event_loop().run_until_complete(run())
