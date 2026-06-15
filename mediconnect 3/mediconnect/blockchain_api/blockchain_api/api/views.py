from django.http import JsonResponse
from web3 import Web3
import os
from dotenv import load_dotenv
import json
from django.views.decorators.csrf import csrf_exempt
from web3.exceptions import ContractLogicError
import logging

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Set up Web3 connection and contract details
ganache_url = os.getenv("GANACHE_URL", "HTTP://127.0.0.1:7545")
web3 = Web3(Web3.HTTPProvider(ganache_url))

# Load the contract details
contract_address = '0x7844F42C14C2e02044e220E989C65cF7f4bB164F'
contract_abi = json.loads(os.getenv("ABI"))

# Set up the contract instance
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

@csrf_exempt
def store_user_profile(request):
    if request.method == "POST":
        try:
            user_data = json.loads(request.body)
            
            sender_address = os.getenv("WALLET_ADDRESS")
            private_key = os.getenv("PRIVATE_KEY")

            if not sender_address or not private_key:
                return JsonResponse({'error': 'Wallet details not configured properly'}, status=400)

            nonce = web3.eth.get_transaction_count(sender_address)

            # Convert user_data to a JSON string
            user_data_json = json.dumps(user_data)

            txn = contract.functions.storeUserProfile(
                user_data['accessCode'],
                user_data_json,
                user_data['username']
            ).build_transaction({
                'from': sender_address,
                'chainId': web3.eth.chain_id,
                'gas': 2000000,
                'gasPrice': web3.eth.gas_price,
                'nonce': nonce
            })

            signed_txn = web3.eth.account.sign_transaction(txn, private_key)
            txn_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)

            return JsonResponse({'tx_hash': txn_hash.hex()}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)

