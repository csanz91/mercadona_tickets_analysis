<script>
	import { onMount } from 'svelte';
	import Cookies from 'js-cookie';
	import { session_id, currentView } from './stores';
	import TicketAnalysis from './components/TicketsAnalysis.svelte';
	import Graph from './components/Graph.svelte';
	import LateralMenu from './components/LateralMenu.svelte';

	onMount(() => {
		const currentSessionId = Cookies.get('session_id');
		if (currentSessionId) {
			session_id.set(currentSessionId);
		}
	});
</script>

<div class="app-container">
	<LateralMenu />
	<div class="content">
		{#if $currentView === 'statistics'}
			<TicketAnalysis />
		{:else if $currentView === 'graph'}
			<Graph />
		{/if}
		<footer>
			<div>
				Cesar Sanz Martinez - <a href="mailto:cesarsanz91@gmail.com">cesarsanz91@gmail.com</a> - 2024
				- Open to Work!
			</div>
			<div>
				Visita <a href="https://github.com/csanz91/mercadona_tickets_analysis">Github</a> para obtener
				el codigo fuente de esta pagina
			</div>
		</footer>
	</div>
</div>

<style>
	.app-container {
		display: flex;
		flex-direction: column;
		min-height: 100vh;
	}

	.content {
		flex: 1;
		margin-left: 200px; /* Width of the sidebar */
		padding: 2em;
		display: flex;
		flex-direction: column;
		justify-content: space-between;
	}

	footer {
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: center;
		padding: 12px;
	}
</style>
