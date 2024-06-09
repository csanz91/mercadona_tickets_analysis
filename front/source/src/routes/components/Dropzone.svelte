<script>
	import { onMount } from 'svelte';
	import { upload_files_url, deleteSession } from '../api';
	// If you are using JavaScript/ECMAScript modules:
	import Dropzone from 'dropzone';
	import 'dropzone/dist/dropzone.css';
	import { session_id } from '../stores';
	import Cookies from 'js-cookie';

	import '../styles.css';

	let wrapper;
	let myDropzone;

	onMount(() => {
		myDropzone = new Dropzone(wrapper, {
			url: upload_files_url,
			maxFiles: 100,
			parallelUploads: 100,
			uploadMultiple: true,
			autoProcessQueue: true,
			paramName: 'files',
			init: function () {
				this.on('sending', function (file, xhr, formData) {
					formData.append('files', file); // Ensures each file gets appended to 'files'
				});
			}
		});
		myDropzone.on('complete', function (file) {
			myDropzone.removeFile(file);
		});
		myDropzone.on('successmultiple', async function (file, response) {
			if (response.session_id) {
				await deleteSession();
				session_id.set(response.session_id);
				Cookies.set('session_id', response.session_id);
				console.log('Session ID set:', response.session_id);
			}
		});
	});
</script>

<form bind:this={wrapper} class="dropzone">
	<div class="dz-message">Arrastre aqui los tickets en .pdf</div>
</form>

<style>
	.dropzone {
		border: 4px solid var(--color-theme-2);
		color: var(--color-text);
		margin: 2rem 0;
	}
</style>
