<script>
	import HelpTooltip from './HelpTooltip.svelte';
	import { session_id } from '../stores';
	import { fetchTicketsAnalysis } from '../api';
	import { onMount } from 'svelte';

	let tickets_analysis;

	// Function to fetch tickets analysis
	async function fetchTickets() {
		tickets_analysis = await fetchTicketsAnalysis();
	}

	// Call fetchTickets when the component mounts or when session_id changes
	onMount(() => {
		const unsubscribe = session_id.subscribe(async (value) => {
			if (value) {
				await fetchTickets();
			} else {
				tickets_analysis = null;
			}
		});

		// Cleanup function to unsubscribe when the component is unmounted
		return unsubscribe;
	});

	/**
	 * @param {number} price
	 */
	function formatPrice(price) {
		return price.toFixed(2) + ' €';
	}

	/**
	 * @param {string} product
	 * @param {number} count
	 */
	function formatProductCount(product, count) {
		const isBulkProduct = count % 1 !== 0;
		return isBulkProduct ? `${count.toFixed(2)} kg` : `${Math.round(count)} uni`;
	}
</script>

{#if tickets_analysis}
	<main>
		<h1>Estadísticas de Compra</h1>
		<div class="stats-container">
			<div class="stat-card">
				<span class="stat-label">Número de Compras:</span>
				<span class="stat-value">{tickets_analysis.num_shoppings}</span>
			</div>
			<div class="stat-card">
				<span class="stat-label">Total Gastado:</span>
				<span class="stat-value">{formatPrice(tickets_analysis.total_spent)}</span>
			</div>
			<div class="stat-card">
				<span class="stat-label">Costo Medio por Ticket:</span>
				<span class="stat-value">{formatPrice(tickets_analysis.mean_ticket_cost)}</span>
			</div>
			<div class="stat-card">
				<span class="stat-label">Promedio de Compras por Mes:</span>
				<span class="stat-value">{tickets_analysis.avg_shoppings_per_month.toFixed(2)}</span>
			</div>
			<div class="stat-card">
				<span class="stat-label">Costo Promedio por Mes:</span>
				<span class="stat-value">{formatPrice(tickets_analysis.avg_cost_per_month)}</span>
			</div>
		</div>

		<h2>
			Productos Populares
			<HelpTooltip text="Estos son los productos más comprados en términos de cantidad." />
		</h2>
		<ul class="product-list">
			{#each Object.entries(tickets_analysis.popular_products) as [product, count]}
				<li>
					<strong>{product}:</strong>
					{formatProductCount(product, count)}
				</li>
			{/each}
		</ul>

		<h2>
			Mayores Reducciones de Precios
			<HelpTooltip text="Estos son los productos más comprados en términos de cantidad." />
		</h2>
		<ul class="product-list">
			{#each Object.entries(tickets_analysis.top_prices_reductions) as [product, details]}
				<li>
					<strong>{product}:</strong>
					<span class="price-change">
						{formatPrice(details.Diff_Unit_Price)} (de {formatPrice(details.Initial_Unit_Price)} el
						{new Date(details.Final_Date).toLocaleDateString()} a {formatPrice(
							details.Final_Unit_Price
						)})</span
					>
				</li>
			{/each}
		</ul>

		<h2>
			Mayores Aumentos de Precios
			<HelpTooltip text="Estos son los productos más comprados en términos de cantidad." />
		</h2>
		<ul class="product-list">
			{#each Object.entries(tickets_analysis.top_prices_increses) as [product, details]}
				<li>
					<strong>{product}:</strong>
					<span class="price-change">
						+{formatPrice(details.Diff_Unit_Price)} (de {formatPrice(details.Initial_Unit_Price)} el
						{new Date(details.Final_Date).toLocaleDateString()} a {formatPrice(
							details.Final_Unit_Price
						)})</span
					>
				</li>
			{/each}
		</ul>

		<h2>
			Productos Más Frecuentes
			<HelpTooltip text="Estos son los productos más comprados en términos de cantidad." />
		</h2>
		<ul class="product-list">
			{#each Object.entries(tickets_analysis.most_frequent_products) as [product, frequency]}
				<li>
					<strong>{product}:</strong>
					{frequency.toFixed(2)}%
				</li>
			{/each}
		</ul>

		<h2>
			Productos Más Caros
			<HelpTooltip text="Estos son los productos más comprados en términos de cantidad." />
		</h2>
		<ul class="product-list">
			{#each Object.entries(tickets_analysis.most_expensive_products) as [product, price]}
				<li>
					<strong>{product}:</strong>
					{formatPrice(price)}
				</li>
			{/each}
		</ul>

		<h2>
			Productos Más Baratos
			<HelpTooltip text="Estos son los productos más comprados en términos de cantidad." />
		</h2>
		<ul class="product-list">
			{#each Object.entries(tickets_analysis.chepeast_products) as [product, price]}
				<li>
					<strong>{product}:</strong>
					{formatPrice(price)}
				</li>
			{/each}
		</ul>
	</main>
{/if}

<style>
	main {
		font-family: Arial, sans-serif;
		padding: 1em;
		max-width: 800px;
		margin: 0 auto;
		box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
		border-radius: 8px;
		background-color: #222;
		color: #fff;
	}

	h1,
	h2 {
		color: #fff;
		text-align: center;
	}

	.stats-container {
		display: flex;
		flex-wrap: wrap;
		justify-content: space-around;
		margin-bottom: 2em;
	}

	.stat-card {
		background-color: #333;
		padding: 1em;
		border-radius: 8px;
		box-shadow: 0 0 5px rgba(0, 0, 0, 0.3);
		text-align: center;
		margin: 0.5em;
		flex-basis: 200px;
	}

	.stat-label {
		display: block;
		font-weight: bold;
		color: #ccc;
		margin-bottom: 0.5em;
	}

	.stat-value {
		font-size: 1.2em;
		font-weight: bold;
		color: #fff;
	}

	.product-list {
		list-style: none;
		padding: 0;
		margin: 0 auto;
		max-width: 600px;
	}

	.product-list li {
		background: #333;
		margin: 0.5em 0;
		padding: 0.5em 1em;
		border-radius: 4px;
		box-shadow: 0 0 5px rgba(0, 0, 0, 0.3);
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	strong {
		color: #f8b500;
		margin-right: 0.5em;
	}

	.price-change {
		color: #ccc;
		font-style: italic;
	}
</style>
