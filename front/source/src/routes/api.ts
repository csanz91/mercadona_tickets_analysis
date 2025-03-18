// api.js
import Cookies from 'js-cookie';
import { get } from 'svelte/store'
import { session_id } from './stores';

// const server_url = "http://localhost:8089";
const server_url = "api"

export const upload_files_url = `${server_url}/upload-tickets`


// Function to fetch tickets analysis from the API
export async function fetchTicketsAnalysis() {
  const session = get(session_id);
  if (!session) {
    console.log("Session id not found. Please upload first the files")
    return;
  }

  console.log("Getting analysis");

  const response = await fetch(`${server_url}/get-tickets-analysis?session_id=${session}`);
  if (response.status === 404) {
    deleteLocalSession();
    return null;
  }
  const data = await response.json();
  return data
}
// Function to fetch tickets analysis from the API
export async function generateGraph(selectedProduct: string) {
  const session = get(session_id);
  if (!session) {
    console.log("Session id not found. Please upload first the files");
    return;
  }

  const response = await fetch(`${server_url}/price-evolution?session_id=${session}&product_name=${selectedProduct}`);

  if (response.status === 404) {
    deleteLocalSession();
    return null;
  }

  const data = await response.json();
  return data;
}

export async function getProducts() {
  const session = get(session_id);
  if (!session) {
    console.log("Session id not found. Please upload first the files")
    return [];
  }

  const response = await fetch(`${server_url}/get-product-names?session_id=${session}`);
  if (response.status === 404) {
    deleteLocalSession();
    return [];
  }
  const data = await response.json();
  return data;
}

// Function to delete the session from the API
export async function deleteSession() {
  const session = get(session_id);
  if (!session) {
    console.log("Session id not found.")
    return;
  }

  await fetch(`${server_url}/delete-session?session_id=${session}`, {
    method: 'POST',
  }).finally(deleteLocalSession);
  console.log('Session %s deleted from API', session);
}

// Function to delete the session_id cookie and reset data
export function deleteLocalSession() {
  Cookies.remove('session_id');
  session_id.set(null);
  console.log('Session cookie deleted');
}
