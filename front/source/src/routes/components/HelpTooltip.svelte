<script>
	export let text = 'This is a help message.';
	let showPopover = false;
</script>

<div
	class="help-icon"
	role="tooltip"
	on:mouseenter={() => (showPopover = true)}
	on:mouseleave={() => (showPopover = false)}
>
	?
	{#if showPopover}
		<div class="popover">
			{text}
		</div>
	{/if}
</div>

<style>
	.help-icon {
		display: inline-block;
		width: 16px;
		height: 16px;
		line-height: 16px;
		text-align: center;
		background-color: #f8b500;
		color: #222;
		border-radius: 50%;
		font-size: 12px;
		margin-left: 0.5em;
		cursor: help;
		position: relative;
	}

	.popover {
		display: inline-block;
		visibility: hidden;
		width: 200px;
		background-color: #555;
		color: #fff;
		text-align: center;
		border-radius: 6px;
		padding: 8px;
		position: absolute;
		z-index: 1;
		bottom: 125%; /* Position the popover above the icon */
		left: 50%;
		margin-left: -100px; /* Center the popover */
		opacity: 0;
		transition: opacity 0.3s;
	}

	.popover::after {
		content: '';
		position: absolute;
		top: 100%;
		left: 50%;
		margin-left: -5px;
		border-width: 5px;
		border-style: solid;
		border-color: #555 transparent transparent transparent;
	}

	.help-icon:hover .popover {
		visibility: visible;
		opacity: 1;
	}
</style>
