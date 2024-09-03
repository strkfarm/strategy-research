import math
from src.utils.ekubo_math import price_to_tick, impermanent_loss

class EkuboStrategyBase:
    def run_simulation(self, liquidity_range, rebalance_range, train_swap_df, initial_liquidity=10000000, fee_percentage=0.00001, decimal = 18):
        """
        Run a simulation based on the provided swap data and strategy parameters.

        Parameters:
        - liquidity_range: The range within which liquidity is considered active.
        - rebalance_range: The range within which rebalancing is not triggered.
        - train_swap_df: DataFrame containing the swap events to simulate.
        - initial_liquidity: Initial liquidity provided in the pool.
        - fee_percentage: The fee percentage for swaps.

        Returns:
        - net_earnings: Net earnings after considering fees and impermanent loss.
        - fees_earned: Total fees earned during the simulation.
        - impermanent_loss_total: Total impermanent loss during the simulation.
        """
        # Check if train_swap_df is empty
        if train_swap_df.empty:
            raise ValueError("train_swap_df is empty, cannot run simulation.")

        # Ensure the price column exists
        if 'price' not in train_swap_df.columns:
            raise ValueError("The 'price' column is missing in train_swap_df.")

        initial_price = train_swap_df['price'].iloc[0]
        fees_earned = 0
        impermanent_loss_total = 0
        current_liquidity = initial_liquidity

        for swap_event in train_swap_df.itertuples():
            current_price = swap_event.price
            amount_swapped = swap_event.amount1
            available_liquidity = swap_event.liquidity_after

            current_tick = price_to_tick(current_price)
            liquidity_lower_bound = initial_price * (1 - liquidity_range)
            liquidity_upper_bound = initial_price * (1 + liquidity_range)
            tick_lower_bound = price_to_tick(liquidity_lower_bound)
            tick_upper_bound = price_to_tick(liquidity_upper_bound)

            if tick_lower_bound <= current_tick <= tick_upper_bound:
                fees_earned += abs(amount_swapped) / 10**decimal * fee_percentage * current_liquidity / available_liquidity

            rebalance_lower_bound = initial_price * (1 - rebalance_range)
            rebalance_upper_bound = initial_price * (1 + rebalance_range)

            if not (rebalance_lower_bound <= current_price <= rebalance_upper_bound):
                price_ratio = current_price / initial_price
                il = impermanent_loss(price_ratio)
                impermanent_loss_total += il
                current_liquidity += fees_earned
                fees_earned = 0
                initial_price = current_price

        net_earnings = fees_earned - impermanent_loss_total
        return net_earnings, fees_earned, impermanent_loss_total
