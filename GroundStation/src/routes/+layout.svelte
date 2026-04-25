<script lang="ts">
	import favicon from '$lib/assets/favicon.svg';
  	import { Navbar, NavbarBrand, Image } from '@sveltestrap/sveltestrap';

	let { children } = $props();
</script>
        
<svelte:head><link rel="icon" href={favicon} />
</svelte:head>
<Navbar color="dark-subtle" dark expand="md" container="md">
    <NavbarBrand href="/" class="d-flex align-items-center gap-2">
        <Image fluid src="/images/logofinal.svg" width=60 />
        Astros Nó Atlântico
    </NavbarBrand>
</Navbar>
{@render children()}

<style>
    :global(.h2), :global(h2) {
        text-align: center;
    }
</style>