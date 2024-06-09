import { writable } from 'svelte/store';

export const session_id = writable(null);
export const currentView = writable('statistics'); // Default view