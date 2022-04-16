import { useContractFunction, useEthers } from "@usedapp/core"
import TokenFarm from "../chain-info/TokenFarm.json"
import ERC20 from "../chain-info/ERC20.json"
import networkMapping from "../chain-info/map.json";
import { constants, utils } from "ethers";
import { Contract } from '@usedapp/core/node_modules/@ethersproject/contracts';
import { useState, useEffect } from "react";

export const useStakeTokens = (tokenAddress: string) => {
  const { chainId } = useEthers();
  const { abi } = TokenFarm
  const tokenFarmAddress = chainId ? networkMapping[String(chainId)]["TokenFarm"][0] : constants.AddressZero;
  const tokenFarmInterface = new utils.Interface(abi)
  const tokenFarmContract = new Contract(tokenFarmAddress, tokenFarmInterface)

  const ERC20Abi = ERC20.abi
  const erc20Interface = new utils.Interface(ERC20Abi)
  const erc20Contract = new Contract(tokenAddress, erc20Interface)

  const { send: approveErc20Send, state: approveAndStakeErc20State } =
    useContractFunction(erc20Contract, "approve", {
      transactionName: "Approve ERC20 transfer",
    })

  const approveAndStake = (amount: string) => {
    setAmountToStake(amount)
    return approveErc20Send(tokenFarmAddress, amount)
  }


  const { send: stakeSend, state: stakeState } =
    useContractFunction(tokenFarmContract, "stakeTokens", {
      transactionName: "Stake tokens",
    })

  const [amountToStake, setAmountToStake] = useState("0");

  useEffect(() => {
    if (approveAndStakeErc20State.status == "Success") {
      stakeSend(amountToStake, tokenAddress)
    }
  }, [approveAndStakeErc20State, tokenAddress, amountToStake])

  const [state, setState] = useState(approveAndStakeErc20State);

  useEffect(() => {
    if (approveAndStakeErc20State.status == "Success") {
      setState(stakeState)
    }else{
      setState(approveAndStakeErc20State)
    }
  }, [approveAndStakeErc20State, stakeState])

  return { approveAndStake, state }
}