import pandas as pd
import requests
import datetime


class dexAPI:

    def __init__(self, api_key, network="ethereum"):
        """
        A Python wrapper class for bitquery.io DEX API.
        :param api_key: str, API key provided by bitquery.io
        :param network: str, optional, default = "ethereum", Ethereum network DEX runs, available options are: [
        "ethereum",
        "bsc"
        ]
        """
        self.api_key = api_key
        self.headers = {"X-API-KEY": self.api_key}
        self.session = requests.Session()
        self.network = network
        self.query = {}

    def __request(self):
        try:
            request = self.session.post("https://graphql.bitquery.io/", json=self.query, headers=self.headers)
        except Exception:
            raise dexAPIError("Can't connect to API. Check your internet connection.")
        if request.status_code == 403:
            raise dexAPIError(f"API Key is not valid. Check your key.")
        elif "errors" in request.json():
            raise dexAPIError(request.json()["errors"][0]["message"])
        return request.json()

    def __time_to_str(self, start, time):
        if start:
            end_str = "T00:00:00"
        else:
            end_str = "T23:59:00"
        if type(time) is datetime.date:
            return time.strftime("%Y-%m-%d") + end_str
        elif type(time) is datetime.datetime:
            return time.strftime("%Y-%m-%dT%H:%M:%S")
        elif type(time) is str and "T" not in time:
            return time + end_str
        else:
            return time

    def get_exchanges(self, start_time=datetime.date.today().strftime("%Y") + "-01-01",
                      end_time=datetime.datetime.now(), limit=20):
        """
        Class function returns highest volume (in USD) DEXs in network between two times.

        :param start_time: str | datetime, optional, default = first day of current year, format = "YYYY-MM-DD",
        datetime.date(YYYY,MM,DD), "YYYY-MM-DDTHH:MM:SS" (ISO8601DateTime), datetime.datetime(YYYY,MM,DD,HH,MM,SS),
        if hours, minutes, seconds are not specified it will be taken as 00:00:00
        :param end_time: str | datetime, optional, default = now, format = "YYYY-MM-DD",
        datetime.date(YYYY,MM,DD), "YYYY-MM-DDTHH:MM:SS" (ISO8601DateTime), datetime.datetime(YYYY,MM,DD,HH,MM,SS),
        if hours, minutes, seconds are not specified it will be taken as 23:59:59
        :param limit: int, optional, default = 20, maximum number of entries function returns

        :return: dataframe, columns = [
        "exchange": DEX name,
        "protocol": protocol DEX uses,
        "count": number of trades,
        "tradeAmount": total volume in USD,
        "exchangeAddress": address of exchange on network
        ]
        """
        query = """
        query ($limit: Int!, $start_time: ISO8601DateTime, $end_time: ISO8601DateTime, $network: EthereumNetwork) {
          ethereum(network: $network) {
            dexTrades(
              options: {limit: $limit, desc: "tradeAmount"}
              time: {since: $start_time, till: $end_time}
            ) {
              exchange {
                fullName
                address {
                  address
                }
              }
              protocol
              count
              tradeAmount(in: USD, calculate: sum)
            }
          }
        }
            """
        variables = {
            "network": self.network,
            "limit": limit,
            "start_time": self.__time_to_str(True, start_time),
            "end_time": self.__time_to_str(False, end_time)
        }
        data = {"query": query, "variables": variables}
        self.query = data
        raw_data = self.__request()
        df = pd.DataFrame(raw_data["data"]["ethereum"]["dexTrades"])
        if len(df) == 0:
            pass
        else:
            df["exchangeAddress"] = [i["address"]["address"] for i in df["exchange"]]
            df["exchange"] = [i["fullName"] for i in df["exchange"]]
        return df

    def get_pairs(self, exchange_address, start_time=datetime.date.today().strftime("%Y") + "-01-01",
                  end_time=datetime.datetime.now(), limit=100):
        """
        Class function returns highest volume (in USD) pairs in the DEX between two times.

        :param exchange_address: str, address of exchange on network
        :param start_time: str | datetime, optional, default = first day of current year, format = "YYYY-MM-DD",
        datetime.date(YYYY,MM,DD), "YYYY-MM-DDTHH:MM:SS" (ISO8601DateTime), datetime.datetime(YYYY,MM,DD,HH,MM,SS),
        if hours, minutes, seconds are not specified it will be taken as 00:00:00
        :param end_time: str | datetime, optional, default = now, format = "YYYY-MM-DD",
        datetime.date(YYYY,MM,DD), "YYYY-MM-DDTHH:MM:SS" (ISO8601DateTime), datetime.datetime(YYYY,MM,DD,HH,MM,SS),
        if hours, minutes, seconds are not specified it will be taken as 23:59:59
        :param limit: int, optional, default = 20, maximum number of entries function returns

        :return: dataframe, columns = [
        "exchange": DEX name,
        "protocol": protocol DEX uses,
        "currency1": first leg of swaps,
        "currency2": second leg of swap,
        "smartContract": address of smart contract trades pair on network
        ]
        """
        query = """
        query ($limit: Int!, $start_time: ISO8601DateTime, $end_time: ISO8601DateTime,
        $exchange_address: String!, $network: EthereumNetwork) {
          ethereum(network: $network) {
            dexTrades(
              options: {limit: $limit, desc: "tradeAmount"}
              time: {since: $start_time, till: $end_time}
              exchangeAddress: {is: $exchange_address}
            ) {
              protocol
              exchange {
                fullName
              }
              smartContract {
                address {
                  address
                }
              }
              tradeAmount(in: USD, calculate: sum)
              buyCurrency {
                symbol
              }
              sellCurrency {
                symbol
              }
            }
          }
        }
        """
        variables = {
            "network": self.network,
            "limit": limit * 2,
            "exchange_address": exchange_address,
            "start_time": self.__time_to_str(True, start_time),
            "end_time": self.__time_to_str(False, end_time)
        }
        data = {"query": query, "variables": variables}
        self.query = data
        raw_data = self.__request()
        df = pd.DataFrame(raw_data["data"]["ethereum"]["dexTrades"])
        if len(df) == 0:
            pass
        else:
            df["smartContract"] = [i["address"]["address"] for i in df["smartContract"]]
            df["currency1"] = [i["symbol"] for i in df["buyCurrency"]]
            df["currency2"] = [i["symbol"] for i in df["sellCurrency"]]
            df["exchange"] = [i["fullName"] for i in df["exchange"]]
            df = df[["exchange", "protocol", "currency1", "currency2", "smartContract"]]
            df = df.drop_duplicates(subset=["smartContract"])
            df.reset_index(drop=True, inplace=True)
        return df

    def get_trades(self, smart_contract, start_time=datetime.date.today(),
                   end_time=datetime.datetime.now(), limit=1000):
        """
        Class function returns most recent trades use the smart contract between two times.

        :param smart_contract: str, address of smart contract on network
        :param start_time: str | datetime, optional, default = today 00:00:00, format = "YYYY-MM-DD",
        datetime.date(YYYY,MM,DD), "YYYY-MM-DDTHH:MM:SS" (ISO8601DateTime), datetime.datetime(YYYY,MM,DD,HH,MM,SS),
        if hours, minutes, seconds are not specified it will be taken as 00:00:00
        :param end_time: str | datetime, optional, default = now, format = "YYYY-MM-DD",
        datetime.date(YYYY,MM,DD), "YYYY-MM-DDTHH:MM:SS" (ISO8601DateTime), datetime.datetime(YYYY,MM,DD,HH,MM,SS),
        if hours, minutes, seconds are not specified it will be taken as 23:59:59
        :param limit: int, optional, default = 1000, maximum number of entries function returns

        :return: dataframe, columns = [
        "exchange": DEX name,
        "protocol": protocol DEX uses,
        "timestamp": timestamp of block,
        "block": block height,
        "buyCurrency": currency DEX buys,
        "sellCurrency": currency DEX sells,
        "price": price of "buyCurrency" in terms of "sellCurrency",
        "tradeAmount": volume in USD
        "transaction": transaction hash
        ]
        """
        query = """
        query ($limit: Int!, $smart_contract: String!, $start_time: ISO8601DateTime,
        $end_time: ISO8601DateTime, $network: EthereumNetwork) {
          ethereum(network: $network) {
            dexTrades(
              options: {limit: $limit, desc: "block.height"}
              smartContractAddress: {is: $smart_contract}
              time: {since: $start_time, till: $end_time}
            ) {
              exchange {
                fullName
              }
              protocol
              buyAmount
              buyCurrency {
                symbol
              }
              sellAmount
              sellCurrency {
                symbol
              }
              tradeAmount(in: USD)
              count
              transaction {
                hash
              }
              price
              tradeIndex
              block {
                height
                timestamp {
                  time
                }
              }
            }
          }
        }
        """
        variables = {
            "limit": limit,
            "network": self.network,
            "smart_contract": smart_contract,
            "start_time": self.__time_to_str(True, start_time),
            "end_time": self.__time_to_str(False, end_time)
        }
        data = {"query": query, "variables": variables}
        self.query = data
        raw_data = self.__request()
        df = pd.DataFrame(raw_data["data"]["ethereum"]["dexTrades"])
        if len(df) == 0:
            pass
        else:
            df["buyCurrency"] = [i["symbol"] for i in df["buyCurrency"]]
            df["sellCurrency"] = [i["symbol"] for i in df["sellCurrency"]]
            df["exchange"] = [i["fullName"] for i in df["exchange"]]
            df["transaction"] = [i["hash"] for i in df["transaction"]]
            df["timestamp"] = [i["timestamp"]["time"] for i in df["block"]]
            df["block"] = [i["height"] for i in df["block"]]
            df = df[
                ["exchange", "protocol", "timestamp", "block", "buyCurrency", "buyAmount", "sellCurrency", "sellAmount",
                 "price", "tradeAmount", "transaction"]]
        return df

    def get_balances(self, address, time=datetime.datetime.now()):
        """
        Class function returns most recent trades use the smart contract between two times.

        :param address: str, address of pair on network
        :param time: str | datetime, optional, default = now, format = "YYYY-MM-DD",
        datetime.date(YYYY,MM,DD), "YYYY-MM-DDTHH:MM:SS" (ISO8601DateTime), datetime.datetime(YYYY,MM,DD,HH,MM,SS),
        if hours, minutes, seconds are not specified it will be taken as 23:59:59s

        :return: dataframe, columns = [
        "currency": currency symbol,
        "value": number of tokens owned by address,
        "currencyAddress": address of currency,
        ]
        """
        query = """
        query ($address: String!, $time: ISO8601DateTime, $network: EthereumNetwork) {
          ethereum(network: $network) {
            address(address: {is: $address}) {
              balances(time: {till: $time}) {
                currency {
                  address
                  symbol
                }
                value
              }
            }
          }
        }
        """
        variables = {
            "network": self.network,
            "time": self.__time_to_str(False, time),
            "address": address
        }
        data = {"query": query, "variables": variables}
        self.query = data
        raw_data = self.__request()
        df = pd.DataFrame(raw_data["data"]["ethereum"]["address"][0]["balances"])
        if len(df) == 0:
            pass
        else:
            df["currencyAddress"] = [i["address"] for i in df["currency"]]
            df["currency"] = [i["symbol"] for i in df["currency"]]
        return df


class dexAPIError(Exception):
    pass
