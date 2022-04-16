// SPDX-License-Identifier: MIT
pragma solidity 0.8.0;
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
// Since token farm doesnt own the tokens that are being deposited. The transfer function is not going to work. 
// In this case approve and transferFrom function is required. For us to talk to the actual ERC20 token we need the ERC20 interface to talk to the contract
// and invoke approve and transferFrom so the TokenFarm is allowed to spend the tokens. 

/**
    This contract drives our token farming and staking platform. 
    This application is a token-centric application.
    The application allows staking and unstaking of some token. 

    Therefore, the first step is to add these staking and unstaking functionality to our contracts
    

 */
contract TokenFarm is Ownable{
    mapping(address => mapping(address => uint)) public stakingBalance;
    mapping(address => uint256) public uniqueTokensStaked;
    mapping(address => address) public tokenPriceFeedMapping;
    address[] public allowedTokens;
    address[] public stakers;
    IERC20 public dappToken;

    constructor(address _dappTokenAddress){
        dappToken=IERC20(_dappTokenAddress);
    }
    // DONE
    // method to add supported tokens
    function addAllowedTokens(address _token) public onlyOwner{
        allowedTokens.push(_token);
    }
    // DONE
    // method to check if the token is in supported tokens
    function tokenIsAllowed(address _token) public view returns(bool){
        for(uint allowedTokensIndex; allowedTokensIndex < allowedTokens.length; allowedTokensIndex++){
            if(allowedTokens[allowedTokensIndex]==_token){
                return true;
            }
        }
        return false;
    }

    /**
        The ability to stake some tokens with our TokenFarm is one of the main features that this contract offers
        In order to stake tokens, We need to know the following questions:

            What type of tokens can they stake? 
                Need to allow users to stake some pre-approved tokens.
                Need to maintain a data structure to keep track of allowed tokens
                Need to add the ability to modify this data structure (Ownable type)
                Need ability to check if the token is allowed

            How much amount are they staking? 0 is invalid


            After answering these two questions. We would like to transfer the token under TokenFarm name
            In order to do that, we would need an Interface. All ERC 20 tokens adhere to the IERC20 interface.

            Since the TokenFarm is not the owner of the Dapp tokens that the user is going to stake. TokenFarm needs prior approval to transfer the tokens. 
            Contracts generally use 3rd party transfer like approve and transferFrom to ensure security.
            Using approve also helps TokenFarm to maintain a mapping

            The TokenFarm contract allows multiple tokens staking for multiple users 
                mapping(address => mapping(address => uint)) public stakingBalance;

            Another use case of the application is that we would want to reward our LPs
            Therefore, recording them or adding them to a mapping makes sense
     
     */
    // DONE
    function stakeTokens(uint _amount, address _token) public {
        // what tokens can they stake 
        require(_amount>0, "Amount must be greater than 0");
        // how much can you stake ?
        require(tokenIsAllowed(_token), "Token not allowed"); //token allowed
        updateUniqueTokensStaked(msg.sender, _token); 
        IERC20(_token).transferFrom(msg.sender, address(this), _amount);
        stakingBalance[_token][msg.sender] = stakingBalance[_token][msg.sender] + _amount;
        if(uniqueTokensStaked[msg.sender] == 1){
            stakers.push(msg.sender);
        }
    }

    /**
        Another major feature is to unstake tokens from the token farm
        This would simply call transfer
            When we staked the tokens we used approve and transfer from to transfer the balance
            Therefore, the TokenFarm contract is able to spend all of the balance
        Since token farm owns all of the tokens it simply calls transfer to transfer them to the caller.

        Once all the tokens are withdrawn, the contract needs to know how many unique tokens are staked
     
     
     */
    function unStakeTokens(address _token) public {
        uint balance = stakingBalance[_token][msg.sender];
        require(balance>0, "No tokens are staked");
        IERC20(_token).transfer(msg.sender, balance);
        uniqueTokensStaked[msg.sender] = uniqueTokensStaked[msg.sender] - 1;
    }

    // This updateUniqueTokensStaked this is a naive approach to calculate wether 
    // the user is staking for the first time update the balance. 
    function updateUniqueTokensStaked(address _user, address _token) internal {
        if(stakingBalance[_token][_user]<=0){
            uniqueTokensStaked[_user]=uniqueTokensStaked[_user] + 1;
        }
    }

    //DONE
    // gets the total staking balance for the user. Avoid iteration 
    function getUserTotalValue(address _user) public view returns(uint256) {
        uint totalValue = 0;
        require(uniqueTokensStaked[_user]>0, "No tokens staked");
        for(uint allowedTokensIndex; allowedTokensIndex<allowedTokens.length; allowedTokensIndex++){
             totalValue = totalValue + getUserSingleTokenValue(_user, allowedTokens[allowedTokensIndex]);
        }
        return totalValue;
    }

    // DONE
    // getUserTokenStakingBalanceEthValue
    // get the current value of the token in price by utilizing a chainlink price feed
    function getUserSingleTokenValue(address _user, address _token) public view returns(uint) {
        if(uniqueTokensStaked[_user]<=0){
            return 0;
        }
        (uint price, uint decimals) =  getTokenValue(_token);
        return (stakingBalance[_token][_user] * price / 10**decimals);
    }

    // DONE
    function setPriceFeedContract(address _token, address _priceFeed) public onlyOwner {
        tokenPriceFeedMapping[_token] = _priceFeed;
    }

    // DONE
    // gets the price from a V3 Aggregator
    function getTokenValue(address _token) public view returns(uint, uint){
        address priceFeedAddress = tokenPriceFeedMapping[_token];
        AggregatorV3Interface priceFeed = AggregatorV3Interface(priceFeedAddress);
        (, int256 price,,,) = priceFeed.latestRoundData();
        uint256 decimals = uint(priceFeed.decimals());
        return(uint(price), decimals);
    }

    // DONE
    // issue reward token to all the stakers based on their stord value
    function issueTokens() public onlyOwner {
        for(
            uint stakersIndex = 0;
            stakersIndex < stakers.length;
            stakersIndex++
        ){
            address recipient = stakers[stakersIndex];
            dappToken.transfer(recipient, getUserTotalValue(recipient));
        }
    }
}

