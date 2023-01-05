from datetime import datetime
from web3 import Web3
from web3.contract import Contract, ContractFunction
from web3.exceptions import ABIFunctionNotFound, ContractLogicError
from web3.logs import DISCARD
from web3.middleware import geth_poa_middleware
from web3.types import ChecksumAddress, HexBytes, Nonce, TxParams, TxReceipt, Wei
from decimal import Decimal
from pathlib import Path
from loguru import logger
from typing import Dict, List, NamedTuple, Optional, Set, Tuple
import telebot
import traceback
import datetime
import variables
from network import Net


class buy_sell():
    def __init__(self, slippage, name, amount=variables.amount) -> None:
        self.slippage = slippage
        self.gas_price = Wei(variables.gas_price)
        self.gas_price_2 = Wei("5")
        self.price_in_usd = False
        self.symbol_usd = "$" if self.price_in_usd else ""
        self.symbol_bnb = "BNB" if not self.price_in_usd else ""
        self.net = Net(variables.sender_address)
        self.amount = Wei(int(amount))
        self.symbol = name

    def buy(self, contr):
        if variables.bot_work:
            id = variables.id_chat
            bot = variables.bot
        res, tokens_out, txhash_or_error = self.net.buy_tokens(
            contr, amount_bnb=self.amount, slippage_percent=self.slippage, gas_price=self.gas_price
        )
        if not res:
            if txhash_or_error[:2] == "0x" and len(txhash_or_error) == 66:
                reason_or_link = f'https://bscscan.com/tx/{txhash_or_error}'
            else:
                reason_or_link = txhash_or_error
            logger.error(f"Transaction failed: {reason_or_link}")
            if variables.bot_work:
                try:
                    bot.send_message(
                        id, f"{self.symbol}\nTransaction failed: {reason_or_link}")
                except:
                    tr = traceback.format_exc()
                    with open("logs.txt", "a") as f:
                        f.write(str(datetime.datetime.now()) +
                                " " + str(tr) + "\n\n\n")
            return
        effective_price = self.get_human_amount(
            contr, "buy") / tokens_out  # in BNB per token
        if self.price_in_usd:  # we need to convert to USD according to settings
            effective_price = effective_price * self.net.get_bnb_price()
            effective_buy_price = str(effective_price)

        def format_token_amount(amount: Decimal) -> str:
            if amount >= 100:
                return f"{amount:,.1f}"
            return f"{amount:.4g}"
        logger.success(
            # символ как получить?
            f"Buy transaction succeeded. Received {format_token_amount(tokens_out)} {self.symbol}. "
            + f"Effective price (after tax) {self.symbol_usd}{effective_price:.4g} {self.symbol_bnb} / token"
        )
        if variables.bot_work:
            try:
                text = f"✅ Buy transaction succeeded.\n Received {format_token_amount(tokens_out)} {self.symbol} at ".replace(
                    ".", "\.") + f'tx [{txhash_or_error[:8]}\.\.\.](https://bscscan.com/tx/{txhash_or_error})\n' + f"Effective price \(after tax\) {effective_price:.4g} BNB / token".replace(".", "\.").replace("-", "\-"),
                bot.send_message(id, text, parse_mode='MarkdownV2')
            except:
                tr = traceback.format_exc()
                with open("logs.txt", "a") as f:
                    f.write(str(datetime.datetime.now()) +
                            " " + str(tr) + "\n\n\n")
        if not self.net.is_approved(token_address=contr):
            # pre-approve for later sell
            # опять же символ
            logger.info(f"Approving {self.symbol} for trading on PancakeSwap.")
            if variables.bot_work:
                try:
                    text = f"Approving {self.symbol} for trading on PancakeSwap..."
                    bot.send_message(
                        id, text=text)
                    res = self.net.approve(token_address=contr)
                    text = "✅ Approval successful!"
                    bot.send_message(
                        id, text=text)
                except:
                    tr = traceback.format_exc()
                    with open("logs.txt", "a") as f:
                        f.write(str(datetime.datetime.now()) +
                                " " + str(tr) + "\n\n\n")
            if not self.net.is_approved(token_address=contr):
                # pre-approve for later sell
                # опять же символ
                logger.info(
                    f"Approving {self.symbol} for trading on PancakeSwap.")
                if variables.bot_work:
                    try:
                        text = f"Approving {self.symbol} for trading on PancakeSwap..."
                        bot.send_message(
                            id, text=text)
                        res = self.net.approve(token_address=contr)
                        text = "✅ Approval successful!"
                        bot.send_message(
                            id, text=text)
                    except:
                        tr = traceback.format_exc()
                        with open("logs.txt", "a") as f:
                            f.write(str(datetime.datetime.now()) +
                                    " " + str(tr) + "\n\n\n")
        return effective_price

    def get_human_amount(self, contr, typ) -> Decimal:
        sellAbi = '[{"inputs":[{"internalType":"string","name":"_NAME","type":"string"},{"internalType":"string","name":"_SYMBOL","type":"string"},{"internalType":"uint256","name":"_DECIMALS","type":"uint256"},{"internalType":"uint256","name":"_supply","type":"uint256"},{"internalType":"uint256","name":"_txFee","type":"uint256"},{"internalType":"uint256","name":"_lpFee","type":"uint256"},{"internalType":"uint256","name":"_MAXAMOUNT","type":"uint256"},{"internalType":"uint256","name":"SELLMAXAMOUNT","type":"uint256"},{"internalType":"address","name":"routerAddress","type":"address"},{"internalType":"address","name":"tokenOwner","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"spender","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"minTokensBeforeSwap","type":"uint256"}],"name":"MinTokensBeforeSwapUpdated","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"tokensSwapped","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"ethReceived","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"tokensIntoLiqudity","type":"uint256"}],"name":"SwapAndLiquify","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"bool","name":"enabled","type":"bool"}],"name":"SwapAndLiquifyEnabledUpdated","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"inputs":[],"name":"_liquidityFee","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"_maxTxAmount","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"_owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"_taxFee","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"claimTokens","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"subtractedValue","type":"uint256"}],"name":"decreaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"tAmount","type":"uint256"}],"name":"deliver","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"excludeFromFee","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"excludeFromReward","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"geUnlockTime","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"includeInFee","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"includeInReward","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"addedValue","type":"uint256"}],"name":"increaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"isExcludedFromFee","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"isExcludedFromReward","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"time","type":"uint256"}],"name":"lock","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"numTokensSellToAddToLiquidity","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"tAmount","type":"uint256"},{"internalType":"bool","name":"deductTransferFee","type":"bool"}],"name":"reflectionFromToken","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"liquidityFee","type":"uint256"}],"name":"setLiquidityFeePercent","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"maxTxPercent","type":"uint256"}],"name":"setMaxTxPercent","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"swapNumber","type":"uint256"}],"name":"setNumTokensSellToAddToLiquidity","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bool","name":"_enabled","type":"bool"}],"name":"setSwapAndLiquifyEnabled","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"taxFee","type":"uint256"}],"name":"setTaxFeePercent","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"swapAndLiquifyEnabled","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"rAmount","type":"uint256"}],"name":"tokenFromReflection","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalFees","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"uniswapV2Pair","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"uniswapV2Router","outputs":[{"internalType":"contract IUniswapV2Router02","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"unlock","outputs":[],"stateMutability":"nonpayable","type":"function"},{"stateMutability":"payable","type":"receive"}]'

        bsc = "https://bsc-dataseed.binance.org/"
        web3 = Web3(Web3.HTTPProvider(bsc))
        cc = web3.eth.contract(
            address=web3.toChecksumAddress(contr), abi=sellAbi)
        decimals = float(cc.functions.decimals().call())
        decimals = decimals if typ == "sell" else 18
        return Decimal(self.amount) / Decimal(10**decimals)

    def sell(self, contr):
        if variables.bot_work:
            id = variables.id_chat
            bot = variables.bot
        # balance_before = self.net.get_token_balance_wei(token_address=contr)
        res, bnb_out, txhash_or_error = self.net.sell_tokens(
            contr,
            amount_tokens=self.amount,
            slippage_percent=self.slippage,
            gas_price=self.gas_price_2,
        )
        if not res:
            logger.error(f"Transaction failed: {txhash_or_error}")
            if txhash_or_error[:2] == "0x" and len(txhash_or_error) == 66:
                reason_or_link = f'https://bscscan.com/tx/{txhash_or_error}'
            else:
                reason_or_link = txhash_or_error
            text = f"{self.symbol}\n⛔️ Transaction failed: {reason_or_link}"
            if variables.bot_work:
                try:
                    bot.send_message(id, text)
                except:
                    tr = traceback.format_exc()
                    with open("logs.txt", "a") as f:
                        f.write(str(datetime.datetime.now()) +
                                " " + str(tr) + "\n\n\n")
            res, bnb_out, txhash_or_error = self.net.sell_tokens(
                contr,
                amount_tokens=self.amount,
                slippage_percent=self.slippage,
                gas_price=self.gas_price_2,
            )
            if not res:
                logger.error(f"Transaction failed: {txhash_or_error}")
                if txhash_or_error[:2] == "0x" and len(txhash_or_error) == 66:
                    reason_or_link = f'https://bscscan.com/tx/{txhash_or_error}'
                else:
                    reason_or_link = txhash_or_error
                text = f"{self.symbol}\n⛔️ Transaction failed: {reason_or_link}"
                if variables.bot_work:
                    try:
                        bot.send_message(id, text)
                    except:
                        tr = traceback.format_exc()
                        with open("logs.txt", "a") as f:
                            f.write(str(datetime.datetime.now()) +
                                    " " + str(tr) + "\n\n\n")
            '''  # will trigger deletion of the object
            return
        effective_price = bnb_out / self.get_human_amount(contr, "sell")  # in BNB
        if self.price_in_usd:  # we need to convert to USD according to settings
            effective_price = effective_price * self.net.get_bnb_price()
        sold_proportion = self.amount / balance_before
        logger.success(
            f"Sell transaction succeeded. Received {bnb_out:.3g} BNB. "
            + f"Effective price (after tax) {self.symbol_usd}{effective_price:.4g} {self.symbol_bnb} / token"
        )
        '''
        else:
            if variables.bot_work():
                try:
                    effective_price = bnb_out / \
                        self.get_human_amount(contr, "sell")  # in BNB
                    if self.price_in_usd:  # we need to convert to USD according to settings
                        effective_price = effective_price * self.net.get_bnb_price()
                    logger.success(
                        f"Sell transaction succeeded.\n Received {bnb_out:.3g} BNB. "
                        + f"Effective price (after tax) {effective_price:.4g} {self.symbol_bnb} / token"
                    )
                    usd_out = self.net.get_bnb_price() * bnb_out
                    text = f"✅ Sell transaction succeeded. Received {bnb_out:.3g} BNB \(${usd_out:.2f}\) at ".replace(
                        '.', '\.') + f'tx [{txhash_or_error[:8]}\.\.\.](https://bscscan.com/tx/{txhash_or_error})\n' + f"Effective price \(after tax\) {effective_price:.4g} BNB / token\n".replace('.', "\.").replace('-', "\-")
                    bot.send_message(id, text, parse_mode='MarkdownV2')
                except:
                    tr = traceback.format_exc()
                    with open("logs.txt", "a") as f:
                        f.write(str(datetime.datetime.now()) +
                                " " + str(tr) + "\n\n\n")

      # will trigger deletion of the object
