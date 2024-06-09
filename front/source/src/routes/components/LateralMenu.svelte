<script>
	import Dropzone from './Dropzone.svelte';
	import { deleteSession } from '../api';
	import { currentView } from '../stores';

	function showStatistics() {
		currentView.set('statistics');
	}

	function showGraph() {
		currentView.set('graph');
	}
</script>

<div class="sidebar">
	<Dropzone />
	<button on:click={showStatistics}>Generar Estadísticas</button>
	<button on:click={showGraph}>Grafica Precios</button>
	<button on:click={() => deleteSession()}>Borrar Datos</button>
</div>

<style>
	.sidebar {
		position: fixed;
		left: 0;
		top: 0;
		height: 100%;
		width: 200px;
		background-color: #333;
		color: white;
		display: flex;
		flex-direction: column;
		padding: 1em;
	}

	button {
		background-color: #555;
		color: white;
		padding: 0.5em 1em;
		border: none;
		border-radius: 4px;
		cursor: pointer;
		margin-bottom: 0.5em;
		transition: background-color 0.3s ease;
	}

	button:hover {
		background-color: #777;
	}
</style>
