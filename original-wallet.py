import asyncio  # Import the asyncio module for asynchronous programming
import json  # Import the json module to handle JSON data
from indy import anoncreds, did, ledger, pool, wallet, error  # Import necessary modules from indy SDK

async def run():
	# Admin inputs for wallet name and credentials
	wallet_name = input("Enter the wallet name: ")  # Prompt the user to enter the wallet name
	wallet_key = input("Enter the wallet key: ")  # Prompt the user to enter the wallet key

	wallet_config = json.dumps({"id": wallet_name})  # Convert wallet name to JSON format
	wallet_credentials = json.dumps({"key": wallet_key})  # Convert wallet key to JSON format

	# Set protocol version
	await pool.set_protocol_version(2)  # Set the protocol version to 2

	# Define pool name
	pool_name = 'sandbox'  # Define the name of the pool

	# Create pool ledger configuration to connect to the ledger
	pool_genesis_txn_path = '/var/lib/indy/sandbox/pool_transactions_genesis'  # Path to the genesis transaction file
	pool_config = json.dumps({"genesis_txn": str(pool_genesis_txn_path)})  # Convert pool configuration to JSON format
	try:
		await pool.create_pool_ledger_config(pool_name, pool_config)  # Create the pool ledger configuration
		print(f"Pool ledger config created: {pool_name}")  # Print a success message
	except error.PoolLedgerConfigAlreadyExistsError:
		print(f"Pool ledger config already exists: {pool_name}")  # Print a message if the pool config already exists
	pool_handle = await pool.open_pool_ledger(pool_name, None)  # Open the pool ledger
	print(f"Pool ledger opened: {pool_name}")  # Print a success message

	# Create a new wallet
	try:
		await wallet.create_wallet(wallet_config, wallet_credentials)  # Create a new wallet
		print(f"Wallet created: {wallet_name}")  # Print a success message
	except error.WalletAlreadyExistsError:
		print(f"Wallet already exists: {wallet_name}")  # Print a message if the wallet already exists
	wallet_handle = await wallet.open_wallet(wallet_config, wallet_credentials)  # Open the wallet
	print(f"Wallet opened: {wallet_name}")  # Print a success message

	# Generate a new DID for the owner
	(owner_did, owner_verkey) = await did.create_and_store_my_did(wallet_handle, "{}")  # Create and store a new DID
	print(f"Owner DID: {owner_did}")  # Print the owner DID
	print(f"Owner Verkey: {owner_verkey}")  # Print the owner verification key

	# Create Master Secret
	master_secret_id = 'prover_master_secret'  # Define the master secret ID
	try:
		await anoncreds.prover_create_master_secret(wallet_handle, master_secret_id)  # Create the master secret
		print(f"Master secret created: {master_secret_id}")  # Print a success message
	except error.AnoncredsMasterSecretDuplicateNameError:
		print(f"Master secret already exists: {master_secret_id}")  # Print a message if the master secret already exists

	# Schema and Credential Definition
	schema_name = 'degree'  # Define the schema name
	schema_version = '1.0'  # Define the schema version
	schema_attributes = ['name', 'degree', 'university', 'graduation_date']  # Define the schema attributes
	(schema_id, schema) = await anoncreds.issuer_create_schema(owner_did, schema_name, schema_version, json.dumps(schema_attributes))  # Create the schema
	print(f"Schema created: {schema_id}")  # Print the schema ID
	schema_request = await ledger.build_schema_request(owner_did, schema)  # Build the schema request
	await ledger.sign_and_submit_request(pool_handle, wallet_handle, owner_did, schema_request)  # Sign and submit the schema request
	print(f"Schema request submitted: {schema_id}")  # Print a success message

	# Define Credential
	cred_def_tag = 'TAG1'  # Define the credential definition tag
	cred_def_config = json.dumps({"support_revocation": False})  # Define the credential definition configuration
	(cred_def_id, cred_def) = await anoncreds.issuer_create_and_store_credential_def(wallet_handle, owner_did, schema, cred_def_tag, None, cred_def_config)  # Create and store the credential definition
	print(f"Credential definition created: {cred_def_id}")  # Print the credential definition ID
	cred_def_request = await ledger.build_cred_def_request(owner_did, cred_def)  # Build the credential definition request
	await ledger.sign_and_submit_request(pool_handle, wallet_handle, owner_did, cred_def_request)  # Sign and submit the credential definition request
	print(f"Credential definition request submitted: {cred_def_id}")  # Print a success message

	# Admin inputs for credential values
	name = input("Enter the name: ")  # Prompt the user to enter the name
	degree = input("Enter the degree: ")  # Prompt the user to enter the degree
	university = input("Enter the university: ")  # Prompt the user to enter the university
	graduation_date = input("Enter the graduation date: ")  # Prompt the user to enter the graduation date

	# Issue Credential
	prover_did = owner_did  # Assuming the prover is the owner for demo purposes
	cred_offer = await anoncreds.issuer_create_credential_offer(wallet_handle, cred_def_id)  # Create the credential offer
	print(f"Credential offer created: {cred_offer}")  # Print the credential offer
	cred_request, cred_request_metadata = await anoncreds.prover_create_credential_req(wallet_handle, prover_did, cred_offer, cred_def, master_secret_id)  # Create the credential request
	print(f"Credential request created: {cred_request}")  # Print the credential request
	cred_values = json.dumps({
	    "name": {"raw": name, "encoded": "1139481716457488690172217916278103335"},
		"degree": {"raw": degree, "encoded": "12434523576212321"},
		"university": {"raw": university, "encoded": "2213454313412354"},
		"graduation_date": {"raw": graduation_date, "encoded": "20200515"}
	})  # Define the credential values
	(credential, _, _) = await anoncreds.issuer_create_credential(wallet_handle, cred_offer, cred_request, cred_values, None, None)  # Create the credential
	print(f"Credential issued: {credential}")  # Print the credential
	await anoncreds.prover_store_credential(wallet_handle, None, cred_request_metadata, credential, cred_def, None)  # Store the credential
	print("Credential stored successfully.")  # Print a success message

	# Show requestor possible credentials to request
	print("Possible credentials to request:")  # Print a message
	for attr in schema_attributes:
		print(f"- {attr}")  # Print each possible credential attribute

	# Requestor specifies the credential to request
	requested_attrs = input("Enter the attributes you want to request (comma separated): ").split(',')  # Prompt the user to enter the requested attributes

	# Proof Request and Verification
	proof_request = {
		"nonce": "123432421212",  # Define the nonce for the proof request
		"name": "proof_req_1",  # Define the name for the proof request
		"version": "0.1",  # Define the version for the proof request
		"requested_attributes": {
			f"attr{i}_referent": {"name": attr.strip()}
			for i, attr in enumerate(requested_attrs, start=1)
		},  # Define the requested attributes
		"requested_predicates": {}  # Define the requested predicates
	}
	print(f"Proof request created: {proof_request}")  # Print the proof request

	# Ask the owner for approval
	approve = input(f"Do you agree to share the following attributes? {requested_attrs} (yes/no): ").strip().lower()  # Prompt the user for approval
	if approve != "yes":
		print("Owner denied the request.")  # Print a message if the owner denies the request
		return

	# Wallet owner (prover) creates the proof when requested
	proof_request_json = json.dumps(proof_request)  # Convert the proof request to JSON format
	search_handle = await anoncreds.prover_search_credentials_for_proof_req(wallet_handle, proof_request_json, None)  # Search for credentials for the proof request
	credentials = {}  # Initialize the credentials dictionary
	for i in range(1, len(requested_attrs) + 1):
		credential_str = await anoncreds.prover_fetch_credentials_for_proof_req(search_handle, f"attr{i}_referent", 1)  # Fetch credentials for the proof request
		credential = json.loads(credential_str)  # Convert the credential string to JSON
		if not credential:
			break  # Break if no credential is found
		credentials[f"attr{i}_referent"] = {"cred_id": credential[0]['cred_info']['referent'], "revealed": True}  # Add the credential to the dictionary
	await anoncreds.prover_close_credentials_search_for_proof_req(search_handle)  # Close the credentials search
	print(f"Credentials for proof request: {credentials}")  # Print the credentials for the proof request

	requested_credentials = json.dumps({
		"self_attested_attributes": {},
		"requested_attributes": credentials,
		"requested_predicates": {}
	})  # Define the requested credentials
	print(f"Requested credentials: {requested_credentials}")  # Print the requested credentials

	schemas = json.dumps({schema_id: schema})  # Convert schemas to JSON format
	cred_defs = json.dumps({cred_def_id: cred_def})  # Convert credential definitions to JSON format
	revoc_states = json.dumps({})  # Initialize revocation states as an empty JSON object

	# Debug print statements for proof creation inputs
	print(f"Schemas: {schemas}")  # Print schemas
	print(f"Credential Definitions: {cred_defs}")  # Print credential definitions
	print(f"Revocation States: {revoc_states}")  # Print revocation states
	print(f"Proof Request: {proof_request}")  # Print proof request
	print(f"Requested Credentials: {requested_credentials}")  # Print requested credentials

	try:
		proof = await anoncreds.prover_create_proof(wallet_handle, proof_request_json, requested_credentials, master_secret_id, schemas, cred_defs, revoc_states)  # Create the proof
		print(f"Proof created: {proof}")  # Print the proof
	except error.IndyError as e:
		print(f"Error creating proof: {str(e)}")  # Print an error message if proof creation fails
		return

	# Verifier verifies the proof
	try:
		verified = await anoncreds.verifier_verify_proof(proof_request_json, proof, schemas, cred_defs, revoc_states, revoc_states)  # Verify the proof
		print(f"Proof verified: {verified}")  # Print the verification result
	except error.IndyError as e:
		print(f"Error verifying proof: {str(e)}")  # Print an error message if proof verification fails

	# Clean up
	await wallet.close_wallet(wallet_handle)  # Close the wallet
	await pool.close_pool_ledger(pool_handle)  # Close the pool ledger
	print("Clean up completed. Wallet and pool closed.")  # Print a success message

asyncio.get_event_loop().run_until_complete(run())  # Run the asynchronous run function