def get_user_profile(request):
    if request.method == "GET":
        access_code = request.GET.get('access_code')
        
        if not access_code:
            logger.warning("Access code not provided in request")
            return JsonResponse({'error': 'Access code not provided'}, status=400)

        try:
            logger.info(f"Retrieving user profile for access code: {access_code}")
            user_profile = contract.functions.getUserProfile(access_code).call()

            profile_data = json.loads(user_profile[0])
            profile_data['ethereumAddress'] = user_profile[1]
            profile_data['username'] = user_profile[2]

            logger.info(f"Successfully retrieved user profile for access code: {access_code}")
            return JsonResponse({'user_profile': profile_data}, status=200)

        except ContractLogicError as e:
            logger.error(f"Smart contract error for access code {access_code}: {str(e)}")
            return JsonResponse({'error': f'Smart contract error: {str(e)}'}, status=400)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON data returned from smart contract for access code {access_code}")
            return JsonResponse({'error': 'Invalid data returned from smart contract'}, status=500)
        except Exception as e:
            logger.exception(f"Unexpected error for access code {access_code}: {str(e)}")
            return JsonResponse({'error': f'Unexpected error: {str(e)}'}, status=500)

    logger.warning(f"Invalid request method: {request.method}")
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def get_user_profile_by_username(request):
    if request.method == "GET":
        username = request.GET.get('username')
        
        if not username:
            logger.warning("Username not provided in request")
            return JsonResponse({'error': 'Username not provided'}, status=400)

        try:
            logger.info(f"Retrieving user profile for username: {username}")
            user_profile = contract.functions.getUserProfileByUsername(username).call()

            profile_data = json.loads(user_profile[0])
            profile_data['ethereumAddress'] = user_profile[1]
            profile_data['username'] = user_profile[2]

            logger.info(f"Successfully retrieved user profile for username: {username}")
            return JsonResponse({'user_profile': profile_data}, status=200)

        except ContractLogicError as e:
            logger.error(f"Smart contract error for username {username}: {str(e)}")
            return JsonResponse({'error': f'Smart contract error: {str(e)}'}, status=400)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON data returned from smart contract for username {username}")
            return JsonResponse({'error': 'Invalid data returned from smart contract'}, status=500)
        except Exception as e:
            logger.exception(f"Unexpected error for username {username}: {str(e)}")
            return JsonResponse({'error': f'Unexpected error: {str(e)}'}, status=500)

    logger.warning(f"Invalid request method: {request.method}")
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def store_lab_report(request):
    if request.method == "POST":
        try:
            report_data = json.loads(request.body)
            
            sender_address = os.getenv("WALLET_ADDRESS")
            private_key = os.getenv("PRIVATE_KEY")

            if not sender_address or not private_key:
                return JsonResponse({'error': 'Wallet details not configured properly'}, status=400)

            nonce = web3.eth.get_transaction_count(sender_address)

            # Convert report_data to a JSON string
            report_data_json = json.dumps(report_data['reportData'])

            txn = contract.functions.storeLabReport(
                report_data_json,
                report_data['accessCode']
            ).build_transaction({
                'from': sender_address,
                'chainId': web3.eth.chain_id,
                'gas': 2000000,
                'gasPrice': web3.eth.gas_price,
                'nonce': nonce
            })

            signed_txn = web3.eth.account.sign_transaction(txn, private_key)
            txn_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)

            print(f"\n=== LAB REPORT STORED ON BLOCKCHAIN ===")
            print(f"Access Code  : {report_data['accessCode']}")
            print(f"Transaction  : {txn_hash.hex()}")
            print(f"Gas Limit    : {txn['gas']}")
            print(f"Gas Price    : {txn['gasPrice']}")
            print(f"Sender       : {sender_address}")
            print(f"=========================================\n")

            return JsonResponse({'tx_hash': txn_hash.hex()}, status=200)

        except Exception as e:
            print(f"\n!!! BLOCKCHAIN ERROR: {e} !!!\n")
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def store_doctor_profile(request):
    if request.method == "POST":
        try:
            doctor_data = json.loads(request.body)
            
            sender_address = os.getenv("WALLET_ADDRESS")
            private_key = os.getenv("PRIVATE_KEY")

            if not sender_address or not private_key:
                return JsonResponse({'error': 'Wallet details not configured properly'}, status=400)

            nonce = web3.eth.get_transaction_count(sender_address)

            # Convert doctor_data to a JSON string
            doctor_data_json = json.dumps(doctor_data)

            txn = contract.functions.storeDoctorProfile(
                doctor_data['username'],
                doctor_data_json
            ).build_transaction({
                'from': sender_address,
                'chainId': web3.eth.chain_id,
                'gas': 2000000,
                'gasPrice': web3.eth.gas_price,
                'nonce': nonce
            })

            signed_txn = web3.eth.account.sign_transaction(txn, private_key)
            txn_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)

            return JsonResponse({'tx_hash': txn_hash.hex()}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)

def get_lab_reports(request):
    if request.method == "GET":
        try:
            access_code = request.GET.get('access_code')
            
            if not access_code:
                return JsonResponse({'error': 'Access code not provided'}, status=400)

            lab_reports = contract.functions.getLabReports(access_code).call()

            formatted_reports = [
                json.loads(report[0]) for report in lab_reports
            ]

            return JsonResponse({'lab_reports': formatted_reports}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)

def get_doctor_profile(request):
    if request.method == "GET":
        try:
            username = request.GET.get('username')
            
            if not username:
                return JsonResponse({'error': 'Doctor username not provided'}, status=400)

            doctor_profile = contract.functions.getDoctorProfile(username).call()

            doctor_data = json.loads(doctor_profile[0])
            doctor_data['ethereumAddress'] = doctor_profile[1]

            return JsonResponse({'doctor_profile': doctor_data}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)

def get_my_access_code(request):
    if request.method == "GET":
        try:
            sender_address = os.getenv("WALLET_ADDRESS")

            if not sender_address:
                return JsonResponse({'error': 'Wallet address not configured'}, status=400)

            access_code = contract.functions.getMyAccessCode().call({'from': sender_address})

            return JsonResponse({'access_code': access_code}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)