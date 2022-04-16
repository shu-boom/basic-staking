from brownie import accounts, network, exceptions
import pytest
from scripts.deploy import deploy_token_farm_and_dapp_token
from scripts.helpful_scripts import DECIMALS, LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account, get_contract, INITIAL_PRICE_FEED_VALUE

def test_stake_tokens(amount_staked):
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for Integration testing")
    token_farm, dapp_token = deploy_token_farm_and_dapp_token()
    account = get_account()
    dapp_token.approve(token_farm.address, amount_staked, {"from": account})
    token_farm.stakeTokens(amount_staked, dapp_token.address, {"from": account})
    starting_balance = dapp_token.balanceOf(account.address)
    ## Now that this is not the mock we cant rely on INITIAL_PRICE posted by mockv3 aggregator. we actually have to get the price
    price_feed_contract = get_contract("dai_usd_price_feed")
    (_, price, _, _, _) = price_feed_contract.latestRoundData()
    amount_token_to_issue = (
        price / 10 ** price_feed_contract.decimals()
    ) * amount_staked
    issue_tx = token_farm.issueTokens({"from": account})
    issue_tx.wait(1)
    assert (
        dapp_token.balanceOf(account.address)
        == amount_token_to_issue + starting_balance
    )