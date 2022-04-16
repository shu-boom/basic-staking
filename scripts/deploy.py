from scripts.helpful_scripts import get_account, get_contract
from brownie import DappToken, TokenFarm, config, network
from web3 import Web3
import os
import shutil
import yaml
import json

KEPT_BALANCE = Web3.toWei(100, "ether")
def main():
    deploy_token_farm_and_dapp_token()

def deploy_token_farm_and_dapp_token():
    account = get_account()
    dapp_token = DappToken.deploy({"from": account})
    token_farm = TokenFarm.deploy(dapp_token.address, {"from": account}, publish_source = config["networks"][network.show_active()]["verify"])
    tx = dapp_token.transfer(token_farm.address, dapp_token.totalSupply() - KEPT_BALANCE)
    tx.wait(1)
    weth_token = get_contract("weth_token")
    fau_token = get_contract("fau_token")
    dict_of_allowed_tokens= {
        dapp_token: get_contract("dai_usd_price_feed"),
        fau_token: get_contract("dai_usd_price_feed"),
        weth_token: get_contract("eth_usd_price_feed")
    }
    add_allowed_tokens(token_farm, dict_of_allowed_tokens, account)
    return token_farm, dapp_token

def add_allowed_tokens(token_farm, dict_of_allowed_tokens, account):
    for token in dict_of_allowed_tokens:
        add_tx = token_farm.addAllowedTokens(token.address, {"from": account})
        add_tx.wait(1)
        set_tx = token_farm.setPriceFeedContract(token.address, dict_of_allowed_tokens[token], {"from": account})
        set_tx.wait(1)
    return token_farm


def update_front_end():
    print("Updating front end...")
    # The Build
    copy_folders_to_front_end("./build/contracts", "./front_end/src/chain-info")

    # The Contracts
    copy_folders_to_front_end("./contracts", "./front_end/src/contracts")

    # The ERC20
    copy_files_to_front_end(
        "./build/contracts/dependencies/OpenZeppelin/openzeppelin-contracts@4.2.0/ERC20.json",
        "./front_end/src/chain-info/ERC20.json",
    )
    # The Map
    copy_files_to_front_end(
        "./build/deployments/map.json",
        "./front_end/src/chain-info/map.json",
    )

    # The Config, converted from YAML to JSON
    with open("brownie-config.yaml", "r") as brownie_config:
        config_dict = yaml.load(brownie_config, Loader=yaml.FullLoader)
        with open(
            "./front_end/src/brownie-config-json.json", "w"
        ) as brownie_config_json:
            json.dump(config_dict, brownie_config_json)
    print("Front end updated!")


def copy_folders_to_front_end(src, dest):
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(src, dest)


def copy_files_to_front_end(src, dest):
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copyfile(src, dest)
