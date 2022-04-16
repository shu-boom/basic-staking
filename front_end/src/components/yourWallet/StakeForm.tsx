import { useEthers, useTokenBalance, useNotifications } from '@usedapp/core'
import { Token } from '../Main'
import { formatUnits } from '@ethersproject/units'
import { Button, CircularProgress, Input } from '@material-ui/core'
import { useEffect, useState } from 'react'
import { useStakeTokens } from '../../hooks/useStakeTokens'
import { utils } from "ethers";
export interface StakeFormProps {
    token: Token
}

export const StakeForm = ({ token }: StakeFormProps) => {
    const [amount, setAmount] = useState<number | string | Array<number | string>>(0)
    const { address, name } = token
    const { account } = useEthers()
    const tokenBalance = useTokenBalance(address, account)
    const formattedTokenBalance: number = tokenBalance
        ? parseFloat(formatUnits(tokenBalance, 18))
        : 0

    const { notifications } = useNotifications()

    const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const newAmount = event.target.value === "" ? "" : Number(event.target.value)
        setAmount(newAmount)
        console.log(newAmount)
    }

    const { approveAndStake, state: approveAndStakeErc20State } = useStakeTokens(address);

    const handleStakeSubmit = () => {
        const amountAsWei = utils.parseEther(amount.toString())
        return approveAndStake(amountAsWei.toString());
    }

    const [showErc20ApprovalSuccess, setShowErc20ApprovalSuccess] = useState(false)
    const [showStakeTokensSuccess, setShowStakeTokensSuccess] = useState(false)


    const isMining = approveAndStakeErc20State.status === "Mining"

    useEffect(() => {
        if (
            notifications.filter(
                (notification) =>
                    notification.type === "transactionSucceed" &&
                    notification.transactionName === "Approve ERC20 transfer"
            ).length > 0
        ) {
            !showErc20ApprovalSuccess && setShowErc20ApprovalSuccess(true)
            showStakeTokensSuccess && setShowStakeTokensSuccess(false)
        }

        if (
            notifications.filter(
                (notification) =>
                    notification.type === "transactionSucceed" &&
                    notification.transactionName === "Stake tokens"
            ).length > 0
        ) {
            showErc20ApprovalSuccess && setShowErc20ApprovalSuccess(false)
            !showStakeTokensSuccess && setShowStakeTokensSuccess(true)
        }
    }, [notifications, showErc20ApprovalSuccess, showStakeTokensSuccess])


    return (
        <>
            <Input onChange={handleInputChange} ></Input>
            <Button color="primary" size="large" onClick={handleStakeSubmit} disabled={isMining}>
                {isMining ? <CircularProgress size={26} /> : "Stake!"}
            </Button>
        </>
    )
}
