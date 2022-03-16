# dexapi

Python wrapper for bitquery.io DEX API

## Installation
Install the latest version from PyPI is by using pip:
```
pip install dexapi
```
Alternatively, install directly from the GitHub repository:
```
pip install git+https://github.com/kayrauygun/dexapi.git
```
## Functions

Create `dexAPI` object using following code:
```python
import  dexapi
api = dexapi.dexAPI("API_KEY", network="NETWORK_NAME")
```
Available networks are "ethereum" and "bsc".

### List of Exchanges
`get_exchanges` function returns DEXs with highest volume (in USD)  in network between two datetimes.
```python
dexapi.dexAPI.get_exchanges(start_time, end_time, limit)
```
`start_time`: *str | datetime, optional, default = first day of current year, format = "YYYY-MM-DD",
datetime.date(YYYY,MM,DD), "YYYY-MM-DDTHH:MM:SS" (ISO8601DateTime), datetime.datetime(YYYY,MM,DD,HH,MM,SS),
if hours, minutes, seconds are not specified it will be taken as 00:00:00*

`end_time`: *str | datetime, optional, default = now, format = "YYYY-MM-DD",
datetime.date(YYYY,MM,DD), "YYYY-MM-DDTHH:MM:SS" (ISO8601DateTime), datetime.datetime(YYYY,MM,DD,HH,MM,SS),
if hours, minutes, seconds are not specified it will be taken as 23:59:59*

`limit`: *int, optional, default = 20, maximum number of entries function returns*

`return`:* dataframe, columns = [
        "exchange": DEX name,
        "protocol": protocol DEX uses,
        "count": number of trades,
        "tradeAmount": total volume in USD,
        "exchangeAddress": address of exchange on network
        ]*

Example usage:
```python
import  dexapi
api = dexapi.dexAPI("API_KEY", network="ethereum")
api.get_exchanges("2022-03-01", "2022-03-15", 20 )
```
### List of Pairs
`get_pairs` function returns pairs with highest volume (in USD) in the DEX between two datetimes.
```python
dexapi.dexAPI.get_pairs(exchange_address, start_time, end_time, limit)
```
`exchange_address`: *str, address of exchange on network*

`start_time`: *str | datetime, optional, default = first day of current year, format = "YYYY-MM-DD",
datetime.date(YYYY,MM,DD), "YYYY-MM-DDTHH:MM:SS" (ISO8601DateTime), datetime.datetime(YYYY,MM,DD,HH,MM,SS),
if hours, minutes, seconds are not specified it will be taken as 00:00:00*

`end_time`: *str | datetime, optional, default = now, format = "YYYY-MM-DD",
datetime.date(YYYY,MM,DD), "YYYY-MM-DDTHH:MM:SS" (ISO8601DateTime), datetime.datetime(YYYY,MM,DD,HH,MM,SS),
if hours, minutes, seconds are not specified it will be taken as 23:59:59*

`limit`: *int, optional, default = 20, maximum number of entries function returns*

`return`: *dataframe, columns = [
        "exchange": DEX name,
        "protocol": protocol DEX uses,
        "currency1": first leg of swaps,
        "currency2": second leg of swap,
        "smartContract": address of smart contract trades pair on network
        ]*

Example usage:
```python
import  dexapi
api = dexapi.dexAPI("API_KEY", network="ethereum")
api.get_exchanges("0x1f98431c8ad98523631ae4a59f267346ea31f984", "2022-03-01", "2022-03-15", 50 )
```
### List of Trades
`get_trades` function returns most recent trades use the smart contract between two times.
```python
dexapi.dexAPI.get_trades(smart_contract, start_time, end_time, limit)
```
`smart_contract`: *str, address of smart contract on network*

`start_time`: *str | datetime, optional, default = today 00:00:00, format = "YYYY-MM-DD",
datetime.date(YYYY,MM,DD), "YYYY-MM-DDTHH:MM:SS" (ISO8601DateTime), datetime.datetime(YYYY,MM,DD,HH,MM,SS),
if hours, minutes, seconds are not specified it will be taken as 00:00:00*

`end_time`: *str | datetime, optional, default = now, format = "YYYY-MM-DD",
datetime.date(YYYY,MM,DD), "YYYY-MM-DDTHH:MM:SS" (ISO8601DateTime), datetime.datetime(YYYY,MM,DD,HH,MM,SS),
if hours, minutes, seconds are not specified it will be taken as 23:59:59*

`limit`: *int, optional, default = 1000, maximum number of entries function returns*

`return`: *dataframe, columns = [
        "exchange": DEX name,
        "protocol": protocol DEX uses,
        "timestamp": timestamp of block,
        "block": block height,
        "buyCurrency": currency DEX buys,
        "sellCurrency": currency DEX sells,
        "price": price of "buyCurrency" in terms of "sellCurrency",
        "tradeAmount": volume in USD
        "transaction": transaction hash
        ]*

Example usage:
```python
import  dexapi
api = dexapi.dexAPI("API_KEY", network="ethereum")
api.get_trades("0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640", "2022-03-15", "2022-03-15", 1500 )
```
### Historical Balance
`get_balances` function returns the balance of the smart contract address at a specific time.
```python
dexapi.dexAPI.get_balances(address, time)
```
`address`: *str, address of the smart contract on network

`time`: *str | datetime, optional, default = now, format = "YYYY-MM-DD",
datetime.date(YYYY,MM,DD), "YYYY-MM-DDTHH:MM:SS" (ISO8601DateTime), datetime.datetime(YYYY,MM,DD,HH,MM,SS),
if hours, minutes, seconds are not specified it will be taken as 23:59:59*

`return`: *dataframe, columns = [
        "currency": currency symbol,
        "value": number of tokens owned by address,
        "currencyAddress": address of currency,
        ]*

Example usage:
```python
import  dexapi
api = dexapi.dexAPI("API_KEY", network="ethereum")
api.get_trades("0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640", "2022-03-15T14:55:55")
```