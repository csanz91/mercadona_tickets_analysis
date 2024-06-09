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
	</div>
</div>

<style>
	.app-container {
		display: flex;
		min-height: 100vh;
	}
	.content {
		margin-left: 200px; /* Width of the sidebar */
		padding: 2em;
		flex: 1;
	}
</style>
