<script>
	import { onMount } from 'svelte';
	import { getProducts, generateGraph } from '../api';
	import { Line } from 'svelte-chartjs';
	import { session_id } from '../stores';

	import {
		Chart as ChartJS,
		Title,
		Tooltip,
		Legend,
		LineElement,
		LinearScale,
		PointElement,
		TimeScale
	} from 'chart.js';
	import 'chartjs-adapter-date-fns';

	ChartJS.register(Title, Tooltip, Legend, LineElement, LinearScale, PointElement, TimeScale);

	let products = [];
	let selectedProduct = '';
	let priceGraph = null;
	let chartOptions = {
		responsive: true,
		maintainAspectRatio: false,
		scales: {
			x: {
				type: 'time',
				time: {
					unit: 'day',
					tooltipFormat: 'PP'
				},
				title: {
					display: true,
					text: 'Date',
					font: {
						color: 'white'
					}
				},
				ticks: {
					color: 'white'
				}
			},
			y: {
				title: {
					display: true,
					text: 'Price',
					font: {
						color: 'white'
					}
				},
				ticks: {
					color: 'white'
				}
			}
		},
		plugins: {
			legend: {
				labels: {
					color: 'white'
				}
			}
		}
	};

	async function fetchProducts() {
		products = await getProducts();
	}

	async function fetchPriceGraph() {
		if (selectedProduct) {
			const response = await generateGraph(selectedProduct);
			const labels = Object.keys(response).map((date) => new Date(date));
			const data = Object.values(response);

			priceGraph = {
				labels: labels,
				datasets: [
					{
						label: 'Price Evolution',
						data: data,
						fill: false,
						borderColor: 'rgba(75, 192, 192, 1)',
						tension: 0.1
					}
				]
			};
		}
	}

	onMount(() => {
		const unsubscribe = session_id.subscribe(async (value) => {
			if (value) {
				await fetchProducts();
				priceGraph = null;
			} else {
				products = [];
				priceGraph = null;
			}
		});

		return unsubscribe;
	});

	$: if (selectedProduct) {
		fetchPriceGraph();
	}
</script>

<main>
	<!-- <label for="product-select">Selecciona un producto:</label> -->
	<select id="product-select" bind:value={selectedProduct}>
		<option value="">-- Selecciona un producto --</option>
		{#each products as product}
			<option value={product}>{product}</option>
		{/each}
	</select>

	{#if priceGraph}
		<div class="chart-container">
			<Line data={priceGraph} options={chartOptions} />
		</div>
	{:else}
		<p>Selecciona un producto para ver su evolucion de precio.</p>
	{/if}
</main>

<style>
	main {
		font-family: Arial, sans-serif;
		color: white; /* Set text color to white */
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: space-between;
	}

	select {
		padding: 0.5em;
		font-size: 1em;
		border: 1px solid #ccc;
		border-radius: 4px;
		background-color: #333; /* Set background color to dark gray */
		color: white; /* Set text color to white */
		width: 100%;
		max-width: 300px; /* Limit max width to 300px */
		margin-bottom: 1em; /* Add margin bottom to create a gap */
	}

	.chart-container {
		height: 300px; /* Increase height for larger graph */
		width: 100%;
		max-width: 1000px; /* Increase max width for larger graph */
	}
</style>
