import pickle
import pandas as pd
import numpy as np
from starknet_py.net.full_node_client import FullNodeClient
from src.utils.ekubo_math import bool_to_sign, price_to_tick_id

class EkuboData:
    def __init__(self, client_url, contract_address, token0_address=None, token1_address=None, pool_fee=None, tick_spacing=None):
        self.client = FullNodeClient(node_url=client_url)
        self.contract_address = contract_address
        self.token0_address = token0_address.lower() if token0_address else None
        self.token1_address = token1_address.lower() if token1_address else None
        self.pool_fee_touse = pool_fee
        self.tick_spacing_touse = tick_spacing

    async def get_events(self, event_key, from_block, to_block):
        return await self.client.get_events(
            address=self.contract_address,
            keys=[event_key],
            from_block_number=from_block,
            to_block_number=to_block,
            follow_continuation_token=True,
            chunk_size=47,
        )

    @staticmethod
    def save_events_to_file(events, filename):
        with open(filename, 'wb') as f:
            pickle.dump(events, f)

    @staticmethod
    def load_events_from_file(filename):
        with open(filename, 'rb') as f:
            return pickle.load(f)

    def filter_events(self, events):
        valid_events = []
        for event in events:
            if (hex(event.data[1]).lower() == self.token0_address and  # Token0 address
                hex(event.data[2]).lower() == self.token1_address and  # Token1 address
                event.data[3] == self.pool_fee_touse and  # Pool fee
                event.data[4] == self.tick_spacing_touse):  # Tick spacing
                valid_events.append(event)
        return valid_events

    def process_events(self, events_response_positions_updated, combined_events_response_swap):
        valid_liquidity_events = self.filter_events(events_response_positions_updated)
        valid_swap_events = self.filter_events(combined_events_response_swap)

        liquidity_data = []
        swap_data = []

        for event in valid_liquidity_events:
            event_data = {
                'block_number': event.block_number,
                'transaction_hash': event.transaction_hash,  
                'delta_liquidity': event.data[11] * bool_to_sign(event.data[12]),
                'tick_lower': event.data[7] * bool_to_sign(event.data[8]),
                'tick_upper': event.data[9] * bool_to_sign(event.data[10])
            }
            liquidity_data.append(event_data)

        for event in valid_swap_events:
            event_data = {
                'block_number': event.block_number,
                'transaction_hash': event.transaction_hash,
                'price': 1.000001**(event.data[18] * bool_to_sign(event.data[19])),
                'tick_id': event.data[18] * bool_to_sign(event.data[19]),
                'liquidity_after': event.data[20],
                'amount0': event.data[12] * bool_to_sign(event.data[13]),  # 0 swapping +ve 
                'amount1': event.data[14] * bool_to_sign(event.data[15])
            }
            swap_data.append(event_data)
        
        df_liquidity = pd.DataFrame(liquidity_data)
        df_swap = pd.DataFrame(swap_data)
        
        return df_liquidity, df_swap

    def compute_cumulative_liquidity(self, data_swap, data_liquidity, price_range_liquidity = 20):
        # Collect block numbers and prices from swap data
        block_price_data = [{'block_number': event['block_number'], 'price': event['price']} for event in data_swap]

        # Convert to DataFrame and calculate median price per block
        df = pd.DataFrame(block_price_data)
        median_prices_df = df.groupby('block_number')['price'].median().reset_index()

        # Add price boundaries and convert them to tick IDs
        median_prices_df['tick_id_median'] = median_prices_df['price'].apply(price_to_tick_id)
        median_prices_df['tick_id_minus%'] = median_prices_df['price'] * (1 - price_range_liquidity * 0.01)
        median_prices_df['tick_id_plus%'] = median_prices_df['price'] * (1 + price_range_liquidity * 0.01)

        # Create tick arrays without rounding
        median_prices_df['tick_id_array'] = median_prices_df.apply(
            lambda row: np.arange(
                price_to_tick_id(row['tick_id_minus%']),
                price_to_tick_id(row['tick_id_plus%']) + self.tick_spacing_touse,
                self.tick_spacing_touse
            ), axis=1
        )

        # Distribute cumulative liquidity per block
        cumulative_liquidity_per_tick = {}
        liquidity_per_block = []

        for _, row in median_prices_df.iterrows():
            block_number = row['block_number']
            tick_array = row['tick_id_array']

            # Initialize or clone current cumulative liquidity state
            current_block_liquidity = cumulative_liquidity_per_tick.copy() or {tick: 0 for tick in tick_array}

            # Update liquidity for the current block
            for event in [e for e in data_liquidity if e['block_number'] == block_number]:
                for tick in tick_array:
                    if event['tick_lower'] <= tick <= event['tick_upper']:
                        current_block_liquidity[tick] += event['delta_liquidity']

            # Update cumulative state and store the result
            cumulative_liquidity_per_tick = current_block_liquidity.copy()
            liquidity_per_block.append({
                'block_number': block_number,
                'tick_liquidity_distribution': current_block_liquidity
            })

        return pd.DataFrame(liquidity_per_block)
