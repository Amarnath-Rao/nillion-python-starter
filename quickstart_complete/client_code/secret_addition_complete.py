"""
In this example, we:
1. import packages we'll be using
2. connect to the local nillion-devnet
3. store the secret addition program
4. store a secret to be used in the computation
5. compute the secret addition program with the stored secret and another computation time secret
6. return the computation result
"""

import asyncio
import os

from nillion_client import (
    InputPartyBinding,
    Network,
    NilChainPayer,
    NilChainPrivateKey,
    OutputPartyBinding,
    Permissions,
    SecretInteger,
    VmClient,
    PrivateKey,
)
from dotenv import load_dotenv

home = os.getenv("HOME")
load_dotenv(f"{home}/.config/nillion/nillion-devnet.env")


async def main():
    # 2. Initial setup/config, then initialize the NillionClient against nillion-devnet
    # Use the devnet configuration generated by `nillion-devnet`
    network = Network.from_config("devnet")

    # Create payments config and set up Nillion wallet with a private key to pay for operations
    nilchain_key: str = os.getenv("NILLION_NILCHAIN_PRIVATE_KEY_0")  # type: ignore
    payer = NilChainPayer(
        network,
        wallet_private_key=NilChainPrivateKey(bytes.fromhex(nilchain_key)),
        gas_limit=10000000,
    )

    # Use a random key to identify ourselves
    signing_key = PrivateKey()
    client = await VmClient.create(signing_key, network, payer)
    party_name = "Party1"
    program_name = "secret_addition_complete"
    program_mir_path = f"../nada_quickstart_programs/target/{program_name}.nada.bin"

    # Adding funds to the client balance so the upcoming operations can be paid for
    funds_amount = 1000
    print(f"💰  Adding some funds to the client balance: {funds_amount}")
    await client.add_funds(funds_amount)

    # 3. Store the program
    print("-----STORE PROGRAM")

    # Store program
    program_mir = open(program_mir_path, "rb").read()
    program_id = await client.store_program(program_name, program_mir).invoke()

    # Print details about stored program
    print(f"Stored program_id: {program_id}")

    # 4. Create the 1st secret, add permissions and store it in the network
    print("-----STORE SECRETS")

    # Create a secret
    values = {
        "my_int1": SecretInteger(500),
    }

    # Create a permissions object to attach to the stored secret
    permissions = Permissions.defaults_for_user(client.user_id).allow_compute(
        client.user_id, program_id
    )

    # Store a secret
    values_id = await client.store_values(
        values, ttl_days=5, permissions=permissions
    ).invoke()

    # 5. Create compute bindings to set input and output parties, add a computation time secret and pay for & run the computation
    print("-----COMPUTE")

    # Bind the parties in the computation to the client to set input and output parties
    input_bindings = [InputPartyBinding(party_name, client.user_id)]
    output_bindings = [OutputPartyBinding(party_name, [client.user_id])]

    # Create a computation time secret to use
    compute_time_values = {"my_int2": SecretInteger(10)}

    # Compute, passing in the compute time values as well as the previously uploaded value.
    print(f"Invoking computation using program {program_id} and values id {values_id}")
    compute_id = await client.compute(
        program_id,
        input_bindings,
        output_bindings,
        values=compute_time_values,
        value_ids=[values_id],
    ).invoke()

    # 6. Return the computation result
    print(f"The computation was sent to the network. compute_id: {compute_id}")
    result = await client.retrieve_compute_results(compute_id).invoke()
    print(f"✅  Compute complete for compute_id {compute_id}")
    print(f"🖥️  The result is {result}")
    balance = await client.balance()
    print(f"💰  Final client balance: {balance.balance}")
    client.close()
    return result


if __name__ == "__main__":
    asyncio.run(main())
