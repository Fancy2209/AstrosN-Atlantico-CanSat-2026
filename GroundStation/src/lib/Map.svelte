<script lang="ts">
	import { onMount } from 'svelte';
	import { Viewer } from 'cesium';
	import '../node_modules/cesium/Build/Cesium/Widgets/widgets.css'

	(window as any).CESIUM_BASE_URL = './build';

    let viewer: Viewer;
	onMount(async () => {
		viewer = new Viewer('cesiumContainer');
	});
	
</script>

<div id="cesiumContainer">
</div>

<style>
:root(html), :root(body), #cesiumContainer {
    width: 100%;
    height: 100%;
    margin: 0;  
    padding: 0;
    overflow: hidden;
}
</style>