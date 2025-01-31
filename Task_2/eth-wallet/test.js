const { Web3 } = require('web3');

async function testContract() {
    // 1. Connect to Ganache
    const web3 = new Web3('http://localhost:7545');
    
    try {
        // 2. Get Accounts
        const accounts = await web3.eth.getAccounts();
        console.log('Testing account:', accounts[0]);

        // 3. Load Contract ABI and Address
        const contractJson = require('./build/contracts/WalletContract.json');
        const networkId = await web3.eth.net.getId();
        const deployedAddress = contractJson.networks[networkId].address;
        const contract = new web3.eth.Contract(contractJson.abi, deployedAddress);

        // 4. Test Initial Balance
        let userBalance = await contract.methods.getBalance().call({ from: accounts[0] });
        console.log('Initial balance:', web3.utils.fromWei(userBalance, 'ether'), 'ETH');

        // 5. Test Deposit
        console.log('\nDepositing 1 ETH...');
        const depositReceipt = await contract.methods.deposit().send({
            from: accounts[0],
            value: web3.utils.toWei('1', 'ether'),
            gas: 300000
        });
        console.log('Deposit TX hash:', depositReceipt.transactionHash);

        // 6. Check Post-Deposit Balance
        userBalance = await contract.methods.getBalance().call({ from: accounts[0] });
        console.log('Balance after deposit:', web3.utils.fromWei(userBalance, 'ether'), 'ETH');

        // 7. Test Withdrawal
        console.log('\nWithdrawing 0.5 ETH...');
        const withdrawReceipt = await contract.methods.withdraw(
            web3.utils.toWei('0.5', 'ether')
        ).send({
            from: accounts[0],
            gas: 300000
        });
        console.log('Withdraw TX hash:', withdrawReceipt.transactionHash);

        // 8. Final Balance Check
        userBalance = await contract.methods.getBalance().call({ from: accounts[0] });
        console.log('Balance after withdrawal:', web3.utils.fromWei(userBalance, 'ether'), 'ETH');

        // 9. Verify Contract Balance
        const contractBalance = await web3.eth.getBalance(deployedAddress);
        console.log('\nContract ETH balance:', web3.utils.fromWei(contractBalance, 'ether'), 'ETH');

    } catch (error) {
        console.error('Test failed:', error);
    }
}

testContract();