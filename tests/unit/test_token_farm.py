from brownie import accounts, network, exceptions
import pytest
from scripts.deploy import deploy_token_farm_and_dapp_token
from scripts.helpful_scripts import DECIMALS, LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account, get_contract, INITIAL_PRICE_FEED_VALUE

def test_set_price_feed_contract():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    account = get_account()
    non_owner = get_account(index=1)
    token_farm, dapp_token = deploy_token_farm_and_dapp_token()
    price_feed = get_contract("eth_usd_price_feed")
    token_farm.setPriceFeedContract(dapp_token.address, price_feed, {"from": account})
    assert token_farm.tokenPriceFeedMapping(dapp_token.address) == price_feed
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.setPriceFeedContract(dapp_token.address, price_feed, {"from": non_owner})

def test_stake_tokens(amount_staked):
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    account=get_account()
    token_farm, dapp_token = deploy_token_farm_and_dapp_token()
    dapp_token.approve(token_farm.address, amount_staked, {"from": account})
    token_farm.stakeTokens(amount_staked, dapp_token.address, {"from": account})
    assert (
        token_farm.stakingBalance(dapp_token.address, account.address) == amount_staked
    )
    assert token_farm.uniqueTokensStaked(account.address) == 1
    assert token_farm.stakers(0) == account.address
    return token_farm, dapp_token

def test_issue_tokens(amount_staked):
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    account=get_account()
    token_farm, dapp_token = test_stake_tokens(amount_staked)
    starting_balance = dapp_token.balanceOf(account.address)
    token_farm.issueTokens({"from": account})
    assert(
        dapp_token.balanceOf(account.address) == starting_balance + INITIAL_PRICE_FEED_VALUE
    )

def test_get_token_value():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    account=get_account()
    token_farm, dapp_token = deploy_token_farm_and_dapp_token()
    assert token_farm.getTokenValue(dapp_token.address) == (INITIAL_PRICE_FEED_VALUE, DECIMALS)

def test_check_token_is_allowed():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    account=get_account()
    token_farm, dapp_token = deploy_token_farm_and_dapp_token()
    token_farm.addAllowedTokens(dapp_token.address, {"from": account})
    assert token_farm.tokenIsAllowed(dapp_token.address) == True

def test_get_user_single_token_value(amount_staked):
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    account=get_account()
    token_farm, dapp_token = test_stake_tokens(amount_staked)
    token_value = token_farm.getUserSingleTokenValue(account.address, dapp_token.address, {"from": account})
    assert token_value == (amount_staked*INITIAL_PRICE_FEED_VALUE) / 10**DECIMALS

def test_get_user_total_value(amount_staked):
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    account=get_account()
    token_farm, dapp_token = test_stake_tokens(amount_staked)
    token_value = token_farm.getUserTotalValue(account.address, {"from": account})
    assert token_value == (amount_staked*INITIAL_PRICE_FEED_VALUE) / 10**DECIMALS


def test_unstake_tokens(amount_staked):
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    account=get_account()
    token_farm, dapp_token = test_stake_tokens(amount_staked)
    token_farm.unStakeTokens(dapp_token.address, {"from": account})
    assert token_farm.uniqueTokensStaked(account.address) == 0

