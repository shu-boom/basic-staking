/* eslint-disable spaced-comment */
/// <reference types="react-scripts" />
import {useEthers} from "@usedapp/core"
import helperConfig from "../helper-config.json";
import networkMapping from "../chain-info/map.json";
import {constants} from "ethers";
import brownieConfig from "../brownie-config.json";
import dapp from "../dapp.png"
import eth from "../eth.png"
import dai from "../dai.png"
import { YourWallet } from "./yourWallet";

export type Token = {
    image: string,
    address: string,
    name: string
}

export const Main = () => {
    const { chainId } = useEthers();
    const networkName = chainId ? helperConfig[chainId] : "dev";
    console.log(chainId);
    console.log(networkName);

    const dappTokenAddress = chainId ?  networkMapping[String(chainId)]["DappToken"][0] : constants.AddressZero;
    const wethTokenAddress = chainId ?  brownieConfig["networks"][networkName]["weth_token"] : constants.AddressZero;
    const fauTokenAddress = chainId ?  brownieConfig["networks"][networkName]["fau_token"] : constants.AddressZero;

    const supportedTokens: Array<Token> = [{
        image: dapp,
        address: dappTokenAddress,
        name: "DAPP"
    },
    {
        image: eth,
        address: wethTokenAddress,
        name: "WETH"
    },
    {
        image: dai,
        address: fauTokenAddress,
        name: "DAI"
    },

]

    return (<YourWallet supportedTokens={supportedTokens} />);
}