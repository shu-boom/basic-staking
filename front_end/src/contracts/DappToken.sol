// SPDX-License-Identifier: MIT
pragma solidity 0.8.0;
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

/**
     This is a DAPP token which is used by our token farm contract to offer rewards to the user. 
 */
contract DappToken is ERC20 {
    constructor() ERC20 ("Dapp Token", "Dapp"){
        _mint(msg.sender, 1000000000000000000000000);
    }
}