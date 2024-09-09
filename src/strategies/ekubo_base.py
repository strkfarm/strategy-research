import pandas as pd
import matplotlib.pyplot as plt
from src.utils.ekubo_math import price_to_tick, impermanent_loss, get_capital_in_token1_terms_fromy, get_liquidity, get_capital_token1_terms_from_L, get_liquidity_from_token1_capital

class EkuboStrategyBase:
    def run_simulation(self, liquidity_range, rebalance_range, train_swap_df, ETH_provided, fee_percentage, decimal):
        """
        Run a simulation of a liquidity strategy based on provided swap events and strategy parameters.

        Parameters:
        - liquidity_range (float): The percentage range within which liquidity is considered active. 
                                   For example, if liquidity_range=0.2, then liquidity is active between 80% and 120% of the initial price.
        - rebalance_range (float): The percentage range within which rebalancing is not triggered. 
                                   If the price moves outside this range, liquidity is rebalanced.
        - train_swap_df (pd.DataFrame): A pandas DataFrame containing swap events, including columns like 'price', 'amount1', 'liquidity_after', and 'block_number'.
        - initial_liquidity (int): Initial liquidity provided in the pool.
        - fee_percentage (float): The fee percentage earned on each swap in fraction i.e value 0.00001 is 0.001%.
        - decimal (int): The decimal precision of the token, usually 18 for ERC20 tokens.

        Returns:
        - block_vs_returns (pd.DataFrame): A DataFrame containing the block number and corresponding cumulative returns.
        - net_earnings (float): Net earnings after considering both fees earned and impermanent loss.
        - fees_earned (float): Total fees earned throughout the simulation.
        - impermanent_loss_total (float): Total impermanent loss incurred during the simulation.

        Raises:
        - ValueError: If the `train_swap_df` is empty or if the 'price' or 'block_number' column is missing.
        """
        
        # Check if the swap DataFrame is empty; raise an error if no data to simulate.
        if train_swap_df.empty:
            raise ValueError("train_swap_df is empty, cannot run simulation.")

        # Ensure the 'price' and 'block_number' columns exist in the DataFrame; raise an error if missing.
        if 'price' not in train_swap_df.columns or 'block_number' not in train_swap_df.columns:
            raise ValueError("The 'price' or 'block_number' column is missing in train_swap_df.")

        # Initialize the starting price from the first row of the swap data.
        initial_price = train_swap_df['price'].iloc[0]
        
        # Initialize accumulators for fees earned and impermanent loss.
        fee_earned_ETH = 0
        impermanent_loss_total = 0
        # Determine the lower and upper bounds for active liquidity based on the liquidity range.
        liquidity_lower_bound = initial_price * (1 - liquidity_range)
        liquidity_upper_bound = initial_price * (1 + liquidity_range)
        sqrt_lower_bound = liquidity_lower_bound**0.5
        sqrt_upper_bound = liquidity_upper_bound**0.5
        sqrt_price = initial_price**0.5
        initial_capital_ETH = get_capital_token1_terms_from_L(ETH_provided, sqrt_price, sqrt_lower_bound, sqrt_upper_bound)
        initial_liquidity = get_liquidity(ETH_provided, sqrt_price, sqrt_lower_bound)
        current_liquidity = initial_liquidity
        
        # List to store block-based returns
        block_vs_returns = []
        
        # Iterate through each row of the swap data (each swap event).
        for swap_event in train_swap_df.itertuples():
            current_price = swap_event.price  # Extract the current price from the swap event.
            amount_swapped = swap_event.amount1  # Get the swapped amount for token1. # Note: this is specific for this pool. We want in ETH
            available_liquidity = swap_event.liquidity_after  # Get the liquidity after the swap event.
            block_number = swap_event.block_number  # Extract the block number for tracking.
            # Convert the current price to its corresponding tick value.
            current_tick = price_to_tick(current_price)

            # Determine the lower and upper bounds for active liquidity based on the liquidity range.
            liquidity_lower_bound = initial_price * (1 - liquidity_range)
            liquidity_upper_bound = initial_price * (1 + liquidity_range)
            # Convert liquidity in ETH terms
            initial_capital_ETH = get_capital_token1_terms_from_L(initial_liquidity, initial_price**0.5, liquidity_lower_bound**0.5, liquidity_upper_bound**0.5)   
            current_capital_ETH = initial_capital_ETH

            # Convert the liquidity range to tick values.
            tick_lower_bound = price_to_tick(liquidity_lower_bound)
            tick_upper_bound = price_to_tick(liquidity_upper_bound)

            # Check if the current tick falls within the active liquidity range.
            if tick_lower_bound <= current_tick <= tick_upper_bound:
                # Calculate the fees earned from this swap based on the fee percentage, amount swapped, and liquidity.
                fee_earned_ETH += (abs(amount_swapped) / 10**decimal) * fee_percentage * current_liquidity / available_liquidity
            # Calculate the lower and upper bounds for rebalancing based on the rebalance range.
            rebalance_lower_bound = initial_price * (1 - rebalance_range)
            rebalance_upper_bound = initial_price * (1 + rebalance_range)

            # If the current price moves outside the rebalance range, trigger a rebalance.
            if not (rebalance_lower_bound <= current_price <= rebalance_upper_bound):
                # Calculate the ratio of the current price to the initial price.
                price_ratio = current_price / initial_price

                # Calculate impermanent loss based on the price ratio.
                il = impermanent_loss(price_ratio)
                # Convert impermanent loss from a percentage to USD
                il_in_eth = il * current_capital_ETH  # Apply percentage to the current liquidity
          
                # Accumulate the impermanent loss to the total.
                impermanent_loss_total += il_in_eth

                # Add the earned fees to the current liquidity, simulating reinvestment.
                current_capital_ETH += fee_earned_ETH
                current_liquidity = get_liquidity_from_token1_capital(current_capital_ETH, sqrt_price, sqrt_lower_bound, sqrt_upper_bound)

                # Reset the earned fees after reinvesting them into liquidity.
                fee_earned_ETH = 0

                # Update the initial price to the current price to track changes in future iterations.
                initial_price = current_price

            # Calculate net earnings at this step
            net_earnings = fee_earned_ETH + current_capital_ETH - initial_capital_ETH - impermanent_loss_total
            
            # Calculate return as a percentage of initial liquidity
            return_percentage = (net_earnings / initial_liquidity) * 100
            
            # Record the block number and return at this step
            block_vs_returns.append((block_number, return_percentage))
        
        # Convert the list to a DataFrame
        block_vs_returns_df = pd.DataFrame(block_vs_returns, columns=['block_number', 'returns'])
        
        # Return the DataFrame containing returns by block number, net earnings, total fees, and impermanent loss.
        return block_vs_returns_df, net_earnings, return_percentage, fee_earned_ETH, impermanent_loss_total, current_liquidity