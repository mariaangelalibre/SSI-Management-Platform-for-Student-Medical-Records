import asyncio
import json
from indy import anoncreds, did, ledger, pool, wallet, error

async def run():
    # Admin inputs for wallet name and credentials
    wallet_name = input("\nEnter the Wallet Name: ")
    wallet_key = input("Enter the Wallet Key: ")

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
        print(f"\nPool ledger config created: {pool_name}")
    except error.PoolLedgerConfigAlreadyExistsError:
        print(f"\nPool ledger config already exists: {pool_name}")
    pool_handle = await pool.open_pool_ledger(pool_name, None)
    print(f"Pool ledger opened: {pool_name}")

    # Create a new wallet
    try:
        await wallet.create_wallet(wallet_config, wallet_credentials)
        print(f"\nWallet created: {wallet_name}")
    except error.WalletAlreadyExistsError:
        print(f"\nWallet already exists: {wallet_name}")
    wallet_handle = await wallet.open_wallet(wallet_config, wallet_credentials)
    print(f"Wallet opened: {wallet_name}")

    # Create Master Secret
    master_secret_id = 'prover_master_secret'
    try:
        await anoncreds.prover_create_master_secret(wallet_handle, master_secret_id)
        print(f"\nMaster secret created: {master_secret_id}")
    except error.AnoncredsMasterSecretDuplicateNameError:
        print(f"\nMaster secret already exists: {master_secret_id}")

    # Generate a new DID for the owner
    (owner_did, owner_verkey) = await did.create_and_store_my_did(wallet_handle, "{}")
    print(f"Owner DID: {owner_did}")
    print(f"Owner Verkey: {owner_verkey}\n")

    # Schema and Credential Definition
    schemas = [
        {
            'schema_name': 'Health ID',
            'schema_version': '1.0',
            'schema_attributes': [
                'given_name', 'surname', 'street_address', 'city', 'region', 'zip_code',
                'country', 'nationality', 'sex', 'gender', 'date_of_birth', 'email',
                'phone_number', 'comorbidity', 'blood_type', 'disability'
            ]
        },
        {
            'schema_name': 'Medications',
            'schema_version': '1.0',
            'schema_attributes': [
                'covid-19_vaccination_status', '1st_dose', '2nd_dose', 'booster', 'medications_for_maintenance'
            ]
        },
        {
            'schema_name': 'Emergency Contact Number',
            'schema_version': '1.0',
            'schema_attributes': [
                'name_of_emergency_contact_person', 'contact_number'
            ]
        }
    ]

    # Function to get schema attribute values from the user
    def get_attribute_values(attributes):
        values = {}
        for attribute in attributes:
            value = input(f"Enter the value for {attribute}: ")
            values[attribute] = value
        return values

    # Function to create and submit a schema
    async def create_and_submit_schema(schema_info, owner_did, pool_handle, wallet_handle):
        schema_name = schema_info['schema_name']
        schema_version = schema_info['schema_version']
        schema_attributes = schema_info['schema_attributes']
        
        (schema_id, schema) = await anoncreds.issuer_create_schema(owner_did, schema_name, schema_version,
                                                             json.dumps(schema_attributes))
        print(f"\nSchema created: {schema_id}")
        
        schema_request = await ledger.build_schema_request(owner_did, schema)
        await ledger.sign_and_submit_request(pool_handle, wallet_handle, owner_did, schema_request)
        
        return schema_id, schema  # Return the schema_id and schema

    # Loop through the predefined schemas
    schema_ids = []
    credential_definitions = []
    for schema_info in schemas:
        print(f"Enter values for schema '{schema_info['schema_name']}' version '{schema_info['schema_version']}':")
        attribute_values = get_attribute_values(schema_info['schema_attributes'])
        schema_id, schema = await create_and_submit_schema(schema_info, owner_did, pool_handle, wallet_handle)

        cred_def_tag = 'TAG1'
        cred_def_config = json.dumps({"support_revocation": False})
        (cred_def_id, cred_def) = await anoncreds.issuer_create_and_store_credential_def(wallet_handle, owner_did,
                                                                                       schema, cred_def_tag, None,
                                                                                       cred_def_config)
        print(f"Credential definition created: {cred_def_id}")
        cred_def_request = await ledger.build_cred_def_request(owner_did, cred_def)
        await ledger.sign_and_submit_request(pool_handle, wallet_handle, owner_did, cred_def_request)

        schema_ids.append(schema_id)
        credential_definitions.append(cred_def_id)

        # Issue Credential
        prover_did = owner_did
        cred_offer = await anoncreds.issuer_create_credential_offer(wallet_handle, cred_def_id)
        print("Credential offer created successfully")
        cred_request, cred_request_metadata = await anoncreds.prover_create_credential_req(wallet_handle, prover_did,
                                                                                         cred_offer, cred_def,
                                                                                         master_secret_id)
        print("Credential request created successfully")

        cred_values = json.dumps({
            attr: {"raw": value, "encoded": str(i+1)} for i, (attr, value) in enumerate(attribute_values.items())
        })
        try:
            (credential, _, _) = await anoncreds.issuer_create_credential(wallet_handle, cred_offer, cred_request,
                                                                          cred_values, None, None)
            print("Credential created successfully.")
        except error.IndyError as e:
            print(f"Error creating credential: {e}")
            return

        print("Credential issued successfully")
        await anoncreds.prover_store_credential(wallet_handle, None, cred_request_metadata, credential, cred_def, None)
        print("Credential stored successfully.\n")

    # Print possible credentials to request
    # Store the list of attributes in an array
    all_attributes = []

    for schema_info in schemas:
        schema_attributes = schema_info['schema_attributes']
        all_attributes.extend(schema_attributes)
        print(f"\nPossible credentials to request for schema '{schema_info['schema_name']}':")
        for attr in schema_attributes:
            print(f"- {attr}")

    # Function to validate requested attributes
    def get_requested_attributes(schema_info):
        while True:
            requested_attrs = input("\nEnter the attributes you want to request (comma separated): ").split(',')
            requested_attrs = [attr.strip() for attr in requested_attrs]
            valid_attrs = all_attributes
            if valid_attrs:
                return requested_attrs
            else:
                print("\nInvalid attribute(s) entered. Please enter valid attributes from the list provided.")

    # Request proof for each schema
    for schema_info in schemas:
        requested_attrs = get_requested_attributes(schema_info)
        print("\nRequested attributes:", requested_attrs)
        
        # Create proof request
        proof_request = {
            "nonce": "123432421212",
            "name": "proof_req_1",
            "version": "0.1",
            "requested_attributes": {
                f"attr{i+1}_referent": {"name": attr} for i, attr in enumerate(requested_attrs)
            },
            "requested_predicates": {}
        }
        print("Proof request created:", proof_request)
        
        # User agreement to share attributes
        agree_to_share = input(f"\nDo you agree to share the following attributes? {requested_attrs} (yes/no): ")
        if agree_to_share.lower() != 'yes':
            print("\nOwner Denied Access")
            exit()

        # Fetch credentials for proof request
        search_handle = await anoncreds.prover_search_credentials_for_proof_req(wallet_handle, json.dumps(proof_request), None)
        credentials = {}
        for attr_referent in proof_request['requested_attributes']:
            fetched_creds = await anoncreds.prover_fetch_credentials_for_proof_req(search_handle, attr_referent, 1)
            credentials[attr_referent] = json.loads(fetched_creds)
        await anoncreds.prover_close_credentials_search_for_proof_req(search_handle)
        
        retrieved_values = {}
        for attr_referent in proof_request['requested_attributes']:
            cred_info = credentials[attr_referent][0]['cred_info']
            for attr in cred_info['attrs']:
                retrieved_values[attr] = cred_info['attrs'][attr]
        print("\nProof created successfully")
        print("\nApproved Requested Credentials:")
        # Print the retrieved attribute values for requested attributes
        for attr in requested_attrs:
            value = retrieved_values.get(attr)
            if value is not None:
                print(f"{attr}: {value}")

        
        exit()
        
        # Build requested credentials JSON
        requested_credentials = {
            "self_attested_attributes": {},
            "requested_attributes": {
                attr_referent: {
                    "cred_id": credentials[attr_referent][0]['cred_info']['referent'],
                    "revealed": True
                } for attr_referent in proof_request['requested_attributes']
            },
            "requested_predicates": {}
        }
        #print("Requested credentials JSON:", requested_credentials)

        # Get credential definitions JSON
        cred_defs_json = json.dumps({cred_def_id: cred_def})
        schemas_json = json.dumps({schema_id: schema})
        rev_states_json = json.dumps({})

        # Create proof
        try:
            proof = await anoncreds.prover_create_proof(
                wallet_handle,
                json.dumps(proof_request),
                json.dumps(requested_credentials),
                master_secret_id,
                schemas_json,
                cred_defs_json,
                rev_states_json
            )
            #print("Proof created successfully:", proof)
        except error.IndyError as e:
            #print(f"Error creating proof: {e}")
            #print(f"Error type: {type(e)}")
            #print(f"Error code: {e.error_code}")
            exit()

    # Close wallet and pool ledger
    await wallet.close_wallet(wallet_handle)
    await pool.close_pool_ledger(pool_handle)

asyncio.get_event_loop().run_until_complete(run())  # Run the asynchronous run function


