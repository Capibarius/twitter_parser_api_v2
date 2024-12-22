import re

class BlockchainAddressFinder:
    def find_all_blockchain_addresses(self, text):
        """
        Находит все адреса блокчейна в заданном тексте.
        
        Args:
            text (str): Текст, в котором нужно искать адреса.

        Returns:
            list: Список кортежей с адресами и типами криптовалют, найденными в тексте.
                Пример: [(адрес, 'BTC'), (адрес, 'ETH')]
        """
        # Обновленные регулярные выражения без захватывающих групп
        btc_pattern = r'(?<![a-zA-Z0-9])(?:1[a-zA-Z0-9]{25,33}|3[a-zA-Z0-9]{25,33}|bc1[a-zA-Z0-9]{23,42}|bc1p[a-zA-Z0-9]{23,42})(?![a-zA-Z0-9])'
        eth_pattern = r'(?<![a-zA-Z0-9])(0x[0-9A-Fa-f]{40})(?![a-zA-Z0-9])'
        trx_pattern = r'(?<![a-zA-Z0-9])(T[A-Za-z1-9]{33})(?![a-zA-Z0-9])'

        # Заменяем символы новой строки на пробелы
        text = text.replace('\n', ' ')

        addresses = []

        # Bitcoin
        btc_addresses = re.findall(btc_pattern, text)
        addresses.extend([(address.strip(), 'BTC') for address in btc_addresses])

        # Ethereum
        eth_addresses = re.findall(eth_pattern, text)
        addresses.extend([(address.strip(), 'ETH') for address in eth_addresses])

        # Tron
        trx_addresses = re.findall(trx_pattern, text)
        addresses.extend([(address.strip(), 'TRX') for address in trx_addresses])

        return addresses
